#!/usr/bin/env python3
"""Script de test fonctionnel de l'API RAG Events.

Ce script teste tous les endpoints de l'API de maniere interactive
avec une sortie coloree et lisible.

Usage:
    uv run python scripts/api_test.py
    uv run python scripts/api_test.py --base-url http://localhost:8000
    uv run python scripts/api_test.py --rebuild-key YOUR_API_KEY
    uv run python scripts/api_test.py -v  # Mode verbeux
"""

import argparse
import json
import sys
import time
from typing import Any

import requests


class Colors:
    """Codes ANSI pour la sortie coloree."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


class APITester:
    """Testeur fonctionnel de l'API avec sortie formatee."""

    def __init__(
        self,
        base_url: str,
        rebuild_key: str | None = None,
        verbose: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.rebuild_key = rebuild_key
        self.verbose = verbose
        self.results: list[dict] = []
        self.session_id: str | None = None

    def _print_header(self, text: str) -> None:
        """Affiche un titre de section."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")

    def _print_test(self, method: str, endpoint: str, description: str) -> None:
        """Affiche le test en cours."""
        print(f"\n{Colors.CYAN}[TEST]{Colors.RESET} {method} {endpoint}")
        print(f"       {description}")

    def _print_result(self, success: bool, message: str, details: dict | None = None) -> None:
        """Affiche le resultat d'un test."""
        icon = f"{Colors.GREEN}PASS{Colors.RESET}" if success else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"       [{icon}] {message}")

        if self.verbose and details:
            formatted = json.dumps(details, indent=2, ensure_ascii=False)
            # Limiter la taille de sortie
            if len(formatted) > 500:
                formatted = formatted[:500] + "..."
            print(f"       Response: {formatted}")

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: dict | None = None,
        headers: dict | None = None,
        expected_status: int | list[int] = 200,
    ) -> tuple[bool, int, Any]:
        """Execute une requete HTTP et retourne (success, status_code, data)."""
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                json=json_data,
                headers=headers,
                timeout=30,
            )

            if isinstance(expected_status, int):
                expected_status = [expected_status]

            success = response.status_code in expected_status

            try:
                data = response.json()
            except json.JSONDecodeError:
                data = response.text

            return success, response.status_code, data

        except requests.exceptions.ConnectionError:
            return False, 0, {"error": "Connection refusee - le serveur est-il demarre?"}
        except requests.exceptions.Timeout:
            return False, 0, {"error": "Timeout de la requete"}
        except Exception as e:
            return False, 0, {"error": str(e)}

    def test_health(self) -> None:
        """Test GET /health."""
        self._print_test("GET", "/health", "Verifie que l'API est operationnelle")

        success, status, data = self._request("GET", "/health", expected_status=[200, 503])

        if success and status == 200:
            docs = data.get("documents", "?")
            dim = data.get("embedding_dim", "?")
            sessions = data.get("active_sessions", "?")
            self._print_result(
                True,
                f"API saine - {docs} documents, dim={dim}, sessions={sessions}",
            )
            self.results.append({"test": "health", "passed": True})
        elif status == 503:
            self._print_result(False, f"API non disponible: {data}")
            self.results.append({"test": "health", "passed": False, "error": "503"})
        else:
            self._print_result(False, f"Erreur: {data}")
            self.results.append({"test": "health", "passed": False, "error": str(data)})

    def test_search(self) -> None:
        """Test POST /search."""
        self._print_test("POST", "/search", "Recherche semantique d'evenements")

        payload = {"query": "concert de jazz", "top_k": 3}
        success, status, data = self._request("POST", "/search", json_data=payload)

        if success:
            num_results = len(data.get("results", []))
            self._print_result(True, f"Recherche OK - {num_results} resultat(s)", data)
            self.results.append({"test": "search", "passed": True, "results": num_results})
        else:
            self._print_result(False, f"Erreur ({status}): {data}")
            self.results.append({"test": "search", "passed": False})

    def test_search_validation(self) -> None:
        """Test validation des parametres de recherche."""
        self._print_test("POST", "/search", "Validation: requete vide doit etre rejetee")

        payload = {"query": "", "top_k": 3}
        success, status, data = self._request(
            "POST", "/search", json_data=payload, expected_status=422
        )

        if success:
            self._print_result(True, "Validation OK - requete vide rejetee (422)")
            self.results.append({"test": "search_validation", "passed": True})
        else:
            self._print_result(False, f"Validation non appliquee ({status})")
            self.results.append({"test": "search_validation", "passed": False})

    def test_chat(self) -> None:
        """Test POST /chat."""
        self._print_test("POST", "/chat", "Chat avec creation de session")

        payload = {"query": "Bonjour, que peux-tu faire pour moi?"}
        success, status, data = self._request("POST", "/chat", json_data=payload)

        if not success and status == 0:
            self._print_result(False, f"Serveur non disponible: {data}")
            self.results.append({"test": "chat", "passed": False})
            return

        if success:
            self.session_id = data.get("session_id")
            response_preview = data.get("response", "")[:80]
            self._print_result(True, f"Session creee: {self.session_id[:8]}...")
            print(f"       Reponse: {response_preview}...")
            self.results.append({"test": "chat", "passed": True, "session_id": self.session_id})
        else:
            self._print_result(False, f"Erreur ({status}): {data}")
            self.results.append({"test": "chat", "passed": False})

    def test_chat_with_session(self) -> None:
        """Test chat avec session existante."""
        if not self.session_id:
            print(f"\n{Colors.YELLOW}[SKIP]{Colors.RESET} Chat avec session - pas de session")
            return

        self._print_test("POST", "/chat", f"Chat avec session ({self.session_id[:8]}...)")

        payload = {"query": "Quels concerts sont prevus?", "session_id": self.session_id}
        success, status, data = self._request("POST", "/chat", json_data=payload)

        if success:
            same_session = data.get("session_id") == self.session_id
            num_sources = len(data.get("sources", []))
            self._print_result(True, f"Session maintenue: {same_session}, Sources: {num_sources}")
            self.results.append({"test": "chat_session", "passed": True})
        else:
            self._print_result(False, f"Erreur ({status})")
            self.results.append({"test": "chat_session", "passed": False})

    def test_get_session(self) -> None:
        """Test GET /session/{session_id}."""
        if not self.session_id:
            print(f"\n{Colors.YELLOW}[SKIP]{Colors.RESET} Get session - pas de session")
            return

        self._print_test("GET", f"/session/{self.session_id[:8]}...", "Recupere l'historique")

        success, status, data = self._request("GET", f"/session/{self.session_id}")

        if success:
            history_len = len(data.get("history", []))
            self._print_result(True, f"Historique recupere - {history_len} messages")
            self.results.append({"test": "get_session", "passed": True})
        else:
            self._print_result(False, f"Erreur ({status})")
            self.results.append({"test": "get_session", "passed": False})

    def test_delete_session(self) -> None:
        """Test DELETE /session/{session_id}."""
        if not self.session_id:
            print(f"\n{Colors.YELLOW}[SKIP]{Colors.RESET} Delete session - pas de session")
            return

        self._print_test("DELETE", f"/session/{self.session_id[:8]}...", "Supprime la session")

        success, status, data = self._request("DELETE", f"/session/{self.session_id}")

        if success:
            self._print_result(True, "Session supprimee")
            self.results.append({"test": "delete_session", "passed": True})

            # Verifier la suppression
            success2, status2, _ = self._request(
                "GET", f"/session/{self.session_id}", expected_status=404
            )
            if success2:
                print(f"       Verification: session supprimee (404)")
        else:
            self._print_result(False, f"Erreur ({status})")
            self.results.append({"test": "delete_session", "passed": False})

    def test_rebuild_no_auth(self) -> None:
        """Test /rebuild sans authentification."""
        self._print_test("POST", "/rebuild", "Sans authentification (doit echouer)")

        success, status, data = self._request("POST", "/rebuild", expected_status=[401, 500])

        if success:
            self._print_result(True, f"Acces refuse correctement ({status})")
            self.results.append({"test": "rebuild_no_auth", "passed": True})
        else:
            self._print_result(False, f"Securite non appliquee ({status})")
            self.results.append({"test": "rebuild_no_auth", "passed": False})

    def test_rebuild_with_auth(self) -> None:
        """Test /rebuild avec authentification."""
        if not self.rebuild_key:
            print(f"\n{Colors.YELLOW}[SKIP]{Colors.RESET} Rebuild - pas de cle (--rebuild-key)")
            return

        self._print_test("POST", "/rebuild", "Avec authentification")

        headers = {"X-API-Key": self.rebuild_key}
        success, status, data = self._request("POST", "/rebuild", headers=headers)

        if success:
            task_id = data.get("task_id", "")
            self._print_result(True, f"Rebuild demarre - task_id: {task_id[:8]}...")
            self.results.append({"test": "rebuild_auth", "passed": True})

            # Verifier le statut
            if task_id:
                print(f"       Attente du statut...")
                time.sleep(2)
                _, _, status_data = self._request("GET", f"/rebuild/{task_id}")
                rebuild_status = status_data.get("status", "unknown")
                progress = status_data.get("progress", 0)
                print(f"       Statut: {rebuild_status} ({progress:.0%})")
        else:
            self._print_result(False, f"Erreur ({status}): {data}")
            self.results.append({"test": "rebuild_auth", "passed": False})

    def print_summary(self) -> bool:
        """Affiche le resume des tests."""
        self._print_header("RESUME DES TESTS")

        passed = sum(1 for r in self.results if r.get("passed"))
        total = len(self.results)

        for result in self.results:
            status = (
                f"{Colors.GREEN}PASS{Colors.RESET}"
                if result["passed"]
                else f"{Colors.RED}FAIL{Colors.RESET}"
            )
            print(f"  [{status}] {result['test']}")

        print()
        if passed == total:
            color = Colors.GREEN
        elif passed > 0:
            color = Colors.YELLOW
        else:
            color = Colors.RED

        print(f"{color}{Colors.BOLD}Total: {passed}/{total} tests reussis{Colors.RESET}")

        return passed == total

    def run_all(self) -> bool:
        """Execute tous les tests."""
        self._print_header("TEST FONCTIONNEL DE L'API RAG EVENTS")
        print(f"URL de base: {self.base_url}")

        self.test_health()
        self.test_search()
        self.test_search_validation()
        self.test_chat()
        self.test_chat_with_session()
        self.test_get_session()
        self.test_delete_session()
        self.test_rebuild_no_auth()
        self.test_rebuild_with_auth()

        return self.print_summary()


def main():
    parser = argparse.ArgumentParser(
        description="Test fonctionnel de l'API RAG Events",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  uv run python scripts/api_test.py
  uv run python scripts/api_test.py --base-url http://localhost:8000
  uv run python scripts/api_test.py --rebuild-key mon-api-key-secret
  uv run python scripts/api_test.py -v
        """,
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="URL de base de l'API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--rebuild-key",
        help="Cle API pour tester l'endpoint /rebuild",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Affiche les reponses completes",
    )

    args = parser.parse_args()

    tester = APITester(
        base_url=args.base_url,
        rebuild_key=args.rebuild_key,
        verbose=args.verbose,
    )

    success = tester.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
