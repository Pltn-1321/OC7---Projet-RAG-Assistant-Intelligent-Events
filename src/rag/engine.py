"""RAG Engine - Moteur de recherche et génération réutilisable."""

import json
from pathlib import Path

import faiss
import numpy as np
from mistralai import Mistral

from src.config.settings import settings
from src.config.constants import PROCESSED_DATA_DIR


class RAGEngine:
    """Moteur RAG pour la recherche sémantique et la génération de réponses."""

    def __init__(self, index_dir: Path | None = None, documents_path: Path | None = None):
        """
        Initialise le moteur RAG.

        Args:
            index_dir: Chemin vers le répertoire de l'index FAISS.
            documents_path: Chemin vers le fichier JSON des documents.
        """
        self.index_dir = index_dir or PROCESSED_DATA_DIR / "faiss_index"
        self.documents_path = documents_path or PROCESSED_DATA_DIR / "rag_documents.json"

        # Charger l'index FAISS
        index_file = self.index_dir / "events.index"
        if not index_file.exists():
            raise FileNotFoundError(f"Index FAISS non trouvé: {index_file}")
        self.index = faiss.read_index(str(index_file))

        # Charger les documents
        if not self.documents_path.exists():
            raise FileNotFoundError(f"Documents non trouvés: {self.documents_path}")
        with open(self.documents_path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        # Charger la configuration de l'index
        config_file = self.index_dir / "config.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {"embedding_dim": 1024, "provider": "mistral"}

        # Client Mistral
        self.mistral_client = Mistral(api_key=settings.mistral_api_key)

        # Provider d'embeddings
        self.embedding_provider = self.config.get("provider", "mistral")

    def needs_rag(self, query: str) -> bool:
        """
        Détermine si la requête nécessite une recherche RAG.

        Returns:
            True si recherche d'événements, False si conversation simple.
        """
        classification_prompt = """Analyse cette requête et réponds uniquement par "SEARCH" ou "CHAT".

SEARCH = L'utilisateur cherche des événements, concerts, expos, spectacles, activités, sorties
CHAT = Salutations, remerciements, questions générales, bavardage

Exemples:
- "Bonjour" → CHAT
- "Merci beaucoup !" → CHAT
- "Comment ça marche ?" → CHAT
- "Tu peux m'aider ?" → CHAT
- "Concerts à Paris" → SEARCH
- "Que faire ce weekend ?" → SEARCH
- "Des expos intéressantes ?" → SEARCH
- "Y a quoi comme festivals ?" → SEARCH

Requête: "{query}"
Réponse:"""

        response = self.mistral_client.chat.complete(
            model=settings.llm_model,
            messages=[{"role": "user", "content": classification_prompt.format(query=query)}],
            temperature=0,
            max_tokens=10,
        )

        result = response.choices[0].message.content.strip().upper()
        return "SEARCH" in result

    def conversation_response(self, query: str, history: list[dict] | None = None) -> str:
        """Génère une réponse conversationnelle sans RAG."""
        system_prompt = """Tu es un assistant sympa spécialisé dans les événements culturels.

Personnalité :
- Tutoie l'utilisateur, sois chaleureux
- Réponds de façon concise
- Si on te demande ce que tu peux faire, explique que tu aides à trouver des événements (concerts, expos, spectacles, etc.)
- Encourage l'utilisateur à poser des questions sur les événements"""

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": query})

        response = self.mistral_client.chat.complete(
            model=settings.llm_model,
            messages=messages,
            temperature=settings.llm_temperature,
            max_tokens=settings.max_tokens,
        )

        return response.choices[0].message.content

    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode une requête en vecteur d'embedding.

        Args:
            query: Texte de la requête.

        Returns:
            Vecteur d'embedding normalisé.
        """
        if self.embedding_provider == "mistral":
            response = self.mistral_client.embeddings.create(
                model=settings.mistral_embedding_model, inputs=[query]
            )
            embedding = np.array([response.data[0].embedding], dtype=np.float32)
        else:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(settings.sentence_transformer_model)
            embedding = model.encode([query], convert_to_numpy=True)

        faiss.normalize_L2(embedding)
        return embedding

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Effectue une recherche sémantique.

        Args:
            query: Requête de recherche.
            top_k: Nombre de résultats à retourner.

        Returns:
            Liste de résultats avec document, similarité et distance.
        """
        query_embedding = self.encode_query(query)
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                results.append(
                    {
                        "document": doc,
                        "similarity": float(1 - dist),
                        "distance": float(dist),
                    }
                )

        return results

    def generate_response(
        self,
        query: str,
        results: list[dict],
        history: list[dict] | None = None,
    ) -> str:
        """
        Génère une réponse conversationnelle avec le LLM.

        Args:
            query: Question de l'utilisateur.
            results: Résultats de la recherche sémantique.
            history: Historique des messages [{"role": "user"|"assistant", "content": "..."}]

        Returns:
            Réponse générée par le LLM.
        """
        # Construire le contexte des événements
        if results:
            context = "Événements pertinents :\n\n"
            for i, result in enumerate(results, 1):
                doc = result["document"]
                context += f"Événement {i}:\n{doc['content']}\n\n"
        else:
            context = "Aucun événement trouvé pour cette recherche."

        system_prompt = f"""Tu es un assistant sympa qui aide à trouver des événements culturels.

Personnalité :
- Tutoie l'utilisateur, sois chaleureux et enthousiaste
- Réponds de façon concise (2-3 phrases max par événement)
- Si l'utilisateur pose une question de suivi, réfère-toi à la conversation précédente
- Si aucun événement ne correspond, propose des alternatives ou demande plus de précisions

{context}"""

        # Construire les messages avec historique
        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": query})

        response = self.mistral_client.chat.complete(
            model=settings.llm_model,
            messages=messages,
            temperature=settings.llm_temperature,
            max_tokens=settings.max_tokens,
        )

        return response.choices[0].message.content

    def chat(
        self,
        query: str,
        top_k: int = 5,
        history: list[dict] | None = None,
    ) -> dict:
        """
        Pipeline intelligent : détecte si RAG nécessaire.

        Args:
            query: Question de l'utilisateur.
            top_k: Nombre de documents à récupérer.
            history: Historique de conversation.

        Returns:
            Dictionnaire avec la réponse, sources et indicateur RAG.
        """
        # Déterminer si on a besoin du RAG
        use_rag = self.needs_rag(query)

        if use_rag:
            results = self.search(query, top_k=top_k)
            response = self.generate_response(query, results, history=history)
        else:
            results = []
            response = self.conversation_response(query, history=history)

        return {
            "response": response,
            "sources": results,
            "query": query,
            "used_rag": use_rag,
        }

    @property
    def num_documents(self) -> int:
        """Nombre de documents indexés."""
        return len(self.documents)

    @property
    def embedding_dim(self) -> int:
        """Dimension des embeddings."""
        return self.config.get("embedding_dim", 1024)
