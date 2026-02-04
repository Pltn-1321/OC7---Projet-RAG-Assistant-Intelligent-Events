# Guide de Démarrage Rapide

Ce guide vous accompagne dans l'installation et le premier lancement du RAG Events Assistant.

## Structure du Projet

Ce projet utilise une **architecture monorepo** :

```
projet/
├── backend/           # API Python + RAG Engine (uv)
│   ├── src/           # Code source Python
│   ├── tests/         # Tests pytest
│   ├── app.py         # Interface Streamlit
│   └── pyproject.toml # Dépendances Python
│
├── frontend/          # Application React (npm)
│   ├── src/           # Code TypeScript/React
│   └── package.json   # Dépendances Node.js
│
└── docker-compose.yml # Orchestration des services
```

## Prérequis

### Système

- **Python**: 3.11 ou supérieur
- **Node.js**: 18+ (pour le frontend React)
- **Docker**: Recommandé pour PostgreSQL
- **Système d'exploitation**: Linux, macOS, ou Windows (WSL2 recommandé)
- **RAM**: Minimum 4 Go (8 Go recommandé)
- **Espace disque**: 2 Go pour les données et index

### Comptes et Clés API

- **Clé API Mistral**: Obligatoire pour le LLM et les embeddings
  - Inscription: https://console.mistral.ai/
  - Gratuit pour commencer (limites de rate)

## Installation

### 1. Cloner le Repository

```bash
git clone https://github.com/votre-repo/rag-events-assistant.git
cd rag-events-assistant
```

### 2. Installer uv (Gestionnaire de Paquets)

**Linux/macOS**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)**:
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Verification**:
```bash
uv --version
# Devrait afficher: uv 0.x.x
```

### 3. Installer les Dépendances

#### Backend (Python)

```bash
cd backend

# Installation de base
uv sync

# Tout installer (recommandé)
uv sync --all-extras
```

#### Frontend (React) - Optionnel

```bash
cd frontend
npm install
```

### 4. Configurer la Base de Données

#### Option A: Docker (Recommandé)

```bash
# Depuis la racine du projet
docker-compose up -d postgres
```

#### Option B: PostgreSQL Local

Installer PostgreSQL et créer la base de données :
```sql
CREATE DATABASE rag_events;
CREATE USER rag_user WITH PASSWORD 'rag_password';
GRANT ALL PRIVILEGES ON DATABASE rag_events TO rag_user;
```

### 5. Configurer les Variables d'Environnement

Créer un fichier `.env` à la racine du projet :

```bash
# Copier le template
cp .env.example .env

# Éditer avec votre éditeur
nano .env  # ou code .env, vim .env, etc.
```

**Contenu du fichier `.env`** :
```env
# Obligatoire - Mistral AI
MISTRAL_API_KEY=votre_cle_mistral_ici

# Base de données PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
POSTGRES_DB=rag_events

# Optionnel
REBUILD_API_KEY=une_cle_secrete_pour_rebuild
LOG_LEVEL=INFO
LLM_TEMPERATURE=0.7
TOP_K_RESULTS=5
```

### 5. Preparer les Donnees

Si vous n'avez pas encore de donnees, suivez les notebooks dans l'ordre:

```bash
# Lancer Jupyter Lab
uv run jupyter lab
```

1. `01_data_collection.ipynb` - Collecter les evenements (Open Agenda)
2. `02_data_preprocessing.ipynb` - Nettoyer et formater les donnees
3. `03_create_embeddings_mistral.ipynb` - Generer les embeddings
4. `04_build_faiss_index.ipynb` - Construire l'index FAISS

**Ou avec les scripts** (si implementes):
```bash
uv run python scripts/fetch_events.py --location marseille --max-events 500
uv run python scripts/build_index.py
```

## Premier Lancement

### Option 1: Docker Compose (Recommandé)

```bash
# Depuis la racine du projet
docker-compose up
```

**URLs disponibles** :
- **Frontend React** : http://localhost:5173
- **API FastAPI** : http://localhost:8000
- **Streamlit** : http://localhost:8501
- **Documentation API** : http://localhost:8000/docs

### Option 2: Développement Séparé

**Terminal 1 - Backend API** :
```bash
cd backend
uv run uvicorn src.api.main:app --reload
```

**Terminal 2 - Frontend React** :
```bash
cd frontend
npm run dev
```

**URLs** :
- Frontend React : http://localhost:5173
- API FastAPI : http://localhost:8000
- Documentation Swagger : http://localhost:8000/docs

### Option 3: Streamlit Uniquement

```bash
cd backend
uv run streamlit run app.py
```

Ouvrez votre navigateur à : http://localhost:8501

## Verification du Fonctionnement

### 1. Verifier l'API

```bash
# Health check
curl http://localhost:8000/health

# Reponse attendue:
# {"status":"healthy","documents":497,"embedding_dim":1024,"active_sessions":0}
```

### 2. Tester une Recherche

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "concert de jazz", "top_k": 3}'
```

### 3. Tester le Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Bonjour, que peux-tu faire ?"}'
```

### 4. Utiliser le Script de Test

```bash
uv run python scripts/api_test.py
```

## Structure des Donnees

Apres l'installation, vous devriez avoir:

```
data/
├── processed/
│   ├── rag_documents.json      # Documents pour le RAG
│   ├── faiss_index/
│   │   ├── events.index        # Index FAISS
│   │   └── config.json         # Configuration de l'index
│   └── embeddings/
│       ├── embeddings.npy      # Vecteurs d'embeddings
│       └── metadata.json       # Metadonnees
└── raw/                         # Donnees brutes (optionnel)
```

## Resolution des Problemes Courants

### Erreur: "Index FAISS non trouve"

**Cause**: L'index n'a pas ete construit.

**Solution**:
```bash
# Executer les notebooks 01 a 04
# Ou utiliser les scripts de build
uv run python scripts/build_index.py
```

### Erreur: "MISTRAL_API_KEY non configuree"

**Cause**: La variable d'environnement n'est pas definie.

**Solution**:
1. Verifier que le fichier `.env` existe
2. Verifier que `MISTRAL_API_KEY` est definie
3. Relancer l'application

### Erreur: "Rate limit exceeded" (Mistral)

**Cause**: Trop de requetes a l'API Mistral.

**Solution**:
- Attendre quelques minutes
- Utiliser `sentence-transformers` pour les embeddings:
  ```env
  EMBEDDING_PROVIDER=sentence-transformers
  ```

### Streamlit ne se lance pas

**Cause possible**: Port deja utilise.

**Solution**:
```bash
# Specifier un autre port
uv run streamlit run app.py --server.port 8502
```

### Docker: Permission denied

**Cause**: Probleme de droits sur les volumes.

**Solution**:
```bash
# Donner les droits au repertoire data
chmod -R 755 data/
```

## Prochaines Etapes

1. **Explorer les notebooks**: Pour comprendre le pipeline de donnees
2. **Lire la documentation API**: `/docs` sur le serveur FastAPI
3. **Personnaliser les prompts**: Dans `src/config/constants.py`
4. **Ajouter vos propres donnees**: Adapter le preprocessing
5. **Evaluer le systeme**: `uv run python scripts/evaluate_rag.py`

## Commandes Utiles

### Backend (depuis `backend/`)

```bash
# Lancer les tests
uv run pytest

# Tests avec couverture
uv run pytest --cov=src --cov-report=html

# Formater le code
uv run black src tests scripts
uv run ruff check src tests scripts

# Évaluation RAG
uv run python scripts/evaluate_rag.py

# Test API interactif
uv run python scripts/api_test.py -v
```

### Frontend (depuis `frontend/`)

```bash
# Développement
npm run dev

# Build production
npm run build

# Lint
npm run lint
```

### Docker (depuis la racine)

```bash
# Démarrer tous les services
docker-compose up

# Démarrer en arrière-plan
docker-compose up -d

# Voir les logs
docker-compose logs -f api

# Arrêter
docker-compose down
```

## Support

- **Issues GitHub**: Pour les bugs et suggestions
- **Documentation**: Dans le dossier `docs/`
- **Code source**: Commente en francais
