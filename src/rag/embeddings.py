"""LangChain Embeddings factory module.

This module provides a factory function to create embeddings instances
based on the configured provider (Mistral or HuggingFace/SentenceTransformers).
"""

from langchain_core.embeddings import Embeddings

from src.config.settings import settings


def get_embeddings() -> Embeddings:
    """Create and return a LangChain Embeddings instance based on settings.

    Returns:
        Embeddings: A LangChain-compatible embeddings instance.
            - MistralAIEmbeddings if provider is "mistral"
            - HuggingFaceEmbeddings if provider is "sentence-transformers"

    Raises:
        ValueError: If the configured provider is not supported.
        ImportError: If the required package is not installed.
    """
    if settings.embedding_provider == "mistral":
        from langchain_mistralai import MistralAIEmbeddings

        return MistralAIEmbeddings(
            model=settings.mistral_embedding_model,
            api_key=settings.mistral_api_key,
        )

    elif settings.embedding_provider == "sentence-transformers":
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name=settings.sentence_transformer_model,
            encode_kwargs={"normalize_embeddings": True},
        )

    else:
        raise ValueError(
            f"Unsupported embedding provider: {settings.embedding_provider}. "
            f"Must be 'mistral' or 'sentence-transformers'."
        )
