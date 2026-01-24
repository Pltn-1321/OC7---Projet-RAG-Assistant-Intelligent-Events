# Livrables du Projet RAG Events Assistant

> **Documentation complète pour la soumission académique du projet RAG Events Assistant**

---

## 📋 Vue d'Ensemble du Projet

**RAG Events Assistant** est un système de **Retrieval-Augmented Generation (RAG)** qui combine la recherche sémantique et l'intelligence artificielle pour aider les utilisateurs à découvrir des événements culturels via des questions en langage naturel en français.

### Qu'est-ce que le RAG ?

Le RAG (Retrieval-Augmented Generation) combine :
- **Retrieval** : Recherche sémantique dans une base de connaissances (FAISS)
- **Augmented** : Enrichissement du contexte avec les documents pertinents
- **Generation** : Production de réponses naturelles par un LLM (Mistral AI)

```
Question utilisateur → Classification → RAG ou Chat → Réponse + Sources
```

---

## 🎯 Contenu des Livrables

Ce dossier contient tous les éléments requis pour l'évaluation du projet :

### 📄 Documentation Principale

| Fichier | Description | Lignes |
|---------|-------------|--------|
| **[01-RAPPORT-TECHNIQUE.md](01-RAPPORT-TECHNIQUE.md)** | Rapport technique complet : architecture, choix technologiques, modèles, résultats, améliorations | ~1000 |
| **[02-GUIDE-UTILISATION.md](02-GUIDE-UTILISATION.md)** | Guide d'installation et d'utilisation pratique du système | ~500 |
| **[03-DOCUMENTATION-API.md](03-DOCUMENTATION-API.md)** | Référence complète de l'API REST FastAPI | ~460 |
| **[04-RESULTATS-EVALUATION.md](04-RESULTATS-EVALUATION.md)** | Analyse détaillée des performances et résultats d'évaluation | ~500 |
| **[05-TESTS-ET-QUALITE.md](05-TESTS-ET-QUALITE.md)** | Stratégie de tests, couverture, et qualité du code | ~600 |

### 📂 Annexes

| Fichier | Description |
|---------|-------------|
| **[annexes/architecture-complete.md](annexes/architecture-complete.md)** | Architecture système détaillée |
| **[annexes/choix-technologiques.md](annexes/choix-technologiques.md)** | Justifications approfondies des choix technologiques |
| **[annexes/ameliorations-futures.md](annexes/ameliorations-futures.md)** | Roadmap détaillée et pistes d'amélioration |
| **[annexes/schemas/](annexes/schemas/)** | Diagrammes ASCII (pipeline RAG, architecture globale) |

### 📊 Données d'Évaluation

| Fichier | Description |
|---------|-------------|
| **[donnees-evaluation/test-questions-annote.json](donnees-evaluation/test-questions-annote.json)** | Dataset de 12 questions annotées avec mots-clés attendus et catégories |
| **[donnees-evaluation/evaluation-results.json](donnees-evaluation/evaluation-results.json)** | Résultats d'évaluation détaillés (latence, couverture, classification) |
| **[donnees-evaluation/test-coverage-report.txt](donnees-evaluation/test-coverage-report.txt)** | Rapport de couverture des tests (pytest --cov) |
| **[donnees-evaluation/exemples-reponses.md](donnees-evaluation/exemples-reponses.md)** | Exemples concrets de questions/réponses du système |

---

## 🏆 Métriques Clés du Projet

### Performance

| Métrique | Valeur | Cible | Statut |
|----------|--------|-------|--------|
| **Latence moyenne** | 2.41s | <3.0s | ✅ PASS |
| **Couverture mots-clés** | 81.5% | >80% | ✅ PASS |
| **Classification accuracy** | 100% | ~95% | ✅ EXCELLENT |
| **Test coverage** | 85% | >80% | ✅ PASS |

### Fonctionnalités

- ✅ **Système RAG fonctionnel** : Classification intelligente SEARCH vs CHAT, recherche sémantique FAISS, génération LLM
- ✅ **API REST complète** : 6 endpoints FastAPI avec sessions, background tasks, documentation Swagger
- ✅ **Interface utilisateur** : Streamlit avec chat, historique, sources, thème sombre
- ✅ **Tests complets** : Unitaires, intégration, end-to-end (pytest + couverture 85%)
- ✅ **Évaluation RAGAS** : Framework d'évaluation RAG avec métriques de qualité
- ✅ **Docker** : Multi-stage build avec support Streamlit et FastAPI
- ✅ **Documentation** : Complète et professionnelle

---

## 🛠️ Technologies Principales

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| **LLM** | Mistral AI | mistral-small-latest | Génération de réponses conversationnelles |
| **Embeddings** | Mistral Embed | 1024d | Vectorisation sémantique multilingue (français) |
| **Vector Store** | FAISS | IndexFlatL2 | Recherche de similarité ultra-rapide |
| **API** | FastAPI | 0.109+ | REST API avec sessions et background tasks |
| **UI** | Streamlit | 1.52+ | Interface chat moderne et réactive |
| **Data Source** | Open Agenda API | - | Événements culturels français |
| **Tests** | pytest + RAGAS | 7.4+ | Tests unitaires/intégration + évaluation RAG |
| **Package Manager** | uv | latest | Gestionnaire de dépendances moderne (10-100x plus rapide que pip) |

---

## 📚 Comment Naviguer les Livrables

### Pour une Évaluation Complète

1. **Commencez par le rapport technique** : [01-RAPPORT-TECHNIQUE.md](01-RAPPORT-TECHNIQUE.md)
   - Vue d'ensemble complète de l'architecture, des choix, et des résultats
   - Comprendre les décisions techniques et leurs justifications

2. **Testez le système** : [02-GUIDE-UTILISATION.md](02-GUIDE-UTILISATION.md)
   - Instructions d'installation pas à pas
   - Exemples d'utilisation concrets
   - Commandes pour lancer l'application

3. **Explorez l'API** : [03-DOCUMENTATION-API.md](03-DOCUMENTATION-API.md)
   - Référence complète des endpoints
   - Exemples de requêtes curl
   - Modèles de données

4. **Analysez les performances** : [04-RESULTATS-EVALUATION.md](04-RESULTATS-EVALUATION.md)
   - Métriques détaillées
   - Résultats par catégorie de questions
   - Analyses et recommandations

5. **Vérifiez la qualité** : [05-TESTS-ET-QUALITE.md](05-TESTS-ET-QUALITE.md)
   - Stratégie de tests
   - Couverture du code
   - Outils de qualité (Black, Ruff, mypy)

6. **Approfondissez** : Consultez les [annexes/](annexes/) pour des détails techniques supplémentaires

### Pour une Évaluation Rapide (15-30 minutes)

1. **Ce README** : Vue d'ensemble et métriques clés (5 min)
2. **[01-RAPPORT-TECHNIQUE.md](01-RAPPORT-TECHNIQUE.md)** : Sections I, II, V, VII (15 min)
3. **[04-RESULTATS-EVALUATION.md](04-RESULTATS-EVALUATION.md)** : Résultats globaux et exemples (10 min)
4. **[donnees-evaluation/exemples-reponses.md](donnees-evaluation/exemples-reponses.md)** : Exemples concrets du système (5 min)

---

## 🔗 Accès au Code Source

Le code source complet du projet est disponible dans le repository :

```
../../                          (Racine du projet)
├── app.py                      (Interface Streamlit)
├── src/                        (Code source principal)
│   ├── api/main.py            (API FastAPI)
│   ├── rag/engine.py          (Moteur RAG)
│   ├── rag/index_builder.py   (Construction d'index FAISS)
│   ├── config/                (Configuration et constantes)
│   └── data/models.py         (Modèles Pydantic)
├── tests/                      (Tests unitaires/intégration/e2e)
├── notebooks/                  (Pipeline de données Jupyter)
├── scripts/                    (Scripts d'évaluation)
├── data/                       (Données et index FAISS)
├── requirements.txt            (Dépendances pip - créé pour ce livrable)
└── pyproject.toml             (Configuration uv)
```

---

## 📦 Installation Rapide

### Prérequis

- Python 3.11+
- Clé API Mistral AI (gratuite sur [console.mistral.ai](https://console.mistral.ai/))

### Option 1 : Avec uv (Recommandé)

```bash
# Installer uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Installer les dépendances
uv sync --all-extras

# Configurer .env
cp .env.example .env
# Éditer .env et ajouter MISTRAL_API_KEY

# Lancer Streamlit
uv run streamlit run app.py

# OU lancer FastAPI
uv run uvicorn src.api.main:app --reload
```

### Option 2 : Avec pip (Compatible)

```bash
# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Installer dépendances
pip install -r requirements.txt

# Configurer .env
cp .env.example .env
# Éditer .env et ajouter MISTRAL_API_KEY

# Lancer l'application
streamlit run app.py
```

### Option 3 : Avec Docker

```bash
# Lancer API + Streamlit
docker-compose up

# Accès:
# - Streamlit: http://localhost:8501
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

---

## 🧪 Lancer les Tests

```bash
# Tous les tests
uv run pytest

# Avec couverture
uv run pytest --cov=src --cov-report=html
# Ouvrir htmlcov/index.html

# Tests spécifiques
uv run pytest tests/unit/              # Tests unitaires
uv run pytest tests/integration/       # Tests d'intégration
uv run pytest tests/e2e/               # Tests end-to-end

# Évaluation RAG
uv run python scripts/evaluate_rag.py --test-file tests/data/test_questions.json
```

---

## 🎓 Points Forts du Projet

### Architecture

- ✅ **Classification intelligente** : Détection automatique SEARCH vs CHAT (100% accuracy)
- ✅ **Pipeline RAG complet** : Embedding → FAISS → LLM avec sources vérifiables
- ✅ **Direct SDK integration** : Mistral AI et FAISS sans abstraction inutile
- ✅ **Session management** : Mémoire conversationnelle (max 5 échanges)
- ✅ **Streaming responses** : UX fluide avec réponses progressives

### Qualité

- ✅ **85% test coverage** : Tests unitaires, intégration, e2e
- ✅ **Code formaté** : Black (line-length 100)
- ✅ **Linté** : Ruff (0 erreurs)
- ✅ **Type hints** : mypy (90% des fonctions typées)
- ✅ **Documentation** : Complète et professionnelle

### Performance

- ✅ **Latence < 3s** : Moyenne de 2.41s pour les requêtes RAG
- ✅ **Relevance > 80%** : 81.5% de couverture des mots-clés attendus
- ✅ **FAISS ultra-rapide** : IndexFlatL2 avec 497 documents
- ✅ **Batch processing** : Embeddings par batch de 32

### Production-Ready

- ✅ **Docker** : Multi-stage build optimisé
- ✅ **API REST** : FastAPI avec OpenAPI/Swagger
- ✅ **Configuration** : Pydantic Settings avec validation
- ✅ **Error handling** : Validation Pydantic sur tous les endpoints
- ✅ **Background tasks** : Rebuild d'index non-bloquant

---

## 📞 Support et Questions

Pour toute question sur les livrables ou le projet :

- **Documentation complète** : Voir les fichiers dans ce dossier
- **Code source** : Voir le repository complet
- **Issues GitHub** : [Créer une issue](../../issues) (si repository GitHub)

---

## 📄 License

Ce projet est sous licence MIT. Voir [LICENSE](../../LICENSE) pour plus de détails.

---

<div align="center">

**Fait avec ❤️ et ☕ en France**

🎭 **RAG Events Assistant** - Découvrez des événements culturels avec l'IA

</div>

---

## 📌 Checklist d'Évaluation

Pour faciliter l'évaluation, voici une checklist des éléments à vérifier :

### Documentation (6/6)
- [x] Rapport technique complet (01-RAPPORT-TECHNIQUE.md)
- [x] Guide d'utilisation pratique (02-GUIDE-UTILISATION.md)
- [x] Documentation API REST (03-DOCUMENTATION-API.md)
- [x] Résultats d'évaluation (04-RESULTATS-EVALUATION.md)
- [x] Tests et qualité (05-TESTS-ET-QUALITE.md)
- [x] Annexes et schémas (annexes/)

### Fonctionnalité (4/4)
- [x] Système RAG fonctionnel (classification, recherche, génération)
- [x] API REST FastAPI (6 endpoints, sessions, background tasks)
- [x] Interface Streamlit (chat, historique, sources)
- [x] Docker containerization (multi-stage, dual-mode)

### Tests (4/4)
- [x] Tests unitaires (test_models.py, test_rag_engine.py)
- [x] Tests d'intégration (test_api.py)
- [x] Tests end-to-end (test_rag_pipeline.py)
- [x] Dataset annoté (12 questions avec expected keywords)

### Performance (4/4)
- [x] Latence < 3s (2.41s moyenne)
- [x] Couverture > 80% (81.5%)
- [x] Classification 100% accuracy
- [x] Test coverage > 80% (85%)

### Qualité Code (4/4)
- [x] Code formaté (Black)
- [x] Linté (Ruff, 0 erreurs)
- [x] Type hints (mypy, 90%)
- [x] Documentation inline et externe

**Total : 22/22 ✅ COMPLET**
