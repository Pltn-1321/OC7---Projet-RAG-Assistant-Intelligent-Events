# Guide de Demarrage Rapide

Ce guide vous accompagne dans l'installation et le premier lancement du RAG Events Assistant.

## Prerequis

### Systeme

- **Python**: 3.11 ou superieur
- **Systeme d'exploitation**: Linux, macOS, ou Windows (WSL2 recommande)
- **RAM**: Minimum 4 Go (8 Go recommande)
- **Espace disque**: 2 Go pour les donnees et index

### Comptes et Cles API

- **Cle API Mistral**: Obligatoire pour le LLM et les embeddings
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

### 3. Installer les Dependances

```bash
# Installation de base
uv sync

# Avec outils de developpement
uv sync --extra dev

# Avec API FastAPI
uv sync --extra api

# Avec evaluation RAGAS
uv sync --extra evaluation

# Tout installer
uv sync --all-extras
```

### 4. Configurer les Variables d'Environnement

Creer un fichier `.env` a la racine du projet:

```bash
# Copier le template
cp .env.example .env

# Editer avec votre editeur
nano .env  # ou code .env, vim .env, etc.
```

**Contenu minimum du fichier `.env`**:
```env
# Obligatoire
MISTRAL_API_KEY=votre_cle_mistral_ici

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

### Option 1: Interface Streamlit (Recommande)

```bash
uv run streamlit run app.py
```

Ouvrez votre navigateur a: http://localhost:8501

### Option 2: API FastAPI

```bash
uv run uvicorn src.api.main:app --reload
```

- API: http://localhost:8000
- Documentation Swagger: http://localhost:8000/docs
- Documentation ReDoc: http://localhost:8000/redoc

### Option 3: Docker

```bash
# Construire l'image
docker-compose build

# Demarrer les services
docker-compose up -d

# Voir les logs
docker-compose logs -f
```

- API: http://localhost:8000
- Streamlit: http://localhost:8501

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

```bash
# Lancer les tests
uv run pytest

# Formater le code
uv run black src tests scripts
uv run ruff check src tests scripts

# Evaluation RAG
uv run python scripts/evaluate_rag.py

# Test API interactif
uv run python scripts/api_test.py -v
```

## Support

- **Issues GitHub**: Pour les bugs et suggestions
- **Documentation**: Dans le dossier `docs/`
- **Code source**: Commente en francais
