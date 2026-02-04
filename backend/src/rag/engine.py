"""RAG Engine - Moteur de recherche et génération avec LangChain LCEL.

This module provides the main RAGEngine class that orchestrates the RAG pipeline
using LangChain components (LCEL chains, FAISS vector store, ChatMistralAI).
"""

import json
from pathlib import Path

import faiss
import numpy as np
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.config.constants import (
    CLASSIFICATION_PROMPT_TEMPLATE,
    CONVERSATION_SYSTEM_PROMPT,
    PROCESSED_DATA_DIR,
    RAG_SYSTEM_PROMPT_TEMPLATE,
)
from src.config.settings import settings
from src.rag.embeddings import get_embeddings
from src.rag.llm import get_llm
from src.rag.vectorstore import load_vectorstore


class RAGEngine:
    """Moteur RAG pour la recherche sémantique et la génération de réponses.

    This class provides the same public interface as the previous SDK-based
    implementation but uses LangChain components internally.

    Public Interface (unchanged):
        - needs_rag(query: str) -> bool
        - conversation_response(query: str, history: list[dict] | None) -> str
        - encode_query(query: str) -> np.ndarray
        - search(query: str, top_k: int) -> list[dict]
        - generate_response(query: str, results: list[dict], history: list[dict] | None) -> str
        - chat(query: str, top_k: int, history: list[dict] | None) -> dict
        - num_documents: int (property)
        - embedding_dim: int (property)
    """

    def __init__(self, index_dir: Path | None = None, documents_path: Path | None = None):
        """Initialise le moteur RAG avec LangChain.

        Args:
            index_dir: Chemin vers le répertoire de l'index FAISS.
            documents_path: Chemin vers le fichier JSON des documents.
        """
        self.index_dir = index_dir or PROCESSED_DATA_DIR / "faiss_index"
        self.documents_path = documents_path or PROCESSED_DATA_DIR / "rag_documents.json"

        # Load documents (for metadata access and backward compatibility)
        if not self.documents_path.exists():
            raise FileNotFoundError(f"Documents non trouvés: {self.documents_path}")
        with open(self.documents_path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        # Load config
        config_file = self.index_dir / "config.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {"embedding_dim": 1024, "provider": "mistral"}

        # Initialize LangChain components
        self._embeddings = get_embeddings()
        self._llm = get_llm()
        self._classification_llm = get_llm(temperature=0, max_tokens=10)

        # Load FAISS vector store (LangChain format)
        index_faiss = self.index_dir / "index.faiss"
        if index_faiss.exists():
            self._vectorstore = load_vectorstore(self._embeddings, self.index_dir)
            self._use_langchain_vectorstore = True
        else:
            # Fallback: check for legacy format (events.index)
            legacy_index = self.index_dir / "events.index"
            if legacy_index.exists():
                self._legacy_index = faiss.read_index(str(legacy_index))
                self._use_langchain_vectorstore = False
            else:
                raise FileNotFoundError(
                    f"Index FAISS non trouvé. "
                    f"Attendu: {index_faiss} (LangChain) ou {legacy_index} (legacy). "
                    f"Exécutez le script de migration ou l'endpoint /rebuild."
                )

        # Build LCEL chains
        self._classification_chain = self._build_classification_chain()
        self._conversation_chain = self._build_conversation_chain()
        self._rag_chain = self._build_rag_chain()

    def _build_classification_chain(self):
        """Build the query classification chain (SEARCH vs CHAT)."""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("human", CLASSIFICATION_PROMPT_TEMPLATE),
            ]
        )
        return prompt | self._classification_llm | StrOutputParser()

    def _build_conversation_chain(self):
        """Build the non-RAG conversation chain."""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", CONVERSATION_SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{query}"),
            ]
        )
        return prompt | self._llm | StrOutputParser()

    def _build_rag_chain(self):
        """Build the RAG chain with context injection."""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", RAG_SYSTEM_PROMPT_TEMPLATE),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{query}"),
            ]
        )
        return prompt | self._llm | StrOutputParser()

    def _convert_history(self, history: list[dict] | None) -> list:
        """Convert dict-based history to LangChain message objects.

        Args:
            history: List of {"role": "user"|"assistant", "content": "..."} dicts.

        Returns:
            List of HumanMessage and AIMessage objects.
        """
        if not history:
            return []
        messages = []
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        return messages

    def _format_context(self, results: list[dict]) -> str:
        """Format search results as context string.

        Args:
            results: List of search results with 'document' key.

        Returns:
            Formatted context string for the RAG prompt.
        """
        if results:
            context = "Événements pertinents :\n\n"
            for i, result in enumerate(results, 1):
                doc = result["document"]
                context += f"Événement {i}:\n{doc['content']}\n\n"
        else:
            context = "Aucun événement trouvé pour cette recherche."
        return context

    def needs_rag(self, query: str) -> bool:
        """Détermine si la requête nécessite une recherche RAG.

        Args:
            query: Question de l'utilisateur.

        Returns:
            True si recherche d'événements, False si conversation simple.
        """
        result = self._classification_chain.invoke({"query": query})
        return "SEARCH" in result.strip().upper()

    def conversation_response(self, query: str, history: list[dict] | None = None) -> str:
        """Génère une réponse conversationnelle sans RAG.

        Args:
            query: Question de l'utilisateur.
            history: Historique de conversation optionnel.

        Returns:
            Réponse textuelle du LLM.
        """
        messages = self._convert_history(history)
        return self._conversation_chain.invoke({"query": query, "history": messages})

    def encode_query(self, query: str) -> np.ndarray:
        """Encode une requête en vecteur d'embedding.

        This method is kept for backward compatibility. Uses LangChain
        embeddings internally.

        Args:
            query: Texte de la requête.

        Returns:
            Vecteur d'embedding normalisé, shape (1, embedding_dim).
        """
        embedding = self._embeddings.embed_query(query)
        result = np.array([embedding], dtype=np.float32)
        faiss.normalize_L2(result)
        return result

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Effectue une recherche sémantique.

        Args:
            query: Requête de recherche.
            top_k: Nombre de résultats à retourner.

        Returns:
            Liste de résultats avec document, similarité et distance.
        """
        if self._use_langchain_vectorstore:
            # Use LangChain FAISS vector store
            docs_with_scores = self._vectorstore.similarity_search_with_score(query, k=top_k)

            results = []
            for doc, score in docs_with_scores:
                # Convert LangChain Document to expected format
                results.append(
                    {
                        "document": {
                            "id": doc.metadata.get("id", ""),
                            "title": doc.metadata.get("title", ""),
                            "content": doc.page_content,
                            "metadata": doc.metadata,
                        },
                        "similarity": float(1 - score),  # L2 distance to similarity
                        "distance": float(score),
                    }
                )
            return results
        else:
            # Legacy: use raw FAISS index
            query_embedding = self.encode_query(query)
            distances, indices = self._legacy_index.search(query_embedding, top_k)

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
        """Génère une réponse conversationnelle avec le LLM.

        Args:
            query: Question de l'utilisateur.
            results: Résultats de la recherche sémantique.
            history: Historique des messages.

        Returns:
            Réponse générée par le LLM.
        """
        context = self._format_context(results)
        messages = self._convert_history(history)
        return self._rag_chain.invoke(
            {
                "context": context,
                "query": query,
                "history": messages,
            }
        )

    def chat(
        self,
        query: str,
        top_k: int = 5,
        history: list[dict] | None = None,
    ) -> dict:
        """Pipeline intelligent : détecte si RAG nécessaire.

        Args:
            query: Question de l'utilisateur.
            top_k: Nombre de documents à récupérer.
            history: Historique de conversation.

        Returns:
            Dictionnaire avec la réponse, sources et indicateur RAG:
            {
                "response": str,
                "sources": list[dict],
                "query": str,
                "used_rag": bool
            }
        """
        # Determine if we need RAG
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
