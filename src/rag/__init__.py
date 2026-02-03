"""RAG (Retrieval-Augmented Generation) module.

This module provides the core RAG pipeline using LangChain LCEL:
- RAGEngine: Main orchestration class with classification, search, and generation
- IndexBuilder: FAISS index construction with LangChain format
- get_embeddings: Factory for Mistral or HuggingFace embeddings
- get_llm: Factory for ChatMistralAI instances
"""

from src.rag.embeddings import get_embeddings
from src.rag.engine import RAGEngine
from src.rag.index_builder import IndexBuilder
from src.rag.llm import get_llm

__all__ = ["RAGEngine", "IndexBuilder", "get_embeddings", "get_llm"]
