"""LangChain FAISS vector store management module.

This module provides functions to load and build FAISS vector stores
using LangChain's FAISS wrapper for semantic search.
"""

from pathlib import Path
from typing import Callable

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from src.config.constants import PROCESSED_DATA_DIR
from src.config.settings import settings


def load_vectorstore(
    embeddings: Embeddings,
    index_dir: Path | None = None,
) -> FAISS:
    """Load an existing FAISS vector store from disk.

    Args:
        embeddings: LangChain Embeddings instance for query encoding.
        index_dir: Directory containing the FAISS index files.
            If None, uses settings.index_path.

    Returns:
        FAISS: A LangChain FAISS vector store instance.

    Raises:
        FileNotFoundError: If the index directory or files don't exist.
    """
    index_dir = index_dir or settings.index_path

    if not index_dir.exists():
        raise FileNotFoundError(f"Index directory not found: {index_dir}")

    index_file = index_dir / "index.faiss"
    if not index_file.exists():
        raise FileNotFoundError(
            f"FAISS index file not found: {index_file}. "
            f"Run the migration script or /rebuild endpoint to create it."
        )

    return FAISS.load_local(
        folder_path=str(index_dir),
        embeddings=embeddings,
        allow_dangerous_deserialization=True,  # Required for pickle-based metadata
    )


def build_vectorstore(
    documents: list[Document],
    embeddings: Embeddings,
    progress_callback: Callable[[str, float], None] | None = None,
    batch_size: int = 32,
) -> FAISS:
    """Build a new FAISS vector store from documents.

    Args:
        documents: List of LangChain Document objects to index.
        embeddings: LangChain Embeddings instance for encoding.
        progress_callback: Optional callback for progress updates.
            Signature: (message: str, percentage: float 0-1) -> None
        batch_size: Number of documents to process per batch.

    Returns:
        FAISS: A new FAISS vector store instance.
    """
    total = len(documents)

    if progress_callback:
        progress_callback("Initialisation du vector store FAISS", 0.10)

    if total <= batch_size:
        # Small dataset: process all at once
        vectorstore = FAISS.from_documents(documents, embeddings)
        if progress_callback:
            progress_callback("Vector store construit", 0.80)
    else:
        # Large dataset: build incrementally with progress reporting
        first_batch = documents[:batch_size]
        vectorstore = FAISS.from_documents(first_batch, embeddings)

        if progress_callback:
            progress_callback(f"Embeddings: {batch_size}/{total}", 0.15)

        for i in range(batch_size, total, batch_size):
            batch = documents[i : i + batch_size]
            vectorstore.add_documents(batch)

            # Progress from 15% to 75% during embedding generation
            progress = 0.15 + (min(i + batch_size, total) / total) * 0.60
            if progress_callback:
                progress_callback(f"Embeddings: {min(i + batch_size, total)}/{total}", progress)

    if progress_callback:
        progress_callback("Vector store prêt", 0.80)

    return vectorstore


def save_vectorstore(
    vectorstore: FAISS,
    index_dir: Path | None = None,
    progress_callback: Callable[[str, float], None] | None = None,
) -> None:
    """Save a FAISS vector store to disk.

    Args:
        vectorstore: The FAISS vector store to save.
        index_dir: Directory to save the index files.
            If None, uses settings.index_path.
        progress_callback: Optional callback for progress updates.
    """
    index_dir = index_dir or settings.index_path
    index_dir.mkdir(parents=True, exist_ok=True)

    if progress_callback:
        progress_callback("Sauvegarde de l'index FAISS", 0.85)

    vectorstore.save_local(str(index_dir))

    if progress_callback:
        progress_callback("Index sauvegardé", 0.95)
