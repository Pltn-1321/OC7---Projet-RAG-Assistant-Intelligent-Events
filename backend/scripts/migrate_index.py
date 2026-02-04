#!/usr/bin/env python3
"""Migration script: Converts existing FAISS index to LangChain format.

This script rebuilds the FAISS index from rag_documents.json using
LangChain's FAISS wrapper, creating the new format (index.faiss + index.pkl).

Usage:
    uv run python scripts/migrate_index.py
"""

# Fix OpenMP duplicate library error on macOS
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.index_builder import IndexBuilder


def progress_callback(message: str, percentage: float) -> None:
    """Display progress to console."""
    bar_length = 30
    filled = int(bar_length * percentage)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r[{bar}] {percentage*100:5.1f}% - {message}", end="", flush=True)
    if percentage >= 1.0:
        print()  # Newline at completion


def main():
    """Run the migration."""
    print("=" * 60)
    print("Migration vers le format LangChain FAISS")
    print("=" * 60)
    print()

    try:
        builder = IndexBuilder(progress_callback=progress_callback)

        print(f"Source: {builder.documents_path}")
        print(f"Destination: {builder.index_dir}")
        print()

        result = builder.rebuild()

        print()
        print("=" * 60)
        print("Migration terminée avec succès!")
        print("=" * 60)
        print(f"  Documents traités: {result['documents_processed']}")
        print(f"  Dimension embeddings: {result['embedding_dimension']}")
        print(f"  Vecteurs indexés: {result['index_vectors']}")
        print(f"  Temps écoulé: {result['elapsed_seconds']}s")
        print(f"  Provider: {result['provider']}")
        print(f"  Modèle: {result['model']}")
        print()
        print("Fichiers créés:")
        print(f"  - {builder.index_dir / 'index.faiss'}")
        print(f"  - {builder.index_dir / 'index.pkl'}")
        print(f"  - {builder.index_dir / 'config.json'}")

    except FileNotFoundError as e:
        print(f"\n❌ Erreur: {e}")
        print("\nAssurez-vous que le fichier rag_documents.json existe.")
        print("Vous pouvez le créer en exécutant les notebooks de préparation des données.")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        raise


if __name__ == "__main__":
    main()
