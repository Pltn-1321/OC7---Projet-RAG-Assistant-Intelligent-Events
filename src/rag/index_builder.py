"""Index Builder - Reconstruction de l'index FAISS a la demande."""

import json
import time
from pathlib import Path
from typing import Callable

import faiss
import numpy as np
from mistralai import Mistral
from tqdm import tqdm

from src.config.constants import PROCESSED_DATA_DIR
from src.config.settings import settings


class IndexBuilder:
    """Construit l'index FAISS a partir des documents avec embeddings."""

    def __init__(self, progress_callback: Callable[[str, float], None] | None = None):
        """
        Initialise le constructeur d'index.

        Args:
            progress_callback: Callback optionnel pour les mises a jour de progression
                              (message, pourcentage entre 0 et 1)
        """
        self.progress_callback = progress_callback
        self.documents_path = PROCESSED_DATA_DIR / "rag_documents.json"
        self.embeddings_dir = PROCESSED_DATA_DIR / "embeddings"
        self.index_dir = PROCESSED_DATA_DIR / "faiss_index"

    def _report_progress(self, message: str, percentage: float) -> None:
        """Rapporte la progression si un callback est defini."""
        if self.progress_callback:
            self.progress_callback(message, percentage)

    def load_documents(self) -> list[dict]:
        """
        Charge les documents depuis le fichier JSON.

        Returns:
            Liste des documents.

        Raises:
            FileNotFoundError: Si le fichier n'existe pas.
        """
        if not self.documents_path.exists():
            raise FileNotFoundError(f"Documents non trouves: {self.documents_path}")

        with open(self.documents_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_embeddings(
        self, documents: list[dict], batch_size: int = 32
    ) -> np.ndarray:
        """
        Genere les embeddings pour les documents.

        Args:
            documents: Liste des documents avec champ 'content'.
            batch_size: Taille des lots pour le traitement.

        Returns:
            Array numpy des embeddings (num_docs, embedding_dim).
        """
        self._report_progress("Initialisation du modele d'embeddings", 0.05)

        contents = [doc["content"] for doc in documents]

        if settings.embedding_provider == "mistral":
            return self._generate_mistral_embeddings(contents, batch_size)
        else:
            return self._generate_sentence_transformer_embeddings(contents, batch_size)

    def _generate_mistral_embeddings(
        self, contents: list[str], batch_size: int
    ) -> np.ndarray:
        """Genere les embeddings avec l'API Mistral."""
        client = Mistral(api_key=settings.mistral_api_key)
        embeddings = []

        total_batches = (len(contents) + batch_size - 1) // batch_size

        for i in range(0, len(contents), batch_size):
            batch = contents[i : i + batch_size]

            response = client.embeddings.create(
                model=settings.mistral_embedding_model, inputs=batch
            )

            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)

            # Progression : 5% -> 65% pour les embeddings
            progress = 0.05 + (i + len(batch)) / len(contents) * 0.6
            self._report_progress(
                f"Generation embeddings: {i + len(batch)}/{len(contents)}", progress
            )

        return np.array(embeddings, dtype=np.float32)

    def _generate_sentence_transformer_embeddings(
        self, contents: list[str], batch_size: int
    ) -> np.ndarray:
        """Genere les embeddings avec SentenceTransformers."""
        from sentence_transformers import SentenceTransformer

        self._report_progress("Chargement du modele SentenceTransformer", 0.10)

        model = SentenceTransformer(settings.sentence_transformer_model)

        self._report_progress("Generation des embeddings", 0.15)

        embeddings = model.encode(
            contents,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        self._report_progress("Embeddings generes", 0.65)

        return embeddings.astype(np.float32)

    def build_index(self, embeddings: np.ndarray) -> faiss.Index:
        """
        Construit l'index FAISS a partir des embeddings.

        Args:
            embeddings: Array numpy des embeddings.

        Returns:
            Index FAISS pret pour la recherche.
        """
        self._report_progress("Construction de l'index FAISS", 0.70)

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)

        # Normaliser pour la similarite cosinus
        embeddings_copy = embeddings.copy()
        faiss.normalize_L2(embeddings_copy)
        index.add(embeddings_copy)

        self._report_progress("Index FAISS construit", 0.80)

        return index

    def save_index(
        self,
        index: faiss.Index,
        embeddings: np.ndarray,
        documents: list[dict],
    ) -> None:
        """
        Sauvegarde l'index et les metadonnees sur disque.

        Args:
            index: Index FAISS a sauvegarder.
            embeddings: Embeddings generes.
            documents: Documents sources.
        """
        self._report_progress("Sauvegarde de l'index", 0.85)

        # Creer les repertoires
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)

        # Sauvegarder l'index FAISS
        index_path = self.index_dir / "events.index"
        faiss.write_index(index, str(index_path))

        # Sauvegarder la configuration de l'index
        config = {
            "provider": settings.embedding_provider,
            "model_name": settings.embedding_model,
            "index_type": "IndexFlatL2",
            "embedding_dim": embeddings.shape[1],
            "num_vectors": index.ntotal,
            "normalized": True,
            "documents_path": str(self.documents_path),
        }

        config_path = self.index_dir / "config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        self._report_progress("Sauvegarde des embeddings", 0.90)

        # Sauvegarder les embeddings
        embeddings_path = self.embeddings_dir / "embeddings.npy"
        np.save(embeddings_path, embeddings)

        # Sauvegarder les metadonnees des embeddings
        metadata = {
            "provider": settings.embedding_provider,
            "model_name": settings.embedding_model,
            "embedding_dim": embeddings.shape[1],
            "num_documents": len(embeddings),
            "document_ids": [doc.get("id", str(i)) for i, doc in enumerate(documents)],
        }

        metadata_path = self.embeddings_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        self._report_progress("Sauvegarde terminee", 0.95)

    def rebuild(self) -> dict:
        """
        Execute le pipeline complet de reconstruction de l'index.

        Returns:
            Dictionnaire avec les statistiques de reconstruction.

        Raises:
            FileNotFoundError: Si les documents source n'existent pas.
            Exception: En cas d'erreur pendant la reconstruction.
        """
        start_time = time.time()

        self._report_progress("Demarrage de la reconstruction", 0.0)

        # Charger les documents
        self._report_progress("Chargement des documents", 0.02)
        documents = self.load_documents()

        # Generer les embeddings
        embeddings = self.generate_embeddings(documents)

        # Construire l'index
        index = self.build_index(embeddings)

        # Sauvegarder
        self.save_index(index, embeddings, documents)

        self._report_progress("Reconstruction terminee", 1.0)

        elapsed = time.time() - start_time

        return {
            "status": "completed",
            "documents_processed": len(documents),
            "embedding_dimension": embeddings.shape[1],
            "index_vectors": index.ntotal,
            "elapsed_seconds": round(elapsed, 2),
            "provider": settings.embedding_provider,
            "model": settings.embedding_model,
        }
