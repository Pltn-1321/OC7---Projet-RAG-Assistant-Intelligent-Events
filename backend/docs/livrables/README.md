# 📦 Livrables - RAG Events Assistant

> **Documentation complète du projet** — Assistant conversationnel intelligent pour la découverte d'événements culturels

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev/)
[![LangChain](https://img.shields.io/badge/LangChain-LCEL-blueviolet.svg)](https://python.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🔗 Dépôt GitHub

**Repository officiel** : [https://github.com/Pltn-1321/OC7---Projet-RAG-Assistant-Intelligent-Events](https://github.com/Pltn-1321/OC7---Projet-RAG-Assistant-Intelligent-Events)

---

## 📋 Contenu du Package

Ce package contient l'ensemble des livrables du projet **RAG Events Assistant**, un système d'IA conversationnelle utilisant la technique RAG (Retrieval-Augmented Generation) pour recommander des événements culturels.

### 📄 Documents Principaux

1. **[01-RAPPORT-TECHNIQUE.md](01-RAPPORT-TECHNIQUE.md)**
   - Architecture complète du système
   - Choix techniques et justifications
   - Pipeline RAG détaillé avec LangChain LCEL
   - Intégration Mistral AI et FAISS

2. **[02-GUIDE-UTILISATION.md](02-GUIDE-UTILISATION.md)**
   - Installation et configuration (Docker + Local)
   - Guide utilisateur Frontend React et Streamlit
   - Exemples d'utilisation et requêtes
   - Résolution de problèmes courants

3. **[03-DOCUMENTATION-API.md](03-DOCUMENTATION-API.md)**
   - API REST FastAPI complète
   - Endpoints détaillés avec exemples
   - Schémas de requêtes/réponses
   - Codes d'erreur et gestion

4. **[04-RESULTATS-EVALUATION.md](04-RESULTATS-EVALUATION.md)**
   - Métriques RAGAS (Faithfulness, Relevance, Context Recall)
   - Analyse des performances
   - Benchmarks de latence
   - Recommandations d'amélioration

5. **[05-TESTS-ET-QUALITE.md](05-TESTS-ET-QUALITE.md)**
   - Stratégie de tests (unitaires, intégration, e2e)
   - Couverture de code (>80%)
   - Standards de qualité (Black, Ruff, mypy)
   - CI/CD avec GitHub Actions

6. **[ARCHITECTURE.md](ARCHITECTURE.md)**
   - Vision d'ensemble du système
   - Diagrammes d'architecture
   - Flux de données et interactions
   - Décisions architecturales

### 📁 Annexes

- **[annexes/](annexes/)** : Documentation complémentaire
  - Améliorations futures
  - Architecture complète détaillée
  - Justifications des choix technologiques
  - Schémas ASCII du système

- **[donnees-evaluation/](donnees-evaluation/)** : Résultats d'évaluation
  - Jeu de questions annotées
  - Exemples de réponses générées
  - Rapports de couverture de tests
  - Résultats JSON d'évaluation RAGAS

- **[presentation/](presentation/)** : Présentation PowerPoint du projet

---

## 🎯 Projet : RAG Events Assistant

### Caractéristiques Principales

- **🔍 Recherche Sémantique** : FAISS + Mistral embeddings (1024 dimensions)
- **🤖 Classification Intelligente** : Détection automatique CHAT vs SEARCH
- **💬 Mémoire Conversationnelle** : Gestion de sessions avec PostgreSQL
- **🎨 Interface Moderne** : React + TypeScript + shadcn/ui
- **⚡ API Performante** : FastAPI asynchrone avec validation Pydantic
- **🔧 Pipeline Modulaire** : Orchestration LangChain LCEL

### Technologies Utilisées

#### Backend
- **Python 3.11+** avec gestionnaire de packages **uv**
- **LangChain LCEL** pour l'orchestration RAG
- **Mistral AI** (LLM + Embeddings)
- **FAISS** pour le stockage vectoriel
- **FastAPI** pour l'API REST
- **PostgreSQL** + **Alembic** pour la persistance
- **Streamlit** pour l'interface alternative

#### Frontend
- **React 18+** avec **TypeScript**
- **Vite** comme build tool
- **Tailwind CSS** + **shadcn/ui** pour le design
- **Zustand** pour la gestion d'état

#### DevOps
- **Docker** + **Docker Compose** pour la conteneurisation
- **GitHub Actions** pour CI/CD
- **Render.com** pour le déploiement
- **RAGAS** pour l'évaluation du RAG

---

## 🚀 Démarrage Rapide

### Option 1 : Docker (Recommandé)

```bash
# Cloner le repository
git clone https://github.com/Pltn-1321/OC7---Projet-RAG-Assistant-Intelligent-Events.git
cd OC7---Projet-RAG-Assistant-Intelligent-Events

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et ajouter votre MISTRAL_API_KEY

# Démarrer les services
docker-compose up
```

**URLs** :
- Frontend React : http://localhost:3000
- API FastAPI : http://localhost:8000
- Streamlit : http://localhost:8501

### Option 2 : Installation Locale

#### Backend

```bash
cd backend

# Installer uv (si nécessaire)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Installer les dépendances
uv sync --all-extras

# Lancer l'API
uv run uvicorn src.api.main:app --reload
```

#### Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev
```

---

## 📖 Documentation Complète

Pour plus d'informations, consultez :
- **[README.md](https://github.com/Pltn-1321/OC7---Projet-RAG-Assistant-Intelligent-Events/blob/main/README.md)** principal du projet
- **[backend/README.md](https://github.com/Pltn-1321/OC7---Projet-RAG-Assistant-Intelligent-Events/blob/main/backend/README.md)** pour la documentation backend complète
- **[frontend/README.md](https://github.com/Pltn-1321/OC7---Projet-RAG-Assistant-Intelligent-Events/blob/main/frontend/README.md)** pour la documentation frontend

---

## 👥 Auteur

**Projet académique** - OpenClassrooms - Parcours Data Scientist
**Promotion** : 2024-2026

---

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](https://github.com/Pltn-1321/OC7---Projet-RAG-Assistant-Intelligent-Events/blob/main/LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- **OpenClassrooms** pour le cadre pédagogique
- **Mistral AI** pour l'API LLM et embeddings
- **LangChain** pour le framework RAG
- **Open Agenda** pour les données d'événements culturels

---

**📦 Package généré le** : 2026-02-04
**📍 Version** : 1.0.0
**🔗 Repository** : [GitHub](https://github.com/Pltn-1321/OC7---Projet-RAG-Assistant-Intelligent-Events)
