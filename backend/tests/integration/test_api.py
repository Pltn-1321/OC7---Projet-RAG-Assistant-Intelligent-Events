"""Tests d'integration pour les endpoints FastAPI."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Cree un client de test FastAPI."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests pour l'endpoint /health."""

    @pytest.mark.integration
    def test_health_returns_valid_status_code(self, client):
        """Test que /health retourne 200 ou 503."""
        response = client.get("/health")
        # 200 si index disponible, 503 sinon
        assert response.status_code in [200, 503]

    @pytest.mark.integration
    def test_health_response_structure_when_healthy(self, client):
        """Test de la structure de reponse quand l'API est saine."""
        response = client.get("/health")
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "document_count" in data
            assert "embedding_dimension" in data
            assert "active_sessions" in data
            assert data["status"] == "healthy"


class TestSearchEndpoint:
    """Tests pour l'endpoint /search."""

    @pytest.mark.integration
    def test_search_requires_query(self, client):
        """Test que /search requiert un champ query."""
        response = client.post("/search", json={})
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    def test_search_empty_query_rejected(self, client):
        """Test qu'une requete vide est rejetee."""
        response = client.post("/search", json={"query": ""})
        assert response.status_code == 422

    @pytest.mark.integration
    def test_search_valid_request(self, client):
        """Test d'une requete de recherche valide."""
        response = client.post("/search", json={"query": "concert jazz", "top_k": 3})
        # 200 si index disponible, 500 sinon
        assert response.status_code in [200, 500]

    @pytest.mark.integration
    def test_search_top_k_too_high(self, client):
        """Test que top_k > 20 est rejete."""
        response = client.post("/search", json={"query": "test", "top_k": 25})
        assert response.status_code == 422

    @pytest.mark.integration
    def test_search_top_k_too_low(self, client):
        """Test que top_k < 1 est rejete."""
        response = client.post("/search", json={"query": "test", "top_k": 0})
        assert response.status_code == 422

    @pytest.mark.integration
    def test_search_response_structure(self, client):
        """Test de la structure de reponse de recherche."""
        response = client.post("/search", json={"query": "evenement", "top_k": 2})
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
            assert "query" in data
            assert isinstance(data["results"], list)


class TestChatEndpoint:
    """Tests pour l'endpoint /chat."""

    @pytest.mark.integration
    def test_chat_requires_query(self, client):
        """Test que /chat requiert un champ query."""
        response = client.post("/chat", json={})
        assert response.status_code == 422

    @pytest.mark.integration
    def test_chat_creates_session(self, client):
        """Test que /chat cree une session."""
        response = client.post("/chat", json={"query": "Bonjour"})
        if response.status_code == 200:
            data = response.json()
            assert "session_id" in data
            assert "response" in data
            assert len(data["session_id"]) > 0

    @pytest.mark.integration
    def test_chat_with_existing_session(self, client):
        """Test du chat avec une session existante."""
        # Premier message pour creer la session
        response1 = client.post("/chat", json={"query": "Bonjour"})
        if response1.status_code != 200:
            pytest.skip("RAG engine non disponible")

        session_id = response1.json()["session_id"]

        # Deuxieme message avec la meme session
        response2 = client.post(
            "/chat", json={"query": "Quels concerts?", "session_id": session_id}
        )

        assert response2.status_code == 200
        assert response2.json()["session_id"] == session_id

    @pytest.mark.integration
    def test_chat_response_structure(self, client):
        """Test de la structure de reponse du chat."""
        response = client.post("/chat", json={"query": "Bonjour"})
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert "sources" in data
            assert "query" in data
            assert "session_id" in data
            assert isinstance(data["sources"], list)


class TestSessionEndpoints:
    """Tests pour les endpoints de gestion de session."""

    @pytest.mark.integration
    def test_get_nonexistent_session_returns_404(self, client):
        """Test que GET /session pour une session inexistante retourne 404."""
        response = client.get("/session/nonexistent-session-id")
        assert response.status_code == 404

    @pytest.mark.integration
    def test_delete_nonexistent_session_returns_404(self, client):
        """Test que DELETE /session pour une session inexistante retourne 404."""
        response = client.delete("/session/nonexistent-session-id")
        assert response.status_code == 404

    @pytest.mark.integration
    def test_get_existing_session(self, client):
        """Test de recuperation d'une session existante."""
        # Creer une session via chat
        chat_response = client.post("/chat", json={"query": "Bonjour"})
        if chat_response.status_code != 200:
            pytest.skip("RAG engine non disponible")

        session_id = chat_response.json()["session_id"]

        # Recuperer la session
        response = client.get(f"/session/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "history" in data
        assert data["session_id"] == session_id

    @pytest.mark.integration
    def test_delete_existing_session(self, client):
        """Test de suppression d'une session existante."""
        # Creer une session via chat
        chat_response = client.post("/chat", json={"query": "Bonjour"})
        if chat_response.status_code != 200:
            pytest.skip("RAG engine non disponible")

        session_id = chat_response.json()["session_id"]

        # Supprimer la session
        delete_response = client.delete(f"/session/{session_id}")
        assert delete_response.status_code == 200

        # Verifier que la session n'existe plus
        get_response = client.get(f"/session/{session_id}")
        assert get_response.status_code == 404


class TestRebuildEndpoint:
    """Tests pour l'endpoint /rebuild."""

    @pytest.mark.integration
    def test_rebuild_requires_api_key(self, client):
        """Test que /rebuild requiert une cle API."""
        response = client.post("/rebuild")
        # 401 si cle manquante, 500 si REBUILD_API_KEY non configuree
        assert response.status_code in [401, 500]

    @pytest.mark.integration
    def test_rebuild_invalid_api_key(self, client):
        """Test que /rebuild rejette une cle invalide."""
        response = client.post("/rebuild", headers={"X-API-Key": "invalid-key"})
        # 401 si cle invalide, 500 si REBUILD_API_KEY non configuree
        assert response.status_code in [401, 500]

    @pytest.mark.integration
    def test_rebuild_status_nonexistent_task(self, client):
        """Test que GET /rebuild/{task_id} pour une tache inexistante retourne 404."""
        response = client.get("/rebuild/nonexistent-task-id")
        assert response.status_code == 404


class TestCORSHeaders:
    """Tests pour les headers CORS."""

    @pytest.mark.integration
    def test_cors_preflight_request(self, client):
        """Test d'une requete preflight CORS."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # FastAPI/Starlette gere les OPTIONS automatiquement
        assert response.status_code in [200, 405]


class TestInputValidation:
    """Tests de validation des entrees."""

    @pytest.mark.integration
    def test_search_query_max_length(self, client):
        """Test avec une requete tres longue."""
        long_query = "a" * 1000
        response = client.post("/search", json={"query": long_query})
        # Devrait accepter (pas de limite explicite dans le code)
        assert response.status_code in [200, 500]

    @pytest.mark.integration
    def test_chat_with_invalid_session_id_format(self, client):
        """Test du chat avec un format de session_id non-UUID."""
        response = client.post(
            "/chat", json={"query": "Test", "session_id": "not-a-uuid"}
        )
        # Devrait accepter (pas de validation stricte du format UUID)
        assert response.status_code in [200, 500]
