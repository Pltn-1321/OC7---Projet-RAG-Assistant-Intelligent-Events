# Rapport Technique - RAG Events Assistant

> **Système RAG (Retrieval-Augmented Generation) pour la découverte d'événements culturels**

**Auteur** : Pierre Pluton
**Date** : Février 2026
**Version** : 2.0 (Monorepo avec React + PostgreSQL)
**Projet** : OpenClassrooms - Projet RAG Assistant Intelligent

---

## Table des Matières

- [I. INTRODUCTION](#i-introduction)
- [II. ARCHITECTURE DU SYSTÈME](#ii-architecture-du-système)
- [III. CHOIX TECHNOLOGIQUES](#iii-choix-technologiques)
- [IV. MODÈLES UTILISÉS](#iv-modèles-utilisés)
- [V. RÉSULTATS OBSERVÉS](#v-résultats-observés)
- [VI. PISTES D'AMÉLIORATION](#vi-pistes-damélioration)
- [VII. CONCLUSION](#vii-conclusion)

---

## I. INTRODUCTION

### 1.1 Contexte du Projet

La découverte d'événements culturels représente un défi pour les utilisateurs :
- **Fragmentation des sources** : Multiples plateformes, agendas, sites web
- **Recherche traditionnelle limitée** : Requêtes par mots-clés exactes, pas de compréhension sémantique
- **Absence de personnalisation** : Difficulté à trouver des événements correspondant à des critères flous ("quelque chose de sympa ce weekend")

**Solution proposée** : Un système RAG (Retrieval-Augmented Generation) qui combine :
- Recherche sémantique dans une base d'événements (FAISS)
- Génération de réponses conversationnelles (Mistral AI)
- Interfaces multiples (Frontend React + Streamlit + API REST)
- Persistence des sessions utilisateurs (PostgreSQL)

### 1.2 Qu'est-ce que le RAG ?

**RAG (Retrieval-Augmented Generation)** est une architecture d'IA qui enrichit les réponses des LLM avec des informations récupérées depuis une base de connaissances externe.

```
┌─────────────────────────────────────────────────────────────────┐
│                      PIPELINE RAG                                │
│                                                                  │
│  Question utilisateur                                            │
│       ↓                                                          │
│  Classification intelligente (needs_rag)                         │
│       ↓                                                          │
│  ┌────────────────────┬────────────────────┐                    │
│  │   CHAT Mode        │   SEARCH Mode      │                    │
│  │   (Simple LLM)     │   (RAG Pipeline)   │                    │
│  │   ↓                │   ↓                │                    │
│  │   Conversation     │   1. Embedding     │                    │
│  │   directe          │   2. FAISS Search  │                    │
│  │                    │   3. LLM + Context │                    │
│  └────────────────────┴────────────────────┘                    │
│       ↓                                                          │
│  Réponse contextuelle + Sources                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Pourquoi le RAG plutôt que le Fine-tuning ?

| Aspect | RAG | Fine-tuning |
|--------|-----|-------------|
| **Mise à jour données** | Instantanée (ré-indexation) | Re-training requis |
| **Coût** | Faible (API embeddings) | Élevé (GPU, compute) |
| **Traçabilité** | Sources citables | Boîte noire |
| **Hallucinations** | Réduites (contexte factuel) | Plus fréquentes |
| **Connaissances** | Limitées à la base | Intégrées au modèle |

**Cas d'usage typiques du RAG** :
- Questions-réponses sur documents internes
- Assistants basés sur données actualisées
- Chatbots avec sources vérifiables
- Recherche sémantique augmentée

### 1.3 Objectifs et Périmètre

**Objectifs fonctionnels** :
- ✅ Permettre la recherche d'événements en langage naturel (français)
- ✅ Fournir des recommandations pertinentes avec sources vérifiables
- ✅ Gérer des conversations multi-tours avec mémoire de session
- ✅ Distinguer questions conversationnelles vs recherches d'événements

**Objectifs techniques** :
- ✅ Latence < 3 secondes pour les requêtes RAG
- ✅ Couverture des mots-clés > 80%
- ✅ Classification SEARCH vs CHAT > 95% accuracy
- ✅ Test coverage > 80%

**Périmètre** :
- Base d'événements : Open Agenda API (événements culturels français)
- Langue : Français uniquement
- Déploiement : Local/Docker (pas de cloud dans ce POC)

### 1.4 Livrables

1. **Système RAG fonctionnel** : Code source complet avec RAGEngine, IndexBuilder
2. **API REST** : FastAPI avec 6 endpoints, sessions PostgreSQL, background tasks
3. **Interfaces utilisateur** :
   - Frontend React (5 vues : Chat, API Explorer, Monitoring, RAGAS, Index)
   - Streamlit (alternative simplifiée)
4. **Tests** : Unitaires, intégration, end-to-end (pytest, 85% coverage)
5. **Documentation** : Complète et professionnelle (ce rapport inclus)
6. **Évaluation** : Framework RAGAS, dataset annoté, métriques
7. **CI/CD** : GitHub Actions (lint, build, docker)

---

## II. ARCHITECTURE DU SYSTÈME

### 2.1 Vue d'Ensemble

L'architecture suit un pattern 4 couches :

```
UTILISATEUR
    ↓
┌─────────────────────────────────────────────────────────┐
│  COUCHE PRÉSENTATION                                     │
│  - Frontend React (5173) ← Application principale        │
│  - Streamlit UI (8501)   ← Alternative                   │
│  - FastAPI REST API (8000)                               │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│  COUCHE LOGIQUE MÉTIER                                   │
│  - RAGEngine (classification, search, generation)        │
│  - IndexBuilder (construction FAISS)                     │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│  COUCHE DONNÉES                                          │
│  - PostgreSQL (sessions, messages, métadonnées)          │
│  - FAISS Index (index.faiss + index.pkl)                │
│  - Documents JSON (rag_documents.json)                   │
│  - Services externes (Mistral API, Open Agenda)         │
└─────────────────────────────────────────────────────────┘
```

**Principe architectural** : Séparation des responsabilités (SoC)
- **Présentation** : Gère l'interaction utilisateur (UI/API)
- **Logique métier** : Implémente le pipeline RAG
- **Données** : Stockage et accès aux événements

### 2.2 Composants Principaux

#### 2.2.1 RAGEngine (`src/rag/engine.py`)

Le cœur du système RAG avec les méthodes :

**`needs_rag(query: str) -> bool`**
- Classifie si la requête nécessite une recherche dans la base
- Utilise un prompt LLM pour distinguer SEARCH vs CHAT
- Exemples SEARCH : "concerts jazz Paris", "expositions gratuites"
- Exemples CHAT : "bonjour", "merci", "comment ça va"
- **Accuracy observée** : 100% (12/12 questions test)

**`encode_query(query: str) -> np.ndarray`**
- Génère l'embedding de la requête
- Support Mistral Embed (1024d) ou SentenceTransformers (768d)
- Normalisation L2 pour compatibilité distance cosinus
- Batch processing pour efficacité

**`search(query: str, top_k: int) -> List[Dict]`**
- Recherche sémantique dans l'index FAISS
- Retourne top-k documents avec scores de similarité
- Filtrage par seuil de similarité (défaut: 0.3)
- Métadonnées enrichies (ville, date, prix, URL)

**`generate_response(query: str, context: str) -> str`**
- Génération LLM avec Mistral AI
- Streaming support pour UX fluide
- Prompt template avec instructions spécifiques (français, 2-3 événements max)
- Température 0.7 pour équilibre créativité/consistance

**`chat(query: str, history: List, top_k: int) -> Dict`**
- Pipeline complet unifié
- Appelle needs_rag() puis search() ou conversation directe
- Gère l'historique de conversation (max 5 échanges)
- Retourne réponse + sources (si RAG) + métadonnées

#### 2.2.2 IndexBuilder (`src/rag/index_builder.py`)

Construction et gestion des index FAISS :

**`load_documents() -> List[Event]`**
- Charge événements depuis `rag_documents.json`
- Validation Pydantic pour intégrité des données
- Conversion en objets Event avec métadonnées

**`generate_embeddings(documents: List[str]) -> np.ndarray`**
- Batch embedding generation (batch_size=32)
- Progress tracking avec tqdm
- Retry logic (3 tentatives avec backoff exponentiel)
- Support Mistral API et modèles locaux

**`build_index(embeddings: np.ndarray) -> faiss.Index`**
- Création IndexFlatL2 (recherche exacte)
- Normalisation L2 des vecteurs (distance L2 ≈ cosinus)
- Ajout des vecteurs à l'index
- Optimisation pour < 1M documents

**`save_index(index, metadata, config)`**
- Sauvegarde index FAISS (`events.index`)
- Persistance métadonnées avec pickle (`metadata.pkl`)
- Configuration JSON (`config.json`) avec:
  - embedding_dim, num_documents, model_name
  - date de création, provider (mistral/sentence-transformers)

**`rebuild() -> Dict`**
- Pipeline complet de reconstruction
- Callbacks pour progress tracking
- Validation des résultats
- Invalidation du cache RAGEngine

#### 2.2.3 API FastAPI (`src/api/main.py`)

API REST complète avec 6 endpoints :

**GET `/health`**
- Health check du service
- Retourne : status, num_documents, embedding_dim, active_sessions
- Code 503 si index non disponible

**POST `/search`**
- Recherche sémantique sans session
- Params : `query` (string), `top_k` (int, défaut 5)
- Retourne : résultats avec scores de similarité

**POST `/chat`**
- Chat avec mémoire conversationnelle
- Params : `query`, `session_id` (optionnel), `top_k`
- Auto-génère session_id si non fourni (UUID v4)
- Retourne : response, sources, session_id

**GET `/session/{session_id}`**
- Récupère historique d'une session
- Retourne : liste de messages (user/assistant)
- Code 404 si session non trouvée

**DELETE `/session/{session_id}`**
- Supprime une session et son historique
- Retourne : confirmation de suppression
- Code 404 si session non trouvée

**POST `/rebuild`**
- Reconstruit l'index FAISS en arrière-plan
- Authentification : Header `X-API-Key`
- Retourne : task_id pour tracking
- Background task avec progress callbacks

**GET `/rebuild/{task_id}`**
- Statut d'une tâche de reconstruction
- Retourne : status (in_progress/completed/failed), progress (0-1), message
- Code 404 si tâche non trouvée

**Caractéristiques techniques** :
- Validation Pydantic pour toutes les requêtes/réponses
- Gestion des sessions en PostgreSQL (SQLAlchemy async)
- Modèles : `SessionModel`, `MessageModel` avec JSONB pour sources
- Historique limité à 5 échanges par session
- Documentation Swagger auto-générée (`/docs`)
- CORS configurable pour intégration frontend React

#### 2.2.4 Interface Streamlit (`app.py`)

Interface chat moderne et réactive :

**Fonctionnalités** :
- Chat conversationnel avec input utilisateur
- Affichage de l'historique (max 5 messages)
- Visualisation des sources avec scores de similarité
- Sidebar avec configuration :
  - top_k (nombre de résultats)
  - température LLM (créativité)
  - bouton réinitialisation conversation
- Thème sombre moderne
- Streaming des réponses (UX fluide)

**Optimisations** :
- `@st.cache_resource` pour RAGEngine (1 instance partagée)
- `st.session_state` pour mémoire de conversation
- CSS personnalisé pour design professionnel

### 2.3 Flux de Données

#### Pipeline de Chat Complet

```
1. Requête utilisateur
       │
       ▼
2. Classification (needs_rag?)
       │
       ├──────────────────────┐
       │                      │
   [SEARCH]               [CHAT]
       │                      │
       ▼                      ▼
3. Encodage requête    4. Réponse directe
   (mistral-embed)        (sans RAG)
   → embedding 1024d
       │
       ▼
4. Recherche FAISS
   (IndexFlatL2)
   → distance L2
       │
       ▼
5. Top-K documents
   (similarité cosinus)
       │
       ▼
6. Génération LLM
   avec contexte
   (mistral-small)
       │
       ▼
7. Réponse + Sources
```

**Temps de traitement typique** :
- CHAT mode : 1.5-2s (pas de FAISS)
- SEARCH mode : 2-3s (embedding + FAISS + LLM)

#### Pipeline de Reconstruction d'Index

```
1. POST /rebuild
   (avec X-API-Key)
       │
       ▼
2. Validation API Key
       │
       ▼
3. Tâche en arrière-plan
       │
       ├─▶ Charger documents (rag_documents.json)
       │
       ├─▶ Générer embeddings (batch de 32)
       │   Progress: 0/497 → 32/497 → ... → 497/497
       │
       ├─▶ Construire index FAISS
       │   IndexFlatL2(dimension=1024)
       │   L2 normalization
       │
       └─▶ Sauvegarder fichiers
           - events.index (FAISS)
           - metadata.pkl (événements + métadonnées)
           - config.json (configuration)

4. Invalidation cache RAGEngine
       │
       ▼
5. Nouvel index disponible
```

**Durée typique** : 30-60 secondes pour 497 événements (Mistral Embed)

### 2.4 Structure des Modules

Le projet utilise une **architecture monorepo** avec séparation backend/frontend :

```
OC7---Projet-RAG-Assistant-Intelligent-Events/
├── backend/                    # API Python + RAG Engine
│   ├── app.py                  # Interface Streamlit
│   ├── src/
│   │   ├── config/             # settings.py, constants.py
│   │   ├── data/               # models.py (Pydantic)
│   │   ├── database/           # 🆕 models.py, repository.py, connection.py
│   │   ├── rag/                # engine.py, index_builder.py, embeddings.py
│   │   └── api/                # main.py (FastAPI)
│   ├── tests/                  # unit, integration, e2e
│   ├── notebooks/              # Pipeline de données (Jupyter)
│   └── pyproject.toml          # Dépendances Python (uv)
│
├── frontend/                   # 🆕 Application React
│   ├── src/
│   │   ├── features/           # chat, api-explorer, monitoring, ragas-metrics
│   │   ├── components/         # ui (shadcn), layout, common
│   │   ├── lib/api/            # client.ts, endpoints.ts, types.ts
│   │   └── store/              # Zustand stores
│   ├── package.json            # Dépendances Node.js
│   └── Dockerfile
│
├── docker-compose.yml          # Orchestration services
├── .github/workflows/          # 🆕 CI/CD GitHub Actions
└── README.md
```

**Avantages du monorepo** :
- Séparation claire backend (Python) / frontend (TypeScript)
- Chaque partie a ses propres dépendances et Dockerfile
- Déploiement unifié via docker-compose
- CI/CD partagé

---

## III. CHOIX TECHNOLOGIQUES

### 3.1 LLM : Mistral AI (`mistral-small-latest`)

#### Justification

**✅ Avantages** :
- **Support natif du français** : Modèle entraîné sur corpus multilingue avec fort biais français
- **Qualité des réponses** : Comparable à GPT-3.5, meilleur que Llama 2
- **API simple** : SDK Python officiel, intégration facile
- **Pricing compétitif** : $0.001/1K tokens (input), $0.003/1K tokens (output)
- **Streaming support** : Réponses progressives pour UX fluide
- **32K context window** : Suffisant pour 5-10 événements + historique

**❌ Alternatives non retenues** :
- **GPT-4** : Plus cher ($0.03/1K), US-centric, latence plus élevée
- **Llama 3** : Nécessite GPU local, déploiement complexe, qualité inférieure pour français
- **Claude** : Support français limité, pas de streaming dans SDK

#### Configuration

```python
{
  "model": "mistral-small-latest",  # Auto-update vers dernière version
  "temperature": 0.7,               # Équilibre créativité/consistance
  "max_tokens": 1000,               # ~750 mots max
  "top_p": 1.0,                     # Nucleus sampling
  "stream": True                    # Streaming des réponses
}
```

**Prompt système** (extrait de `constants.py`) :
```
Tu es un assistant intelligent qui aide les utilisateurs à découvrir 
des événements culturels. Réponds en français de manière naturelle 
et conversationnelle. Recommande 2-3 événements pertinents maximum 
avec informations pratiques (date, lieu, prix). Si aucun événement 
ne correspond, propose des alternatives. Sois concis mais informatif.
```

### 3.2 Embeddings : Mistral Embed (1024d)

#### Justification

**✅ Avantages** :
- **Multilingue optimisé** : Excellent sur français (meilleur que OpenAI ada-002)
- **Dimension élevée** : 1024d vs 1536d (OpenAI) ou 768d (sentence-transformers)
- **Même provider** : Cohérence avec LLM, facturation unifiée
- **Pas de modèle local** : Pas de gestion de dépendances ML lourdes
- **Normalisation incluse** : Vecteurs pré-normalisés

**❌ Alternatives non retenues** :
- **OpenAI ada-002** : Plus cher, US-centric, 1536d (surdimensionné)
- **Voyage AI** : Moins connu, pas de SDK Python mature
- **E5-multilingual** : Qualité inférieure sur français

#### Fallback : sentence-transformers

Configuration alternative pour développement local :

```python
{
  "model": "paraphrase-multilingual-mpnet-base-v2",
  "dimension": 768,
  "device": "cpu",  # ou "cuda" si GPU disponible
  "normalize": True
}
```

**Utilisé quand** :
- Développement sans connexion internet
- Tests CI/CD (évite appels API)
- Budget limité (free, local)

**Performance** : ~80% de la qualité Mistral Embed sur français

### 3.3 Vector Store : FAISS

#### Justification

**✅ Avantages** :
- **Ultra-rapide** : Optimisé C++, recherche en <1ms pour 1K vecteurs
- **Pas de serveur** : Fichiers locaux (.index + .pkl)
- **Flexible** : Multiples types d'index (Flat, IVF, HNSW)
- **Open source** : Facebook Research, mature (depuis 2017)
- **Python bindings** : Intégration native

**Index actuel** : `IndexFlatL2` (recherche exacte)
- Complexité : O(n × d) par requête
- Optimal pour < 100K vecteurs
- 100% recall (pas d'approximation)

**❌ Alternatives non retenues** :

| Alternative | Avantages | Pourquoi non retenu |
|-------------|-----------|---------------------|
| **Pinecone** | Cloud, scalable | Coût mensuel, dépendance externe |
| **Weaviate** | GraphQL, filtres | Overkill pour 500 événements |
| **Qdrant** | Performant, Rust | Complexité déploiement |
| **Chroma** | Simple, embeddings | Moins performant que FAISS |
| **Milvus** | Distribué | Pour >1M vecteurs |

**Évolution future** : `IndexIVFFlat` pour >10K événements
- Recherche approximative (95-98% recall)
- 10-100x plus rapide
- Trade-off acceptable pour production

### 3.4 API Framework : FastAPI

#### Justification

**✅ Avantages** :
- **Async native** : Support asyncio pour haute concurrence
- **Validation automatique** : Pydantic pour requêtes/réponses
- **Documentation auto** : Swagger UI + ReDoc gratuits
- **Performance** : Comparable à Node.js/Go (Starlette + uvicorn)
- **Type hints** : Sécurité des types au développement
- **Background tasks** : Support natif pour tâches longues

**❌ Alternative non retenue** :
- **Flask** : Pas d'async natif, validation manuelle, plus lent

**Exemple d'endpoint avec validation** :
```python
@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    # Pydantic valide automatiquement:
    # - query: str (min 1, max 500 chars)
    # - top_k: int (1-20)
    ...
```

### 3.5 UI : Streamlit

#### Justification

**✅ Avantages** :
- **Prototypage rapide** : Chat interface en <200 lignes
- **Python pur** : Pas de JavaScript/HTML/CSS requis
- **Session state** : Gestion mémoire conversationnelle intégrée
- **Composants riches** : Chat, markdown, code, graphiques
- **Réactivité** : Re-run automatique sur changement

**❌ Limitations** :
- Pas pour production web (performances limitées)
- Customisation CSS difficile
- Multi-utilisateurs limité (pas de vrais WebSockets)

**Pour production** : Frontend React + API FastAPI séparée

### 3.6 Package Manager : uv

#### Justification

**✅ Avantages** :
- **10-100x plus rapide** que pip
- **Lock file** : Builds reproductibles (uv.lock)
- **Résolution moderne** : Gère les conflits de dépendances
- **Virtual env intégré** : Pas besoin de venv manuel
- **Compatible pip** : `uv pip install` marchant comme pip

**Commandes équivalentes** :
```bash
# pip
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# uv (simplifié)
uv sync
```

### 3.7 Data Source : Open Agenda API

#### Justification

**✅ Avantages** :
- **Exhaustif** : Milliers d'événements culturels français
- **Gratuit** : Tier gratuit suffisant (rate limits raisonnables)
- **Structuré** : JSON avec métadonnées riches (date, lieu, prix, catégories)
- **Actualisé** : Mise à jour quotidienne par organisateurs
- **API REST** : Facile d'intégration

**Structure événement** :
```json
{
  "uid": "123456",
  "title": "Concert de Jazz",
  "description": "...",
  "location": {
    "city": "Paris",
    "address": "...",
    "latitude": 48.8566,
    "longitude": 2.3522
  },
  "timings": [{
    "begin": "2025-01-20T20:00:00",
    "end": "2025-01-20T23:00:00"
  }],
  "freeText": {
    "fr": "Gratuit"
  },
  "links": ["https://..."]
}
```

### 3.8 Database : PostgreSQL + SQLAlchemy

#### Justification

**✅ Avantages** :
- **Persistence** : Sessions survivent aux redémarrages du serveur
- **Async Support** : SQLAlchemy 2.0 avec asyncpg pour performances
- **JSONB** : Stockage flexible des métadonnées et sources RAG
- **Scalabilité** : Prêt pour déploiement multi-instances
- **Transactions** : Garanties ACID pour intégrité des données

**❌ Alternatives non retenues** :
- **Redis** : Plus rapide mais moins structuré, pas de requêtes complexes
- **MongoDB** : Overkill pour ce cas d'usage, pas d'async natif mature
- **SQLite** : Pas adapté pour multi-utilisateurs concurrents

#### Modèles de Données

```python
class SessionModel(Base):
    id: UUID                    # Primary key
    user_id: Optional[str]      # Pour filtrage par utilisateur
    created_at: datetime        # Avec timezone
    updated_at: datetime
    metadata: dict              # JSONB

class MessageModel(Base):
    id: int                     # Auto-increment
    session_id: UUID            # Foreign key → Session
    role: str                   # 'user' ou 'assistant'
    content: str                # Texte du message
    sources: Optional[dict]     # JSONB avec événements RAG
    latency_ms: Optional[float] # Performance tracking
    query_type: Optional[str]   # 'chat' ou 'search'
```

#### Configuration

```python
{
  "pool_size": 10,           # Connexions persistentes
  "max_overflow": 20,        # Connexions additionnelles
  "pool_pre_ping": True,     # Health check automatique
  "echo": False              # Debug SQL (désactivé en prod)
}
```

### 3.9 Frontend : React 18 + TypeScript + Vite

#### Justification

**✅ Avantages** :
- **Type Safety** : TypeScript pour robustesse et meilleure DX
- **Performance** : Vite pour builds ultra-rapides (<1s HMR)
- **UI Components** : shadcn/ui + Tailwind CSS pour design moderne
- **State Management** : TanStack Query (server) + Zustand (client)
- **Production-ready** : Docker multi-stage build optimisé

**❌ Pourquoi pas rester sur Streamlit seul ?**
- Streamlit limité en personnalisation UI
- Pas de vrais WebSockets pour temps réel
- Performances multi-utilisateurs limitées
- Difficile à intégrer dans infrastructure existante

#### Stack Frontend

| Technologie | Version | Rôle |
|-------------|---------|------|
| React | 18+ | Framework UI |
| TypeScript | 5.9 | Typage statique |
| Vite | 7.2 | Build tool |
| Tailwind CSS | 4.1 | Styling utility-first |
| shadcn/ui | latest | Composants UI |
| TanStack Query | 5.90 | Server state |
| Zustand | 5.0 | Client state |
| Axios | 1.13 | HTTP client |
| Recharts | 3.7 | Graphiques |

#### Fonctionnalités

L'application React inclut **5 vues principales** :

1. **ChatView** : Conversation avec le chatbot RAG
   - Sessions persistentes
   - Affichage des sources avec scores
   - Paramètre top_k configurable

2. **ApiExplorerView** : Test des endpoints API
   - Onglets Chat, Search, Health, Rebuild, Session
   - Requêtes en temps réel

3. **MonitoringView** : Santé du système
   - Polling automatique du health endpoint
   - Métriques (documents, sessions, embedding dim)

4. **RagasMetricsView** : Visualisation évaluation
   - Upload de rapports JSON
   - Graphiques Recharts
   - Tableau de résultats détaillés

5. **IndexManagementView** : Gestion FAISS
   - Informations sur l'index actuel
   - Déclenchement rebuild avec progress

---

## IV. MODÈLES UTILISÉS

### 4.1 Configuration LLM

**Modèle** : `mistral-small-latest`
- Provider : Mistral AI
- Version : Auto-updated (toujours dernière version stable)
- Context window : 32K tokens
- Output max : 1000 tokens (~750 mots)

**Paramètres de génération** :
```python
{
  "temperature": 0.7,      # Créativité modérée
  "max_tokens": 1000,      # Limite longueur réponse
  "top_p": 1.0,           # Nucleus sampling (toute la distribution)
  "stream": True           # Streaming pour UX
}
```

**Explication température 0.7** :
- 0.0 : Déterministe, répétitif
- 0.7 : Équilibre créativité/consistance (recommandé)
- 1.0+ : Très créatif, risque d'incohérence

### 4.2 Configuration Embeddings

**Modèle** : `mistral-embed`
- Dimension : 1024
- Langue : Multilingue (optimisé français)
- Max input : ~8192 tokens
- Output : Vecteurs normalisés L2

**Batch processing** :
```python
{
  "batch_size": 32,        # Documents par requête API
  "max_retries": 3,        # Tentatives en cas d'échec
  "timeout": 30            # Timeout par requête (secondes)
}
```

**Performance** :
- Latence : ~200-300ms par batch de 32
- Coût : $0.0001/1K tokens (~500 événements = $0.05)

### 4.3 Configuration Vector Index

**Type d'index** : `faiss.IndexFlatL2`
```python
{
  "index_type": "IndexFlatL2",       # Recherche exacte
  "dimension": 1024,                 # Correspond à mistral-embed
  "metric_type": "L2",               # Distance euclidienne
  "normalize_vectors": True,         # Pour cosine similarity
  "num_documents": 497               # Taille actuelle
}
```

**Normalisation L2** :
```python
import faiss
faiss.normalize_L2(embeddings)  # ||v|| = 1
```

**Équivalence cosine ↔ L2** (avec normalisation) :
```
similarity_cosine = 1 - (distance_L2 / 2)
```

**Paramètres de recherche** :
```python
{
  "top_k": 5,                  # Nombre de résultats (configurable 1-20)
  "min_similarity": 0.3        # Seuil de filtrage
}
```

### 4.4 Prompt Template

**Template système** (de `src/config/constants.py`) :
```python
SYSTEM_PROMPT_TEMPLATE = """Tu es un assistant intelligent qui aide les 
utilisateurs à découvrir des événements culturels.

Contexte des événements trouvés :
{context}

Question de l'utilisateur : {question}

Instructions :
- Réponds en français de manière naturelle et conversationnelle
- Recommande 2-3 événements pertinents maximum
- Mentionne les informations pratiques (date, lieu, prix)
- Si aucun événement ne correspond, propose des alternatives
- Sois concis mais informatif

Réponse :"""
```

**Variables de template** :
- `{context}` : Documents récupérés par FAISS (formatés en texte)
- `{question}` : Requête utilisateur originale

**Format du contexte** :
```
Titre: Concert de Jazz
Ville: Paris
Date: 20/01/2025 20:00
Prix: Gratuit
Description: Un concert de jazz exceptionnel...
URL: https://openagenda.com/...

---

Titre: Festival Électro
...
```

---

## V. RÉSULTATS OBSERVÉS

### 5.1 Métriques de Performance

**Source** : `data/processed/evaluation_results.json` + tests manuels

#### Métriques Globales

| Métrique | Valeur | Cible | Statut |
|----------|--------|-------|--------|
| **Latence moyenne** | 2.41s | <3.0s | ✅ PASS (+0.59s marge) |
| **Couverture mots-clés** | 81.5% | >80% | ✅ PASS (+1.5%) |
| **Classification accuracy** | 100% | ~95% | ✅ EXCELLENT (+5%) |
| **Test coverage code** | 85% | >80% | ✅ PASS (+5%) |
| **Questions RAG** | 9/12 (75%) | - | ✅ Good |
| **Questions conversationnelles** | 3/12 (25%) | - | ✅ Good |

#### Latence par Catégorie

| Catégorie | Nb Questions | Latence Moy. | Couverture Moy. | Statut |
|-----------|--------------|--------------|-----------------|--------|
| **Recherche simple** | 4 | 2.56s | 91.7% | ✅ |
| **Filtres multiples** | 2 | 3.28s | 100% | ⚠️ Limite |
| **Recherche temporelle** | 2 | 2.97s | 50% | ⚠️ |
| **Conversation** | 3 | 1.50s | 100% | ✅ |
| **Recherche style** | 1 | 1.69s | 66.7% | ⚠️ |

**Observations** :
- ✅ Recherches simples excellentes (91.7% couverture)
- ✅ Filtres multiples parfait mais lent (3.28s)
- ⚠️ Temporalité à améliorer (50% couverture sur "été", "weekend")
- ✅ Conversations très rapides (1.5s, pas de FAISS)
- ⚠️ Recherches par style à améliorer (66.7%)

### 5.2 Analyse de Classification (needs_rag)

**Matrice de confusion** (12 questions test) :

|  | Prédit SEARCH | Prédit CHAT |
|---|---------------|-------------|
| **Réel SEARCH** | 9 (TP) | 0 (FN) |
| **Réel CHAT** | 0 (FP) | 3 (TN) |

**Métriques** :
- Accuracy : **100%** (12/12)
- Precision : 100%
- Recall : 100%
- F1-score : 100%

**Exemples correctement classifiés** :

**SEARCH** :
- ✅ "Quels concerts de jazz sont prévus ce weekend à Paris ?"
- ✅ "Y a-t-il des événements gratuits pour enfants dimanche ?"
- ✅ "Je cherche une exposition d'art contemporain à Marseille"

**CHAT** :
- ✅ "Bonjour, comment ça va ?"
- ✅ "Merci beaucoup pour ton aide !"
- ✅ "Tu peux m'aider à trouver des sorties ?"

**Importance** : Évite recherches FAISS inutiles (~1s économisé par requête conversationnelle)

### 5.3 Exemples de Réponses

**Exemple 1** : Recherche simple
```
Question: "Quels concerts de jazz sont prévus ce weekend à Paris ?"
Latence: 1.47s
Couverture: 100% (3/3)
Classification: SEARCH ✅

Réponse:
"Salut ! Voici quelques concerts de jazz ce weekend à Paris :
1. Paris Jazz Festival - Sam 18/01 à 20h, Parc Floral, Gratuit
2. Jazz au Caveau - Dim 19/01 à 19h30, Caveau de la Huchette, 15€
N'hésite pas si tu veux plus d'infos ! 🎷"

Sources: 3 événements (similarité: 0.87, 0.82, 0.76)
```

**Exemple 2** : Filtres multiples
```
Question: "Y a-t-il des événements gratuits pour enfants dimanche ?"
Latence: 3.88s ⚠️
Couverture: 100% (3/3)
Classification: SEARCH ✅

Réponse:
"Oui, voici quelques événements gratuits pour enfants ce dimanche :
1. Atelier Créatif Enfants - Dim 19/01 à 14h, Bibliothèque Municipale
2. Spectacle de Marionnettes - Dim 19/01 à 16h, Parc Borély
C'est des activités sympas pour les petits ! 😊"

Sources: 3 événements (similarité: 0.91, 0.85, 0.73)
```

**Exemple 3** : Conversation
```
Question: "Bonjour, comment ça va ?"
Latence: 1.98s
Classification: CHAT ✅

Réponse:
"Salut ! Je vais très bien, merci ! 😊
Je suis là pour t'aider à trouver des événements culturels sympas.
Tu cherches quelque chose en particulier ?"

Sources: Aucune (pas de RAG)
```

### 5.4 Analyse de Qualité

**Points forts** :
- ✅ Réponses naturelles en français (ton conversationnel)
- ✅ Informations pratiques complètes (date, lieu, prix, URL)
- ✅ Classification fiable (100% accuracy)
- ✅ Sources vérifiables (liens Open Agenda)
- ✅ Suggestions alternatives quand pas de match
- ✅ Latence respectée (2.41s moyenne < 3s cible)

**Limitations identifiées** :
- ⚠️ Filtres temporels complexes ("été", "weekend") parfois incomplets
- ⚠️ Genres musicaux spécifiques ("techno", "electro") parfois manqués
- ⚠️ Pas de reformulation de requête si aucun résultat
- ⚠️ Latence variable (1.5s CHAT vs 3.9s SEARCH multi-filtres)

---

## VI. PISTES D'AMÉLIORATION

### 6.1 Performance

**Optimisation FAISS** :
- **Actuel** : IndexFlatL2 (recherche exacte, O(n))
- **Amélioration** : IndexIVFFlat pour >10K événements
  - Recherche approximative (95-98% recall)
  - 10-100x plus rapide
  - Trade-off acceptable pour production
  
```python
# Configuration IVF recommandée
nlist = 100  # Nombre de clusters
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
index.train(embeddings)  # Entraînement requis
```

**Caching stratégies** :
- Cache embeddings pour requêtes fréquentes (Redis)
  - Évite appels API Mistral répétés
  - Réduction 50% du coût pour queries répétées
- Cache réponses LLM (TTL 1h)
  - Pour requêtes identiques
  - Trade-off fraîcheur vs performance

**Batch optimizations** :
- Batch size dynamique basé sur GPU memory
- Streaming embeddings vers FAISS (réduit RAM)

### 6.2 Fonctionnalité

**Session Persistence** : ✅ **IMPLÉMENTÉ**
- **Avant** : In-memory (perdu au restart)
- **Maintenant** : PostgreSQL avec SQLAlchemy async
- **Modèles** : `SessionModel`, `MessageModel` avec JSONB
- **Bénéfices obtenus** :
  - Sessions persistent entre redémarrages
  - Historique stocké avec sources et latence
  - Multi-instance ready
  - Analytics possibles sur requêtes

**Frontend React** : ✅ **IMPLÉMENTÉ**
- Application complète avec 5 vues
- shadcn/ui + Tailwind CSS
- TanStack Query + Zustand

**Authentification Utilisateurs** :
- OAuth2 (Google, GitHub)
- JWT tokens pour stateless auth
- Per-user query history et préférences
- Rate limiting par utilisateur

**Support Multi-Langues** :
- Anglais, Espagnol (en plus du français)
- Language detection dans query
- Multilingual embeddings déjà supportés (Mistral Embed)

**Filtres Avancés** :
- Prix range slider (0-50€)
- Distance radius from location (5km, 10km, 20km)
- Event duration (1h, 2h+, full day)
- Accessibility filters (wheelchair, hearing loop)

### 6.3 Qualité RAG

**Reranking avec Cross-Encoder** :
- **Actuel** : Single-pass retrieval (bi-encoder)
- **Amélioration** : Two-stage pipeline
  1. FAISS retrieves top-20 (bi-encoder rapide)
  2. Cross-encoder reranks to top-5 (lent mais précis)
- **Gain attendu** : +10-15% relevance

**Hybrid Search** :
- Combiner semantic (FAISS) + keyword (BM25/Elasticsearch)
- Weighted: 0.7 × semantic + 0.3 × keyword
- Meilleur pour exact name matches ("Festival d'Avignon")

**Query Expansion** :
- LLM-based query reformulation
- Extract filters: "weekend" → "samedi" OR "dimanche"
- Expand genres: "jazz" → "jazz", "blues", "soul"

**Vector Memory** :
- Store conversation history as embeddings
- Semantic search over past exchanges
- Better long-term context preservation

### 6.4 Opérations

**Monitoring Production** :
- Prometheus metrics (latency, error rate, API calls)
- Grafana dashboards
- Alerts si latency >5s ou error rate >5%

**CI/CD Pipeline** :
- GitHub Actions :
  - pytest on every PR
  - Black/Ruff checks
  - Docker build and push
  - Deploy to staging on merge to main

**Automated Index Refresh** :
- Cron job to fetch new events daily
- Incremental index updates (FAISS add_with_ids)
- Blue-green deployment pour zero-downtime

**A/B Testing Framework** :
- Test prompt variations
- Compare embedding models
- Measure impact of reranking

### 6.5 Priorisation (Mise à Jour Février 2026)

**✅ COMPLÉTÉ** :
1. ~~Session persistence~~ → PostgreSQL + SQLAlchemy async
2. ~~Frontend React~~ → Application complète avec 5 vues
3. ~~CI/CD pipeline~~ → GitHub Actions (lint, build, docker)

**High Priority** (Restant) :
1. Monitoring + alerting (Prometheus/Grafana)
2. FAISS IVF pour scalabilité (>10K events)
3. Rate limiting API

**Medium Priority** (Quality improvement) :
4. Reranking (cross-encoder)
5. Hybrid search (BM25 + FAISS)
6. Advanced filters (prix, distance, durée)
7. Query expansion

**Low Priority** (Nice-to-have) :
8. Multi-language support (EN, ES)
9. User authentication (OAuth2)
10. A/B testing framework
11. Vector memory

**Estimation effort** (1 développeur) :
- High priority restant : 1-2 semaines
- Medium priority : 3-4 semaines
- Low priority : 2-3 semaines

---

## VII. CONCLUSION

### 7.1 Réalisations

Ce projet démontre une implémentation complète et fonctionnelle d'un système RAG production-ready :

**Succès techniques** :
- ✅ Architecture 4 couches bien séparée
- ✅ Pipeline RAG complet (classification, retrieval, generation)
- ✅ Performance cibles atteintes (latence, relevance, accuracy)
- ✅ Tests complets (85% coverage, 3 niveaux)
- ✅ Documentation professionnelle
- ✅ Déploiement Docker ready

**Succès fonctionnels** :
- ✅ Classification intelligente SEARCH vs CHAT (100% accuracy)
- ✅ Recherche sémantique pertinente (81.5% keyword coverage)
- ✅ Réponses naturelles en français
- ✅ Sources vérifiables citées
- ✅ Session management fonctionnel

### 7.2 Évaluation Production-Readiness

| Aspect | Statut | Notes |
|--------|--------|-------|
| **Functionality** | ✅ Ready | RAG + React frontend + API complète |
| **Performance** | ✅ Ready | Meets latency/relevance targets |
| **Reliability** | ✅ Ready | PostgreSQL sessions + error handling |
| **Scalability** | ⚠️ Partial | Works <1K events, needs IVF for scale |
| **Security** | ⚠️ Partial | Basic validation, needs auth/rate limiting |
| **Observability** | ⚠️ Partial | Frontend monitoring, needs Prometheus |
| **Deployment** | ✅ Ready | Docker + compose + CI/CD GitHub Actions |

**Recommandation** : Ready for **production MVP deployment**. Ajouter Prometheus/Grafana et authentification pour production complète.

### 7.3 Leçons Apprises

**Techniques** :
- Direct SDK integration > abstraction frameworks (pour cette échelle)
- FAISS parfait pour <1M documents
- Mistral AI excellent pour français
- Query classification critique pour UX (évite RAG inutiles)
- Streaming responses améliore significativement UX

**Méthodologiques** :
- Jupyter notebooks excellents pour expérimentation
- TDD pays off (détection bugs précoce)
- RAGAS framework valuable mais requires labeled data
- Documentation from day 1 crucial

**Architecturales** :
- Séparation présentation/logique/données facilite tests
- Pydantic validation sauve beaucoup de bugs
- Background tasks essentiels pour opérations longues
- PostgreSQL pour sessions = scalabilité et persistence
- Monorepo (backend/frontend) simplifie le déploiement unifié

### 7.4 Prochaines Étapes

**✅ Complété** :
- ~~Session persistence~~ → PostgreSQL implémenté
- ~~CI/CD pipeline~~ → GitHub Actions configuré
- ~~Frontend web React~~ → Application complète

**Court terme (1 mois)** :
1. Ajouter Prometheus + Grafana monitoring
2. Add temporal filter expansion ("été" → months)
3. Rate limiting API

**Moyen terme (3 mois)** :
4. Implement reranking (cross-encoder)
5. Scale to 10K+ events (FAISS IVF)
6. Add user authentication (OAuth2)
7. Advanced filtering (price, distance)

**Long terme (6+ mois)** :
8. Multi-language support (EN, ES)
9. Automated daily index refresh
10. A/B testing framework

---

## ANNEXES

Voir le dossier `annexes/` pour :
- **[architecture-complete.md](annexes/architecture-complete.md)** : Architecture système détaillée
- **[choix-technologiques.md](annexes/choix-technologiques.md)** : Comparaisons technologiques approfondies
- **[ameliorations-futures.md](annexes/ameliorations-futures.md)** : Roadmap détaillée avec estimations
- **[schemas/](annexes/schemas/)** : Diagrammes d'architecture ASCII

---

## RÉFÉRENCES

### Documentation

- **README.md** : Vue d'ensemble du projet
- **ARCHITECTURE.md** : Architecture système
- **COMPRENDRE_LE_RAG.md** : Guide pédagogique RAG
- **GUIDE_DEMARRAGE.md** : Installation et démarrage
- **REFERENCE_API.md** : Documentation API REST

### Sources Externes

- Mistral AI Documentation : https://docs.mistral.ai/
- FAISS Documentation : https://github.com/facebookresearch/faiss
- FastAPI Documentation : https://fastapi.tiangolo.com/
- Streamlit Documentation : https://docs.streamlit.io/
- Open Agenda API : https://openagenda.com/developers
- RAGAS Framework : https://docs.ragas.io/

### Articles de Référence

- Lewis et al. (2020) : "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
- Johnson et al. (2019) : "Billion-scale similarity search with GPUs" (FAISS)
- Reimers & Gurevych (2019) : "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks"

---

**Date de rédaction** : 4 Février 2026 (v2.0)  
**Auteur** : Pierre Pluton  
**Contact** : pierre.pluton@outlook.fr  
**Repository** : https://github.com/[username]/OC7---Projet-RAG-Assistant-Intelligent-Events

---

<div align="center">

**Fait avec ❤️ et ☕ dans le cadre du parcours OpenClassrooms**

🎭 **RAG Events Assistant** - Découvrez des événements culturels avec l'IA

</div>
