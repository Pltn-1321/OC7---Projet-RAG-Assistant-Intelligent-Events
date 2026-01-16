# Guide Pédagogique : Comprendre pyproject.toml

## Introduction

Le fichier `pyproject.toml` est le **fichier de configuration central** d'un projet Python moderne. Il remplace les anciens fichiers comme `setup.py`, `setup.cfg`, `requirements.txt`, et les configs séparées pour chaque outil.

**Format** : TOML (Tom's Obvious Minimal Language) - un format lisible par les humains, similaire à INI mais plus puissant.

```
┌─────────────────────────────────────────────────────────────┐
│                     pyproject.toml                          │
├─────────────────────────────────────────────────────────────┤
│  [project]           → Métadonnées du projet                │
│  [project.optional-dependencies] → Dépendances optionnelles │
│  [build-system]      → Comment construire le package        │
│  [tool.*]            → Configuration des outils (pytest...) │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Section [project] - Identité du Projet

```toml
[project]
name = "rag-events-assistant"      # Nom unique du package (pour pip/PyPI)
version = "0.1.0"                  # Version sémantique (MAJOR.MINOR.PATCH)
description = "RAG-based intelligent events discovery chatbot..."
readme = "README.md"               # Fichier description longue
requires-python = ">=3.11"         # Version Python minimale requise
license = {text = "MIT"}           # Licence open-source
```

### Explication des champs

| Champ             | Rôle                                               | Exemple                            |
| ----------------- | -------------------------------------------------- | ---------------------------------- |
| `name`            | Identifiant unique pour pip/PyPI                   | `pip install rag-events-assistant` |
| `version`         | Suivi des versions ([SemVer](https://semver.org/)) | `0.1.0` = version alpha            |
| `requires-python` | Empêche l'installation sur Python incompatible     | `>=3.11` exclut Python 3.10        |

### Versioning Sémantique (SemVer)

```
MAJOR.MINOR.PATCH
  │     │     │
  │     │     └── Corrections de bugs (compatible)
  │     └──────── Nouvelles fonctionnalités (compatible)
  └────────────── Changements incompatibles (breaking changes)

Exemples:
  0.1.0 → 0.1.1  : Bug fix
  0.1.0 → 0.2.0  : Nouvelle feature
  0.1.0 → 1.0.0  : API stable / breaking change
```

### Auteurs et Mots-clés

```toml
authors = [
    {name = "Pierre", email = "pierre.pluton@outlook.fr"}
]
keywords = ["rag", "llm", "chatbot", "events", "openagenda", "mistral", "langchain"]
```

- **authors** : Crédit et contact
- **keywords** : Améliore la recherche sur PyPI

### Classifiers PyPI

```toml
classifiers = [
    "Development Status :: 3 - Alpha",           # Niveau de maturité
    "Intended Audience :: Developers",           # Public cible
    "License :: OSI Approved :: MIT License",    # Type de licence
    "Programming Language :: Python :: 3.11",   # Versions supportées
]
```

Les classifiers sont des **tags standardisés** pour catégoriser le projet sur PyPI.
Liste complète : https://pypi.org/classifiers/

---

## 2. Section dependencies - Dépendances Principales

```toml
dependencies = [
    # Core RAG
    "langchain>=0.1.0,<0.2.0",
    "langchain-community>=0.0.20,<0.1.0",

    # Vector Store
    "faiss-cpu>=1.7.4,<2.0.0",

    # Interface
    "streamlit>=1.29.0,<2.0.0",
]
```

### Syntaxe des Versions

```
package>=1.0.0,<2.0.0
   │     │        │
   │     │        └── Version maximale (exclue)
   │     └────────── Version minimale (incluse)
   └──────────────── Nom du package

Opérateurs disponibles:
  ==1.0.0    Exactement cette version
  >=1.0.0    Cette version ou plus récente
  <=1.0.0    Cette version ou plus ancienne
  >1.0.0     Plus récent que cette version
  <1.0.0     Plus ancien que cette version
  ~=1.0.0    Compatible avec 1.0.x (équivalent >=1.0.0,<1.1.0)
  !=1.0.0    Toute version sauf celle-ci
```

### Pourquoi borner les versions ?

```toml
# ❌ RISQUÉ - Peut casser avec une mise à jour majeure
"langchain"

# ⚠️ MIEUX - Borne inférieure seulement
"langchain>=0.1.0"

# ✅ RECOMMANDÉ - Bornes inférieure ET supérieure
"langchain>=0.1.0,<0.2.0"
```

**Raison** : Les versions majeures (0.x → 1.x) peuvent introduire des **breaking changes** qui cassent votre code.

---

## 3. Section [project.optional-dependencies] - Dépendances Optionnelles

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.3,<8.0.0",      # Tests
    "black>=23.12.0,<24.0.0",    # Formatage
    "ruff>=0.1.8,<1.0.0",        # Linting
    "mypy>=1.8.0,<2.0.0",        # Type checking
]

api = [
    "fastapi>=0.109.0,<1.0.0",   # Framework API
    "uvicorn[standard]>=0.25.0", # Serveur ASGI
]

evaluation = [
    "ragas>=0.1.0,<1.0.0",       # Évaluation RAG
]

all = [
    "rag-events-assistant[dev,api,evaluation]",  # Tout inclus
]
```

### Comment les installer ?

```bash
# Dépendances principales uniquement
uv sync

# Avec les outils de développement
uv sync --extra dev

# Avec plusieurs extras
uv sync --extra dev --extra api

# Tout installer
uv sync --all-extras
# ou
uv sync --extra all
```

### Pourquoi séparer les dépendances ?

```
┌─────────────────────────────────────────────────────────────┐
│  Production (dependencies)                                  │
│  └── Minimum requis pour faire tourner l'application        │
│      langchain, faiss, streamlit, pydantic...              │
├─────────────────────────────────────────────────────────────┤
│  Développement (dev)                                        │
│  └── Outils pour développer, tester, formater              │
│      pytest, black, ruff, mypy, jupyter...                 │
├─────────────────────────────────────────────────────────────┤
│  API (api)                                                  │
│  └── Optionnel : serveur REST                              │
│      fastapi, uvicorn                                       │
├─────────────────────────────────────────────────────────────┤
│  Évaluation (evaluation)                                    │
│  └── Optionnel : métriques RAG                             │
│      ragas, datasets                                        │
└─────────────────────────────────────────────────────────────┘
```

**Avantage** : En production, on n'installe pas pytest, black, jupyter → image Docker plus légère !

---

## 4. Section [project.scripts] - Points d'Entrée CLI

```toml
[project.scripts]
rag-events = "src.rag.chatbot:main"
```

### Comment ça marche ?

```
rag-events = "src.rag.chatbot:main"
    │              │           │
    │              │           └── Fonction à exécuter
    │              └────────────── Module Python
    └────────────────────────────── Commande CLI créée
```

Après installation, vous pouvez exécuter :

```bash
uv run rag-events
# Équivalent à : uv run python -c "from src.rag.chatbot import main; main()"
```

---

## 5. Section [build-system] - Construction du Package

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

### Explication

| Champ           | Rôle                                          |
| --------------- | --------------------------------------------- |
| `requires`      | Outils nécessaires pour construire le package |
| `build-backend` | Quel système utiliser pour la construction    |

### Backends disponibles

```
setuptools.build_meta  → Standard, le plus répandu
flit_core.flit_core    → Simple, pour packages purs Python
hatchling.build        → Moderne, flexible
poetry.core.masonry.api → Utilisé par Poetry
maturin                 → Pour packages Rust+Python
```

### Configuration setuptools

```toml
[tool.setuptools.packages.find]
where = ["."]           # Chercher depuis la racine
include = ["src*"]      # Inclure seulement src/ et ses sous-packages
```

---

## 6. Section [tool.pytest] - Configuration des Tests

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]              # Où chercher les tests
python_files = "test_*.py"         # Pattern des fichiers de test
python_functions = "test_*"        # Pattern des fonctions de test
python_classes = "Test*"           # Pattern des classes de test
```

### Options par défaut (addopts)

```toml
addopts = [
    "-v",                    # Verbose : affiche chaque test
    "--tb=short",            # Traceback court en cas d'erreur
    "--strict-markers",      # Erreur si marker non déclaré
    "--cov=src",             # Mesure couverture du dossier src/
    "--cov-report=html",     # Génère rapport HTML
    "--cov-report=term-missing",  # Affiche lignes non couvertes
]
```

### Markers personnalisés

```toml
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "e2e: marks tests as end-to-end tests",
]
```

**Utilisation dans le code :**

```python
import pytest

@pytest.mark.slow
def test_full_indexation():
    """Test lent qui indexe 1000 événements"""
    ...

@pytest.mark.integration
def test_api_connection():
    """Test qui nécessite une connexion API réelle"""
    ...
```

**Exécution sélective :**

```bash
uv run pytest                      # Tous les tests
uv run pytest -m "not slow"        # Exclure les tests lents
uv run pytest -m integration       # Seulement les tests d'intégration
uv run pytest -m "not (slow or e2e)"  # Exclure slow ET e2e
```

---

## 7. Section [tool.black] - Formatage du Code

```toml
[tool.black]
line-length = 100                  # Longueur max des lignes
target-version = ['py311']         # Version Python cible
include = '\.pyi?$'                # Fichiers à formater (.py et .pyi)
extend-exclude = '''
/(
  \.venv
  | build
  | dist
)/
'''
```

### Avant/Après Black

```python
# Avant (code mal formaté)
def calculate_score(events,threshold,weights): return sum([e.score*w for e,w in zip(events,weights) if e.score>threshold])

# Après Black
def calculate_score(events, threshold, weights):
    return sum(
        [e.score * w for e, w in zip(events, weights) if e.score > threshold]
    )
```

**Commande :**

```bash
uv run black src tests scripts
```

---

## 8. Section [tool.ruff] - Linting Rapide

```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = [
    "E",   # Erreurs pycodestyle (ex: E501 ligne trop longue)
    "W",   # Warnings pycodestyle
    "F",   # Erreurs pyflakes (imports inutilisés, variables non définies)
    "I",   # Isort (ordre des imports)
    "C",   # Flake8-comprehensions (list comprehensions optimisées)
    "B",   # Flake8-bugbear (bugs potentiels)
    "UP",  # Pyupgrade (modernisation syntaxe Python)
]
```

### Règles ignorées

```toml
ignore = [
    "E501",  # Ligne trop longue → Black s'en charge
    "B008",  # Appel de fonction dans argument par défaut → Courant avec FastAPI
    "C901",  # Fonction trop complexe → Parfois nécessaire
]
```

### Ignorer des règles par fichier

```toml
[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # F401 = import inutilisé
                          # Normal dans __init__.py pour réexporter
```

**Commande :**

```bash
uv run ruff check src tests       # Vérifier
uv run ruff check --fix src tests # Corriger automatiquement
```

---

## 9. Section [tool.mypy] - Vérification des Types

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true              # Avertir si fonction retourne Any
warn_unused_configs = true          # Avertir si config inutilisée
check_untyped_defs = true           # Vérifier fonctions sans annotations
no_implicit_optional = true         # None doit être explicite
warn_redundant_casts = true         # Avertir si cast inutile
strict_equality = true              # Comparaisons strictes
```

### Ignorer les bibliothèques sans types

```toml
[[tool.mypy.overrides]]
module = [
    "langchain.*",
    "faiss.*",
    "streamlit.*",
]
ignore_missing_imports = true  # Ne pas échouer si pas de stubs
```

**Pourquoi ?** Certaines bibliothèques n'ont pas de fichiers `.pyi` (type stubs). Sans cette config, mypy échouerait.

**Commande :**

```bash
uv run mypy src
```

---

## 10. Section [tool.coverage] - Couverture de Code

```toml
[tool.coverage.run]
source = ["src"]           # Mesurer seulement src/
omit = [
    "*/tests/*",           # Exclure les tests eux-mêmes
    "*/__pycache__/*",     # Exclure cache Python
    "*/.venv/*",           # Exclure environnement virtuel
]
```

### Lignes à exclure du rapport

```toml
[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",           # Commentaire explicite
    "def __repr__",               # Méthodes de debug
    "if __name__ == .__main__.:", # Bloc d'exécution directe
    "raise NotImplementedError",  # Méthodes abstraites
    "if TYPE_CHECKING:",          # Imports pour type checking seulement
]
```

**Utilisation dans le code :**

```python
def complex_function():
    if some_condition:
        return result
    else:  # pragma: no cover
        # Ce code est exclu de la couverture
        raise NotImplementedError("Cas non géré")
```

---

## Résumé : Structure Complète

```
pyproject.toml
│
├── [project]                    # QUI est ce projet ?
│   ├── name, version, description
│   ├── dependencies             # De quoi a-t-il besoin ?
│   └── optional-dependencies    # Extras optionnels
│
├── [build-system]               # COMMENT le construire ?
│   └── setuptools.build_meta
│
└── [tool.*]                     # COMMENT configurer les outils ?
    ├── pytest    → Tests
    ├── black     → Formatage
    ├── ruff      → Linting
    ├── mypy      → Types
    └── coverage  → Couverture
```

---

## Commandes Essentielles

```bash
# Installation
uv sync                    # Dépendances principales
uv sync --all-extras       # Tout installer

# Qualité du code
uv run black src tests     # Formater
uv run ruff check src      # Linter
uv run mypy src            # Vérifier types

# Tests
uv run pytest              # Lancer tests
uv run pytest --cov        # Avec couverture
uv run pytest -m "not slow" # Exclure tests lents

# Exécution
uv run rag-events          # CLI du projet
uv run streamlit run app.py # Lancer Streamlit
```

---

## Ressources

- [PEP 621](https://peps.python.org/pep-0621/) - Spécification pyproject.toml
- [uv Documentation](https://docs.astral.sh/uv/)
- [Ruff Rules](https://docs.astral.sh/ruff/rules/)
- [Black Documentation](https://black.readthedocs.io/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
