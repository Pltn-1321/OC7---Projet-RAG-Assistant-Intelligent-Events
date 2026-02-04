# Architecture du Systeme RAG Events Assistant

Ce document decrit l'architecture technique du systeme RAG (Retrieval-Augmented Generation) pour la decouverte d'evenements culturels.

## Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           UTILISATEUR                                    │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                         COUCHE PRESENTATION                               │
│  ┌─────────────────────┐         ┌─────────────────────────────────────┐  │
│  │   Streamlit UI      │         │         FastAPI REST API            │  │
│  │   (Port 8501)       │         │         (Port 8000)                 │  │
│  │                     │         │                                     │  │
│  │  - Chat interface   │         │  - POST /search                     │  │
│  │  - Historique       │         │  - POST /chat                       │  │
│  │  - Sources          │         │  - POST /rebuild                    │  │
│  │  - Configuration    │         │  - GET  /health                     │  │
│  └─────────────────────┘         └─────────────────────────────────────┘  │
└───────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                         COUCHE LOGIQUE METIER                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                         RAGEngine                                    │  │
│  │                                                                      │  │
│  │  ┌──────────────┐    ┌──────────────┐    ┌───────────────────────┐  │  │
│  │  │  needs_rag() │───▶│   search()   │───▶│  generate_response()  │  │  │
│  │  │  (Classif.)  │    │  (Retrieval) │    │    (Generation)       │  │  │
│  │  └──────────────┘    └──────────────┘    └───────────────────────┘  │  │
│  │         │                    │                      │                │  │
│  │         ▼                    ▼                      ▼                │  │
│  │  ┌──────────────┐    ┌──────────────┐    ┌───────────────────────┐  │  │
│  │  │ Mistral LLM  │    │ FAISS Index  │    │    Mistral LLM        │  │  │
│  │  │ (Classif.)   │    │ (Recherche)  │    │   (Generation)        │  │  │
│  │  └──────────────┘    └──────────────┘    └───────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                         COUCHE DONNEES                                    │
│  ┌─────────────────────┐    ┌─────────────────────────────────────────┐  │
│  │  data/processed/    │    │         Services Externes                │  │
│  │                     │    │                                          │  │
│  │  - faiss_index/     │    │  ┌────────────────┐ ┌─────────────────┐  │  │
│  │    - events.index   │    │  │  Mistral API   │ │ Open Agenda API │  │  │
│  │    - config.json    │    │  │  (Embeddings)  │ │    (Events)     │  │  │
│  │                     │    │  │  (LLM)         │ │                 │  │  │
│  │  - rag_documents.   │    │  └────────────────┘ └─────────────────┘  │  │
│  │    json             │    │                                          │  │
│  │                     │    │                                          │  │
│  │  - embeddings/      │    │                                          │  │
│  │    - embeddings.npy │    │                                          │  │
│  └─────────────────────┘    └─────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
```

## Composants Principaux

### 1. Interface Utilisateur (Streamlit)

**Fichier**: `app.py`

L'interface Streamlit offre:
- Une interface de chat intuitive
- L'affichage de l'historique des conversations
- La visualisation des sources (evenements trouves)
- Un panneau de configuration (top_k, reinitialisation)

**Caracteristiques techniques**:
- Utilisation de `@st.cache_resource` pour le cache du RAGEngine
- Gestion de l'etat via `st.session_state`
- Design responsive avec CSS personnalise

### 2. API REST (FastAPI)

**Fichier**: `src/api/main.py`

Endpoints disponibles:

| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/health` | GET | Verification de l'etat du service |
| `/search` | POST | Recherche semantique d'evenements |
| `/chat` | POST | Chat avec memoire conversationnelle |
| `/session/{id}` | GET | Recuperer l'historique d'une session |
| `/session/{id}` | DELETE | Supprimer une session |
| `/rebuild` | POST | Reconstruire l'index FAISS |
| `/rebuild/{task_id}` | GET | Statut d'une reconstruction |

**Caracteristiques techniques**:
- Validation Pydantic pour toutes les requetes/reponses
- Gestion des sessions en memoire
- Documentation Swagger auto-generee (`/docs`)
- Support CORS configurable

### 3. Moteur RAG (RAGEngine)

**Fichier**: `src/rag/engine.py`

Le coeur du systeme avec les methodes:

1. **`needs_rag(query)`**: Classifie si la requete necessite une recherche
2. **`encode_query(query)`**: Convertit le texte en embedding
3. **`search(query, top_k)`**: Recherche semantique dans FAISS
4. **`generate_response(query, results)`**: Genere une reponse avec le LLM
5. **`chat(query, top_k, history)`**: Pipeline complet intelligent

### 4. Constructeur d'Index (IndexBuilder)

**Fichier**: `src/rag/index_builder.py`

Responsable de la reconstruction de l'index:
1. Charge les documents (`rag_documents.json`)
2. Genere les embeddings (Mistral ou sentence-transformers)
3. Construit l'index FAISS (IndexFlatL2 normalise)
4. Sauvegarde l'index et les metadonnees

## Structure des Repertoires

```
rag-events-assistant/
├── app.py                    # Interface Streamlit
├── src/
│   ├── api/
│   │   └── main.py          # Endpoints FastAPI
│   ├── config/
│   │   ├── settings.py      # Configuration Pydantic
│   │   └── constants.py     # Constantes (chemins, prompts)
│   ├── data/
│   │   └── models.py        # Modeles Pydantic (Event, etc.)
│   ├── rag/
│   │   ├── engine.py        # Moteur RAG principal
│   │   └── index_builder.py # Construction d'index
│   └── utils/               # Utilitaires
├── scripts/
│   ├── evaluate_rag.py      # Evaluation RAGAS
│   └── api_test.py          # Tests fonctionnels API
├── tests/
│   ├── unit/                # Tests unitaires
│   ├── integration/         # Tests d'integration
│   └── e2e/                 # Tests end-to-end
├── data/
│   ├── raw/                 # Donnees brutes Open Agenda
│   ├── processed/           # Donnees traitees et index
│   └── indexes/             # (alias vers processed/faiss_index)
├── notebooks/               # Notebooks d'exploration
└── docs/                    # Documentation
```

## Flux de Donnees

### Pipeline de Chat

```
1. Requete utilisateur
       │
       ▼
2. Classification (needs_rag?)
       │
       ├──────────────────────┐
       │                      │
   [SEARCH]               [CHAT]
       │                      │
       ▼                      ▼
3. Encodage requete    4. Reponse directe
       │                   (sans RAG)
       ▼
4. Recherche FAISS
       │
       ▼
5. Top-K documents
       │
       ▼
6. Generation LLM
   avec contexte
       │
       ▼
7. Reponse + Sources
```

### Pipeline de Reconstruction d'Index

```
1. POST /rebuild
       │
       ▼
2. Validation API Key
       │
       ▼
3. Tache en arriere-plan
       │
       ├─▶ Charger documents
       │
       ├─▶ Generer embeddings
       │   (batch de 32)
       │
       ├─▶ Construire index FAISS
       │
       └─▶ Sauvegarder fichiers

4. Invalidation cache RAGEngine
       │
       ▼
5. Nouvel index disponible
```

## Configuration

### Variables d'Environnement

| Variable | Description | Defaut |
|----------|-------------|--------|
| `MISTRAL_API_KEY` | Cle API Mistral (obligatoire) | - |
| `REBUILD_API_KEY` | Cle pour /rebuild | - |
| `EMBEDDING_PROVIDER` | `mistral` ou `sentence-transformers` | `mistral` |
| `LLM_MODEL` | Modele Mistral | `mistral-small-latest` |
| `LLM_TEMPERATURE` | Temperature LLM | `0.7` |
| `TOP_K_RESULTS` | Nombre de resultats | `5` |
| `LOG_LEVEL` | Niveau de log | `INFO` |

### Fichiers de Configuration

- **`.env`**: Variables d'environnement (non versionne)
- **`pyproject.toml`**: Dependances et configuration outils
- **`data/processed/faiss_index/config.json`**: Metadonnees de l'index

## Securite

### Mesures Implementees

1. **Validation des entrees**: Pydantic sur tous les endpoints
2. **Authentification /rebuild**: Header `X-API-Key`
3. **Gestion des cles API**: Variables d'environnement
4. **Pas de SQL**: FAISS est une base vectorielle (pas d'injection SQL)
5. **Erreurs generiques**: Pas d'exposition de details internes

### Recommandations Production

- Utiliser HTTPS (reverse proxy nginx/traefik)
- Limiter le rate limiting
- Ajouter une authentification sur tous les endpoints
- Monitorer les logs et metriques
