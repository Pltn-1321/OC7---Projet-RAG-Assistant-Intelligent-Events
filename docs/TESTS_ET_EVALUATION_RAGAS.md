# Tests et Évaluation RAGAS - Documentation Approfondie

> **Guide complet de la stratégie de tests et de l'évaluation RAGAS du système RAG Events Assistant**

---

## Table des Matières

1. [Vue d'ensemble de la stratégie de tests](#vue-densemble)
2. [Architecture des tests](#architecture-des-tests)
3. [Tests unitaires](#tests-unitaires)
4. [Tests d'intégration](#tests-dintégration)
5. [Tests end-to-end](#tests-end-to-end)
6. [Framework d'évaluation RAGAS](#framework-dévaluation-ragas)
7. [Métriques personnalisées](#métriques-personnalisées)
8. [Dataset de test annoté](#dataset-de-test-annoté)
9. [Exécution et interprétation](#exécution-et-interprétation)
10. [Guide d'amélioration](#guide-damélioration)

---

## Vue d'ensemble

### Philosophie de test

Le projet adopte une approche **pyramidale** des tests avec trois niveaux complémentaires :

```
          ╭──────────────╮
          │   E2E (10)   │  ← Pipeline complet, qualité réponses
          ├──────────────┤
          │Integration(17)│  ← Endpoints API, sessions
          ├──────────────┤
          │  Unit (~50+) │  ← Modèles, classification, embeddings
          ╰──────────────╯
                 +
     ╭─────────────────────╮
     │  Évaluation RAGAS   │  ← Qualité sémantique du RAG
     ╰─────────────────────╯
```

### Chiffres clés

| Métrique | Valeur |
|----------|--------|
| Lignes de code de test | ~1 354 |
| Fichiers de test | 4 modules + conftest |
| Questions d'évaluation annotées | 12 |
| Catégories de test | 5 (recherche_simple, filtres_multiples, temporelle, style, conversation) |
| Markers pytest | 4 (slow, integration, e2e, requires_api) |
| Cible couverture code | >80% |
| Cible latence | <3.0s |
| Cible pertinence | >80% |

---

## Architecture des tests

### Structure du répertoire

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures partagées (142 lignes)
│                                  # - sample_event, sample_events
│                                  # - mock_env_file, mock_faiss_index
│                                  # - sample_test_questions
├── data/
│   └── test_questions.json        # 12 questions annotées pour évaluation
├── unit/
│   ├── __init__.py
│   ├── test_models.py             # 463 lignes - Modèles Pydantic
│   └── test_rag_engine.py         # 273 lignes - RAGEngine
├── integration/
│   ├── __init__.py
│   └── test_api.py                # 245 lignes - FastAPI endpoints
└── e2e/
    ├── __init__.py
    └── test_rag_pipeline.py       # 232 lignes - Pipeline complet

scripts/
├── evaluate_rag.py                # Script d'évaluation RAGAS + métriques custom
└── api_test.py                    # Tests fonctionnels API (colorés)
```

### Configuration pytest (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
python_classes = "Test*"
markers = [
    "slow: marks tests as slow",
    "integration: marks integration tests",
    "e2e: marks end-to-end tests",
]
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
]
```

### Dépendances de test

```toml
# pyproject.toml - groupe "dev"
dev = [
    "pytest>=7.4.3,<9.0.0",
    "pytest-cov>=4.1.0,<6.0.0",
    "pytest-asyncio>=0.23.0,<1.0.0",
    # ...
]

# pyproject.toml - groupe "evaluation" (RAGAS)
evaluation = [
    "ragas>=0.1.0,<1.0.0",
    "datasets>=2.16.0,<3.0.0",
]
```

---

## Tests unitaires

### test_models.py — Validation des modèles Pydantic

**Objectif** : Garantir l'intégrité des structures de données utilisées dans tout le pipeline.

| Classe de test | Nombre de tests | Ce qui est vérifié |
|---|---|---|
| `TestCoordinates` | 8 | Lat/lon dans les bornes (-90/90, -180/180) |
| `TestLocation` | 6 | Nettoyage ville (trim, title case), valeurs par défaut |
| `TestDateRange` | 6 | Validité plages de dates, calcul durée |
| `TestEvent` | 13 | Propriétés calculées (`is_free`, `is_upcoming`), méthodes de transformation |
| `TestEvaluationQuestion` | 4 | Validation des questions d'évaluation |
| `TestEvaluationResult` | 4 | Calcul `keyword_coverage`, bornes des scores |
| `TestQueryResponse` | 2 | Structure réponse, comptage des sources |

**Patterns utilisés** :

```python
# Test de validation avec rejet attendu
def test_invalid_latitude(self):
    with pytest.raises(ValidationError):
        Coordinates(latitude=91.0, longitude=0.0)  # > 90°

# Test de propriétés calculées
def test_is_free_property_gratuit(self, sample_event):
    sample_event.price = "Gratuit"
    assert sample_event.is_free is True

# Test de transformation de données
def test_to_search_text_format(self, sample_event):
    text = sample_event.to_search_text()
    assert "Concert" in text
    assert "Paris" in text
```

### test_rag_engine.py — Logique du moteur RAG

**Objectif** : Valider chaque composant du pipeline RAG indépendamment.

| Classe de test | Marker | Ce qui est vérifié |
|---|---|---|
| `TestRAGEngineInitialization` | `requires_api` | Chargement index, gestion d'erreurs |
| `TestNeedsRAG` | `requires_api` | Classification SEARCH vs CHAT |
| `TestEncodeQuery` | `requires_api` | Vecteurs normalisés (norme ≈ 1.0), bonne dimension |
| `TestSearch` | `requires_api` | Structure résultats, scores de similarité |
| `TestChat` | `requires_api`, `slow` | Pipeline complet, gestion historique |
| `TestConversationResponse` | `requires_api` | Réponses conversationnelles (sans RAG) |
| `TestGenerateResponse` | `requires_api`, `slow` | Génération avec/sans contexte |

**Pattern de dégradation gracieuse** :

```python
@pytest.mark.requires_api
def test_search_returns_results(self):
    try:
        engine = RAGEngine()
    except FileNotFoundError:
        pytest.skip("Index FAISS non disponible")

    results = engine.search("concert", top_k=3)
    assert isinstance(results, list)
    assert len(results) <= 3
```

---

## Tests d'intégration

### test_api.py — Endpoints FastAPI

**Objectif** : Valider le comportement de l'API REST sans dépendance au pipeline RAG complet.

| Classe de test | Tests | Endpoints |
|---|---|---|
| `TestHealthEndpoint` | 2 | `GET /health` — codes 200/503 |
| `TestSearchEndpoint` | 6 | `POST /search` — validation, bornes top_k (1-20) |
| `TestChatEndpoint` | 5 | `POST /chat` — sessions, persistance |
| `TestSessionEndpoints` | 5 | `GET/DELETE /session/{id}` — cycle CRUD |
| `TestRebuildEndpoint` | 3 | `POST /rebuild` — authentification API key |
| `TestCORSHeaders` | 1 | `OPTIONS /health` — CORS preflight |
| `TestInputValidation` | 2 | Requêtes longues, formats invalides |

**Pattern de test API** :

```python
@pytest.mark.integration
def test_search_top_k_validation(self, client):
    # top_k trop élevé → erreur de validation
    response = client.post("/search", json={"query": "test", "top_k": 25})
    assert response.status_code == 422  # Validation error Pydantic

    # top_k dans les bornes → OK
    response = client.post("/search", json={"query": "test", "top_k": 5})
    assert response.status_code in [200, 500]  # 500 si engine non dispo
```

---

## Tests end-to-end

### test_rag_pipeline.py — Pipeline complet

**Objectif** : Valider les workflows utilisateur de bout en bout.

| Classe de test | Tests | Scénario |
|---|---|---|
| `TestRAGPipeline` | 4 | Workflows RAG complets, persistance sessions, sessions concurrentes |
| `TestSearchQuality` | 4 | Qualité par thème (musique, art, gratuit, géo) |
| `TestChatQuality` | 2 | Réponse en français, provision des sources |

**Test de sessions concurrentes** :

```python
@pytest.mark.e2e
def test_multiple_concurrent_sessions(self, client):
    sessions = []
    for i in range(3):
        resp = client.post("/chat", json={"query": f"Question {i}"})
        sessions.append(resp.json()["session_id"])

    # Vérifier que chaque session est indépendante
    assert len(set(sessions)) == 3
```

---

## Framework d'évaluation RAGAS

### Qu'est-ce que RAGAS ?

**RAGAS** (Retrieval Augmented Generation Assessment) est un framework open-source qui évalue spécifiquement les systèmes RAG selon deux axes :

1. **Qualité du Retrieval** : Les bons documents sont-ils récupérés ?
2. **Qualité de la Génération** : La réponse est-elle fidèle aux documents récupérés ?

### Pourquoi RAGAS pour ce projet ?

Les métriques classiques (BLEU, ROUGE, accuracy) sont inadaptées aux systèmes RAG car :

- **BLEU/ROUGE** comparent des n-grams → ne capturent pas la pertinence sémantique
- **Accuracy** nécessite une réponse exacte → impossible avec du texte généré
- **Perplexité** mesure la fluidité → pas la factualité

RAGAS évalue spécifiquement :
- La réponse est-elle **fidèle** aux sources (pas d'hallucination) ?
- Les sources sont-elles **pertinentes** à la question ?
- La réponse est-elle **complète** par rapport au contexte ?

### Métriques RAGAS implémentées

Le script `scripts/evaluate_rag.py` configure 4 métriques RAGAS :

#### 1. Faithfulness (Fidélité)

```
Score : 0.0 → 1.0
Question : "La réponse est-elle fidèle au contexte récupéré ?"
```

**Fonctionnement** :
1. Décompose la réponse en affirmations individuelles
2. Pour chaque affirmation, vérifie si elle est supportée par le contexte
3. Score = affirmations supportées / total affirmations

**Exemple** :
```
Contexte : "Concert de jazz au Caveau, 15€, le 25 janvier"
Réponse : "Il y a un concert de jazz au Caveau à 15€"
→ Faithfulness = 1.0 (toutes les affirmations sont dans le contexte)

Réponse : "Il y a un concert de jazz gratuit au Caveau"
→ Faithfulness = 0.67 ("gratuit" n'est pas dans le contexte = hallucination)
```

**Importance pour ce projet** : Détecte les hallucinations du LLM sur les prix, dates, lieux.

#### 2. Answer Relevancy (Pertinence de la réponse)

```
Score : 0.0 → 1.0
Question : "La réponse est-elle pertinente à la question posée ?"
```

**Fonctionnement** :
1. Génère N questions à partir de la réponse
2. Calcule la similarité cosinus entre les questions générées et la question originale
3. Score = moyenne des similarités

**Exemple** :
```
Question : "Concerts de jazz à Paris ce weekend ?"
Réponse : "Voici des concerts de jazz à Paris samedi..."
→ Questions générées : "Quels concerts à Paris ?", "Jazz ce weekend ?"
→ Similarité élevée → Answer Relevancy ≈ 0.9

Réponse : "Le jazz est un genre musical né à la Nouvelle-Orléans..."
→ Questions générées : "Qu'est-ce que le jazz ?", "Origine du jazz ?"
→ Similarité faible → Answer Relevancy ≈ 0.3
```

**Importance pour ce projet** : Vérifie que le chatbot répond à la question posée et ne divague pas.

#### 3. Context Precision (Précision du contexte)

```
Score : 0.0 → 1.0
Question : "Les documents récupérés sont-ils pertinents ?"
```

**Fonctionnement** :
1. Pour chaque document récupéré, évalue s'il est pertinent pour la question
2. Pondère par le rang (documents en premier = plus importants)
3. Score = précision pondérée

**Exemple** :
```
Question : "Concerts jazz Paris"
Contexte récupéré :
  1. Concert jazz Caveau (Paris) → Pertinent ✅
  2. Exposition photo (Lyon) → Non pertinent ❌
  3. Festival jazz Sunset (Paris) → Pertinent ✅
→ Context Precision = (1×1 + 0×0.5 + 1×0.33) / normalization
```

**Importance pour ce projet** : Évalue la qualité du retrieval FAISS — les embeddings Mistral trouvent-ils les bons événements ?

#### 4. Context Recall (Rappel du contexte)

```
Score : 0.0 → 1.0
Question : "Tous les documents nécessaires sont-ils récupérés ?"
```

**Fonctionnement** :
1. Compare la réponse attendue (ground truth) avec les contextes récupérés
2. Vérifie que chaque élément de la réponse attendue est couvert par au moins un contexte
3. Score = éléments couverts / total éléments attendus

**Exemple** :
```
Ground truth : "concert jazz paris janvier"
Contextes récupérés mentionnent : "concert", "jazz", "Paris"
→ "janvier" non couvert → Context Recall = 0.75
```

**Importance pour ce projet** : Vérifie que `top_k=5` est suffisant pour couvrir les besoins informationnels.

### Implémentation dans le projet

#### Pipeline d'évaluation

```
┌─────────────────────────────────────────────────────────────────┐
│                    scripts/evaluate_rag.py                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. load_test_questions()                                       │
│     └─ Charge tests/data/test_questions.json                    │
│     └─ Valide avec modèle EvaluationQuestion                   │
│                                                                 │
│  2. run_rag_queries()                                           │
│     ├─ Initialise RAGEngine                                     │
│     ├─ Pour chaque question :                                   │
│     │   ├─ engine.search(query, top_k) → contextes              │
│     │   ├─ engine.chat(query) → réponse + used_rag              │
│     │   ├─ Mesure latence (time.time)                           │
│     │   └─ calculate_keyword_coverage()                         │
│     └─ Retourne liste de résultats                              │
│                                                                 │
│  3. run_ragas_evaluation() [optionnel]                          │
│     ├─ Filtre résultats RAG uniquement (used_rag=True)          │
│     ├─ Construit Dataset HuggingFace :                          │
│     │   ├─ question: str                                        │
│     │   ├─ answer: str                                          │
│     │   ├─ contexts: list[str]                                  │
│     │   └─ ground_truth: str (mots-clés concaténés)             │
│     ├─ ragas.evaluate(dataset, metrics=[...])                   │
│     └─ Retourne scores RAGAS                                    │
│                                                                 │
│  4. generate_report()                                           │
│     ├─ Agrège métriques (latence, couverture, par catégorie)    │
│     ├─ Intègre scores RAGAS                                     │
│     └─ Sauvegarde JSON → data/processed/evaluation_results.json │
│                                                                 │
│  5. print_summary()                                             │
│     └─ Affichage formaté console                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Code de l'évaluation RAGAS

```python
# scripts/evaluate_rag.py - Fonction clé

def run_ragas_evaluation(results: list[dict]) -> dict:
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import (
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )

    # Seuls les résultats ayant utilisé le RAG sont évalués
    rag_results = [r for r in results if r["used_rag"] and r["contexts"]]

    # Construction du dataset au format RAGAS
    dataset_dict = {
        "question": [r["question"] for r in rag_results],
        "answer": [r["answer"] for r in rag_results],
        "contexts": [r["contexts"] for r in rag_results],
        "ground_truth": [
            " ".join(r["expected_keywords"]) if r["expected_keywords"]
            else r["question"]
            for r in rag_results
        ],
    }

    dataset = Dataset.from_dict(dataset_dict)

    ragas_results = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
    )
    return dict(ragas_results)
```

#### Préparation du ground truth

Le ground truth RAGAS est construit à partir des `expected_keywords` du dataset de test :

```python
# Pour une question avec expected_keywords = ["concert", "jazz", "paris"]
# → ground_truth = "concert jazz paris"

# Pour une question sans keywords (conversation)
# → Filtrée car used_rag = False
```

> **Note** : Cette approche par mots-clés est une approximation. Un ground truth idéal
> contiendrait des réponses complètes rédigées manuellement (voir section Améliorations).

---

## Métriques personnalisées

En complément de RAGAS, le projet implémente des métriques custom rapides :

### 1. Latence (Performance)

```python
start_time = time.time()
# ... exécution pipeline ...
latency = time.time() - start_time
```

- **Cible** : < 3.0 secondes (défini dans `constants.py` : `TARGET_LATENCY_SECONDS = 3.0`)
- **Inclut** : Encoding query + recherche FAISS + génération LLM
- **N'inclut pas** : Temps réseau client, rendu UI

### 2. Couverture de mots-clés (Pertinence)

```python
def calculate_keyword_coverage(answer: str, expected_keywords: list[str]) -> dict:
    answer_lower = answer.lower()
    found = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return {
        "keywords_found": found,
        "keywords_total": len(expected_keywords),
        "coverage": found / len(expected_keywords),
    }
```

- **Cible** : > 80% (`TARGET_RELEVANCE_SCORE = 0.8`)
- **Méthode** : Recherche sous-chaîne case-insensitive
- **Limites** : Ne capture pas les synonymes ni la sémantique

### 3. Classification RAG (Accuracy)

- **Mesure** : Le champ `used_rag` dans la réponse de `engine.chat()`
- **Attendu** : Questions de catégorie `conversation` → `used_rag=False`, autres → `used_rag=True`
- **Cible** : 100% (atteint actuellement)

### Comparaison métriques custom vs RAGAS

| Aspect | Métriques Custom | RAGAS |
|--------|-----------------|-------|
| **Vitesse** | Instantané | Plusieurs minutes |
| **Dépendances** | Aucune | ragas, datasets, LLM |
| **Profondeur** | Surface (mots-clés) | Sémantique (compréhension) |
| **Hallucinations** | Non détectées | Détectées (faithfulness) |
| **Coût** | Gratuit | Appels LLM supplémentaires |
| **Quand utiliser** | CI/CD, itérations rapides | Évaluations ponctuelles |

---

## Dataset de test annoté

### Structure (`tests/data/test_questions.json`)

```json
{
    "id": 1,
    "question": "Quels concerts de jazz sont prevus ce weekend a Paris ?",
    "expected_keywords": ["concert", "jazz", "paris"],
    "category": "recherche_simple",
    "notes": "Test de recherche basique avec filtres musicaux et geographiques"
}
```

### Modèle de validation

```python
# src/data/models.py
class EvaluationQuestion(BaseModel):
    id: int = Field(..., description="Question ID")
    question: str = Field(..., min_length=3, description="Test question")
    expected_keywords: list[str] = Field(default_factory=list)
    category: str = Field("general", description="Question category")
    expected_event_count: Optional[int] = Field(None)
    notes: Optional[str] = Field(None)
```

### Répartition par catégorie

| Catégorie | Questions | Rôle dans l'évaluation | Évaluée par RAGAS ? |
|-----------|-----------|------------------------|---------------------|
| `recherche_simple` | 4 | Valider le retrieval de base | ✅ Oui |
| `filtres_multiples` | 2 | Tester la combinaison de critères | ✅ Oui |
| `recherche_temporelle` | 2 | Évaluer la compréhension du temps | ✅ Oui |
| `recherche_style` | 1 | Tester les genres/styles | ✅ Oui |
| `conversation` | 3 | Vérifier la classification CHAT | ❌ Non (pas de RAG) |

### Détail des 12 questions

| ID | Question | Mots-clés | Catégorie |
|----|----------|-----------|-----------|
| 1 | Concerts de jazz ce weekend à Paris ? | concert, jazz, paris | recherche_simple |
| 2 | Événements gratuits pour enfants dimanche ? | gratuit, enfants, dimanche | filtres_multiples |
| 3 | Exposition d'art contemporain à Marseille | exposition, art, marseille | recherche_simple |
| 4 | Spectacles de théâtre cette semaine ? | theatre, spectacle, semaine | recherche_temporelle |
| 5 | Bonjour, comment ça va ? | _(aucun)_ | conversation |
| 6 | Merci beaucoup pour ton aide ! | _(aucun)_ | conversation |
| 7 | Que faire ce soir à Marseille ? | marseille, soir | recherche_simple |
| 8 | Des festivals de musique cet été ? | festival, musique, été | recherche_temporelle |
| 9 | Activités culturelles gratuites le weekend | gratuit, culturel, weekend | filtres_multiples |
| 10 | Concerts electro ou techno à Lyon | concert, electro, lyon | recherche_style |
| 11 | Tu peux m'aider à trouver des sorties ? | _(aucun)_ | conversation |
| 12 | Ateliers créatifs pour adultes | atelier, creatif, adulte | recherche_simple |

---

## Exécution et interprétation

### Commandes

```bash
# Installation des dépendances RAGAS
uv sync --extra evaluation

# Évaluation complète (métriques custom + RAGAS)
uv run python scripts/evaluate_rag.py

# Évaluation rapide (sans RAGAS)
uv run python scripts/evaluate_rag.py --skip-ragas

# Avec fichier de questions personnalisé
uv run python scripts/evaluate_rag.py --test-file tests/data/custom_questions.json

# Avec paramètres personnalisés
uv run python scripts/evaluate_rag.py --top-k 10 --output reports/eval.json
```

### Prérequis

1. **Index FAISS construit** : Les fichiers `data/indexes/index.faiss` et `index.pkl` doivent exister
2. **Clé API Mistral** : Variable `MISTRAL_API_KEY` dans `.env`
3. **Pour RAGAS** : Packages `ragas` et `datasets` installés (`uv sync --extra evaluation`)

### Sortie console

```
============================================================
EVALUATION DU SYSTEME RAG
============================================================
Fichier de questions: tests/data/test_questions.json
Fichier de sortie: data/processed/evaluation_results.json
Top-K: 5
RAGAS: Active

12 questions chargees

============================================================
INITIALISATION
============================================================
Index charge: 497 documents
Dimension embeddings: 1024

============================================================
EXECUTION DES 12 REQUETES
============================================================

[1/12] Quels concerts de jazz sont prevus ce weekend...
   Latence: 1.47s | RAG: True | Keywords: 100%

[5/12] Bonjour, comment ca va ?...
   Latence: 1.98s | RAG: False | Keywords: 100%

============================================================
EVALUATION RAGAS
============================================================
Cela peut prendre plusieurs minutes...

============================================================
RESUME DE L'EVALUATION
============================================================

Questions evaluees: 12
  - Requetes RAG: 9
  - Conversations: 3

Performance:
  Latence moyenne: 2.41s
  Temps total: 28.95s

Qualite:
  Couverture mots-cles: 81.5%

Scores RAGAS:
  faithfulness: 0.847
  answer_relevancy: 0.791
  context_precision: 0.722
  context_recall: 0.683
```

### Format du rapport JSON

```json
{
  "timestamp": "2026-01-16T14:30:00",
  "num_questions": 12,
  "aggregate_metrics": {
    "avg_latency_seconds": 2.413,
    "avg_keyword_coverage": 0.815,
    "total_execution_time": 28.95,
    "rag_queries": 9,
    "conversation_queries": 3
  },
  "ragas_scores": {
    "faithfulness": 0.847,
    "answer_relevancy": 0.791,
    "context_precision": 0.722,
    "context_recall": 0.683
  },
  "by_category": {
    "recherche_simple": {
      "count": 4,
      "avg_latency": 2.56,
      "avg_coverage": 0.917
    }
  },
  "individual_results": [
    {
      "question_id": 1,
      "question": "Quels concerts de jazz...",
      "category": "recherche_simple",
      "latency": 1.47,
      "used_rag": true,
      "keywords_found": 3,
      "keywords_total": 3,
      "coverage": 1.0
    }
  ]
}
```

### Interprétation des scores RAGAS

| Score | Interprétation | Action recommandée |
|-------|---------------|-------------------|
| **Faithfulness > 0.85** | Le LLM ne hallucine presque jamais | Maintenir |
| **Faithfulness < 0.7** | Hallucinations fréquentes | Revoir le prompt, réduire temperature |
| **Answer Relevancy > 0.8** | Réponses pertinentes | Maintenir |
| **Answer Relevancy < 0.6** | Réponses hors sujet | Vérifier la classification needs_rag |
| **Context Precision > 0.75** | Retrieval précis | Maintenir |
| **Context Precision < 0.5** | Documents non pertinents récupérés | Améliorer embeddings ou reranking |
| **Context Recall > 0.7** | Informations suffisantes | Maintenir |
| **Context Recall < 0.5** | Infos manquantes | Augmenter top_k ou enrichir l'index |

### Seuils cibles du projet

Définis dans `src/config/constants.py` :

```python
TARGET_LATENCY_SECONDS = 3.0   # Temps de réponse max
TARGET_RELEVANCE_SCORE = 0.8   # Couverture mots-clés min
TARGET_COVERAGE = 0.7          # Couverture questions réussies
```

---

## Fixtures et patterns de test

### Fixtures principales (`conftest.py`)

```python
@pytest.fixture
def sample_event() -> Event:
    """Événement jazz futur à Paris (dans 7 jours)."""
    return Event(
        id="test-event-001",
        title="Concert de Jazz au Caveau",
        description_clean="Soirée jazz manouche avec Django Legacy Quartet",
        location=Location(city="Paris", address="15 rue de la Huchette"),
        dates=DateRange(start=now + 7days, end=now + 7days + 3hrs),
        price="15€",
        category="Concert",
        tags=["jazz", "concert", "musique"]
    )

@pytest.fixture
def sample_events() -> list[Event]:
    """10 événements variés (alternance Paris/Lyon, Concert/Exposition)."""

@pytest.fixture
def mock_faiss_index(tmp_path) -> Path:
    """Répertoire temporaire simulant un index FAISS."""

@pytest.fixture
def sample_test_questions() -> list[dict]:
    """Charge les 12 questions de test_questions.json."""
```

### Pattern : Dégradation gracieuse

Tous les tests dépendant de ressources externes utilisent ce pattern :

```python
try:
    engine = RAGEngine()
except FileNotFoundError:
    pytest.skip("Index FAISS non disponible")
```

### Pattern : Flexibilité de status code

Les tests d'intégration acceptent des codes alternatifs pour fonctionner sans engine :

```python
response = client.post("/search", json={"query": "test", "top_k": 5})
assert response.status_code in [200, 500]  # 500 si engine non initialisé
```

---

## Guide d'amélioration

### Améliorations RAGAS recommandées

#### 1. Enrichir le ground truth

**État actuel** : Le ground truth est une concaténation des `expected_keywords`.

**Amélioration** : Rédiger des réponses de référence complètes.

```json
{
    "id": 1,
    "question": "Quels concerts de jazz sont prévus ce weekend à Paris ?",
    "expected_keywords": ["concert", "jazz", "paris"],
    "ground_truth": "Ce weekend à Paris, il y a un concert de jazz au Caveau de la Huchette le samedi à 20h (15€) et un concert de jazz manouche au Duc des Lombards le dimanche à 21h (20€).",
    "expected_contexts": [
        "Concert jazz Caveau de la Huchette - Paris - samedi 20h - 15€",
        "Jazz manouche Duc des Lombards - Paris - dimanche 21h - 20€"
    ],
    "category": "recherche_simple"
}
```

**Impact** : Context Recall beaucoup plus précis, Faithfulness plus fiable.

#### 2. Augmenter le dataset à 30+ questions

| Catégorie | Actuel | Cible | Exemples à ajouter |
|-----------|--------|-------|---------------------|
| recherche_simple | 4 | 8 | Musées, spectacles, conférences |
| filtres_multiples | 2 | 6 | Prix+lieu, date+catégorie+public |
| recherche_temporelle | 2 | 5 | "Ce mois-ci", "demain soir", "vacances" |
| recherche_style | 1 | 4 | Classique, hip-hop, théâtre contemporain |
| conversation | 3 | 5 | Questions ambiguës, reformulations |
| edge_cases | 0 | 4 | Ville inconnue, requêtes vides, langues mixtes |

#### 3. Ajouter des métriques RAGAS supplémentaires

```python
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    # Nouvelles métriques
    answer_correctness,    # Correction factuelle vs ground truth
    answer_similarity,     # Similarité sémantique avec ground truth
)
```

#### 4. Intégrer RAGAS dans le CI/CD

```yaml
# .github/workflows/evaluation.yml (exemple)
evaluate:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: uv sync --extra evaluation
    - run: uv run python scripts/evaluate_rag.py --skip-ragas  # Rapide en CI
    - run: |
        # Vérifier les seuils
        python -c "
        import json
        report = json.load(open('data/processed/evaluation_results.json'))
        assert report['aggregate_metrics']['avg_latency_seconds'] < 3.0
        assert report['aggregate_metrics']['avg_keyword_coverage'] > 0.8
        "
```

#### 5. Comparaison entre configurations

Utiliser l'évaluation pour comparer :
- **Embedding providers** : Mistral vs Sentence-Transformers
- **Valeurs de top_k** : 3 vs 5 vs 10
- **Modèles LLM** : mistral-small vs mistral-medium
- **Temperatures** : 0.3 vs 0.7 vs 1.0

```bash
# Exemple : comparer top_k
uv run python scripts/evaluate_rag.py --top-k 3 --output eval_k3.json
uv run python scripts/evaluate_rag.py --top-k 5 --output eval_k5.json
uv run python scripts/evaluate_rag.py --top-k 10 --output eval_k10.json
```

---

## Commandes de référence rapide

```bash
# === Tests pytest ===
uv run pytest                              # Tous les tests
uv run pytest tests/unit/                  # Unitaires seulement
uv run pytest tests/integration/           # Intégration seulement
uv run pytest tests/e2e/                   # E2E seulement
uv run pytest -m "not slow"               # Exclure tests lents
uv run pytest -m "requires_api"           # Seulement tests API
uv run pytest --cov=src --cov-report=html  # Avec couverture HTML
uv run pytest -x                           # Arrêter au premier échec
uv run pytest -k "test_search"            # Par nom de test

# === Évaluation RAGAS ===
uv sync --extra evaluation                 # Installer RAGAS
uv run python scripts/evaluate_rag.py      # Évaluation complète
uv run python scripts/evaluate_rag.py --skip-ragas  # Sans RAGAS (rapide)
uv run python scripts/evaluate_rag.py --top-k 10    # Avec 10 documents

# === Qualité de code ===
uv run black src tests scripts             # Formatage
uv run ruff check src tests scripts        # Linting
uv run mypy src                            # Type checking

# === Tests API fonctionnels ===
uv run python scripts/api_test.py          # Tests API colorés
uv run python scripts/api_test.py -v       # Mode verbose
```

---

## Conclusion

### Forces du système d'évaluation

- **Double niveau** : Métriques rapides (CI) + RAGAS approfondi (ponctuellement)
- **Dataset structuré** : Questions annotées par catégorie avec mots-clés attendus
- **Automatisation** : Script unique pour évaluation complète avec rapport JSON
- **Modèles validés** : Pydantic garantit l'intégrité des données d'évaluation
- **Dégradation gracieuse** : Fonctionne sans RAGAS (`--skip-ragas`) si les dépendances manquent

### Limites actuelles

- **Ground truth simplifié** : Mots-clés uniquement, pas de réponses de référence complètes
- **Dataset limité** : 12 questions (9 évaluées par RAGAS)
- **Pas d'évaluation automatisée en CI** : RAGAS nécessite un LLM (coûteux)
- **Pas de tracking temporel** : Pas d'historique des scores pour détecter les régressions

### Priorités d'amélioration

1. **Court terme** : Enrichir le ground truth avec des réponses complètes
2. **Court terme** : Ajouter 20 questions pour couvrir plus de cas
3. **Moyen terme** : Intégrer les métriques custom (sans RAGAS) dans le CI
4. **Moyen terme** : Créer un dashboard de suivi des scores dans le temps
5. **Long terme** : Évaluation A/B entre configurations d'embeddings et modèles
