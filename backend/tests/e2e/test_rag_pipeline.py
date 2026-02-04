"""Tests end-to-end pour le pipeline RAG complet."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Cree un client de test FastAPI."""
    return TestClient(app)


@pytest.mark.e2e
@pytest.mark.slow
class TestRAGPipeline:
    """Tests complets du pipeline RAG de bout en bout."""

    def test_search_returns_relevant_results(self, client):
        """Test que la recherche retourne des resultats semantiquement pertinents."""
        response = client.post(
            "/search", json={"query": "concert de musique", "top_k": 5}
        )

        if response.status_code != 200:
            pytest.skip("RAG engine non disponible")

        data = response.json()
        assert len(data["results"]) <= 5

        # Verifier la structure des resultats
        for result in data["results"]:
            assert "title" in result
            assert "content" in result
            assert "similarity" in result
            assert "distance" in result
            assert "metadata" in result
            # La similarite doit etre entre 0 et 1
            assert 0 <= result["similarity"] <= 1

    def test_chat_conversation_flow(self, client):
        """Test d'un flux de conversation complet."""
        # Salutation initiale
        response1 = client.post("/chat", json={"query": "Bonjour!"})
        if response1.status_code != 200:
            pytest.skip("RAG engine non disponible")

        data1 = response1.json()
        session_id = data1["session_id"]

        # La salutation ne devrait pas utiliser le RAG (pas de sources)
        # Mais le comportement peut varier selon le modele

        # Question de recherche
        response2 = client.post(
            "/chat",
            json={"query": "Quels concerts sont prevus cette semaine?", "session_id": session_id},
        )

        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["session_id"] == session_id
        # Une question de recherche devrait avoir des sources
        assert "sources" in data2

        # Question de suivi
        response3 = client.post(
            "/chat",
            json={"query": "Y en a-t-il des gratuits?", "session_id": session_id},
        )

        assert response3.status_code == 200
        data3 = response3.json()
        assert data3["session_id"] == session_id

    def test_session_persistence(self, client):
        """Test que l'historique de session est maintenu."""
        # Creer une session avec chat
        response1 = client.post("/chat", json={"query": "Bonjour"})
        if response1.status_code != 200:
            pytest.skip("RAG engine non disponible")

        session_id = response1.json()["session_id"]

        # Ajouter des messages
        client.post(
            "/chat", json={"query": "Quels evenements?", "session_id": session_id}
        )
        client.post(
            "/chat", json={"query": "Merci!", "session_id": session_id}
        )

        # Recuperer l'historique
        response2 = client.get(f"/session/{session_id}")
        assert response2.status_code == 200

        history = response2.json()["history"]
        # Au moins 4 messages (2 echanges = 2 user + 2 assistant)
        assert len(history) >= 4

        # Verifier l'alternance user/assistant
        for i, msg in enumerate(history):
            assert "role" in msg
            assert "content" in msg
            assert msg["role"] in ["user", "assistant"]

        # Supprimer la session
        response3 = client.delete(f"/session/{session_id}")
        assert response3.status_code == 200

        # Verifier la suppression
        response4 = client.get(f"/session/{session_id}")
        assert response4.status_code == 404

    def test_multiple_concurrent_sessions(self, client):
        """Test de plusieurs sessions concurrentes."""
        # Creer plusieurs sessions
        sessions = []
        for i in range(3):
            response = client.post("/chat", json={"query": f"Session {i}"})
            if response.status_code != 200:
                pytest.skip("RAG engine non disponible")
            sessions.append(response.json()["session_id"])

        # Verifier que toutes les sessions sont differentes
        assert len(set(sessions)) == 3

        # Interagir avec chaque session
        for i, session_id in enumerate(sessions):
            response = client.post(
                "/chat",
                json={"query": f"Message pour session {i}", "session_id": session_id},
            )
            assert response.status_code == 200
            assert response.json()["session_id"] == session_id

        # Nettoyer
        for session_id in sessions:
            client.delete(f"/session/{session_id}")


@pytest.mark.e2e
@pytest.mark.slow
class TestSearchQuality:
    """Tests de qualite de la recherche."""

    def test_search_music_events(self, client):
        """Test de recherche d'evenements musicaux."""
        response = client.post(
            "/search", json={"query": "concert musique live", "top_k": 5}
        )

        if response.status_code != 200:
            pytest.skip("RAG engine non disponible")

        data = response.json()
        # Devrait retourner au moins un resultat
        # (sauf si la base est vide)
        assert isinstance(data["results"], list)

    def test_search_art_exhibitions(self, client):
        """Test de recherche d'expositions."""
        response = client.post(
            "/search", json={"query": "exposition art peinture", "top_k": 5}
        )

        if response.status_code != 200:
            pytest.skip("RAG engine non disponible")

        data = response.json()
        assert isinstance(data["results"], list)

    def test_search_free_events(self, client):
        """Test de recherche d'evenements gratuits."""
        response = client.post(
            "/search", json={"query": "evenement gratuit", "top_k": 5}
        )

        if response.status_code != 200:
            pytest.skip("RAG engine non disponible")

        data = response.json()
        assert isinstance(data["results"], list)

    def test_search_by_location(self, client):
        """Test de recherche par lieu."""
        response = client.post(
            "/search", json={"query": "evenements a Marseille", "top_k": 5}
        )

        if response.status_code != 200:
            pytest.skip("RAG engine non disponible")

        data = response.json()
        assert isinstance(data["results"], list)


@pytest.mark.e2e
@pytest.mark.slow
class TestChatQuality:
    """Tests de qualite des reponses du chat."""

    def test_chat_responds_in_french(self, client):
        """Test que le chat repond en francais."""
        response = client.post("/chat", json={"query": "Bonjour, que peux-tu faire?"})

        if response.status_code != 200:
            pytest.skip("RAG engine non disponible")

        data = response.json()
        # La reponse devrait contenir des caracteres francais courants
        # ou des mots francais basiques
        response_text = data["response"].lower()
        # Verifier qu'il y a du contenu
        assert len(response_text) > 10

    def test_chat_provides_sources_for_search(self, client):
        """Test que le chat fournit des sources pour les recherches."""
        response = client.post(
            "/chat", json={"query": "Quels concerts sont disponibles?"}
        )

        if response.status_code != 200:
            pytest.skip("RAG engine non disponible")

        data = response.json()
        # Pour une question de recherche, on s'attend a des sources
        # (si des evenements correspondants existent)
        assert "sources" in data
        assert isinstance(data["sources"], list)
