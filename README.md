# 🎭 RAG Events Assistant

> **Assistant conversationnel intelligent** pour la découverte d'événements culturels — Propulsé par RAG, LangChain et Mistral AI

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)](https://www.typescriptlang.org/)
[![LangChain](https://img.shields.io/badge/LangChain-LCEL-blueviolet.svg)](https://python.langchain.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_Store-orange.svg)](https://github.com/facebookresearch/faiss)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 À propos du projet

**RAG Events Assistant** est un système avancé d'IA conversationnelle qui utilise la technique **RAG (Retrieval-Augmented Generation)** pour recommander des événements culturels de manière personnalisée et contextuelle.

### 🎯 Caractéristiques principales

- **🔍 Recherche sémantique avancée** : Utilise FAISS et les embeddings Mistral pour comprendre l'intention utilisateur au-delà des mots-clés
- **🤖 Classification intelligente** : Distingue automatiquement les questions conversationnelles des recherches d'événements
- **💬 Mémoire conversationnelle** : Maintient le contexte sur plusieurs échanges pour des recommandations cohérentes
- **🎨 Interface moderne** : Frontend React avec TypeScript et design system shadcn/ui
- **⚡ API haute performance** : Backend FastAPI asynchrone avec validation Pydantic
- **🔧 Architecture modulaire** : Orchestration LangChain LCEL pour faciliter l'évolution du pipeline

### 🏗️ Architecture système

```
┌─────────────────────────────────────────────────────────────────────┐
│                         UTILISATEUR                                 │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
            ┌───────────────┴────────────────┐
            │                                │
            ▼                                ▼
    ┌───────────────┐              ┌──────────────────┐
    │   Frontend    │    HTTP      │    Streamlit     │
    │   React +     │◄────────────►│   (Alternative)  │
    │  TypeScript   │              │                  │
    └───────┬───────┘              └────────┬─────────┘
            │                               │
            └───────────────┬───────────────┘
                            │ REST API
                            ▼
            ┌──────────────────────────────────────┐
            │       Backend FastAPI                │
            │   • Validation Pydantic              │
            │   • Session Management               │
            │   • Background Tasks                 │
            └────────────────┬─────────────────────┘
                             │
                             ▼
            ┌──────────────────────────────────────┐
            │      RAG Engine (LangChain LCEL)     │
            │                                      │
            │  Query → Classification → Routing   │
            │      ↓           ↓                   │
            │   [CHAT]    [SEARCH + RAG]          │
            └────────────────┬─────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    ┌────────┐         ┌──────────┐      ┌──────────┐
    │ FAISS  │         │ Mistral  │      │ Session  │
    │Vector  │         │   AI     │      │  Store   │
    │ Store  │         │   API    │      │ (Memory) │
    └────────┘         └──────────┘      └──────────┘
    1024-dim            LLM + Emb         History
    embeddings          API calls         Management
```

---

## Structure du Monorepo

```
.
├── backend/                 # API Python + RAG Engine
│   ├── src/                 # Code source Python
│   │   ├── api/             # FastAPI REST API
│   │   ├── rag/             # Moteur RAG (LangChain LCEL)
│   │   ├── config/          # Configuration & constantes
│   │   └── data/            # Modèles de données
│   ├── tests/               # Tests unitaires, intégration, e2e
│   ├── notebooks/           # Jupyter notebooks (pipeline data)
│   ├── scripts/             # Scripts utilitaires
│   ├── docs/                # Documentation backend
│   ├── app.py               # Interface Streamlit (alternative)
│   └── pyproject.toml       # Dépendances Python (uv)
│
├── frontend/                # Application React
│   ├── src/                 # Code source TypeScript
│   ├── docs/                # Documentation frontend
│   └── package.json         # Dépendances Node.js
│
├── docker-compose.yml       # Orchestration des services
├── CLAUDE.md                # Instructions Claude Code
├── LICENSE                  # Licence MIT
└── README.md                # Ce fichier
```

---

## 🚀 Démarrage Rapide

### 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python 3.11+** ([télécharger](https://www.python.org/downloads/))
- **uv** - Gestionnaire de paquets Python ultra-rapide ([installer](https://github.com/astral-sh/uv))
- **Node.js 18+** et **npm** ([télécharger](https://nodejs.org/))
- **Docker** et **Docker Compose** (optionnel, pour conteneurisation) ([installer](https://docs.docker.com/get-docker/))
- **Clé API Mistral AI** - Créer un compte gratuit sur [console.mistral.ai](https://console.mistral.ai/)

### 📦 Installation

#### 1️⃣ Cloner le repository

```bash
git clone https://github.com/votre-username/OC7---Projet-RAG-Assistant-Intelligent-Events.git
cd OC7---Projet-RAG-Assistant-Intelligent-Events
```

#### 2️⃣ Configuration des variables d'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env et ajouter votre clé API Mistral
# MISTRAL_API_KEY=votre_cle_api_ici
```

#### 3️⃣ Installation des dépendances

**Backend** (depuis la racine) :
```bash
cd backend

# Installation avec uv (recommandé - ultra-rapide)
uv sync --all-extras

# Ou avec pip classique
pip install -e ".[dev,test]"

cd ..
```

**Frontend** (depuis la racine) :
```bash
cd frontend

# Installation des dépendances npm
npm install

# Configuration de l'URL API (optionnel)
echo "VITE_API_URL=http://localhost:8000" > .env.local

cd ..
```

### ▶️ Lancement du projet

#### Option 1 : Docker Compose (recommandé pour la production)

```bash
# Lancer tous les services en une commande
docker-compose up

# En mode détaché (background)
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down
```

#### Option 2 : Développement local (recommandé pour le développement)

**Terminal 1 - Backend API** :
```bash
cd backend

# Lancer FastAPI avec rechargement automatique
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Ou avec uvicorn directement
uvicorn src.api.main:app --reload
```

**Terminal 2 - Frontend React** (dans un nouveau terminal) :
```bash
cd frontend

# Lancer le serveur de développement Vite
npm run dev

# Ou avec un port spécifique
npm run dev -- --port 5173
```

**Terminal 3 - Streamlit (optionnel, interface alternative)** :
```bash
cd backend

# Lancer l'interface Streamlit
uv run streamlit run app.py

# Ou avec streamlit directement
streamlit run app.py --server.port 8501
```

### 🌐 Services disponibles

Une fois lancé, les services sont accessibles aux URLs suivantes :

| Service | URL | Description | Technologies |
|---------|-----|-------------|--------------|
| **Frontend React** | [http://localhost:5173](http://localhost:5173) | Interface utilisateur moderne et responsive | React 18, TypeScript, Tailwind CSS |
| **API FastAPI** | [http://localhost:8000](http://localhost:8000) | REST API + Documentation Swagger | FastAPI, Python 3.11+ |
| **API Docs (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) | Documentation interactive de l'API | OpenAPI 3.0 |
| **Streamlit UI** | [http://localhost:8501](http://localhost:8501) | Interface alternative Python | Streamlit |

### ✅ Vérification de l'installation

**Tester l'API** :
```bash
# Health check
curl http://localhost:8000/health

# Recherche d'événements
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "concerts ce week-end", "top_k": 3}'
```

**Tester le backend** :
```bash
cd backend

# Lancer les tests
uv run pytest

# Avec couverture de code
uv run pytest --cov=src --cov-report=html

# Ouvrir le rapport de couverture
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Tester le frontend** :
```bash
cd frontend

# Lancer les tests
npm run test

# Build de production
npm run build

# Prévisualiser le build
npm run preview
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [backend/README.md](backend/README.md) | Guide complet du backend Python |
| [backend/docs/](backend/docs/) | Architecture, API, guides techniques |
| [frontend/README.md](frontend/README.md) | Guide du frontend React |
| [frontend/docs/](frontend/docs/) | Composants, design system |

---

## 🛠️ Stack Technique Complète

### Backend & IA/ML

| Technologie | Version | Usage | Rôle dans le projet |
|-------------|---------|-------|---------------------|
| **Python** | 3.11+ | Langage principal | Base du backend avec typage moderne (`list[str]`) |
| **LangChain** | Latest | Framework RAG | Orchestration du pipeline avec LCEL (Expression Language) |
| **LangChain Core** | Latest | Abstractions | Prompts, output parsers, runnables |
| **LangChain Community** | Latest | Intégrations | FAISS vectorstore wrapper |
| **Mistral AI** | API | LLM + Embeddings | Génération de texte (mistral-small) & embeddings (1024-dim) |
| **FAISS** | CPU | Vector store | Recherche sémantique avec IndexFlatL2 normalisé |
| **FastAPI** | 0.109+ | Framework web | API REST asynchrone avec validation Pydantic v2 |
| **Pydantic** | v2 | Validation | Modèles de données typés (Settings, Event, etc.) |
| **uv** | Latest | Package manager | Gestion ultra-rapide des dépendances Python |
| **pytest** | Latest | Testing | Tests unitaires, intégration, e2e |
| **RAGAS** | Latest | Évaluation | Métriques RAG (faithfulness, relevance, etc.) |
| **Streamlit** | Latest | Interface alt. | Prototypage rapide d'UI |

### Frontend & UI

| Technologie | Version | Usage | Rôle dans le projet |
|-------------|---------|-------|---------------------|
| **React** | 18+ | Framework UI | Interface utilisateur avec hooks (useState, useEffect) |
| **TypeScript** | 5+ | Typage statique | Type safety à la compilation |
| **Vite** | Latest | Build tool | Dev server ultra-rapide + HMR |
| **Tailwind CSS** | 3+ | Styling | Utility-first CSS framework |
| **shadcn/ui** | Latest | Composants | Design system moderne et accessible |
| **React Router** | Latest | Routing | Navigation SPA |

### DevOps & Infrastructure

| Technologie | Usage | Rôle dans le projet |
|-------------|-------|---------------------|
| **Docker** | Conteneurisation | Images multi-stage pour backend/frontend |
| **Docker Compose** | Orchestration | Lancement de tous les services en une commande |
| **Git** | Versioning | Conventional commits, branches feature |
| **GitHub Actions** | CI/CD | Tests automatisés (prévu) |

---

## 💡 Compétences Développées

Ce projet démontre une expertise approfondie en **développement backend**, **IA/ML** et **ingénierie de systèmes RAG**.

### 🐍 Backend & Architecture

#### **API REST Asynchrone (FastAPI)**
- Design d'API RESTful avec OpenAPI/Swagger
- Programmation asynchrone Python (`async`/`await`)
- Validation de données avec Pydantic v2 (Settings, models)
- Gestion de sessions en mémoire avec historique conversationnel
- Background tasks pour opérations longues (rebuild d'index)
- Middleware CORS et gestion d'erreurs centralisée
- Documentation auto-générée (Swagger UI)

**Code illustratif** :
```python
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Endpoint de chat avec mémoire conversationnelle"""
    session = sessions.get(request.session_id, ChatSession())
    result = await rag_engine.chat(
        query=request.query,
        history=session.history,
        top_k=request.top_k
    )
    session.add_message(request.query, result.response)
    return ChatResponse(**result.dict())
```

#### **Architecture Modulaire & Clean Code**
- Séparation des responsabilités (API, RAG, config, data)
- Dependency Injection avec FastAPI
- Configuration centralisée (Pydantic Settings + `.env`)
- Gestion des paths avec `pathlib.Path`
- Logging structuré avec niveaux configurables
- Typage moderne Python 3.11+ (`list[str]`, `dict[str, Any]`)

### 🤖 Intelligence Artificielle & Machine Learning

#### **RAG (Retrieval-Augmented Generation)**
- Conception et implémentation d'un pipeline RAG complet
- **Classification de requêtes** : Détection d'intention avec LLM
- **Retrieval** : Recherche sémantique dans un vector store
- **Generation** : Synthèse de réponses contextualisées
- Gestion de l'historique conversationnel (mémoire)

**Pipeline RAG** :
```
User Query → Classification (needs_rag?)
              ↓
          [SEARCH Mode]
              ↓
     Encode with Mistral Embeddings (1024-dim)
              ↓
     FAISS similarity_search (top-k)
              ↓
     Format context from events
              ↓
     Generate response with ChatMistralAI + context
              ↓
     Return response + sources
```

#### **LangChain LCEL (Expression Language)**
- Orchestration de pipelines LLM avec syntaxe déclarative
- Chaînage d'opérations avec l'opérateur pipe (`|`)
- Utilisation de `ChatPromptTemplate`, `MessagesPlaceholder`
- Output parsing avec `StrOutputParser`
- Composition de runnables complexes

**Exemple LCEL** :
```python
from langchain_core.runnables import RunnablePassthrough

chain = (
    {
        "context": vectorstore.as_retriever() | format_docs,
        "question": RunnablePassthrough(),
        "history": RunnablePassthrough()
    }
    | ChatPromptTemplate.from_template(prompt)
    | ChatMistralAI(model="mistral-small-latest")
    | StrOutputParser()
)
```

#### **Embeddings & Recherche Vectorielle**
- Génération d'embeddings avec **Mistral AI** (dimension 1024)
- Construction d'index FAISS (IndexFlatL2 avec normalisation L2)
- Recherche de similarité cosinus dans l'espace vectoriel
- Persistence et chargement d'index (format LangChain)
- Gestion de métadonnées et mapping documents

**Concepts maîtrisés** :
- Espace vectoriel et distance cosinus
- Normalisation L2 pour similarité
- Trade-off précision/vitesse (flat vs IVF index)
- Batch processing pour génération d'embeddings

#### **Prompt Engineering**
- Design de prompts système pour classification
- Templates de prompts avec contexte dynamique
- Gestion de l'historique conversationnel
- Few-shot prompting (exemples dans prompts)
- Contraintes de génération (langue, format, sources)

**Exemple de prompt RAG** :
```python
RAG_PROMPT = """Tu es un assistant culturel expert.
Contexte (événements trouvés):
{context}

Historique:
{history}

Question: {question}

Instructions:
- Réponds en français
- Base-toi UNIQUEMENT sur les événements fournis
- Cite tes sources
- Sois conversationnel et enthousiaste
"""
```

#### **Évaluation de Modèles (RAGAS)**
- Métriques de qualité RAG : faithfulness, answer relevance
- Évaluation de la pertinence des documents récupérés
- Mesure de la cohérence des réponses
- Génération de datasets de test
- Benchmarking et comparaison de modèles

### 🔬 Data Engineering & Pipeline ML

#### **Pipeline de Données**
- Collecte de données (Open Agenda API)
- Nettoyage et preprocessing (normalisation, déduplication)
- Transformation en format LangChain `Document[]`
- Génération d'embeddings en batch
- Construction d'index FAISS
- Persistence avec métadonnées (JSON config)

**Notebooks Jupyter** :
- `01_data_collection.ipynb` : Scraping API
- `02_data_preprocessing.ipynb` : Nettoyage
- `03_create_embeddings_mistral.ipynb` : Embeddings
- `04_build_faiss_index.ipynb` : Construction index
- `05_rag_chatbot_mistral.ipynb` : Tests RAG

#### **Vectorstores & FAISS**
- Compréhension des différents types d'index FAISS
- Optimisation mémoire et performance
- Sérialisation/désérialisation d'index
- Gestion du docstore (mapping ID → document)
- Update incrémental d'index (rebuild)

### 📊 Testing & Quality Assurance

- **Tests unitaires** : pytest avec fixtures et mocks
- **Tests d'intégration** : API endpoints avec TestClient
- **Tests e2e** : Pipeline RAG complet
- **Couverture de code** : pytest-cov > 80%
- **Linting** : ruff (remplace flake8, isort, pylint)
- **Formatting** : black (line length 100)
- **Type checking** : mypy pour typage statique

### 🎨 Frontend & UI/UX

- Développement React moderne (hooks, functional components)
- TypeScript pour type safety côté client
- Design responsive avec Tailwind CSS
- Intégration de design system (shadcn/ui)
- Communication REST avec backend (fetch API)
- Gestion d'état locale (useState, useContext)

### 🐳 DevOps & Deployment

- Conteneurisation Docker (multi-stage builds)
- Orchestration avec docker-compose
- Configuration par variables d'environnement
- Monorepo avec séparation backend/frontend
- Documentation technique complète
- READMEs et guides d'installation

---

## Tests & Qualité

```bash
# Backend
cd backend
uv run pytest --cov=src           # Tests avec couverture
uv run black . && uv run ruff .   # Formatage + linting

# Frontend
cd frontend
npm run test                       # Tests unitaires
npm run lint                       # ESLint
npm run build                      # Build production
```

---

## Contribution

Les contributions sont bienvenues ! Voir [backend/CONTRIBUTING.md](backend/CONTRIBUTING.md) pour les guidelines.

1. Fork le repository
2. Créer une branche (`git checkout -b feature/ma-feature`)
3. Commit (`git commit -m "feat: Description"`)
4. Push (`git push origin feature/ma-feature`)
5. Ouvrir une Pull Request

---

## Licence

Ce projet est sous licence **MIT**. Voir [LICENSE](LICENSE) pour plus de détails.

---

<div align="center">

**[Backend](backend/) | [Frontend](frontend/) | [Documentation](backend/docs/)**

</div>
