# 📓 Notebooks - Pipeline de Données RAG

Ce dossier contient les notebooks Jupyter pour préparer les données du système RAG.
**Exécuter dans l'ordre** avant de lancer l'application.

---

## 🎯 Vue d'ensemble du Pipeline

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  01 Collection  │ ──▶ │ 02 Prétraitement│ ──▶ │  03 Embeddings  │
│   (API → JSON)  │     │  (Nettoyage)    │     │   (Vecteurs)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                        ┌─────────────────┐             │
                        │   05 Test RAG   │ ◀───────────┤
                        │  (Validation)   │             │
                        └─────────────────┘             ▼
                                                ┌─────────────────┐
                                                │ 04 Index FAISS  │
                                                │  (Recherche)    │
                                                └─────────────────┘
```

---

## 📋 Notebooks

### 01 - Collecte des Données
**Fichier** : `01_data_collection.ipynb`

Récupération des événements depuis l'API OpenDataSoft (OpenAgenda).

| Entrée | Sortie |
|--------|--------|
| API OpenDataSoft | `data/raw/events_raw.json` |
| | `data/processed/events_processed.json` |

**Étapes :**
1. Appelle l'API OpenDataSoft avec filtres (ville, dates)
2. Valide chaque événement avec un modèle Pydantic
3. Filtre les événements trop anciens (> 1 an)
4. Exporte les données brutes et validées

**Configuration** :
- `LOCATION` : Ville ciblée (défaut: "Marseille")
- `MAX_EVENTS` : Nombre max d'événements (défaut: 10000)

---

### 02 - Prétraitement
**Fichier** : `02_data_preprocessing.ipynb`

Nettoyage et structuration des données pour le RAG.

| Entrée | Sortie |
|--------|--------|
| `data/processed/events_processed.json` | `data/processed/rag_documents.json` |

**Étapes :**
1. Nettoie le HTML des descriptions (BeautifulSoup)
2. Formate les dates en format lisible
3. Tronque les textes longs (max 500 caractères)
4. Crée des documents structurés

**Format du document RAG :**
```json
{
  "id": "12345",
  "title": "Concert Jazz",
  "content": "Titre: Concert Jazz\nVille: Marseille\nDate: Du 15/01/2025...",
  "metadata": {
    "city": "Marseille",
    "start_date": "2025-01-15T20:00:00",
    "url": "https://...",
    "address": "..."
  }
}
```

Le champ `content` est le texte qui sera vectorisé pour la recherche sémantique.

---

### 03 - Création des Embeddings
**Fichier** : `03_create_embeddings_mistral.ipynb`

Génération des vecteurs d'embeddings avec Mistral AI.

| Entrée | Sortie |
|--------|--------|
| `data/processed/rag_documents.json` | `data/processed/embeddings/embeddings.npy` |
| | `data/processed/embeddings/metadata.json` |

**Étapes :**
1. Charge les documents prétraités
2. Initialise le client Mistral (ou SentenceTransformers en fallback)
3. Encode chaque `content` en vecteur
4. Valide les embeddings (pas de NaN, statistiques)
5. Exporte les vecteurs au format NumPy

**Providers supportés :**

| Provider | Modèle | Dimension |
|----------|--------|-----------|
| `mistral` | `mistral-embed` | 1024 |
| `sentence-transformers` | `paraphrase-multilingual-mpnet-base-v2` | 768 |

---

### 04 - Construction de l'Index FAISS
**Fichier** : `04_build_faiss_index.ipynb`

Création de l'index vectoriel pour la recherche sémantique.

| Entrée | Sortie |
|--------|--------|
| `data/processed/embeddings/embeddings.npy` | `data/processed/faiss_index/events.index` |
| `data/processed/rag_documents.json` | `data/processed/faiss_index/config.json` |

**Étapes :**
1. Charge les embeddings NumPy
2. Normalise les vecteurs (L2) pour similarité cosinus
3. Crée un index FAISS `IndexFlatL2`
4. Teste des recherches de validation
5. Mesure la performance (temps de recherche)
6. Exporte l'index et sa configuration

**Configuration exportée :**
```json
{
  "model_name": "mistral-embed",
  "index_type": "IndexFlatL2",
  "dimension": 1024,
  "num_vectors": 497,
  "normalized": true,
  "provider": "mistral"
}
```

---

### 05 - Test du Système RAG
**Fichier** : `05_rag_chatbot_mistral.ipynb`

Validation du pipeline complet : recherche + génération LLM.

| Entrée | Sortie |
|--------|--------|
| Index FAISS + Documents | Réponses conversationnelles |

**Étapes :**
1. Charge le système RAG complet
2. Teste différents types de requêtes :
   - Par type (concerts, expos, théâtre)
   - Par ville
   - Par public (enfants, famille)
   - Événements gratuits
3. Mesure les performances end-to-end
4. Fournit une interface interactive (widgets)

**Métriques mesurées :**
- Temps de réponse moyen (~4s)
- Pertinence des résultats
- Qualité des réponses LLM

---

## 🚀 Exécution

```bash
# Lancer JupyterLab
uv run jupyter lab

# Ou Jupyter Notebook classique
uv run jupyter notebook
```

Puis exécuter les notebooks dans l'ordre : **01 → 02 → 03 → 04 → 05**

---

## 📁 Structure des Données Générées

```
data/
├── raw/
│   └── events_raw.json           # Données brutes API
└── processed/
    ├── events_processed.json     # Événements validés (Pydantic)
    ├── rag_documents.json        # Documents structurés pour RAG
    ├── embeddings/
    │   ├── embeddings.npy        # Vecteurs NumPy (N x 1024)
    │   └── metadata.json         # Config embeddings
    └── faiss_index/
        ├── events.index          # Index FAISS binaire
        └── config.json           # Config index
```

---

## ⚙️ Configuration

Les notebooks utilisent `src/config/settings.py` :

| Variable | Description | Notebooks |
|----------|-------------|-----------|
| `MISTRAL_API_KEY` | Clé API Mistral | 03, 04, 05 |
| `EMBEDDING_PROVIDER` | `mistral` ou `sentence-transformers` | 03, 04 |
| `LLM_MODEL` | Modèle LLM (ex: `mistral-small-latest`) | 05 |
| `MAX_EVENTS` | Limite d'événements à récupérer | 01 |

---

## 🔄 Mise à jour des Données

| Besoin | Action |
|--------|--------|
| Nouvelles données | Réexécuter `01` → `02` → `03` → `04` |
| Changer le provider d'embeddings | Réexécuter `03` → `04` |
| Test uniquement | Exécuter `05` seul |

---

## ❓ Dépannage

| Problème | Solution |
|----------|----------|
| `MISTRAL_API_KEY not found` | Créer/vérifier le fichier `.env` |
| `Index FAISS manquant` | Exécuter notebooks 01-04 |
| `Documents non trouvés` | Exécuter notebook 02 |
| Dimension mismatch | Réexécuter 03 et 04 avec le même provider |
| `ModuleNotFoundError` | Lancer depuis la racine du projet |
