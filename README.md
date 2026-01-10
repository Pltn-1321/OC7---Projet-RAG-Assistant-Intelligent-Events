# 🎭 RAG Events Assistant - Assistant Intelligent Événements

Assistant conversationnel intelligent basé sur RAG (Retrieval-Augmented Generation) pour découvrir des événements culturels via des questions en langage naturel.

**Stack**: Streamlit + LangChain + Mistral AI + FAISS + Python 3.11+

---

## 📋 Vue d'ensemble

Ce projet implémente un chatbot RAG qui :
- 🔍 Récupère des événements culturels depuis l'API Open Agenda
- 🧠 Indexe les événements avec des embeddings vectoriels (FAISS)
- 💬 Répond à des questions en langage naturel via Mistral AI
- 🎨 Propose une interface Streamlit intuitive
- 🌐 Expose une API REST (optionnel)

### Métriques cibles
- ✅ Pertinence réponses > 80%
- ✅ Temps de réponse < 3 secondes
- ✅ Couverture questions > 70%

---

## 🚀 Démarrage rapide

### Prérequis

- Python 3.11 ou supérieur
- [uv](https://github.com/astral-sh/uv) (gestionnaire de paquets moderne)
- Clé API Mistral AI ([obtenir ici](https://console.mistral.ai/))
- Clé API Open Agenda (optionnel, [obtenir ici](https://openagenda.com/))

### Installation

1. **Cloner le repository**
```bash
git clone <repository-url>
cd OC7---Projet-RAG-Assistant-Intelligent-Events
```

2. **Installer uv** (si pas déjà installé)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# ou avec Homebrew
brew install uv
```

3. **Créer le fichier .env**
```bash
cp .env.example .env
# Éditer .env et ajouter vos clés API
```

4. **Installer les dépendances**
```bash
# Installation complète (dev + api)
uv sync --extra dev --extra api

# Ou seulement les dépendances principales
uv sync
```

5. **Vérifier l'installation**
```bash
uv run python -c "import langchain; import faiss; import streamlit; print('✅ Installation OK')"
```

---

## 📊 Structure du projet

```
.
├── src/                        # Code source (pattern src-layout)
│   ├── config/                 # Configuration
│   │   ├── settings.py         # Paramètres (Pydantic)
│   │   └── constants.py        # Constantes
│   ├── data/                   # Accès données
│   │   ├── models.py           # Modèles Pydantic
│   │   ├── fetcher.py          # Client API Open Agenda
│   │   └── preprocessor.py     # Nettoyage données
│   ├── rag/                    # Logique RAG
│   │   ├── chatbot.py          # Orchestrateur principal
│   │   ├── retriever.py        # Recherche vectorielle
│   │   ├── generator.py        # Génération LLM
│   │   ├── embeddings.py       # Gestion embeddings
│   │   ├── prompts.py          # Templates prompts
│   │   └── index_manager.py    # Opérations FAISS
│   ├── api/                    # API REST (FastAPI)
│   ├── ui/                     # Composants UI
│   └── utils/                  # Utilitaires
│
├── scripts/                    # Scripts autonomes
│   ├── fetch_events.py         # Récupération événements
│   ├── build_index.py          # Construction index FAISS
│   └── evaluate_rag.py         # Évaluation système
│
├── tests/                      # Tests (unit/integration/e2e)
├── data/                       # Données (non versionné)
├── docs/                       # Documentation
├── notebooks/                  # Notebooks Jupyter
└── app.py                      # Application Streamlit
```

---

## 🎯 Utilisation

### 1. Récupérer les événements

```bash
uv run python scripts/fetch_events.py --location paris --max-events 1000
```

### 2. Construire l'index vectoriel

```bash
uv run python scripts/build_index.py --input data/processed/events.json
```

### 3. Lancer l'application Streamlit

```bash
uv run streamlit run app.py
```

Accéder à l'interface : [http://localhost:8501](http://localhost:8501)

### 4. Lancer l'API REST (optionnel)

```bash
uv run uvicorn src.api.main:app --reload
```

Documentation API : [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Tests

### Exécuter tous les tests
```bash
uv run pytest
```

### Tests avec couverture
```bash
uv run pytest --cov=src --cov-report=html
```

### Tests spécifiques
```bash
# Tests unitaires uniquement
uv run pytest tests/unit/

# Tests d'intégration
uv run pytest tests/integration/ -m integration

# Exclure les tests lents
uv run pytest -m "not slow"
```

### Évaluation du système RAG
```bash
uv run python scripts/evaluate_rag.py --test-file tests/data/test_questions.json
```

---

## 🐳 Docker

### Build et run avec Docker Compose

```bash
# Construire et démarrer
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

### Build manuel

```bash
# Construire l'image
docker build -t rag-events-assistant .

# Exécuter le container
docker run -p 8501:8501 \
  -e MISTRAL_API_KEY=$MISTRAL_API_KEY \
  -v $(pwd)/data:/app/data \
  rag-events-assistant
```

---

## ⚙️ Configuration

Toutes les configurations se font via le fichier `.env`. Voir `.env.example` pour la liste complète des variables.

### Variables principales

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `MISTRAL_API_KEY` | Clé API Mistral AI | **Requis** |
| `OPENAGENDA_API_KEY` | Clé API Open Agenda | Optionnel |
| `EMBEDDING_MODEL` | Modèle d'embeddings | `all-MiniLM-L6-v2` |
| `LLM_MODEL` | Modèle Mistral | `mistral-small-latest` |
| `LLM_TEMPERATURE` | Température LLM | `0.3` |
| `TOP_K_RESULTS` | Nombre de résultats | `5` |
| `LOG_LEVEL` | Niveau de logging | `INFO` |

---

## 🛠️ Développement

### Installation des outils de développement

```bash
uv sync --extra dev
```

### Linting et formatage

```bash
# Formatter le code avec Black
uv run black src tests scripts

# Linting avec Ruff
uv run ruff check src tests scripts

# Type checking avec mypy
uv run mypy src
```

### Pre-commit hooks

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

### Jupyter notebooks

```bash
# Lancer JupyterLab
uv run jupyter lab

# Ou Jupyter Notebook
uv run jupyter notebook
```

---

## 📚 Documentation

- [Architecture](docs/architecture.md) - Architecture système
- [API Reference](docs/api_reference.md) - Documentation API
- [Deployment](docs/deployment.md) - Guide de déploiement
- [Troubleshooting](docs/troubleshooting.md) - Résolution de problèmes
- [Guide complet](Guide%20complet%20projet%20RAG.md) - Guide détaillé du projet

---

## 🎯 Roadmap

### Phase 1: MVP (Semaines 1-2) ✅
- [x] Structure du projet
- [ ] Pipeline de données
- [ ] Système RAG de base
- [ ] Interface Streamlit
- [ ] Tests et évaluation

### Phase 2: Amélioration (Semaines 3-4)
- [ ] Optimisation performances
- [ ] API REST complète
- [ ] Tests end-to-end
- [ ] Documentation complète
- [ ] Déploiement

### Phase 3: Extensions (Futur)
- [ ] Support multi-villes
- [ ] Filtres avancés
- [ ] Personnalisation utilisateur
- [ ] Historique conversations
- [ ] Système de réservation

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📝 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- [Mistral AI](https://mistral.ai/) - LLM
- [LangChain](https://python.langchain.com/) - Framework RAG
- [Open Agenda](https://openagenda.com/) - Données événements
- [FAISS](https://github.com/facebookresearch/faiss) - Recherche vectorielle
- [Streamlit](https://streamlit.io/) - Interface web

---

## 📧 Contact

Pierre - [GitHub](https://github.com/ppluton)

Lien du projet: [https://github.com/ppluton/OC7---Projet-RAG-Assistant-Intelligent-Events](https://github.com/ppluton/OC7---Projet-RAG-Assistant-Intelligent-Events)
