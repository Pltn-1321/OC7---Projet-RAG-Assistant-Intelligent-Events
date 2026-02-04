# Tests et Qualité du Code - RAG Events Assistant

> **Documentation de la stratégie de tests et qualité du code**

---

## Stratégie de Test

### Vue d'Ensemble

**Framework** : pytest 7.4+
**Coverage Target** : >80% (actuel : 85%)
**Test Types** : Unit, Integration, E2E
**Total Tests** : ~20 tests
**Total Lines** : ~1,200 lignes de code de test

**Philosophie** :
- Tests as documentation (tests lisibles = documentation)
- Test-Driven Development encouragé
- Fixtures réutilisables (DRY)
- Isolation des tests (pas de side effects)

### Organisation des Tests

```
tests/
├── conftest.py              # Fixtures partagées (365 lignes)
├── data/
│   └── test_questions.json  # Dataset annoté (12 questions)
├── unit/                    # Tests unitaires (734 lignes)
│   ├── __init__.py
│   ├── test_models.py       # Pydantic models (462 lignes)
│   └── test_rag_engine.py   # RAGEngine methods (272 lignes)
├── integration/             # Tests d'intégration (245 lignes)
│   └── test_api.py          # FastAPI endpoints
└── e2e/                     # Tests end-to-end (232 lignes)
    └── test_rag_pipeline.py # Pipeline complet
```

---

## Tests Unitaires (tests/unit/)

### test_models.py (462 lignes)

**Objectif** : Validation des modèles Pydantic

#### Test Cases

**1. Event Model** :
```python
def test_event_creation_valid():
    """Test création événement valide."""
    event = Event(
        title="Concert Jazz",
        city="Paris",
        start_date="2025-01-20T20:00:00",
        price_info="Gratuit",
        url="https://example.com"
    )
    assert event.title == "Concert Jazz"
    assert event.city == "Paris"
```

**Couverture** :
- ✅ Création événement valide
- ✅ Validation champs requis (title, city)
- ✅ Parsing dates ISO 8601
- ✅ Validation prix (free events)
- ✅ Helper methods :
  - `to_search_text()` : Format pour embedding FAISS
  - `to_display_dict()` : Format pour UI
  - Properties : `is_free`, `is_upcoming`, `is_past`

**2. Location Model** :
- ✅ City validation (non-empty)
- ✅ Optional fields (address, postal_code)
- ✅ Coordinates validation (latitude, longitude)

**3. DateRange Model** :
- ✅ Start/end date validation
- ✅ Date ordering (start < end)
- ✅ Duration calculation

**4. QueryResponse Model** :
- ✅ Response text validation
- ✅ Sources list validation
- ✅ Processing time validation

### test_rag_engine.py (272 lignes)

**Objectif** : Validation logique RAGEngine

#### Test Cases

**1. Classification (needs_rag)** :
```python
def test_needs_rag_search_queries(rag_engine):
    """Test classification SEARCH queries."""
    assert rag_engine.needs_rag("concerts jazz Paris")
    assert rag_engine.needs_rag("événements gratuits")
    assert rag_engine.needs_rag("expositions ce weekend")
```

```python
def test_needs_rag_chat_queries(rag_engine):
    """Test classification CHAT queries."""
    assert not rag_engine.needs_rag("bonjour")
    assert not rag_engine.needs_rag("merci beaucoup")
    assert not rag_engine.needs_rag("comment ça va")
```

**2. Embeddings (encode_query)** :
```python
def test_encode_query_returns_vector(rag_engine):
    """Test génération embedding."""
    embedding = rag_engine.encode_query("concert jazz")
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (1024,)  # Mistral Embed
    assert np.linalg.norm(embedding) == pytest.approx(1.0)  # Normalized
```

**3. Search (FAISS)** :
```python
def test_search_returns_top_k(rag_engine):
    """Test recherche FAISS retourne top-k."""
    results = rag_engine.search("concert jazz Paris", top_k=3)
    assert len(results) <= 3
    assert all("similarity" in r for r in results)
    assert all(0 <= r["similarity"] <= 1 for r in results)
```

**4. Generation (LLM)** :
```python
def test_generate_response_non_empty(rag_engine):
    """Test génération réponse non vide."""
    response = rag_engine.generate_response(
        query="concerts jazz",
        context="Concert Paris..."
    )
    assert len(response) > 0
    assert isinstance(response, str)
```

**5. Chat (Pipeline complet)** :
```python
def test_chat_search_mode(rag_engine):
    """Test chat en mode SEARCH (RAG)."""
    result = rag_engine.chat("concerts jazz Paris")
    assert result["used_rag"] is True
    assert len(result["sources"]) > 0
    assert "response" in result
```

```python
def test_chat_conversation_mode(rag_engine):
    """Test chat en mode CHAT (conversation)."""
    result = rag_engine.chat("bonjour")
    assert result["used_rag"] is False
    assert len(result["sources"]) == 0
```

---

## Tests d'Intégration (tests/integration/)

### test_api.py (245 lignes)

**Objectif** : Validation endpoints FastAPI

#### Test Cases

**1. GET /health** :
```python
@pytest.mark.integration
def test_health_endpoint(test_client):
    """Test health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "documents" in data
    assert data["status"] == "healthy"
```

**2. POST /search** :
```python
@pytest.mark.integration
def test_search_endpoint_valid(test_client):
    """Test search endpoint avec query valide."""
    response = test_client.post(
        "/search",
        json={"query": "concert jazz", "top_k": 3}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) <= 3
```

```python
@pytest.mark.integration
def test_search_endpoint_invalid_query(test_client):
    """Test search avec query invalide (vide)."""
    response = test_client.post(
        "/search",
        json={"query": "", "top_k": 5}
    )
    assert response.status_code == 422  # Validation Error
```

**3. POST /chat** :
```python
@pytest.mark.integration
def test_chat_creates_session(test_client):
    """Test chat crée nouvelle session si absente."""
    response = test_client.post(
        "/chat",
        json={"query": "Bonjour"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "response" in data
```

```python
@pytest.mark.integration
def test_chat_reuses_session(test_client):
    """Test chat réutilise session existante."""
    # Premier message
    resp1 = test_client.post("/chat", json={"query": "Bonjour"})
    session_id = resp1.json()["session_id"]
    
    # Deuxième message (même session)
    resp2 = test_client.post(
        "/chat",
        json={"query": "Des concerts ?", "session_id": session_id}
    )
    assert resp2.json()["session_id"] == session_id
```

**4. GET/DELETE /session/{id}** :
```python
@pytest.mark.integration
def test_get_session_history(test_client):
    """Test récupération historique session."""
    # Créer session
    resp = test_client.post("/chat", json={"query": "Bonjour"})
    session_id = resp.json()["session_id"]
    
    # Récupérer historique
    response = test_client.get(f"/session/{session_id}")
    assert response.status_code == 200
    history = response.json()["history"]
    assert len(history) >= 2  # user + assistant
```

**5. POST /rebuild** :
```python
@pytest.mark.integration
def test_rebuild_requires_api_key(test_client):
    """Test rebuild nécessite X-API-Key."""
    response = test_client.post("/rebuild")
    assert response.status_code == 401  # Unauthorized
```

---

## Tests End-to-End (tests/e2e/)

### test_rag_pipeline.py (232 lignes)

**Objectif** : Validation pipeline complet

#### Test Cases

**1. Full RAG Pipeline** :
```python
@pytest.mark.e2e
def test_full_rag_pipeline(rag_engine):
    """Test pipeline RAG complet de query à réponse."""
    query = "concerts de jazz ce weekend"
    
    # Exécuter pipeline complet
    result = rag_engine.chat(query)
    
    # Vérifier structure réponse
    assert "response" in result
    assert "sources" in result
    assert len(result["sources"]) > 0
    
    # Vérifier latence
    assert result["processing_time"] < 5.0  # Généreux pour e2e
    
    # Vérifier format sources
    for source in result["sources"]:
        assert "title" in source
        assert "similarity" in source
        assert 0 <= source["similarity"] <= 1
```

**2. Conversation Pipeline** :
```python
@pytest.mark.e2e
def test_conversation_pipeline(rag_engine):
    """Test pipeline conversation (sans RAG)."""
    result = rag_engine.chat("bonjour")
    
    assert result["used_rag"] is False
    assert len(result["sources"]) == 0
    assert len(result["response"]) > 0
```

**3. Multi-Turn Conversation** :
```python
@pytest.mark.e2e
def test_multi_turn_conversation(rag_engine):
    """Test conversation multi-tours avec mémoire."""
    history = []
    
    # Tour 1
    result1 = rag_engine.chat("Bonjour", history=history)
    history.extend([
        {"role": "user", "content": "Bonjour"},
        {"role": "assistant", "content": result1["response"]}
    ])
    
    # Tour 2 (avec contexte)
    result2 = rag_engine.chat("Des concerts ?", history=history)
    assert result2["used_rag"] is True
```

**4. Error Handling** :
```python
@pytest.mark.e2e
def test_handles_invalid_index(monkeypatch):
    """Test gestion erreur index FAISS invalide."""
    # Simuler index manquant
    monkeypatch.setattr("os.path.exists", lambda x: False)
    
    with pytest.raises(FileNotFoundError):
        RAGEngine()
```

---

## Fixtures Partagées (tests/conftest.py)

### Fixtures Principales

**1. sample_event** :
```python
@pytest.fixture
def sample_event() -> Event:
    """Événement de test unique."""
    return Event(
        title="Concert de Jazz",
        city="Paris",
        start_date="2025-01-20T20:00:00",
        end_date="2025-01-20T23:00:00",
        price_info="Gratuit",
        url="https://example.com/event1",
        category="Concert"
    )
```

**2. sample_events** :
```python
@pytest.fixture
def sample_events() -> list[Event]:
    """Liste d'événements pour tests intégration."""
    return [
        Event(...),  # 10-15 événements variés
        Event(...),
        ...
    ]
```

**3. rag_engine** :
```python
@pytest.fixture
def rag_engine() -> RAGEngine:
    """Instance RAGEngine pour tests."""
    # Utilise index test ou mock
    return RAGEngine()
```

**4. test_client** :
```python
@pytest.fixture
def test_client() -> TestClient:
    """Client FastAPI pour tests API."""
    from fastapi.testclient import TestClient
    from src.api.main import app
    return TestClient(app)
```

---

## Couverture de Code

### Résultats pytest --cov

```
---------- coverage: platform darwin, python 3.11.x -----------
Name                              Stmts   Miss  Cover
-----------------------------------------------------
src/__init__.py                       0      0   100%
src/api/main.py                     156     22    86%
src/config/constants.py              45      2    96%
src/config/settings.py               38      5    87%
src/data/models.py                  128     12    91%
src/rag/engine.py                   187     28    85%
src/rag/index_builder.py            142     35    75%
src/utils/__init__.py                 0      0   100%
-----------------------------------------------------
TOTAL                               696    104    85%
```

**Analyse** :
- ✅ **Global** : 85% (dépasse 80% cible)
- ✅ **Models** : 91% (excellent)
- ✅ **API** : 86% (très bon)
- ✅ **RAG Engine** : 85% (bon)
- ⚠️ **IndexBuilder** : 75% (acceptable, surtout build paths)

**Zones Non Couvertes** :
- Error handling edge cases (~40 lignes)
- Background tasks rebuild (~15 lignes)
- Logging statements (~20 lignes)
- Init code (~10 lignes)

---

## Outils de Qualité

### 1. Black (Formatage)

**Configuration** (`pyproject.toml`) :
```toml
[tool.black]
line-length = 100
target-version = ['py311']
```

**Usage** :
```bash
uv run black src tests scripts
```

**Résultat** : 100% des fichiers formatés automatiquement

### 2. Ruff (Linting)

**Configuration** :
```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "C", "B", "UP"]
ignore = ["E501"]  # Line too long (handled by black)
```

**Usage** :
```bash
uv run ruff check src tests scripts
```

**Résultat** : 0 erreurs, ~5 warnings (acceptable)

### 3. mypy (Type Checking)

**Configuration** :
```toml
[tool.mypy]
python_version = "3.11"
strict = true
disallow_untyped_defs = false  # Progressif
```

**Usage** :
```bash
uv run mypy src
```

**Résultat** : ~90% des fonctions typées

### 4. pre-commit (Hooks)

**Configuration** (`.pre-commit-config.yaml`) :
```yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    hooks:
      - id: ruff
```

**Usage** :
```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

---

## Dataset de Test Annoté

### tests/data/test_questions.json

**Structure** : 12 questions avec annotations

**Exemple** :
```json
{
  "id": 1,
  "question": "Quels concerts de jazz sont prévus ce weekend à Paris ?",
  "expected_keywords": ["concert", "jazz", "paris"],
  "category": "recherche_simple",
  "notes": "Test recherche basique avec filtres musicaux et géographiques"
}
```

**Catégories** :
- recherche_simple (4)
- filtres_multiples (2)
- recherche_temporelle (2)
- conversation (3)
- recherche_style (1)

**Usage** :
- Évaluation automatique (`scripts/evaluate_rag.py`)
- Regression testing
- Benchmarking qualité

---

## Commandes de Test

### Exécution Standard
```bash
# Tous les tests
uv run pytest

# Verbose avec détails
uv run pytest -v

# Avec couverture
uv run pytest --cov=src --cov-report=term

# Rapport HTML
uv run pytest --cov=src --cov-report=html
# Ouvrir htmlcov/index.html
```

### Sélection de Tests
```bash
# Par répertoire
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/e2e/

# Par marker
uv run pytest -m "not slow"
uv run pytest -m integration
uv run pytest -m e2e

# Par nom de fonction
uv run pytest -k "test_search"
uv run pytest -k "test_classification"
```

### Options Avancées
```bash
# Stop au premier échec
uv run pytest -x

# Réexécuter derniers échecs
uv run pytest --lf

# Parallélisation (requires pytest-xdist)
uv run pytest -n auto

# Verbose avec output
uv run pytest -v -s
```

---

## Métriques de Qualité

| Métrique | Cible | Actuel | Statut |
|----------|-------|--------|--------|
| **Test Coverage** | >80% | 85% | ✅ +5% |
| **Code Formatted** | 100% | 100% | ✅ |
| **Lint Errors** | 0 | 0 | ✅ |
| **Type Coverage** | >80% | 90% | ✅ +10% |
| **Tests Passing** | 100% | 100% | ✅ |
| **Pre-commit Hooks** | Pass | Pass | ✅ |

---

## Améliorations Futures

### Tests

**1. Property-Based Testing** (Hypothesis) :
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=500))
def test_encode_query_any_text(rag_engine, text):
    """Test encoding avec texte aléatoire."""
    embedding = rag_engine.encode_query(text)
    assert embedding.shape == (1024,)
```

**2. Mutation Testing** (mutpy) :
- Vérifie que tests détectent changements code
- Target : 80% mutation score

**3. Performance Benchmarks** (pytest-benchmark) :
```python
def test_search_performance(rag_engine, benchmark):
    """Benchmark recherche FAISS."""
    result = benchmark(rag_engine.search, "concert jazz", 5)
    assert benchmark.stats.mean < 0.1  # <100ms
```

**4. Contract Testing** :
- OpenAPI spec compliance
- Pact pour consumer contracts

### Qualité

**5. Stricter mypy** :
```toml
disallow_untyped_defs = true
disallow_any_generics = true
```

**6. Security Linting** (bandit) :
```bash
uv run bandit -r src
```

**7. Dependency Scanning** (safety) :
```bash
uv run safety check
```

**8. Code Complexity** (radon) :
```bash
uv run radon cc src -a
```

---

## Conclusion

### Points Forts

✅ **Coverage élevée** : 85% (5% au-dessus cible)
✅ **Tests organisés** : 3 niveaux (unit, integration, e2e)
✅ **Fixtures réutilisables** : DRY principle
✅ **Code formaté** : Black + Ruff (0 erreurs)
✅ **Type hints** : 90% des fonctions
✅ **Dataset annoté** : 12 questions test
✅ **Pre-commit hooks** : Qualité automatique

### Axes d'Amélioration

⚠️ **IndexBuilder coverage** : 75% → 85% (cible)
⚠️ **Performance tests** : Ajouter benchmarks
⚠️ **RAGAS tests** : Implémenter tests complets
⚠️ **Mutation testing** : Vérifier qualité tests

**Recommandation** : La stratégie de tests actuelle est **solide et production-ready**. Les améliorations listées sont des **optimisations** pour passer à un niveau enterprise.
