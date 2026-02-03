# 🎭 RAG Events Assistant

> **Assistant conversationnel intelligent** pour découvrir des événements culturels via des questions en langage naturel

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-LCEL-blueviolet.svg)](https://python.langchain.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41+-red.svg)](https://streamlit.io/)
[![Mistral AI](https://img.shields.io/badge/Mistral%20AI-latest-orange.svg)](https://mistral.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table des Matières

- [🎯 À Propos du Projet](#-à-propos-du-projet)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🏗️ Architecture](#️-architecture)
- [🚀 Installation](#-installation)
- [📊 Utilisation](#-utilisation)
- [🔌 API Reference](#-api-reference)
- [🧪 Tests & Évaluation](#-tests--évaluation)
- [🐳 Docker](#-docker)
- [📚 Documentation](#-documentation)
- [🤝 Contribution](#-contribution)
- [📄 License](#-license)

---

## 🎯 À Propos du Projet

**RAG Events Assistant** est un système de **Retrieval-Augmented Generation (RAG)** qui combine la puissance de la recherche sémantique avec l'intelligence des LLM pour aider les utilisateurs à découvrir des événements culturels pertinents.

### Qu'est-ce que le RAG ?

Le RAG (Retrieval-Augmented Generation) est une architecture d'IA qui enrichit les réponses des LLM avec des informations récupérées depuis une base de connaissances externe :

```
┌─────────────────────────────────────────────────────────────────┐
│                      PIPELINE RAG                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Question utilisateur                                            │
│       ↓                                                          │
│  Classification intelligente                                     │
│       ↓                                                          │
│  ┌────────────────────┬────────────────────┐                    │
│  │                    │                    │                    │
│  │   CHAT Mode        │   SEARCH Mode      │                    │
│  │   (Simple LLM)     │   (RAG Pipeline)   │                    │
│  │                    │                    │                    │
│  │   ↓                │   ↓                │                    │
│  │   Conversation     │   1. Embedding     │                    │
│  │   directe          │   2. FAISS Search  │                    │
│  │                    │   3. LLM + Context │                    │
│  │                    │                    │                    │
│  └────────────────────┴────────────────────┘                    │
│       ↓                                                          │
│  Réponse contextuelle + Sources                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

> **Architecture interne** : Chaque étape utilise des **chaînes LCEL** (LangChain Expression Language) composables via l'opérateur `|` : `prompt | llm | parser`

### Pourquoi ce projet ?

- **🎓 Pédagogique** : Implémentation complète d'un système RAG moderne
- **🏗️ Production-ready** : API REST, Docker, tests, évaluation RAGAS
- **🇫🇷 Multilingue** : Support du français avec embeddings Mistral
- **⚡ Performant** : FAISS pour la recherche vectorielle ultra-rapide
- **🔧 Flexible** : Support de plusieurs providers d'embeddings

### Stack Technologique

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Orchestration** | LangChain LCEL | Composition de chaînes RAG modulaires |
| **LLM** | Mistral AI via `langchain-mistralai` | Génération de réponses conversationnelles |
| **Embeddings** | Mistral Embed / HuggingFace via LangChain | Vectorisation sémantique multilingue |
| **Vector Store** | FAISS via `langchain-community` | Recherche de similarité ultra-rapide |
| **API** | FastAPI | REST API avec sessions et background tasks |
| **UI** | Streamlit | Interface chat moderne et réactive |
| **Data** | Open Agenda API | Source d'événements culturels |
| **Tests** | pytest + RAGAS | Tests unitaires/intégration + évaluation RAG |
| **Package Manager** | uv | Gestionnaire de dépendances moderne |

---

## ✨ Fonctionnalités

### 🤖 Intelligence Conversationnelle

- **Classification automatique** : Distingue questions conversationnelles vs recherches d'événements
- **Mémoire contextuelle** : Garde en mémoire les 5 derniers échanges
- **Réponses naturelles** : Génération en français avec ton conversationnel

### 🔍 Recherche Sémantique

- **Embeddings multilingues** : Support Mistral Embed (1024d) et Sentence Transformers (768d)
- **Recherche FAISS** : Top-k retrieval avec scores de similarité
- **Métadonnées riches** : Date, lieu, prix, URL, description

### 🌐 API REST & Interface

- **FastAPI** : Endpoints `/search`, `/chat`, `/session`, `/rebuild`
- **Streamlit** : Interface chat moderne avec thème sombre
- **Sessions** : Gestion de conversations multi-utilisateurs
- **Background tasks** : Rebuild d'index sans bloquer l'API

### 📊 Évaluation & Monitoring

- **RAGAS Integration** : Métriques de context precision, faithfulness, relevance
- **Métriques custom** : Keyword coverage, latency, success rate
- **Rapports JSON** : Résultats d'évaluation détaillés

---

## 🏗️ Architecture

### Structure du Projet

```
.
├── 📱 app.py                      # Interface Streamlit
├── 📦 src/
│   ├── config/                   # Configuration & constantes
│   │   ├── settings.py           # Pydantic Settings (env vars)
│   │   └── constants.py          # Constantes (prompts, paths, thresholds)
│   ├── data/                     # Modèles de données
│   │   └── models.py             # Pydantic models (Event, QueryResponse, etc.)
│   ├── rag/                      # Moteur RAG
│   │   ├── engine.py             # RAGEngine (classification, search, generation)
│   │   └── index_builder.py     # IndexBuilder (FAISS index construction)
│   └── api/                      # API REST
│       └── main.py               # FastAPI app (endpoints + sessions)
├── 📓 notebooks/                  # Pipeline de données (01-05)
├── 🧪 tests/                      # Tests unitaires/intégration/e2e
├── 📚 docs/                       # Documentation complète
├── 🐳 Dockerfile                  # Multi-stage build
├── 🐳 docker-compose.yml          # Orchestration API + Streamlit
└── ⚙️ pyproject.toml              # Configuration projet (uv)
```

### Modules Principaux

#### **RAGEngine** (`src/rag/engine.py`)

Le cœur du système RAG orchestré par **3 chaînes LCEL** :

- **Classification Chain** : `needs_rag(query)` → Routage CHAT vs SEARCH
- **Conversation Chain** : `conversation_response(query, history)` → Mode CHAT (sans contexte)
- **RAG Chain** : `generate_response(query, context, history)` → Mode SEARCH (avec contexte)
- `search(query, top_k)` : Recherche sémantique via `FAISS.similarity_search_with_score()`
- `chat(query, history)` : Pipeline complet unifié avec détection automatique

#### **Composants LangChain** (`src/rag/`)

| Module | Fonction | Composant LangChain |
|--------|----------|---------------------|
| `embeddings.py` | `get_embeddings()` | `MistralAIEmbeddings` / `HuggingFaceEmbeddings` |
| `llm.py` | `get_llm()` | `ChatMistralAI` avec paramètres configurables |
| `vectorstore.py` | `load/build/save_vectorstore()` | `FAISS` de `langchain-community` |

#### **IndexBuilder** (`src/rag/index_builder.py`)

Construction et gestion des index FAISS via LangChain :

- `load_documents()` : Chargement des événements vers `Document` LangChain
- `build_and_save()` : Construction via `FAISS.from_documents()` avec batch processing
- `rebuild()` : Pipeline complet avec callbacks de progression

### Chaînes LCEL

Le système utilise **LangChain Expression Language (LCEL)** pour composer des pipelines modulaires et testables :

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# Classification Chain - Détermine SEARCH vs CHAT
classification_chain = ChatPromptTemplate | LLM(temperature=0) | StrOutputParser

# Conversation Chain - Mode CHAT (sans contexte RAG)
conversation_chain = ChatPromptTemplate([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder("history"),
    ("human", "{query}")
]) | LLM | StrOutputParser

# RAG Chain - Mode SEARCH (avec contexte injecté)
rag_chain = ChatPromptTemplate([
    ("system", RAG_PROMPT_WITH_CONTEXT),
    MessagesPlaceholder("history"),
    ("human", "{query}")
]) | LLM | StrOutputParser
```

> 📚 Voir **[INTEGRATION_LANGCHAIN.md](docs/INTEGRATION_LANGCHAIN.md)** pour l'architecture complète et **[GUIDE_LANGCHAIN.md](docs/GUIDE_LANGCHAIN.md)** pour un guide pédagogique.

#### **FastAPI** (`src/api/main.py`)

API REST complète avec :

- **Sessions** : Stockage en mémoire avec historique (max 5 messages)
- **Endpoints** :
  - `GET /health` : Health check
  - `POST /search` : Recherche sans session
  - `POST /chat` : Chat avec session auto-créée
  - `GET/DELETE /session/{id}` : Gestion de sessions
  - `POST /rebuild` : Rebuild background avec auth API key
- **CORS** : Configuration pour intégration frontend
- **Background Tasks** : Rebuild non-bloquant

---

## 🚀 Installation

### Prérequis

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **uv** ([Installation](https://github.com/astral-sh/uv))
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Clé API Mistral AI** ([Console Mistral](https://console.mistral.ai/))

### Installation Locale

```bash
# 1. Cloner le repository
git clone https://github.com/votre-username/OC7---Projet-RAG-Assistant-Intelligent-Events.git
cd OC7---Projet-RAG-Assistant-Intelligent-Events

# 2. Installer les dépendances
uv sync --all-extras

# 3. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et ajouter votre MISTRAL_API_KEY

# 4. Préparer les données (voir section suivante)
uv run jupyter lab  # Exécuter notebooks 01-04
```

---

## 📊 Utilisation

### 1️⃣ Préparation des Données

Les notebooks Jupyter préparent les données dans l'ordre :

```bash
uv run jupyter lab
```

**Pipeline complet** :

1. **`01_data_collection.ipynb`** : Récupération depuis Open Agenda API
2. **`02_data_preprocessing.ipynb`** : Nettoyage HTML et structuration
3. **`03_create_embeddings_mistral.ipynb`** : Génération embeddings (Mistral ou ST)
4. **`04_build_faiss_index.ipynb`** : Construction index FAISS
5. **`05_rag_chatbot_mistral.ipynb`** : Test et validation du système

📚 Voir [notebooks/README.md](notebooks/README.md) pour plus de détails

### 2️⃣ Lancer l'Application

#### Option A : Interface Streamlit

```bash
uv run streamlit run app.py
```

Ouvrir http://localhost:8501 dans votre navigateur.

**Fonctionnalités UI** :
- Chat conversationnel avec mémoire
- Thème sombre moderne
- Affichage des sources et scores
- Paramètres ajustables (top_k, température)

#### Option B : API REST

```bash
uv run uvicorn src.api.main:app --reload
```

- **API** : http://localhost:8000
- **Documentation Swagger** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

---

## 🔌 API Reference

### Endpoints Principaux

#### 🏥 Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "index_loaded": true,
  "num_documents": 497
}
```

#### 🔍 Recherche Sémantique

```bash
POST /search
Content-Type: application/json

{
  "query": "concerts jazz à Paris ce weekend",
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "concerts jazz à Paris ce weekend",
  "response": "Voici 3 concerts de jazz à Paris ce weekend...",
  "sources": [
    {
      "title": "Paris Jazz Festival",
      "city": "Paris",
      "start_date": "2025-01-18T20:00:00",
      "url": "https://...",
      "score": 0.87
    }
  ],
  "processing_time": 1.23
}
```

#### 💬 Chat avec Session

```bash
POST /chat
Content-Type: application/json

{
  "query": "Bonjour, peux-tu me recommander un concert ?",
  "session_id": "optional-custom-id"
}
```

**Response:**
```json
{
  "session_id": "abc-123-def",
  "query": "Bonjour, peux-tu me recommander un concert ?",
  "response": "Bonjour ! Bien sûr, voici quelques concerts...",
  "sources": [...],
  "processing_time": 1.45
}
```

**Continuer la conversation:**

```bash
POST /chat
Content-Type: application/json

{
  "query": "Et à Marseille ?",
  "session_id": "abc-123-def"
}
```

#### 🔄 Rebuild Index

```bash
POST /rebuild
Content-Type: application/json
X-API-Key: your-rebuild-api-key

{
  "events": [...],
  "use_mistral_embeddings": true
}
```

**Response:**
```json
{
  "status": "started",
  "task_id": "rebuild-task-123"
}
```

### Gestion de Sessions

```bash
# Récupérer historique
GET /session/{session_id}

# Supprimer session
DELETE /session/{session_id}
```

---

## 🧪 Tests & Évaluation

### Tests Unitaires & Intégration

```bash
# Tous les tests
uv run pytest

# Avec couverture
uv run pytest --cov=src --cov-report=html
# Voir htmlcov/index.html

# Tests spécifiques
uv run pytest tests/unit/              # Tests unitaires
uv run pytest tests/integration/       # Tests d'intégration
uv run pytest tests/e2e/               # Tests end-to-end

# Exclure tests lents
uv run pytest -m "not slow"
```

### Évaluation RAGAS

```bash
# Évaluer le système RAG
uv run python scripts/evaluate_rag.py --test-file tests/data/test_questions.json

# Voir les résultats
cat tests/data/evaluation_results.json
```

**Métriques évaluées :**

| Métrique | Description | Cible |
|----------|-------------|-------|
| **Latency** | Temps de réponse moyen | < 3.0s |
| **Relevance** | Coverage des mots-clés attendus | > 80% |
| **Success Rate** | Taux de réponses réussies | > 70% |
| **RAGAS Scores** | Context precision, faithfulness | > 0.7 |

### Qualité du Code

```bash
# Formatage automatique
uv run black src tests scripts

# Linting
uv run ruff check src tests scripts

# Type checking
uv run mypy src
```

---

## 🐳 Docker

### Build & Run

```bash
# Build l'image
docker build -t rag-events-assistant .

# Run Streamlit (par défaut)
docker run -p 8501:8501 --env-file .env \
  -v $(pwd)/data:/app/data \
  rag-events-assistant

# Run FastAPI
docker run -p 8000:8000 --env-file .env \
  -v $(pwd)/data:/app/data \
  rag-events-assistant api
```

### Docker Compose

```bash
# Lancer API + Streamlit
docker-compose up

# Lancer uniquement l'API
docker-compose up api

# Lancer uniquement Streamlit
docker-compose up streamlit

# Logs en temps réel
docker-compose logs -f

# Arrêter
docker-compose down
```

**Services disponibles :**
- **API** : http://localhost:8000
- **Streamlit** : http://localhost:8501

---

## 📚 Documentation

Documentation complète dans le dossier `docs/` :

| Document | Description |
|----------|-------------|
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** | Architecture système détaillée |
| **[INTEGRATION_LANGCHAIN.md](docs/INTEGRATION_LANGCHAIN.md)** | Architecture LangChain LCEL complète |
| **[GUIDE_LANGCHAIN.md](docs/GUIDE_LANGCHAIN.md)** | Guide pédagogique LangChain (concepts, patterns) |
| **[COMPRENDRE_LE_RAG.md](docs/COMPRENDRE_LE_RAG.md)** | Guide pédagogique sur le RAG |
| **[GUIDE_DEMARRAGE.md](docs/GUIDE_DEMARRAGE.md)** | Guide de démarrage complet |
| **[REFERENCE_API.md](docs/REFERENCE_API.md)** | Documentation API complète |
| **[CLAUDE.md](CLAUDE.md)** | Instructions pour Claude Code |

---

## ⚙️ Configuration

Variables d'environnement (`.env`) :

| Variable | Description | Défaut | Requis |
|----------|-------------|--------|--------|
| `MISTRAL_API_KEY` | Clé API Mistral AI | - | ✅ |
| `REBUILD_API_KEY` | Clé pour endpoint `/rebuild` | - | ❌ |
| `EMBEDDING_PROVIDER` | `mistral` ou `sentence-transformers` | `mistral` | ❌ |
| `MISTRAL_EMBEDDING_MODEL` | Modèle d'embeddings Mistral | `mistral-embed` | ❌ |
| `SENTENCE_TRANSFORMER_MODEL` | Modèle ST alternatif | `paraphrase-multilingual-mpnet-base-v2` | ❌ |
| `LLM_MODEL` | Modèle LLM Mistral | `mistral-small-latest` | ❌ |
| `LLM_TEMPERATURE` | Température génération (0-2) | `0.7` | ❌ |
| `TOP_K_RESULTS` | Nombre de résultats FAISS | `5` | ❌ |
| `MIN_SIMILARITY_SCORE` | Seuil de similarité | `0.3` | ❌ |
| `DEFAULT_LOCATION` | Ville par défaut | `marseille` | ❌ |

---

## 🔧 Développement

### Structure de Développement

```bash
# Installer avec dépendances dev
uv sync --all-extras

# Pre-commit hooks
uv run pre-commit install
uv run pre-commit run --all-files
```

### Workflow de Contribution

1. **Fork** le repository
2. **Créer une branche** : `git checkout -b feature/ma-feature`
3. **Implémenter** avec tests
4. **Formatter** : `uv run black . && uv run ruff check .`
5. **Tests** : `uv run pytest --cov=src`
6. **Commit** : `git commit -m "feat: Description"`
7. **Push** : `git push origin feature/ma-feature`
8. **Pull Request** avec description détaillée

### Conventions de Code

- **Formatage** : Black (line length 100)
- **Linting** : Ruff
- **Type hints** : Python 3.11+ syntax (`list[str]` not `List[str]`)
- **Docstrings** : Google style
- **Commits** : [Conventional Commits](https://www.conventionalcommits.org/)

---

## 📈 Roadmap

### ✅ Implémenté

- [x] Pipeline RAG complet (RAGEngine, IndexBuilder)
- [x] API REST FastAPI avec sessions
- [x] Interface Streamlit moderne
- [x] Support multi-providers (Mistral + SentenceTransformers)
- [x] Tests unitaires/intégration/e2e
- [x] Évaluation RAGAS
- [x] Docker + docker-compose
- [x] Documentation complète

### 🚧 En Cours / Futur

- [ ] Persistance sessions (Redis/PostgreSQL)
- [ ] Authentification utilisateurs
- [ ] Mémoire de conversation avancée (vector memory)
- [ ] Support multi-langues (EN, ES)
- [ ] Cache intelligent pour embeddings
- [ ] Monitoring Prometheus + Grafana
- [ ] CI/CD GitHub Actions
- [ ] Deployment Kubernetes

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour plus de détails.

**Types de contributions :**
- 🐛 Bug fixes
- ✨ Nouvelles fonctionnalités
- 📝 Améliorations de documentation
- 🧪 Tests supplémentaires
- 🌍 Traductions

---

## 📄 License

Ce projet est sous licence **MIT**. Voir [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- **[LangChain](https://python.langchain.com/)** : Framework d'orchestration LLM avec LCEL
- **[Mistral AI](https://mistral.ai/)** : LLM et embeddings français de qualité
- **[FAISS](https://github.com/facebookresearch/faiss)** : Bibliothèque de recherche vectorielle ultra-rapide
- **[Open Agenda](https://openagenda.com/)** : API d'événements culturels
- **[Streamlit](https://streamlit.io/)** : Framework UI réactif
- **[FastAPI](https://fastapi.tiangolo.com/)** : Framework API moderne
- **[uv](https://github.com/astral-sh/uv)** : Gestionnaire de paquets Python rapide

---

## 📞 Contact & Support

- **Issues** : [GitHub Issues](https://github.com/votre-username/OC7---Projet-RAG-Assistant-Intelligent-Events/issues)
- **Discussions** : [GitHub Discussions](https://github.com/votre-username/OC7---Projet-RAG-Assistant-Intelligent-Events/discussions)

---

<div align="center">

**Fait avec ❤️ et ☕ en France**

[⬆ Retour en haut](#-rag-events-assistant)

</div>
