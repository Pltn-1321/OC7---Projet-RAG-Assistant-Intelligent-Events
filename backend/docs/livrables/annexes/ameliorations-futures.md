# Améliorations Futures - Roadmap Détaillée

> **Feuille de route technique avec estimations d'effort et priorisation**

---

## Vue d'Ensemble

Ce document détaille les améliorations futures identifiées pour le projet RAG Events Assistant, avec :
- Descriptions techniques détaillées
- Estimations d'effort (jours-développeur)
- Dépendances entre tâches
- Impact business/technique estimé
- Priorisation (High/Medium/Low)

**Contexte** : 1 développeur full-stack expérimenté

---

## Priorité HAUTE (Production-Critical)

### H1. Session Persistence avec Redis

**Problème actuel** :
- Sessions stockées en mémoire (dict Python)
- Perdues au restart serveur
- Impossible multi-instance deployment

**Solution proposée** :
```python
import redis
from src.config.settings import settings

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True
)

# Stocker session
redis_client.setex(
    f"session:{session_id}",
    3600,  # TTL 1h
    json.dumps(history)
)
```

**Effort estimé** : 2-3 jours
**Dépendances** : Redis server installé
**Impact technique** : ⭐⭐⭐⭐⭐ (critique pour production)
**Impact business** : ⭐⭐⭐⭐ (meilleure UX)

**Tâches** :
1. Ajouter `redis` dependency
2. Configuration Redis dans settings
3. Session manager class avec Redis backend
4. Migration sessions existantes
5. Tests (unit + integration)

---

### H2. Monitoring et Alerting (Prometheus + Grafana)

**Problème actuel** :
- Pas de métriques exposées
- Pas de dashboards
- Debugging difficile en production

**Solution proposée** :

**Prometheus Metrics** :
```python
from prometheus_client import Counter, Histogram, Gauge

# Métriques à tracker
request_count = Counter("rag_requests_total", "Total requests", ["endpoint", "status"])
request_latency = Histogram("rag_request_duration_seconds", "Request latency")
rag_queries = Counter("rag_queries_total", "RAG queries", ["mode"])  # SEARCH/CHAT
faiss_search_time = Histogram("faiss_search_duration_seconds", "FAISS search time")
llm_generation_time = Histogram("llm_generation_duration_seconds", "LLM time")
active_sessions = Gauge("rag_active_sessions", "Active sessions")
```

**Grafana Dashboards** :
- Request rate (req/sec)
- Latency distribution (P50, P95, P99)
- Error rate (%)
- RAG vs Chat ratio
- FAISS search performance
- Active sessions trend

**Effort estimé** : 3-4 jours
**Dépendances** : Prometheus + Grafana deployment
**Impact technique** : ⭐⭐⭐⭐⭐
**Impact business** : ⭐⭐⭐⭐

**Alertes** :
- Latency P95 > 5s
- Error rate > 5%
- FAISS index not found

---

### H3. CI/CD Pipeline (GitHub Actions)

**Problème actuel** :
- Tests manuels
- Déploiement manuel
- Pas de validation automatique

**Solution proposée** :

**`.github/workflows/ci.yml`** :
```yaml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: astral-sh/setup-uv@v1
      - run: uv sync --all-extras
      - run: uv run pytest --cov=src
      - run: uv run black --check src
      - run: uv run ruff check src
      - run: uv run mypy src

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: docker build -t rag-assistant .
      - run: docker push ghcr.io/user/rag-assistant:latest

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: kubectl apply -f k8s/deployment.yaml
```

**Effort estimé** : 2 jours
**Impact technique** : ⭐⭐⭐⭐⭐
**Impact business** : ⭐⭐⭐

---

### H4. FAISS IVF Index (Scalability)

**Problème actuel** :
- IndexFlatL2 : O(n) search
- Lent pour >10K événements

**Solution** :
```python
nlist = 100  # Clusters
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

# Entraînement requis
index.train(embeddings)
index.add(embeddings)

# Recherche (nprobe contrôle recall)
index.nprobe = 10  # Clusters à explorer
distances, indices = index.search(query, k=5)
```

**Trade-off** :
- Recall : 95-98% (vs 100% Flat)
- Speed : 10-100x plus rapide

**Effort estimé** : 2 jours
**Impact technique** : ⭐⭐⭐⭐
**Impact business** : ⭐⭐⭐ (si scale >10K)

---

## Priorité MOYENNE (Quality Improvement)

### M1. Reranking avec Cross-Encoder

**Problème actuel** :
- Single-pass retrieval (bi-encoder)
- Top-5 parfois sub-optimal

**Solution** :
```python
from sentence_transformers import CrossEncoder

# Bi-encoder : retrieval rapide top-20
results_top20 = faiss_search(query, k=20)

# Cross-encoder : rerank précis top-5
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
pairs = [[query, doc] for doc in results_top20]
scores = reranker.predict(pairs)

# Top-5 reranké
top5_indices = np.argsort(scores)[-5:][::-1]
results_top5 = [results_top20[i] for i in top5_indices]
```

**Gain attendu** : +10-15% relevance
**Effort estimé** : 3 jours
**Impact technique** : ⭐⭐⭐⭐
**Impact business** : ⭐⭐⭐⭐

---

### M2. Hybrid Search (BM25 + FAISS)

**Problème actuel** :
- Pure semantic search
- Mauvais pour exact name matches

**Solution** :
```python
from rank_bm25 import BM25Okapi

# BM25 indexation
corpus = [event.to_search_text() for event in events]
tokenized = [doc.split() for doc in corpus]
bm25 = BM25Okapi(tokenized)

# Hybrid search
def hybrid_search(query, top_k=5, alpha=0.7):
    # Semantic (FAISS)
    semantic_results = faiss_search(query, k=20)
    semantic_scores = {r["id"]: r["similarity"] for r in semantic_results}
    
    # Lexical (BM25)
    bm25_scores = bm25.get_scores(query.split())
    lexical_scores = {i: score for i, score in enumerate(bm25_scores)}
    
    # Combine (weighted)
    combined = {}
    for id in set(semantic_scores.keys()) | set(lexical_scores.keys()):
        combined[id] = (
            alpha * semantic_scores.get(id, 0) +
            (1 - alpha) * lexical_scores.get(id, 0)
        )
    
    # Top-K
    top_ids = sorted(combined, key=combined.get, reverse=True)[:top_k]
    return [events[id] for id in top_ids]
```

**Gain attendu** : +20% pour noms exacts
**Effort estimé** : 4 jours
**Impact technique** : ⭐⭐⭐⭐
**Impact business** : ⭐⭐⭐⭐

---

### M3. Query Expansion (Temporal + Genres)

**Problème actuel** :
- "été" non converti en mois
- "electro" manque synonymes

**Solution** :
```python
TEMPORAL_EXPANSION = {
    "été": ["juin", "juillet", "août"],
    "hiver": ["décembre", "janvier", "février"],
    "weekend": ["samedi", "dimanche"],
    "semaine": ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]
}

GENRE_EXPANSION = {
    "jazz": ["jazz", "blues", "swing", "soul"],
    "electro": ["électronique", "techno", "house", "EDM", "trance"],
    "rock": ["rock", "metal", "punk", "grunge"]
}

def expand_query(query):
    expanded = query
    for term, synonyms in {**TEMPORAL_EXPANSION, **GENRE_EXPANSION}.items():
        if term in query.lower():
            expanded += " " + " ".join(synonyms)
    return expanded
```

**Gain attendu** : +30% coverage temporalité, +15% genres
**Effort estimé** : 2 jours
**Impact technique** : ⭐⭐⭐
**Impact business** : ⭐⭐⭐⭐

---

### M4. Advanced Filters (Prix, Distance, Accessibilité)

**Solution UI (Streamlit sidebar)** :
```python
st.sidebar.header("Filtres")
price_range = st.sidebar.slider("Prix (€)", 0, 100, (0, 50))
distance_km = st.sidebar.selectbox("Distance", [5, 10, 20, 50])
accessibility = st.sidebar.multiselect(
    "Accessibilité",
    ["Fauteuil roulant", "Boucle magnétique", "LSF"]
)
```

**Filtrage post-retrieval** :
```python
def filter_results(results, filters):
    filtered = []
    for r in results:
        # Prix
        if filters["price_range"]:
            price = parse_price(r["price_info"])
            if not (filters["price_range"][0] <= price <= filters["price_range"][1]):
                continue
        
        # Distance
        if filters["distance_km"]:
            dist = calculate_distance(user_location, r["location"])
            if dist > filters["distance_km"]:
                continue
        
        filtered.append(r)
    return filtered
```

**Effort estimé** : 5 jours
**Impact technique** : ⭐⭐⭐
**Impact business** : ⭐⭐⭐⭐⭐

---

## Priorité BASSE (Nice-to-Have)

### L1. Multi-Language Support

**Langues cibles** : EN, ES (en plus de FR)

**Solution** :
```python
from langdetect import detect

def detect_language(query):
    return detect(query)  # 'fr', 'en', 'es'

SYSTEM_PROMPTS = {
    "fr": "Tu es un assistant...",
    "en": "You are an assistant...",
    "es": "Eres un asistente..."
}

def chat(query, history):
    lang = detect_language(query)
    system_prompt = SYSTEM_PROMPTS[lang]
    # Use appropriate prompt
```

**Effort estimé** : 6 jours (traduction prompts, tests)
**Impact business** : ⭐⭐⭐

---

### L2. User Authentication (OAuth2)

**Providers** : Google, GitHub

**Solution** :
```python
from fastapi_oauth2 import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/login")
async def login(provider: str):
    # Redirect to OAuth provider
    return RedirectResponse(oauth_providers[provider].authorize_url)

@app.get("/callback/{provider}")
async def callback(provider: str, code: str):
    # Exchange code for token
    token = await oauth_providers[provider].get_token(code)
    return {"access_token": token}
```

**Effort estimé** : 4 jours
**Impact business** : ⭐⭐⭐

---

### L3. A/B Testing Framework

**Métriques à tester** :
- Prompt variations
- Embedding models (Mistral vs OpenAI)
- Reranking impact
- top_k optimal

**Solution** :
```python
from abtest import ABTest

ab_test = ABTest("embedding_model")
ab_test.add_variant("mistral", weight=0.5)
ab_test.add_variant("openai", weight=0.5)

@app.post("/search")
def search(request: SearchRequest):
    variant = ab_test.get_variant(user_id)
    embedding_model = variant.name
    # Use selected model
```

**Effort estimé** : 5 jours
**Impact technique** : ⭐⭐⭐⭐

---

## Récapitulatif Roadmap

### Court Terme (Mois 1)

| Tâche | Priorité | Effort | Impact |
|-------|----------|--------|--------|
| Session Persistence (Redis) | HIGH | 3j | ⭐⭐⭐⭐⭐ |
| Query Expansion | MEDIUM | 2j | ⭐⭐⭐⭐ |
| **Total** | - | **5j** | - |

### Moyen Terme (Mois 2-3)

| Tâche | Priorité | Effort | Impact |
|-------|----------|--------|--------|
| Monitoring (Prometheus) | HIGH | 4j | ⭐⭐⭐⭐⭐ |
| CI/CD Pipeline | HIGH | 2j | ⭐⭐⭐⭐⭐ |
| Reranking | MEDIUM | 3j | ⭐⭐⭐⭐ |
| Hybrid Search | MEDIUM | 4j | ⭐⭐⭐⭐ |
| Advanced Filters | MEDIUM | 5j | ⭐⭐⭐⭐⭐ |
| **Total** | - | **18j** | - |

### Long Terme (Mois 4-6)

| Tâche | Priorité | Effort | Impact |
|-------|----------|--------|--------|
| FAISS IVF | HIGH | 2j | ⭐⭐⭐⭐ |
| Multi-Language | LOW | 6j | ⭐⭐⭐ |
| User Auth | LOW | 4j | ⭐⭐⭐ |
| A/B Testing | LOW | 5j | ⭐⭐⭐⭐ |
| **Total** | - | **17j** | - |

**Total estimé** : ~40 jours-développeur (~8 semaines)

---

## Dépendances Entre Tâches

```
Session Persistence → Monitoring (track sessions)
                  ↓
            CI/CD Pipeline → Automated Deploy
                  ↓
         Reranking + Hybrid Search → A/B Testing
```

---

## Conclusion

Cette roadmap propose **40 jours** d'améliorations pour passer d'un MVP fonctionnel à un système production-ready scalable.

**Recommandation** : Commencer par priorité HIGH (semaines 1-2), puis MEDIUM (semaines 3-6), enfin LOW (semaines 7-8) si budget le permet.
