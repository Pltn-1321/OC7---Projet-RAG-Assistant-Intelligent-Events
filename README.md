# 🎭 RAG Events Assistant

Assistant conversationnel intelligent pour découvrir des événements culturels via des questions en langage naturel.

**Stack** : Python 3.11+ | Streamlit | FAISS | Mistral AI | FastAPI

---

## 🎯 Fonctionnalités

- 💬 **Chatbot conversationnel** avec mémoire (5 derniers échanges)
- 🧠 **Détection intelligente** : distingue conversation simple vs recherche d'événements
- 🔍 **Recherche sémantique** via embeddings Mistral + FAISS
- 🎨 **Interface moderne** Streamlit avec thème sombre
- 🌐 **API REST** FastAPI avec gestion de sessions

---

## 🚀 Démarrage rapide

### Prérequis

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- Clé API [Mistral AI](https://console.mistral.ai/)

### Installation

```bash
# Cloner le repo
git clone <repository-url>
cd OC7---Projet-RAG-Assistant-Intelligent-Events

# Installer les dépendances
uv sync --all-extras

# Configurer l'environnement
cp .env.example .env
# Ajouter MISTRAL_API_KEY dans .env
```

### Préparer les données

Exécuter les notebooks dans l'ordre :

```bash
uv run jupyter lab
```

1. `01_data_collection.ipynb` - Récupération des événements
2. `02_data_preprocessing.ipynb` - Nettoyage des données
3. `03_create_embeddings.ipynb` - Création des embeddings
4. `04_build_faiss_index.ipynb` - Construction de l'index FAISS

### Lancer l'application

```bash
# Interface Streamlit
uv run streamlit run app.py

# API REST
uv run uvicorn src.api.main:app --reload
```

- Streamlit : http://localhost:8501
- API docs : http://localhost:8000/docs

---

## 📁 Structure

```
├── app.py                  # Chatbot Streamlit
├── src/
│   ├── config/
│   │   ├── settings.py     # Configuration (Pydantic Settings)
│   │   └── constants.py    # Constantes
│   ├── rag/
│   │   └── engine.py       # Moteur RAG (recherche + génération)
│   └── api/
│       └── main.py         # API FastAPI
├── notebooks/              # Préparation des données
├── data/
│   └── processed/          # Index FAISS + documents
└── tests/
```

---

## 🔌 API Endpoints

| Méthode  | Endpoint        | Description          |
| -------- | --------------- | -------------------- |
| `GET`    | `/health`       | État de l'API        |
| `POST`   | `/search`       | Recherche sémantique |
| `POST`   | `/chat`         | Chat avec mémoire    |
| `GET`    | `/session/{id}` | Historique session   |
| `DELETE` | `/session/{id}` | Effacer session      |

### Exemple

```bash
# Premier message (crée une session)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "concerts jazz à Paris"}'

# Continuer la conversation
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "et à Marseille ?", "session_id": "<id-retourné>"}'
```

---

## ⚙️ Configuration

Variables d'environnement (`.env`) :

| Variable             | Description                          | Défaut                 |
| -------------------- | ------------------------------------ | ---------------------- |
| `MISTRAL_API_KEY`    | Clé API Mistral                      | **Requis**             |
| `EMBEDDING_PROVIDER` | `mistral` ou `sentence-transformers` | `mistral`              |
| `LLM_MODEL`          | Modèle LLM                           | `mistral-small-latest` |
| `LLM_TEMPERATURE`    | Température                          | `0.7`                  |
| `TOP_K_RESULTS`      | Résultats par recherche              | `5`                    |

---

## 🧪 Tests

```bash
# Tous les tests
uv run pytest

# Avec couverture
uv run pytest --cov=src --cov-report=html
```

---

## 🛠️ Développement

```bash
# Formatage
uv run black src tests

# Linting
uv run ruff check src tests

# Type checking
uv run mypy src
```

---

## 📝 License

MIT

## TO DO

- Gerer l'application contre les Injection SQL
- Gerer le build
- Un endpoint/rebuild(GET ou POST) pour reconstruire la base vectorielle à la demande
- Une documentation Swagger générée automatiquement (si FastAPI est utilisé)
- Implementation de Ragas
- Un test fonctionnel de l’API dans un script ou fichierapi_test.py
- Creer les test unitaire et fonctionnels
- comprendre Flask et voir les differences pour implementation
