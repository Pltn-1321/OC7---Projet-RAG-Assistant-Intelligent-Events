"""Index Builder - Reconstruction de l'index FAISS avec LangChain.

This module provides the IndexBuilder class for building and saving
FAISS vector stores using LangChain's document and embedding abstractions.
"""

import json
import time
from pathlib import Path
from typing import Callable

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from src.config.constants import PROCESSED_DATA_DIR
from src.config.settings import settings
from src.rag.embeddings import get_embeddings


class IndexBuilder:
    """Construit l'index FAISS avec LangChain à partir des documents."""

    def __init__(self, progress_callback: Callable[[str, float], None] | None = None):
        """Initialise le constructeur d'index.

        Args:
            progress_callback: Callback optionnel pour les mises à jour de progression
                              (message, pourcentage entre 0 et 1)
        """
        self.progress_callback = progress_callback
        self.documents_path = PROCESSED_DATA_DIR / "rag_documents.json"
        self.index_dir = PROCESSED_DATA_DIR / "faiss_index"

    def _report_progress(self, message: str, percentage: float) -> None:
        """Rapporte la progression si un callback est défini."""
        if self.progress_callback:
            self.progress_callback(message, percentage)

    def load_documents(self) -> list[Document]:
        """Charge les documents et les convertit en format LangChain.

        Returns:
            Liste de LangChain Document objects.

        Raises:
            FileNotFoundError: Si le fichier n'existe pas.
        """
        if not self.documents_path.exists():
            raise FileNotFoundError(f"Documents non trouvés: {self.documents_path}")

        with open(self.documents_path, "r", encoding="utf-8") as f:
            raw_docs = json.load(f)

        # Convert to LangChain Documents
        documents = []
        for doc in raw_docs:
            lc_doc = Document(
                page_content=doc["content"],
                metadata={
                    "id": doc.get("id", ""),
                    "title": doc.get("title", ""),
                    **doc.get("metadata", {}),
                },
            )
            documents.append(lc_doc)

        return documents

    def build_and_save(self, documents: list[Document], batch_size: int = 32) -> dict:
        """Construit et sauvegarde l'index FAISS avec LangChain.

        Args:
            documents: Liste de LangChain Document objects.
            batch_size: Taille des lots pour le traitement.

        Returns:
            Configuration de l'index créé.
        """
        self._report_progress("Initialisation du modèle d'embeddings", 0.05)
        embeddings = get_embeddings()

        total = len(documents)
        self._report_progress(f"Génération des embeddings pour {total} documents", 0.10)

        # Build vectorstore with batch processing for progress reporting
        if total <= batch_size:
            vectorstore = FAISS.from_documents(documents, embeddings)
            self._report_progress("Embeddings générés", 0.70)
        else:
            # Build incrementally for progress reporting
            first_batch = documents[:batch_size]
            vectorstore = FAISS.from_documents(first_batch, embeddings)
            self._report_progress(f"Embeddings: {batch_size}/{total}", 0.15)

            for i in range(batch_size, total, batch_size):
                batch = documents[i : i + batch_size]
                vectorstore.add_documents(batch)

                # Progress from 15% to 70% during embedding generation
                progress = 0.15 + (min(i + batch_size, total) / total) * 0.55
                self._report_progress(
                    f"Embeddings: {min(i + batch_size, total)}/{total}", progress
                )

        self._report_progress("Construction de l'index FAISS terminée", 0.75)

        # Save using LangChain format
        self._report_progress("Sauvegarde de l'index", 0.80)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(self.index_dir))

        # Save config.json for compatibility
        config = {
            "provider": "mistral",
            "model_name": settings.embedding_model,
            "index_type": "FAISS_LangChain",
            "embedding_dim": settings.embedding_dimension,
            "num_vectors": total,
            "normalized": True,
            "documents_path": str(self.documents_path),
            "format": "langchain",
        }

        config_path = self.index_dir / "config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        self._report_progress("Sauvegarde terminée", 0.95)

        return config

    def rebuild(self) -> dict:
        """Exécute le pipeline complet de reconstruction de l'index.

        Returns:
            Dictionnaire avec les statistiques de reconstruction:
            {
                "status": "completed",
                "documents_processed": int,
                "embedding_dimension": int,
                "index_vectors": int,
                "elapsed_seconds": float,
                "provider": str,
                "model": str
            }

        Raises:
            FileNotFoundError: Si les documents source n'existent pas.
        """
        start_time = time.time()

        self._report_progress("Démarrage de la reconstruction", 0.0)

        # Load documents
        self._report_progress("Chargement des documents", 0.02)
        documents = self.load_documents()

        self._report_progress(f"{len(documents)} documents chargés", 0.05)

        # Build and save index
        config = self.build_and_save(documents)

        self._report_progress("Reconstruction terminée", 1.0)

        elapsed = time.time() - start_time

        return {
            "status": "completed",
            "documents_processed": len(documents),
            "embedding_dimension": config["embedding_dim"],
            "index_vectors": config["num_vectors"],
            "elapsed_seconds": round(elapsed, 2),
            "provider": "mistral",
            "model": settings.embedding_model,
        }
