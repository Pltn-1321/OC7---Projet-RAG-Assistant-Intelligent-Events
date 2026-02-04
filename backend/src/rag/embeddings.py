"""LangChain Embeddings factory module.

This module provides a factory function to create Mistral embeddings instances.
"""

from langchain_core.embeddings import Embeddings
from langchain_mistralai import MistralAIEmbeddings

from src.config.settings import settings


def get_embeddings() -> Embeddings:
    """Create and return a Mistral Embeddings instance.

    Returns:
        Embeddings: A LangChain-compatible MistralAIEmbeddings instance.

    Raises:
        ValueError: If the Mistral API key is not configured.
    """
    if not settings.mistral_api_key:
        raise ValueError("MISTRAL_API_KEY is required for embeddings")

    return MistralAIEmbeddings(
        model=settings.mistral_embedding_model,
        api_key=settings.mistral_api_key,
    )
