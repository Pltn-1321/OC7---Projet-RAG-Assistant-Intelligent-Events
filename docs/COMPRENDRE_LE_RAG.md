# Comprendre le RAG : Guide Pedagogique

Ce document explique les concepts fondamentaux du RAG (Retrieval-Augmented Generation) utilises dans ce projet, avec un niveau de detail intermediaire pour les developpeurs familiers avec le machine learning et le NLP.

---

## Table des Matieres

1. [Introduction au RAG](#1-introduction-au-rag)
2. [Les Embeddings](#2-les-embeddings-representations-vectorielles)
3. [Les Bases Vectorielles (FAISS)](#3-les-bases-vectorielles-faiss)
4. [La Recherche Semantique](#4-la-recherche-semantique)
5. [La Generation Augmentee](#5-la-generation-augmentee)
6. [Evaluation avec RAGAS](#6-evaluation-avec-ragas)
7. [Ressources pour Aller Plus Loin](#7-ressources-pour-aller-plus-loin)

---

## 1. Introduction au RAG

### Qu'est-ce que le RAG ?

**RAG (Retrieval-Augmented Generation)** est une architecture qui combine:
- **Retrieval**: Recherche d'informations pertinentes dans une base de connaissances
- **Augmented**: Enrichissement du contexte du modele de langage
- **Generation**: Production d'une reponse naturelle par un LLM

```
┌─────────────────────────────────────────────────────────────────┐
│                          Pipeline RAG                            │
│                                                                  │
│   Question ──▶ Retriever ──▶ Contexte ──▶ LLM ──▶ Reponse       │
│     "Quels      (FAISS)     [Doc1,Doc2]  (Mistral) "Voici les   │
│     concerts?"                                     concerts..." │
└─────────────────────────────────────────────────────────────────┘
```

### Pourquoi le RAG plutot que le Fine-tuning ?

| Aspect | RAG | Fine-tuning |
|--------|-----|-------------|
| **Mise a jour des donnees** | Instantanee (re-indexation) | Requires re-training |
| **Cout** | Faible (API embeddings) | Eleve (GPU, compute) |
| **Tracabilite** | Sources citables | Boite noire |
| **Hallucinations** | Reduites (contexte factuel) | Plus frequentes |
| **Connaissances** | Limitees a la base | Integrees au modele |

**Cas d'usage typiques du RAG**:
- Questions-reponses sur des documents internes
- Assistants bases sur des donnees actualisees
- Chatbots avec sources verifiables
- Recherche semantique augmentee

---

## 2. Les Embeddings (Representations Vectorielles)

### Principe Mathematique

Un **embedding** est une projection d'un texte dans un espace vectoriel de dimension fixe ou les relations semantiques sont preservees.

```
                    Espace Semantique (dim=1024)

"concert de jazz"  ────▶  [0.12, -0.34, 0.56, ..., 0.23]
"musique live"     ────▶  [0.11, -0.32, 0.54, ..., 0.21]  ← similaire !
"exposition art"   ────▶  [-0.45, 0.67, -0.12, ..., 0.89] ← different
```

**Proprietes cles**:
- **Dimension fixe**: 768 (sentence-transformers) ou 1024 (Mistral)
- **Continuite semantique**: textes similaires → vecteurs proches
- **Operabilite vectorielle**: addition, soustraction, moyenne

### Modeles d'Embeddings

#### Mistral Embed (utilise par defaut)

```python
from mistralai import Mistral

client = Mistral(api_key="...")
response = client.embeddings.create(
    model="mistral-embed",
    inputs=["concert de jazz a Paris"]
)
embedding = response.data[0].embedding  # dim=1024
```

**Caracteristiques**:
- Dimension: 1024
- Multilingue (dont francais)
- API cloud (pas de modele local)
- Limite de tokens: ~8192

#### Sentence-Transformers (alternative locale)

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
embedding = model.encode("concert de jazz a Paris")  # dim=768
```

**Caracteristiques**:
- Dimension: 768 (varie selon le modele)
- Execution locale (pas d'API)
- Plus rapide pour le prototypage
- Open source (Apache 2.0)

### Mesures de Similarite

#### Distance Cosinus

Mesure l'angle entre deux vecteurs, independamment de leur norme.

```
                    cos(θ) = (A · B) / (||A|| × ||B||)

cos(θ) = 1  → identiques
cos(θ) = 0  → orthogonaux (non relies)
cos(θ) = -1 → opposes
```

**En pratique** (avec normalisation L2):
```python
import numpy as np
import faiss

# Normaliser les vecteurs
faiss.normalize_L2(embeddings)

# Distance L2 sur vecteurs normalises = 2 * (1 - cos_sim)
# Similarite cosinus = 1 - distance_L2 / 2
```

#### Distance Euclidienne (L2)

```
                    d(A, B) = √(Σ(Ai - Bi)²)
```

FAISS utilise L2 par defaut. Avec la normalisation L2, les deux metriques sont equivalentes.

---

## 3. Les Bases Vectorielles (FAISS)

### Pourquoi FAISS ?

**FAISS** (Facebook AI Similarity Search) est une bibliotheque optimisee pour la recherche de vecteurs similaires.

| Alternative | Avantages | Inconvenients |
|-------------|-----------|---------------|
| **FAISS** | Rapide, leger, local | Pas de persistance native |
| **Pinecone** | Cloud, scalable | Payant, dependance externe |
| **Chroma** | Simple, persistant | Moins performant a grande echelle |
| **Weaviate** | GraphQL, filtres | Plus complexe |
| **Milvus** | Distribue | Overkill pour <1M vecteurs |

**FAISS est ideal pour**:
- Prototypes et POC
- Datasets < 1 million de vecteurs
- Recherche pure sans filtres complexes

### Structures d'Index

#### IndexFlatL2 (utilise dans ce projet)

Recherche **exacte** par force brute.

```python
import faiss

dimension = 1024
index = faiss.IndexFlatL2(dimension)

# Ajouter des vecteurs
index.add(embeddings)  # numpy array (n, dim)

# Rechercher
distances, indices = index.search(query_vector, k=5)
```

**Complexite**: O(n × d) par requete

**Quand l'utiliser**: < 100k vecteurs

#### IndexIVF (pour grands datasets)

Recherche **approximative** avec partitionnement.

```python
# Creer un index IVF
nlist = 100  # nombre de clusters
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

# Entrainer sur les donnees
index.train(embeddings)
index.add(embeddings)

# Rechercher (nprobe clusters)
index.nprobe = 10
distances, indices = index.search(query, k=5)
```

**Compromis precision/performance**:
- `nlist` eleve → plus precis, plus lent
- `nprobe` eleve → plus precis, plus lent

### Normalisation L2

Pour utiliser la similarite cosinus avec FAISS L2:

```python
# Avant d'ajouter a l'index
faiss.normalize_L2(embeddings)

# Avant chaque recherche
faiss.normalize_L2(query_embedding)

# Conversion distance → similarite
similarity = 1 - distance  # pour vecteurs normalises
```

---

## 4. La Recherche Semantique

### Pipeline de Recherche

```
┌─────────────────────────────────────────────────────────────────┐
│                    Pipeline de Recherche                         │
│                                                                  │
│  1. Query: "concerts jazz ce weekend"                           │
│            │                                                     │
│            ▼                                                     │
│  2. Encoding: [0.12, -0.34, ..., 0.23] (dim=1024)               │
│            │                                                     │
│            ▼                                                     │
│  3. Normalisation L2                                            │
│            │                                                     │
│            ▼                                                     │
│  4. Recherche kNN dans FAISS                                    │
│            │                                                     │
│            ▼                                                     │
│  5. Top-K documents avec scores                                 │
│     - "Concert Jazz Manouche" (sim=0.72)                        │
│     - "Festival Jazz en Juin" (sim=0.68)                        │
│     - "Soiree Blues & Jazz" (sim=0.65)                          │
└─────────────────────────────────────────────────────────────────┘
```

### Parametres Importants

#### Top-K

Nombre de documents a recuperer.

```python
results = engine.search(query, top_k=5)
```

**Trade-offs**:
- K trop petit → contexte insuffisant
- K trop grand → bruit, tokens gaspilles, cout API

**Recommandation**: 3-5 pour la generation, 10+ pour l'affichage

#### Seuil de Similarite

Filtrer les resultats peu pertinents:

```python
min_similarity = 0.3  # rejeter si < 0.3
results = [r for r in results if r["similarity"] >= min_similarity]
```

### Reranking (Optionnel)

Affiner l'ordre des resultats avec un modele de reranking:

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Reranker les top-20 pour obtenir les meilleurs 5
pairs = [(query, doc["content"]) for doc in results[:20]]
scores = reranker.predict(pairs)
reranked = sorted(zip(results[:20], scores), key=lambda x: x[1], reverse=True)[:5]
```

---

## 5. La Generation Augmentee

### Construction du Prompt

Le contexte recupere est injecte dans le prompt du LLM:

```python
system_prompt = f"""Tu es un assistant pour evenements culturels.

Contexte (evenements pertinents):
{formatted_context}

Instructions:
- Reponds de maniere concise
- Cite les evenements par leur titre
- Si aucun evenement ne correspond, dis-le clairement
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_query}
]
```

### Gestion de la Fenetre de Contexte

Les LLM ont une limite de tokens (ex: 32k pour Mistral).

**Calcul approximatif**:
- 1 token ≈ 4 caracteres en francais
- 5 documents × 500 caracteres = 625 tokens de contexte

**Strategies si depassement**:
1. Reduire top_k
2. Tronquer les documents
3. Resumer le contexte
4. Utiliser un modele avec fenetre plus grande

### Temperature et Parametres

```python
response = client.chat.complete(
    model="mistral-small-latest",
    messages=messages,
    temperature=0.3,   # 0=deterministe, 1=creatif
    max_tokens=500,    # limite de la reponse
    top_p=0.9          # nucleus sampling
)
```

**Temperature recommandee**:
- 0.0-0.3: Reponses factuelles (RAG)
- 0.5-0.7: Equilibre
- 0.8-1.0: Creative writing

### Hallucinations et Mitigation

**Causes des hallucinations**:
1. Contexte insuffisant ou non pertinent
2. Question hors-scope
3. Temperature trop elevee

**Strategies de mitigation**:
1. Verifier que le contexte repond a la question
2. Ajouter "Si tu ne sais pas, dis-le" dans le prompt
3. Utiliser temperature basse (0.2-0.3)
4. Validation post-generation (entites presentes dans le contexte)

---

## 6. Evaluation avec RAGAS

### Metriques RAGAS

[RAGAS](https://github.com/explodinggradients/ragas) (Retrieval Augmented Generation Assessment) fournit des metriques standardisees.

#### Faithfulness (Fidelite)

Mesure si la reponse est fidele au contexte fourni.

```
                    Nombre de claims verifiables dans le contexte
Faithfulness = ────────────────────────────────────────────────────
                    Nombre total de claims dans la reponse
```

- **1.0**: Parfaitement fidele au contexte
- **0.0**: Hallucinations completes

#### Answer Relevancy (Pertinence)

Mesure si la reponse repond a la question.

```
                    Similarite(question, reponse_generee)
Relevancy = ───────────────────────────────────────────────
                              max_similarity
```

#### Context Precision

Mesure si les documents recuperes sont pertinents.

```
                    Documents pertinents dans le contexte
Precision = ─────────────────────────────────────────────────
                    Total documents recuperes
```

#### Context Recall

Mesure si tous les elements necessaires sont dans le contexte.

```
                    Elements de la reponse ideale trouves
Recall = ───────────────────────────────────────────────────
                    Elements de la reponse ideale totale
```

### Utilisation dans ce Projet

```bash
# Executer l'evaluation
uv run python scripts/evaluate_rag.py

# Sans RAGAS (plus rapide)
uv run python scripts/evaluate_rag.py --skip-ragas
```

**Format du rapport**:
```json
{
    "aggregate_metrics": {
        "avg_latency_seconds": 2.3,
        "avg_keyword_coverage": 0.75
    },
    "ragas_scores": {
        "faithfulness": 0.82,
        "answer_relevancy": 0.78,
        "context_precision": 0.65,
        "context_recall": 0.71
    }
}
```

### Interpretation des Scores

| Metrique | Excellent | Bon | A ameliorer |
|----------|-----------|-----|-------------|
| Faithfulness | > 0.9 | 0.7-0.9 | < 0.7 |
| Answer Relevancy | > 0.85 | 0.7-0.85 | < 0.7 |
| Context Precision | > 0.8 | 0.6-0.8 | < 0.6 |
| Context Recall | > 0.75 | 0.5-0.75 | < 0.5 |

### Amelioration Iterative

1. **Faithfulness faible** → Ameliorer le prompt, reduire temperature
2. **Relevancy faible** → Affiner le prompt, ajouter des exemples
3. **Precision faible** → Meilleurs embeddings, filtres metadata
4. **Recall faible** → Augmenter top_k, meilleur preprocessing

---

## 7. Ressources pour Aller Plus Loin

### Papers Fondateurs

1. **Lewis et al. (2020)**: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
   - Paper original introduisant le RAG
   - https://arxiv.org/abs/2005.11401

2. **Karpukhin et al. (2020)**: "Dense Passage Retrieval for Open-Domain Question Answering"
   - DPR: methode de retrieval dense
   - https://arxiv.org/abs/2004.04906

3. **Izacard & Grave (2021)**: "Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering"
   - Fusion-in-Decoder
   - https://arxiv.org/abs/2007.01282

### Documentation Technique

- **LangChain**: https://python.langchain.com/docs/
- **FAISS**: https://faiss.ai/
- **Mistral AI**: https://docs.mistral.ai/
- **Sentence-Transformers**: https://www.sbert.net/
- **RAGAS**: https://docs.ragas.io/

### Tutoriels Avances

1. **Advanced RAG Techniques** (LangChain)
   - https://python.langchain.com/docs/tutorials/rag/

2. **Building Production-Ready RAG** (LlamaIndex)
   - https://docs.llamaindex.ai/

3. **FAISS Tutorial** (Facebook)
   - https://github.com/facebookresearch/faiss/wiki

### Communaute

- **Discord LangChain**: https://discord.gg/langchain
- **Hugging Face Forums**: https://discuss.huggingface.co/
- **Reddit r/LocalLLaMA**: Discussions sur les LLM locaux

---

## Resume

Le RAG combine le meilleur des deux mondes:
- **Retrieval**: Acces a des connaissances actualisees et specifiques
- **Generation**: Reponses naturelles et contextualisees

**Pipeline type**:
```
Query → Embed → Search (FAISS) → Context → LLM → Response
```

**Points cles a retenir**:
1. La qualite des embeddings est cruciale
2. FAISS est suffisant pour < 1M vecteurs
3. Le prompt engineering impacte fortement la qualite
4. Evaluez systematiquement avec RAGAS
5. Iterez sur les metriques faibles

Ce projet illustre ces concepts avec une application concrete de decouverte d'evenements culturels.
