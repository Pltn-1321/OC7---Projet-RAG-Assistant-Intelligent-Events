# Architecture du Système RAG Events Assistant

Ce document décrit l'architecture technique du système RAG (Retrieval-Augmented Generation) pour la découverte d'événements culturels.

## Architecture Monorepo

Le projet est organisé en monorepo avec deux applications principales:

```
.
├── backend/                 # Python API + RAG Engine
├── frontend/                # React TypeScript Application
├── docker-compose.yml       # Orchestration des services
└── README.md
```

## Vue d'Ensemble Globale

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           UTILISATEUR                                    │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                ┌───────────────┴────────────────┐
                │                                │
                ▼                                ▼
┌────────────────────────────┐  ┌────────────────────────────────────────┐
│    FRONTEND (React)        │  │    ALTERNATIVE UI (Streamlit)          │
│    Port 5173 (dev)         │  │    Port 8501                           │
│                            │  │                                        │
│  - TypeScript + Vite       │  │  - Chat interface                      │
│  - Tailwind CSS + shadcn   │  │  - Historique                          │
│  - Modern chat UI          │  │  - Sources                             │
└────────────┬───────────────┘  └────────────┬───────────────────────────┘
             │                               │
             └───────────────┬───────────────┘
                             │ HTTP/REST
                             ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                     BACKEND - FASTAPI REST API (Port 8000)                │
│                                                                           │
│  Endpoints:                                                               │
│  • POST /search      - Recherche sémantique (sans session)                │
│  • POST /chat        - Chat avec mémoire conversationnelle                │
│  • GET/DELETE /session/{id} - Gestion des sessions                        │
│  • POST /rebuild     - Reconstruction de l'index FAISS                    │
│  • GET /health       - Health check                                       │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                   COUCHE LOGIQUE MÉTIER - RAGEngine                       │
│                        (LangChain LCEL Orchestration)                     │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                  Pipeline RAG avec LangChain                         │  │
│  │                                                                      │  │
│  │  Query → needs_rag() ──┐                                            │  │
│  │                        │                                            │  │
│  │         ┌──────────────┴──────────────────┐                         │  │
│  │         │                                 │                         │  │
│  │      [CHAT]                           [SEARCH/RAG]                  │  │
│  │         │                                 │                         │  │
│  │         ▼                                 ▼                         │  │
│  │  Simple LLM Chat                   1. Encode query (Mistral)        │  │
│  │  (no context)                      2. FAISS semantic search         │  │
│  │         │                           3. Generate with context        │  │
│  │         │                                 │                         │  │
│  │         └──────────────┬──────────────────┘                         │  │
│  │                        ▼                                            │  │
│  │              Response + Sources (if RAG)                            │  │
│  │                                                                      │  │
│  │  Components:                                                         │  │
│  │  • ChatMistralAI       - LLM wrapper                                │  │
│  │  • MistralAIEmbeddings - Embeddings provider                        │  │
│  │  • FAISS vectorstore   - Semantic search                            │  │
│  │  • ChatPromptTemplate  - Prompt engineering                         │  │
│  │  • LCEL chains         - Pipeline orchestration                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                         COUCHE DONNÉES                                    │
│  ┌─────────────────────┐    ┌─────────────────────────────────────────┐  │
│  │  data/indexes/      │    │         Services Externes                │  │
│  │                     │    │                                          │  │
│  │  - index.faiss      │    │  ┌────────────────┐ ┌─────────────────┐  │  │
│  │  - index.pkl        │    │  │  Mistral API   │ │ Open Agenda API │  │  │
│  │  - config.json      │    │  │  - Embeddings  │ │  - Events data  │  │  │
│  │                     │    │  │  - LLM         │ │                 │  │  │
│  │  (LangChain format) │    │  └────────────────┘ └─────────────────┘  │  │
│  │                     │    │                                          │  │
│  └─────────────────────┘    └─────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
```

## Composants Principaux

### 1. Frontend React (Application Principale)

**Répertoire**: `frontend/`

Interface moderne avec TypeScript:
- **Framework**: React 18+ avec Vite
- **Styling**: Tailwind CSS + shadcn/ui components
- **Type safety**: TypeScript pour validation à la compilation
- **Communication**: Fetch API vers backend FastAPI

**Caractéristiques**:
- Interface de chat responsive et moderne
- Gestion d'état locale (React hooks)
- Design system cohérent avec shadcn/ui
- Build optimisé avec Vite

### 2. Interface Alternative (Streamlit)

**Fichier**: `backend/app.py`

Interface Python alternative pour prototypage rapide:
- Interface de chat intuitive
- Affichage de l'historique des conversations
- Visualisation des sources (événements trouvés)
- Panneau de configuration (top_k, réinitialisation)

**Caractéristiques techniques**:
- Utilisation de `@st.cache_resource` pour le cache du RAGEngine
- Gestion de l'état via `st.session_state`
- Design responsive avec CSS personnalisé

### 3. API REST (FastAPI)

**Fichier**: `backend/src/api/main.py`

Endpoints disponibles:

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Vérification de l'état du service |
| `/search` | POST | Recherche sémantique (sans session) |
| `/chat` | POST | Chat avec mémoire conversationnelle |
| `/session/{id}` | GET | Récupérer l'historique d'une session |
| `/session/{id}` | DELETE | Supprimer une session |
| `/rebuild` | POST | Reconstruire l'index FAISS (arrière-plan) |

**Caractéristiques techniques**:
- Validation Pydantic pour toutes les requêtes/réponses
- Gestion des sessions en mémoire (dict)
- Documentation Swagger auto-générée (`/docs`)
- Support CORS configurable
- Tâches en arrière-plan pour rebuild

### 4. Moteur RAG (RAGEngine) - LangChain LCEL

**Fichier**: `backend/src/rag/engine.py`

Le cœur du système orchestré avec **LangChain LCEL**:

**Architecture LangChain**:
```python
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# Pipeline LCEL (Expression Language)
chain = ChatPromptTemplate | ChatMistralAI | StrOutputParser
```

**Méthodes principales**:

1. **`needs_rag(query)`**: Classification intelligente
   - Détecte si la requête nécessite une recherche dans la base
   - Utilise le LLM pour analyser l'intention

2. **`search(query, top_k)`**: Recherche sémantique
   - Encode la requête avec `MistralAIEmbeddings`
   - Recherche dans FAISS vectorstore (LangChain wrapper)
   - Retourne les top-k événements pertinents

3. **`generate_response(query, results)`**: Génération RAG
   - Formate le contexte (événements trouvés)
   - Utilise `ChatPromptTemplate` avec contexte
   - Génère réponse avec `ChatMistralAI`

4. **`conversation_response(query, history)`**: Chat simple
   - Chat sans RAG (conversation générale)
   - Utilise l'historique conversationnel
   - `MessagesPlaceholder` pour mémoire

5. **`chat(query, top_k, history)`**: Pipeline complet
   - Point d'entrée principal
   - Route vers SEARCH ou CHAT selon classification
   - Gère l'historique conversationnel

### 5. Modules RAG Supportaires

**`backend/src/rag/embeddings.py`**:
- Factory pour `MistralAIEmbeddings`
- Configuration centralisée des embeddings

**`backend/src/rag/llm.py`**:
- Factory pour `ChatMistralAI`
- Gestion des paramètres LLM (température, modèle)

**`backend/src/rag/vectorstore.py`**:
- Gestion du FAISS vectorstore (LangChain)
- Chargement/sauvegarde avec `load_local()` / `save_local()`
- Gestion des métadonnées (config.json)

**`backend/src/rag/index_builder.py`**:
- Construction de l'index FAISS à partir des événements
- Génère embeddings avec Mistral
- Sauvegarde au format LangChain:
  - `index.faiss` (index binaire FAISS)
  - `index.pkl` (docstore et mapping)
  - `config.json` (métadonnées personnalisées)

## Structure des Répertoires (Monorepo)

```
.
├── backend/                      # Application Backend Python
│   ├── src/
│   │   ├── api/
│   │   │   └── main.py          # FastAPI REST API
│   │   ├── config/
│   │   │   ├── settings.py      # Configuration Pydantic
│   │   │   └── constants.py     # Constantes (chemins, prompts)
│   │   ├── data/
│   │   │   └── models.py        # Modèles Pydantic (Event, etc.)
│   │   └── rag/                 # ⭐ Cœur RAG avec LangChain
│   │       ├── engine.py        # RAGEngine (orchestration LCEL)
│   │       ├── embeddings.py    # Factory Mistral embeddings
│   │       ├── llm.py           # Factory ChatMistralAI
│   │       ├── vectorstore.py   # Gestion FAISS (LangChain)
│   │       └── index_builder.py # Construction d'index
│   ├── tests/
│   │   ├── unit/                # Tests unitaires
│   │   ├── integration/         # Tests d'intégration
│   │   └── e2e/                 # Tests end-to-end
│   ├── scripts/
│   │   ├── evaluate_rag.py      # Évaluation RAGAS
│   │   └── api_test.py          # Tests fonctionnels API
│   ├── data/                    # ❌ Non versionné (.gitignore)
│   │   ├── raw/                 # Données brutes Open Agenda
│   │   ├── processed/           # Données traitées
│   │   └── indexes/             # Index FAISS (format LangChain)
│   │       ├── index.faiss      # Index binaire FAISS
│   │       ├── index.pkl        # Docstore et mapping
│   │       └── config.json      # Métadonnées
│   ├── notebooks/               # Jupyter notebooks (pipeline data)
│   ├── docs/                    # Documentation backend
│   ├── app.py                   # Interface Streamlit alternative
│   ├── pyproject.toml           # Dépendances Python (uv)
│   └── Dockerfile               # Image Docker backend
│
├── frontend/                    # Application Frontend React
│   ├── src/
│   │   ├── components/          # Composants React
│   │   ├── pages/               # Pages de l'application
│   │   ├── services/            # Services (API calls)
│   │   └── App.tsx              # Composant racine
│   ├── docs/                    # Documentation frontend
│   ├── package.json             # Dépendances Node.js
│   └── Dockerfile               # Image Docker frontend
│
├── docker-compose.yml           # ⭐ Orchestration des services
├── .env.example                 # Template variables d'environnement
├── .gitignore                   # Monorepo gitignore
├── LICENSE                      # MIT License
├── README.md                    # Overview du projet
└── CLAUDE.md                    # Instructions pour Claude Code
```

## Flux de Données

### Pipeline de Chat RAG (LangChain LCEL)

```
1. Frontend (React) / Streamlit
   POST /chat {"query": "...", "session_id": "..."}
       │
       ▼
2. FastAPI (main.py)
   Validation Pydantic + Session management
       │
       ▼
3. RAGEngine.chat(query, history)
       │
       ▼
4. Classification LLM (needs_rag?)
   "Cette requête concerne-t-elle des événements?"
       │
       ├────────────────────────────────────┐
       │                                    │
   [YES - SEARCH Mode]              [NO - CHAT Mode]
       │                                    │
       ▼                                    ▼
5. Encode query                      Conversation simple
   MistralAIEmbeddings                     │
   → vector [1024]                         │
       │                                    │
       ▼                             ChatPromptTemplate
6. FAISS.similarity_search()         + MessagesPlaceholder
   vectorstore.search(vector, k=5)   → ChatMistralAI
       │                             → StrOutputParser
       ▼                                    │
7. Top-K Events Retrieved                  │
   [Event1, Event2, ...]                   │
       │                                    │
       ▼                                    │
8. Format Context                          │
   "Événements trouvés:\n..."              │
       │                                    │
       ▼                                    │
9. Generate Response (LCEL)                │
   ChatPromptTemplate                      │
   + context + history                     │
   → ChatMistralAI                         │
   → StrOutputParser                       │
       │                                    │
       └────────────────┬───────────────────┘
                        ▼
10. Response + Sources (if SEARCH mode)
    {"response": "...", "sources": [...]}
       │
       ▼
11. FastAPI Response
    Store history in session
       │
       ▼
12. Frontend Update
    Display response + sources
```

### Pipeline de Reconstruction d'Index

```
1. POST /rebuild
   Header: X-API-Key
       │
       ▼
2. Validation API Key
   (si REBUILD_API_KEY configuré)
       │
       ▼
3. BackgroundTask lancée
   IndexBuilder.build_index()
       │
       ├─▶ 1. Charger événements
       │   data/processed/events.json
       │
       ├─▶ 2. Préparer documents
       │   Format LangChain Document[]
       │
       ├─▶ 3. Générer embeddings
       │   MistralAIEmbeddings.embed_documents()
       │   Batch processing
       │
       ├─▶ 4. Construire FAISS index
       │   FAISS.from_documents()
       │   IndexFlatL2 avec normalisation
       │
       └─▶ 5. Sauvegarder (LangChain format)
           vectorstore.save_local()
           → index.faiss
           → index.pkl
           → config.json

4. Invalidation cache
   Prochain appel rechargera l'index
       │
       ▼
5. Réponse 202 Accepted
   {"status": "started", "task_id": "..."}
```

## Configuration

### Variables d'Environnement

**Fichier**: `.env` à la racine du monorepo

| Variable | Description | Défaut | Obligatoire |
|----------|-------------|--------|-------------|
| `MISTRAL_API_KEY` | Clé API Mistral AI | - | ✅ Oui |
| `REBUILD_API_KEY` | Clé pour sécuriser `/rebuild` | - | ❌ Non |

**Configuration par défaut** (dans `backend/src/config/settings.py`):
```python
class Settings(BaseSettings):
    # LLM
    llm_model: str = "mistral-small-latest"
    llm_temperature: float = 0.7

    # RAG
    top_k_results: int = 5
    embedding_provider: str = "mistral"  # LangChain MistralAIEmbeddings

    # Paths
    data_dir: Path = Path("data")
    index_path: Path = Path("data/indexes")

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
```

### Fichiers de Configuration

**Backend**:
- **`.env`** (racine): Variables d'environnement (non versionné)
- **`backend/pyproject.toml`**: Dépendances Python (uv)
- **`backend/data/indexes/config.json`**: Métadonnées de l'index FAISS

**Frontend**:
- **`frontend/package.json`**: Dépendances Node.js
- **`frontend/vite.config.ts`**: Configuration Vite

**Docker**:
- **`docker-compose.yml`**: Orchestration des services
  - Service `api`: Backend FastAPI (port 8000)
  - Service `streamlit`: Interface Streamlit (port 8501)
  - Service `frontend`: React dev server (port 5173)

## Intégration LangChain LCEL

### Pourquoi LangChain?

**LangChain** est un framework pour construire des applications avec des LLMs. Il fournit:
- **Abstractions standardisées**: Wrappers pour différents LLMs et embeddings
- **LCEL (LangChain Expression Language)**: Syntaxe déclarative pour chaîner les opérations
- **Vectorstores intégrés**: Support natif de FAISS, Pinecone, Chroma, etc.
- **Gestion de mémoire**: Historique conversationnel avec `MessagesPlaceholder`

### Architecture LCEL

**Pipeline déclaratif** avec l'opérateur `|`:

```python
# Exemple: Pipeline RAG complet
from langchain_core.runnables import RunnablePassthrough

chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
        "history": RunnablePassthrough()
    }
    | ChatPromptTemplate.from_template(RAG_TEMPLATE)
    | ChatMistralAI(model="mistral-small-latest")
    | StrOutputParser()
)

# Invocation
response = chain.invoke({
    "question": "Concerts ce soir?",
    "history": previous_messages
})
```

### Composants LangChain Utilisés

| Composant | Module | Usage |
|-----------|--------|-------|
| `ChatMistralAI` | `langchain_mistralai` | Wrapper LLM Mistral |
| `MistralAIEmbeddings` | `langchain_mistralai` | Génération d'embeddings |
| `FAISS` | `langchain_community.vectorstores` | Store vectoriel |
| `ChatPromptTemplate` | `langchain_core.prompts` | Templates de prompts |
| `MessagesPlaceholder` | `langchain_core.prompts` | Historique conversationnel |
| `StrOutputParser` | `langchain_core.output_parsers` | Parse la sortie LLM |
| `Document` | `langchain_core.documents` | Format de documents |

### Format FAISS (LangChain)

LangChain utilise un format spécifique pour sauvegarder les vectorstores:

**Fichiers générés par `vectorstore.save_local(path)`**:
1. **`index.faiss`**: Index binaire FAISS (vecteurs + structure)
2. **`index.pkl`**: Pickle contenant:
   - `docstore`: Stockage des documents originaux
   - `index_to_docstore_id`: Mapping index → document ID
3. **`config.json`** (custom): Métadonnées projet (nombre de docs, timestamp, etc.)

**Chargement**:
```python
from langchain_community.vectorstores import FAISS

vectorstore = FAISS.load_local(
    folder_path="data/indexes",
    embeddings=MistralAIEmbeddings(api_key=key),
    allow_dangerous_deserialization=True  # Requis pour pickle
)
```

## Stack Technique Complète

### Backend
- **Python 3.11+** avec gestionnaire de paquets **uv**
- **LangChain LCEL** pour orchestration RAG
- **Mistral AI** (LLM + Embeddings via API)
- **FAISS** (Facebook AI Similarity Search) pour recherche vectorielle
- **FastAPI** pour API REST asynchrone
- **Pydantic v2** pour validation de données
- **Streamlit** pour interface alternative
- **pytest** + **RAGAS** pour tests et évaluation

### Frontend
- **React 18+** avec **TypeScript**
- **Vite** comme build tool et dev server
- **Tailwind CSS** pour styling utilitaire
- **shadcn/ui** pour composants UI
- **React Hooks** pour gestion d'état

### Infrastructure
- **Docker** + **docker-compose** pour conteneurisation
- **uv** pour gestion rapide des dépendances Python
- **npm** pour gestion des dépendances Node.js

## Sécurité

### Mesures Implémentées

1. **Validation des entrées**: Pydantic sur tous les endpoints
2. **Authentification `/rebuild`**: Header `X-API-Key` (optionnel)
3. **Gestion des clés API**: Variables d'environnement (`.env`)
4. **Pas de SQL**: FAISS est une base vectorielle (pas d'injection SQL)
5. **Erreurs génériques**: Pas d'exposition de détails internes
6. **CORS configuré**: Limitation des origines autorisées
7. **Désérialisation contrôlée**: Flag `allow_dangerous_deserialization` explicite

### Recommandations Production

**Infrastructure**:
- Utiliser HTTPS (reverse proxy nginx/traefik)
- Configurer rate limiting sur l'API
- Ajouter authentification JWT sur tous les endpoints
- Isoler les services avec réseau Docker privé

**Monitoring**:
- Logs structurés (JSON) avec rotation
- Métriques Prometheus (latence, taux d'erreur)
- Alertes sur disponibilité et performance
- Traçabilité des requêtes (request IDs)

**Données**:
- Backups réguliers de l'index FAISS
- Versioning des indexes (timestamps)
- Validation des événements à l'ingestion
- Nettoyage des sessions expirées

## Limitations Connues

### Fonctionnelles
- **Mise à jour manuelle**: Pas de synchronisation automatique avec Open Agenda API
- **Mémoire limitée**: Seulement 5 derniers messages par session
- **Localisation fixe**: Configuré pour Marseille par défaut
- **Pas d'authentification**: Accès public à l'API et Streamlit
- **Sessions volatiles**: Perdues au redémarrage (stockage en mémoire)

### Techniques
- **Langue unique**: Tous les prompts et réponses sont en français
- **Latence API externe**: Dépendance à Mistral AI (réseau)
- **Scalabilité**: FAISS en mémoire (limite par RAM disponible)
- **Concurrence**: Pas de queue pour les reconstructions d'index

### Améliorations Futures

**Court terme**:
- Persistance des sessions (Redis, PostgreSQL)
- Authentification utilisateur (JWT, OAuth)
- Métriques et monitoring (Prometheus, Grafana)
- Tests de charge et optimisation

**Moyen terme**:
- Multi-langue (anglais, espagnol)
- Synchronisation automatique Open Agenda
- Support multi-villes
- Recommandations personnalisées

**Long terme**:
- Fine-tuning du modèle sur événements culturels
- Vectorstore distribué (Pinecone, Weaviate)
- Interface vocale (Speech-to-Text)
- Intégration calendrier (Google Calendar, iCal)
