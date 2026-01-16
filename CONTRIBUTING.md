# 🤝 Guide de Contribution

Merci de votre intérêt pour contribuer au **RAG Events Assistant** ! Ce document vous guidera à travers le processus de contribution.

## 📋 Table des Matières

- [Code de Conduite](#code-de-conduite)
- [Comment Contribuer](#comment-contribuer)
- [Configuration de l'Environnement](#configuration-de-lenvironnement)
- [Standards de Code](#standards-de-code)
- [Processus de Pull Request](#processus-de-pull-request)
- [Types de Contributions](#types-de-contributions)
- [Signaler des Bugs](#signaler-des-bugs)
- [Proposer des Fonctionnalités](#proposer-des-fonctionnalités)

---

## 📜 Code de Conduite

### Notre Engagement

Dans l'intérêt de favoriser un environnement ouvert et accueillant, nous nous engageons à faire de la participation à notre projet une expérience sans harcèlement pour tous.

### Comportements Attendus

- Utiliser un langage accueillant et inclusif
- Respecter les points de vue et expériences différents
- Accepter gracieusement les critiques constructives
- Se concentrer sur ce qui est meilleur pour la communauté
- Faire preuve d'empathie envers les autres membres

### Comportements Inacceptables

- Commentaires insultants/désobligeants et attaques personnelles
- Harcèlement public ou privé
- Publication d'informations privées sans permission
- Autre conduite inappropriée dans un cadre professionnel

---

## 🚀 Comment Contribuer

### 1. Fork le Repository

```bash
# Cliquer sur "Fork" sur GitHub
# Puis cloner votre fork
git clone https://github.com/votre-username/OC7---Projet-RAG-Assistant-Intelligent-Events.git
cd OC7---Projet-RAG-Assistant-Intelligent-Events

# Ajouter le repo original comme upstream
git remote add upstream https://github.com/original-owner/OC7---Projet-RAG-Assistant-Intelligent-Events.git
```

### 2. Créer une Branche

Utilisez des noms de branches descriptifs :

```bash
# Pour une nouvelle fonctionnalité
git checkout -b feature/nom-de-la-fonctionnalite

# Pour un bug fix
git checkout -b fix/description-du-bug

# Pour de la documentation
git checkout -b docs/description-de-la-doc

# Pour du refactoring
git checkout -b refactor/description
```

### 3. Faire vos Modifications

Consultez les sections [Configuration](#configuration-de-lenvironnement) et [Standards](#standards-de-code) ci-dessous.

### 4. Tester vos Modifications

```bash
# Exécuter les tests
uv run pytest

# Vérifier la couverture
uv run pytest --cov=src --cov-report=html

# Formatter le code
uv run black src tests scripts

# Linter
uv run ruff check src tests scripts

# Type checking
uv run mypy src
```

### 5. Committer

Utilisez des messages de commit clairs suivant la convention [Conventional Commits](https://www.conventionalcommits.org/) :

```bash
# Format
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types :**
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation seulement
- `style`: Changements qui n'affectent pas le sens du code (espaces, formatage)
- `refactor`: Changement de code qui ne corrige pas de bug ni n'ajoute de fonctionnalité
- `perf`: Amélioration de performance
- `test`: Ajout de tests manquants
- `chore`: Changements aux outils de build ou dépendances

**Exemples :**

```bash
git commit -m "feat(rag): add multi-language support for embeddings"
git commit -m "fix(api): correct session memory leak in /chat endpoint"
git commit -m "docs(readme): update installation instructions for Docker"
git commit -m "test(engine): add unit tests for query classification"
```

### 6. Pousser et Créer une PR

```bash
# Pousser vers votre fork
git push origin feature/nom-de-la-fonctionnalite

# Aller sur GitHub et créer une Pull Request
```

---

## ⚙️ Configuration de l'Environnement

### Prérequis

- **Python 3.11+**
- **uv** (gestionnaire de paquets)
- **Git**
- **Clé API Mistral AI** (pour les tests d'intégration)

### Installation

```bash
# 1. Installer uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Installer les dépendances (toutes les extras)
uv sync --all-extras

# 3. Configurer l'environnement
cp .env.example .env
# Éditer .env et ajouter votre MISTRAL_API_KEY

# 4. Installer les pre-commit hooks
uv run pre-commit install

# 5. Préparer les données de test
uv run jupyter lab  # Exécuter notebooks 01-04
```

### Structure du Projet

Familiarisez-vous avec l'architecture :

```
src/
├── config/          # Configuration (settings.py, constants.py)
├── data/            # Modèles Pydantic (models.py)
├── rag/             # Moteur RAG (engine.py, index_builder.py)
└── api/             # API REST (main.py)

tests/
├── unit/            # Tests unitaires
├── integration/     # Tests d'intégration
└── e2e/             # Tests end-to-end

docs/                # Documentation
notebooks/           # Jupyter notebooks pour pipeline de données
scripts/             # Scripts utilitaires
```

---

## 📏 Standards de Code

### Style Python

Nous suivons les conventions Python modernes :

#### Formatage

- **Black** pour le formatage automatique (line length: 100)
- **Ruff** pour le linting
- **mypy** pour le type checking

```bash
# Formatter automatiquement
uv run black src tests scripts

# Vérifier le style
uv run ruff check src tests scripts

# Vérifier les types
uv run mypy src
```

#### Type Hints

Utilisez la syntaxe Python 3.11+ :

```python
# ✅ CORRECT
def process_events(events: list[Event]) -> dict[str, Any]:
    results: dict[str, list[str]] = {}
    return results

# ❌ INCORRECT (ancienne syntaxe)
from typing import List, Dict, Any
def process_events(events: List[Event]) -> Dict[str, Any]:
    ...
```

#### Docstrings

Utilisez le style Google :

```python
def search(self, query: str, top_k: int = 5) -> list[dict]:
    """Search for events matching the query.

    Args:
        query: User search query in natural language
        top_k: Number of top results to return

    Returns:
        List of event dictionaries with scores

    Raises:
        ValueError: If query is empty or top_k is invalid
        IndexError: If FAISS index is not loaded

    Example:
        >>> results = engine.search("concerts jazz Paris", top_k=3)
        >>> len(results)
        3
    """
    ...
```

#### Naming Conventions

- **Variables/Fonctions** : `snake_case`
- **Classes** : `PascalCase`
- **Constantes** : `UPPER_SNAKE_CASE`
- **Modules** : `snake_case.py`
- **Privé** : `_leading_underscore`

```python
# ✅ CORRECT
class EventChatbot:
    MAX_HISTORY = 5

    def __init__(self):
        self._index = None

    def search_events(self, query: str) -> list[Event]:
        ...
```

### Organisation du Code

#### Imports

Organisez les imports dans l'ordre :

1. Standard library
2. Third-party packages
3. Local imports

```python
# Standard library
import json
from pathlib import Path
from typing import Any

# Third-party
import faiss
import numpy as np
from mistralai import Mistral

# Local
from src.config.settings import settings
from src.data.models import Event
```

#### Structure des Fonctions

- Limiter à ~50 lignes par fonction
- Une fonction = une responsabilité
- Extraire la logique complexe dans des fonctions helper

```python
# ✅ CORRECT - Fonction focused
def classify_query(self, query: str) -> str:
    """Classify query as CHAT or SEARCH."""
    return self._detect_search_intent(query)

def _detect_search_intent(self, query: str) -> str:
    """Internal logic for intent detection."""
    # Complex logic here
    ...

# ❌ INCORRECT - Fonction trop longue et complexe
def process_query(self, query: str) -> dict:
    # 150 lignes de code mélangées...
    ...
```

---

## 🧪 Tests

### Écrire des Tests

Chaque contribution doit inclure des tests :

#### Tests Unitaires (`tests/unit/`)

```python
# tests/unit/test_engine.py
import pytest
from src.rag.engine import RAGEngine

def test_needs_rag_detects_search_queries():
    """Test query classification for search queries."""
    engine = RAGEngine()

    # Test cases
    assert engine.needs_rag("concerts jazz Paris") == "SEARCH"
    assert engine.needs_rag("événements gratuits ce weekend") == "SEARCH"
    assert engine.needs_rag("Bonjour") == "CHAT"
    assert engine.needs_rag("Merci !") == "CHAT"
```

#### Tests d'Intégration (`tests/integration/`)

```python
# tests/integration/test_api.py
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_search_endpoint_returns_results():
    """Test /search endpoint with real RAG engine."""
    response = client.post(
        "/search",
        json={"query": "concerts Paris", "top_k": 3}
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["sources"]) <= 3
```

### Exécuter les Tests

```bash
# Tous les tests
uv run pytest

# Tests spécifiques
uv run pytest tests/unit/test_engine.py
uv run pytest tests/integration/

# Avec couverture
uv run pytest --cov=src --cov-report=term-missing

# Exclure tests lents
uv run pytest -m "not slow"

# Verbose
uv run pytest -v
```

### Couverture de Code

Visez une couverture > 70% pour le nouveau code :

```bash
# Générer rapport HTML
uv run pytest --cov=src --cov-report=html

# Ouvrir dans navigateur
open htmlcov/index.html
```

---

## 🔄 Processus de Pull Request

### Checklist Avant Soumission

- [ ] Le code suit les [standards de style](#standards-de-code)
- [ ] Tous les tests passent (`uv run pytest`)
- [ ] Couverture de code adéquate (> 70% pour nouveau code)
- [ ] Documentation mise à jour (docstrings, README, CLAUDE.md si nécessaire)
- [ ] Pas de warnings lors du linting (`uv run ruff check`)
- [ ] Type hints vérifiés (`uv run mypy src`)
- [ ] Commit messages suivent [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] Pas de secrets ou clés API committés

### Description de la PR

Utilisez ce template :

```markdown
## Description
[Description claire de ce que fait la PR]

## Type de Changement
- [ ] Bug fix (non-breaking change qui corrige un problème)
- [ ] Nouvelle fonctionnalité (non-breaking change qui ajoute une fonctionnalité)
- [ ] Breaking change (fix ou feature qui causerait un dysfonctionnement de fonctionnalités existantes)
- [ ] Documentation

## Tests
- [ ] Tests unitaires ajoutés/mis à jour
- [ ] Tests d'intégration ajoutés/mis à jour
- [ ] Tous les tests passent

## Checklist
- [ ] Code suit les standards du projet
- [ ] Auto-review effectuée
- [ ] Documentation mise à jour
- [ ] Pas de warnings
```

### Revue de Code

Attendez-vous à :
- Questions sur les choix de design
- Suggestions d'amélioration
- Demandes de tests supplémentaires
- Discussions sur les impacts

**Soyez patient et ouvert aux retours !**

---

## 📝 Types de Contributions

### 🐛 Bug Fixes

1. Vérifier qu'une issue n'existe pas déjà
2. Créer une issue si nécessaire
3. Créer branche `fix/description-du-bug`
4. Ajouter tests reproduisant le bug
5. Corriger le bug
6. Vérifier que les tests passent
7. Soumettre PR

### ✨ Nouvelles Fonctionnalités

1. Discuter dans une issue d'abord (évite le travail inutile)
2. Attendre validation des mainteneurs
3. Créer branche `feature/nom-fonctionnalite`
4. Implémenter avec tests
5. Mettre à jour documentation
6. Soumettre PR

### 📚 Documentation

- Améliorer README.md
- Ajouter/améliorer docstrings
- Créer/améliorer guides dans `docs/`
- Ajouter exemples dans notebooks
- Corriger typos

### 🧪 Tests

- Augmenter couverture de code
- Ajouter tests edge cases
- Améliorer fixtures existants
- Ajouter tests de performance

### 🌍 Traductions

- Traduire documentation en anglais/autres langues
- Traduire messages d'erreur
- Support multi-langue dans UI

---

## 🐞 Signaler des Bugs

### Avant de Signaler

1. Vérifier les [issues existantes](https://github.com/votre-username/OC7---Projet-RAG-Assistant-Intelligent-Events/issues)
2. Vérifier avec la dernière version
3. Vérifier les logs et messages d'erreur

### Template d'Issue Bug

```markdown
## Description du Bug
[Description claire et concise du bug]

## Comment Reproduire
1. Aller à '...'
2. Cliquer sur '...'
3. Scroller vers '...'
4. Voir l'erreur

## Comportement Attendu
[Ce qui devrait se passer]

## Comportement Actuel
[Ce qui se passe réellement]

## Screenshots
[Si applicable]

## Environnement
- OS: [ex. macOS 14.0]
- Python: [ex. 3.11.5]
- Version du Projet: [ex. commit hash ou version]

## Logs
```
[Coller les logs pertinents]
```

## Contexte Additionnel
[Tout autre contexte pertinent]
```

---

## 💡 Proposer des Fonctionnalités

### Template d'Issue Feature Request

```markdown
## Problème à Résoudre
[Quel problème cette feature résoudrait-elle?]

## Solution Proposée
[Comment vous imaginez la solution]

## Alternatives Considérées
[Autres approches possibles]

## Contexte Additionnel
[Tout autre contexte, screenshots, exemples, etc.]

## Impact
- [ ] Utilisateurs finaux
- [ ] Développeurs
- [ ] Performance
- [ ] Documentation
```

---

## 🎓 Ressources pour Contribuer

### Documentation Projet

- [README.md](README.md) - Vue d'ensemble
- [CLAUDE.md](CLAUDE.md) - Instructions Claude Code
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architecture détaillée
- [docs/COMPRENDRE_LE_RAG.md](docs/COMPRENDRE_LE_RAG.md) - Concepts RAG

### Outils et Standards

- [Black](https://black.readthedocs.io/) - Code formatter
- [Ruff](https://docs.astral.sh/ruff/) - Linter
- [mypy](https://mypy.readthedocs.io/) - Type checker
- [pytest](https://docs.pytest.org/) - Testing framework
- [Conventional Commits](https://www.conventionalcommits.org/) - Commit conventions

### Technologies Clés

- [Mistral AI Docs](https://docs.mistral.ai/) - LLM et embeddings
- [FAISS](https://github.com/facebookresearch/faiss/wiki) - Vector search
- [FastAPI](https://fastapi.tiangolo.com/) - API framework
- [Streamlit](https://docs.streamlit.io/) - UI framework
- [Pydantic](https://docs.pydantic.dev/) - Data validation

---

## ❓ Questions

Si vous avez des questions :

1. Consultez la [documentation](docs/)
2. Cherchez dans les [issues existantes](https://github.com/votre-username/OC7---Projet-RAG-Assistant-Intelligent-Events/issues)
3. Créez une [nouvelle discussion](https://github.com/votre-username/OC7---Projet-RAG-Assistant-Intelligent-Events/discussions)

---

## 🙏 Remerciements

Merci d'avoir pris le temps de contribuer ! Chaque contribution, petite ou grande, fait une différence. 🎉

---

<div align="center">

**Fait avec ❤️ par la communauté**

[⬆ Retour en haut](#-guide-de-contribution)

</div>
