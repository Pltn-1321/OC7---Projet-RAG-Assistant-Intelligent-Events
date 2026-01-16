"""Tests unitaires pour la classe RAGEngine."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.rag.engine import RAGEngine


class TestRAGEngineInitialization:
    """Tests pour l'initialisation du RAGEngine."""

    def test_missing_index_raises_error(self, tmp_path):
        """Test qu'un index manquant leve FileNotFoundError."""
        nonexistent_path = tmp_path / "nonexistent"
        with pytest.raises(FileNotFoundError) as exc_info:
            RAGEngine(index_dir=nonexistent_path)
        assert "Index FAISS non trouve" in str(exc_info.value)

    def test_missing_documents_raises_error(self, tmp_path, mock_faiss_index):
        """Test que des documents manquants levent FileNotFoundError."""
        # Creer un faux fichier index
        import faiss

        index = faiss.IndexFlatL2(1024)
        index_file = mock_faiss_index / "events.index"
        faiss.write_index(index, str(index_file))

        # Le documents_path par defaut n'existe pas
        with pytest.raises(FileNotFoundError) as exc_info:
            RAGEngine(
                index_dir=mock_faiss_index,
                documents_path=tmp_path / "missing_documents.json",
            )
        assert "Documents non trouves" in str(exc_info.value)

    @pytest.mark.requires_api
    def test_engine_loads_successfully(self):
        """Test que le moteur se charge correctement avec des fichiers valides."""
        # Ce test necessite des fichiers d'index reels
        try:
            engine = RAGEngine()
            assert engine.num_documents > 0
            assert engine.embedding_dim > 0
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible pour ce test")


class TestRAGEngineProperties:
    """Tests pour les proprietes du RAGEngine."""

    @pytest.fixture
    def mock_engine(self, tmp_path):
        """Cree un RAGEngine mocke pour les tests."""
        # Creer les fichiers necessaires
        import faiss

        index_dir = tmp_path / "faiss_index"
        index_dir.mkdir()

        # Creer un index FAISS factice
        dimension = 1024
        index = faiss.IndexFlatL2(dimension)
        # Ajouter quelques vecteurs
        vectors = np.random.rand(5, dimension).astype(np.float32)
        faiss.normalize_L2(vectors)
        index.add(vectors)
        faiss.write_index(index, str(index_dir / "events.index"))

        # Creer la configuration
        config = {
            "embedding_dim": dimension,
            "provider": "mistral",
            "model_name": "mistral-embed",
        }
        with open(index_dir / "config.json", "w") as f:
            json.dump(config, f)

        # Creer les documents
        documents = [
            {
                "id": f"doc-{i}",
                "title": f"Document {i}",
                "content": f"Contenu du document {i}",
                "metadata": {"city": "Paris"},
            }
            for i in range(5)
        ]
        documents_path = tmp_path / "documents.json"
        with open(documents_path, "w") as f:
            json.dump(documents, f)

        # Mocker le client Mistral
        with patch("src.rag.engine.Mistral"):
            engine = RAGEngine(index_dir=index_dir, documents_path=documents_path)

        return engine

    def test_num_documents_property(self, mock_engine):
        """Test de la propriete num_documents."""
        assert mock_engine.num_documents == 5

    def test_embedding_dim_property(self, mock_engine):
        """Test de la propriete embedding_dim."""
        assert mock_engine.embedding_dim == 1024


class TestNeedsRAG:
    """Tests pour la classification needs_rag."""

    @pytest.mark.requires_api
    def test_search_query_returns_true(self):
        """Test qu'une requete de recherche retourne True."""
        try:
            engine = RAGEngine()
            # Les requetes de recherche devraient retourner True
            assert engine.needs_rag("Concerts a Paris ce weekend") is True
            assert engine.needs_rag("Quelles expositions sont disponibles?") is True
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")

    @pytest.mark.requires_api
    def test_greeting_returns_false(self):
        """Test qu'une salutation retourne False."""
        try:
            engine = RAGEngine()
            # Les salutations devraient retourner False
            assert engine.needs_rag("Bonjour!") is False
            assert engine.needs_rag("Merci beaucoup") is False
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")


class TestSearch:
    """Tests pour la fonctionnalite de recherche."""

    @pytest.mark.requires_api
    def test_search_returns_results(self):
        """Test que la recherche retourne des resultats."""
        try:
            engine = RAGEngine()
            results = engine.search("concert", top_k=3)
            assert isinstance(results, list)
            assert len(results) <= 3
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")

    @pytest.mark.requires_api
    def test_search_result_structure(self):
        """Test de la structure des resultats de recherche."""
        try:
            engine = RAGEngine()
            results = engine.search("evenement", top_k=1)
            if results:
                result = results[0]
                assert "document" in result
                assert "similarity" in result
                assert "distance" in result
                assert 0 <= result["similarity"] <= 1
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")


class TestEncodeQuery:
    """Tests pour l'encodage des requetes."""

    @pytest.mark.requires_api
    def test_encode_returns_normalized_vector(self):
        """Test que le vecteur encode est normalise."""
        try:
            engine = RAGEngine()
            embedding = engine.encode_query("test query")
            assert isinstance(embedding, np.ndarray)
            # Verifier que le vecteur est normalise (norme ~= 1)
            norm = np.linalg.norm(embedding)
            assert 0.99 <= norm <= 1.01
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")

    @pytest.mark.requires_api
    def test_encode_returns_correct_dimension(self):
        """Test que l'embedding a la bonne dimension."""
        try:
            engine = RAGEngine()
            embedding = engine.encode_query("test")
            assert embedding.shape[1] == engine.embedding_dim
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")


class TestChat:
    """Tests pour le pipeline de chat complet."""

    @pytest.mark.requires_api
    @pytest.mark.slow
    def test_chat_returns_response_structure(self):
        """Test que chat retourne la structure attendue."""
        try:
            engine = RAGEngine()
            result = engine.chat("Bonjour", top_k=3)
            assert "response" in result
            assert "sources" in result
            assert "query" in result
            assert "used_rag" in result
            assert isinstance(result["response"], str)
            assert isinstance(result["sources"], list)
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")

    @pytest.mark.requires_api
    @pytest.mark.slow
    def test_chat_with_history(self):
        """Test du chat avec historique."""
        try:
            engine = RAGEngine()
            history = [
                {"role": "user", "content": "Bonjour"},
                {"role": "assistant", "content": "Bonjour! Comment puis-je t'aider?"},
            ]
            result = engine.chat("Quels concerts?", top_k=3, history=history)
            assert "response" in result
            assert result["used_rag"] is True
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")


class TestConversationResponse:
    """Tests pour les reponses conversationnelles."""

    @pytest.mark.requires_api
    def test_conversation_response_without_rag(self):
        """Test d'une reponse conversationnelle sans RAG."""
        try:
            engine = RAGEngine()
            response = engine.conversation_response("Bonjour, comment ca va?")
            assert isinstance(response, str)
            assert len(response) > 0
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")


class TestGenerateResponse:
    """Tests pour la generation de reponses avec contexte."""

    @pytest.mark.requires_api
    @pytest.mark.slow
    def test_generate_response_with_results(self):
        """Test de generation avec des resultats."""
        try:
            engine = RAGEngine()
            # D'abord faire une recherche
            results = engine.search("concert", top_k=2)
            if results:
                response = engine.generate_response("Quels concerts?", results)
                assert isinstance(response, str)
                assert len(response) > 0
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")

    @pytest.mark.requires_api
    def test_generate_response_without_results(self):
        """Test de generation sans resultats."""
        try:
            engine = RAGEngine()
            response = engine.generate_response("Question sans resultats", [])
            assert isinstance(response, str)
            assert len(response) > 0
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")
