# RAG Events Assistant

> Découvrez des événements culturels grâce à un assistant conversationnel intelligent alimenté par le RAG

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)](https://www.typescriptlang.org/)
[![LangChain](https://img.shields.io/badge/LangChain-LCEL-blueviolet.svg)](https://python.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Présentation

**RAG Events Assistant** est un assistant conversationnel qui utilise la technique **RAG (Retrieval-Augmented Generation)** pour recommander des événements culturels de manière personnalisée.

Le système combine :
- **Recherche sémantique** via FAISS pour trouver des événements pertinents
- **LLM Mistral AI** pour générer des réponses conversationnelles en français
- **Classification intelligente** pour distinguer les questions de conversation des recherches d'événements

```
┌──────────────────────────────────────────────────────────┐
│                    ARCHITECTURE                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│   ┌─────────────┐         ┌─────────────┐               │
│   │  Frontend   │  HTTP   │   Backend   │               │
│   │   React     │◄───────►│   FastAPI   │               │
│   │ TypeScript  │         │   Python    │               │
│   └─────────────┘         └──────┬──────┘               │
│                                  │                       │
│                           ┌──────▼──────┐               │
│                           │  RAG Engine │               │
│                           │  LangChain  │               │
│                           └──────┬──────┘               │
│                                  │                       │
│                    ┌─────────────┼─────────────┐        │
│                    │             │             │        │
│              ┌─────▼─────┐ ┌─────▼─────┐ ┌────▼────┐   │
│              │   FAISS   │ │  Mistral  │ │ Session │   │
│              │  Vector   │ │    AI     │ │ Memory  │   │
│              │   Store   │ │    LLM    │ │         │   │
│              └───────────┘ └───────────┘ └─────────┘   │
│                                                          │
└──────────────────────────────────────────────────────────┘
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

## Démarrage Rapide

### Prérequis

- **Python 3.11+** et **uv** (backend)
- **Node.js 18+** et **npm** (frontend)
- **Clé API Mistral AI** ([console.mistral.ai](https://console.mistral.ai/))

### Installation

```bash
# Cloner le repository
git clone https://github.com/votre-username/OC7---Projet-RAG-Assistant-Intelligent-Events.git
cd OC7---Projet-RAG-Assistant-Intelligent-Events

# Backend
cd backend
uv sync --all-extras
cp .env.example .env  # Ajouter MISTRAL_API_KEY
cd ..

# Frontend
cd frontend
npm install
cp .env.example .env.local  # Configurer l'URL de l'API
cd ..
```

### Lancement

```bash
# Option 1: Docker Compose (recommandé)
docker-compose up

# Option 2: Développement local
# Terminal 1 - Backend API
cd backend && uv run uvicorn src.api.main:app --reload

# Terminal 2 - Frontend
cd frontend && npm run dev
```

**Services disponibles :**
| Service | URL | Description |
|---------|-----|-------------|
| Frontend React | http://localhost:5173 | Interface utilisateur moderne |
| API FastAPI | http://localhost:8000 | REST API + Swagger |
| Streamlit | http://localhost:8501 | Interface alternative |

---

## Documentation

| Document | Description |
|----------|-------------|
| [backend/README.md](backend/README.md) | Guide complet du backend Python |
| [backend/docs/](backend/docs/) | Architecture, API, guides techniques |
| [frontend/README.md](frontend/README.md) | Guide du frontend React |
| [frontend/docs/](frontend/docs/) | Composants, design system |

---

## Stack Technique

### Backend
- **LangChain LCEL** - Orchestration RAG
- **Mistral AI** - LLM + Embeddings
- **FAISS** - Vector store
- **FastAPI** - REST API
- **Streamlit** - Interface alternative
- **uv** - Package manager

### Frontend
- **React 18** - Framework UI
- **TypeScript** - Typage statique
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Composants

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

## Déploiement (Gratuit)

### Architecture de production

| Service | Plateforme | URL |
|---------|------------|-----|
| Backend API | **Render** | `https://rag-events-api.onrender.com` |
| Frontend | **Vercel** | `https://rag-events.vercel.app` |

### Déployer le Backend sur Render

1. Créer un compte sur [render.com](https://render.com)
2. **New > Web Service** > Connecter le repo GitHub
3. Configurer :
   - **Root Directory** : `backend`
   - **Runtime** : Docker
   - **Plan** : Free
4. Ajouter les variables d'environnement :
   - `MISTRAL_API_KEY` : Votre clé API Mistral

### Déployer le Frontend sur Vercel

1. Créer un compte sur [vercel.com](https://vercel.com)
2. **Import Project** > Sélectionner le repo GitHub
3. Configurer :
   - **Root Directory** : `frontend`
   - **Framework Preset** : Vite
4. Ajouter la variable d'environnement :
   - `VITE_API_URL` : URL de votre API Render (ex: `https://rag-events-api.onrender.com`)

### Note sur le Free Tier Render

Le plan gratuit met le service en veille après 15 min d'inactivité. La première requête peut prendre 30-60s (cold start).

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
