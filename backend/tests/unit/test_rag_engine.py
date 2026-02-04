"""Tests unitaires pour la classe RAGEngine (version LangChain)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.rag.engine import RAGEngine


class TestRAGEngineInitialization:
    """Tests pour l'initialisation du RAGEngine."""

    def test_missing_index_raises_error(self, tmp_path):
        """Test qu'un index manquant lève FileNotFoundError."""
        # Create documents file but no index
        documents = [{"id": "1", "content": "test", "title": "Test"}]
        documents_path = tmp_path / "documents.json"
        with open(documents_path, "w") as f:
            json.dump(documents, f)

        index_dir = tmp_path / "nonexistent"
        index_dir.mkdir()

        with pytest.raises(FileNotFoundError) as exc_info:
            RAGEngine(index_dir=index_dir, documents_path=documents_path)
        assert "Index FAISS non trouvé" in str(exc_info.value)

    def test_missing_documents_raises_error(self, tmp_path):
        """Test que des documents manquants lèvent FileNotFoundError."""
        with pytest.raises(FileNotFoundError) as exc_info:
            RAGEngine(
                index_dir=tmp_path,
                documents_path=tmp_path / "missing_documents.json",
            )
        assert "Documents non trouvés" in str(exc_info.value)

    @pytest.mark.requires_api
    def test_engine_loads_successfully(self):
        """Test que le moteur se charge correctement avec des fichiers valides."""
        try:
            engine = RAGEngine()
            assert engine.num_documents > 0
            assert engine.embedding_dim > 0
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible pour ce test")


class TestRAGEngineProperties:
    """Tests pour les propriétés du RAGEngine."""

    @pytest.fixture
    def mock_engine(self, tmp_path):
        """Crée un RAGEngine mocké pour les tests avec support legacy."""
        import faiss

        index_dir = tmp_path / "faiss_index"
        index_dir.mkdir()

        # Créer un index FAISS factice (legacy format pour tests unitaires)
        dimension = 1024
        index = faiss.IndexFlatL2(dimension)
        vectors = np.random.rand(5, dimension).astype(np.float32)
        faiss.normalize_L2(vectors)
        index.add(vectors)
        faiss.write_index(index, str(index_dir / "events.index"))

        # Créer la configuration
        config = {
            "embedding_dim": dimension,
            "provider": "mistral",
            "model_name": "mistral-embed",
        }
        with open(index_dir / "config.json", "w") as f:
            json.dump(config, f)

        # Créer les documents
        documents = [
            {
                "id": f"doc-{i}",
                "title": f"Document {i}",
                "content": f"Contenu du document {i} avec événement culturel",
                "metadata": {"city": "Paris"},
            }
            for i in range(5)
        ]
        documents_path = tmp_path / "documents.json"
        with open(documents_path, "w") as f:
            json.dump(documents, f)

        # Mock LangChain components
        with (
            patch("src.rag.engine.get_embeddings") as mock_emb,
            patch("src.rag.engine.get_llm") as mock_llm,
        ):

            # Mock embeddings
            mock_embeddings = MagicMock()
            mock_embeddings.embed_query.return_value = np.random.rand(dimension).tolist()
            mock_emb.return_value = mock_embeddings

            # Mock LLM
            mock_llm_instance = MagicMock()
            mock_llm.return_value = mock_llm_instance

            engine = RAGEngine(index_dir=index_dir, documents_path=documents_path)

        return engine

    def test_num_documents_property(self, mock_engine):
        """Test de la propriété num_documents."""
        assert mock_engine.num_documents == 5

    def test_embedding_dim_property(self, mock_engine):
        """Test de la propriété embedding_dim."""
        assert mock_engine.embedding_dim == 1024


class TestNeedsRAG:
    """Tests pour la classification needs_rag."""

    @pytest.mark.requires_api
    def test_search_query_returns_true(self):
        """Test qu'une requête de recherche retourne True."""
        try:
            engine = RAGEngine()
            assert engine.needs_rag("Concerts à Paris ce weekend") is True
            assert engine.needs_rag("Quelles expositions sont disponibles?") is True
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")

    @pytest.mark.requires_api
    def test_greeting_returns_false(self):
        """Test qu'une salutation retourne False."""
        try:
            engine = RAGEngine()
            assert engine.needs_rag("Bonjour!") is False
            assert engine.needs_rag("Merci beaucoup") is False
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")


class TestSearch:
    """Tests pour la fonctionnalité de recherche."""

    @pytest.mark.requires_api
    def test_search_returns_results(self):
        """Test que la recherche retourne des résultats."""
        try:
            engine = RAGEngine()
            results = engine.search("concert", top_k=3)
            assert isinstance(results, list)
            assert len(results) <= 3
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")

    @pytest.mark.requires_api
    def test_search_result_structure(self):
        """Test de la structure des résultats de recherche."""
        try:
            engine = RAGEngine()
            results = engine.search("événement", top_k=1)
            if results:
                result = results[0]
                assert "document" in result
                assert "similarity" in result
                assert "distance" in result
                assert 0 <= result["similarity"] <= 1
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")


class TestEncodeQuery:
    """Tests pour l'encodage des requêtes."""

    @pytest.mark.requires_api
    def test_encode_returns_normalized_vector(self):
        """Test que le vecteur encodé est normalisé."""
        try:
            engine = RAGEngine()
            embedding = engine.encode_query("test query")
            assert isinstance(embedding, np.ndarray)
            # Vérifier que le vecteur est normalisé (norme ~= 1)
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
    """Tests pour les réponses conversationnelles."""

    @pytest.mark.requires_api
    def test_conversation_response_without_rag(self):
        """Test d'une réponse conversationnelle sans RAG."""
        try:
            engine = RAGEngine()
            response = engine.conversation_response("Bonjour, comment ça va?")
            assert isinstance(response, str)
            assert len(response) > 0
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")


class TestGenerateResponse:
    """Tests pour la génération de réponses avec contexte."""

    @pytest.mark.requires_api
    @pytest.mark.slow
    def test_generate_response_with_results(self):
        """Test de génération avec des résultats."""
        try:
            engine = RAGEngine()
            results = engine.search("concert", top_k=2)
            if results:
                response = engine.generate_response("Quels concerts?", results)
                assert isinstance(response, str)
                assert len(response) > 0
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")

    @pytest.mark.requires_api
    def test_generate_response_without_results(self):
        """Test de génération sans résultats."""
        try:
            engine = RAGEngine()
            response = engine.generate_response("Question sans résultats", [])
            assert isinstance(response, str)
            assert len(response) > 0
        except FileNotFoundError:
            pytest.skip("Index FAISS non disponible")


class TestLangChainComponents:
    """Tests spécifiques aux composants LangChain."""

    def test_history_conversion(self, tmp_path):
        """Test de la conversion de l'historique vers les messages LangChain."""
        import faiss
        from langchain_core.messages import AIMessage, HumanMessage

        index_dir = tmp_path / "faiss_index"
        index_dir.mkdir()

        # Create minimal setup
        dimension = 1024
        index = faiss.IndexFlatL2(dimension)
        vectors = np.random.rand(2, dimension).astype(np.float32)
        faiss.normalize_L2(vectors)
        index.add(vectors)
        faiss.write_index(index, str(index_dir / "events.index"))

        config = {"embedding_dim": dimension, "provider": "mistral"}
        with open(index_dir / "config.json", "w") as f:
            json.dump(config, f)

        documents = [{"id": "1", "content": "test", "title": "Test"}]
        documents_path = tmp_path / "documents.json"
        with open(documents_path, "w") as f:
            json.dump(documents, f)

        with (
            patch("src.rag.engine.get_embeddings") as mock_emb,
            patch("src.rag.engine.get_llm") as mock_llm,
        ):

            mock_embeddings = MagicMock()
            mock_embeddings.embed_query.return_value = np.random.rand(dimension).tolist()
            mock_emb.return_value = mock_embeddings
            mock_llm.return_value = MagicMock()

            engine = RAGEngine(index_dir=index_dir, documents_path=documents_path)

            # Test history conversion
            history = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ]
            converted = engine._convert_history(history)

            assert len(converted) == 2
            assert isinstance(converted[0], HumanMessage)
            assert isinstance(converted[1], AIMessage)
            assert converted[0].content == "Hello"
            assert converted[1].content == "Hi there!"

    def test_empty_history_conversion(self, tmp_path):
        """Test de la conversion d'un historique vide."""
        import faiss

        index_dir = tmp_path / "faiss_index"
        index_dir.mkdir()

        dimension = 1024
        index = faiss.IndexFlatL2(dimension)
        vectors = np.random.rand(2, dimension).astype(np.float32)
        faiss.normalize_L2(vectors)
        index.add(vectors)
        faiss.write_index(index, str(index_dir / "events.index"))

        config = {"embedding_dim": dimension, "provider": "mistral"}
        with open(index_dir / "config.json", "w") as f:
            json.dump(config, f)

        documents = [{"id": "1", "content": "test", "title": "Test"}]
        documents_path = tmp_path / "documents.json"
        with open(documents_path, "w") as f:
            json.dump(documents, f)

        with (
            patch("src.rag.engine.get_embeddings") as mock_emb,
            patch("src.rag.engine.get_llm") as mock_llm,
        ):

            mock_embeddings = MagicMock()
            mock_embeddings.embed_query.return_value = np.random.rand(dimension).tolist()
            mock_emb.return_value = mock_embeddings
            mock_llm.return_value = MagicMock()

            engine = RAGEngine(index_dir=index_dir, documents_path=documents_path)

            # Test empty and None history
            assert engine._convert_history(None) == []
            assert engine._convert_history([]) == []
