# Intégration LangChain - Architecture et Guide

Ce document décrit l'architecture LangChain utilisée dans le projet RAG Events Assistant.

## Vue d'ensemble

Le projet utilise **LangChain LCEL** (LangChain Expression Language) pour orchestrer le pipeline RAG. Cette approche remplace l'intégration directe du SDK Mistral par des abstractions LangChain tout en préservant l'interface publique.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAGEngine                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Query                                                     │
│      │                                                          │
│      ▼                                                          │
│  ┌─────────────────────────────────────┐                        │
│  │   Classification Chain (LCEL)       │                        │
│  │   ChatPromptTemplate | LLM | Parser │                        │
│  └─────────────────────────────────────┘                        │
│      │                                                          │
│      ├─── SEARCH ──────────────────────────────────┐            │
│      │                                             │            │
│      │  ┌─────────────────────────────────────┐    │            │
│      │  │   FAISS VectorStore (LangChain)     │    │            │
│      │  │   similarity_search_with_score()    │    │            │
│      │  └─────────────────────────────────────┘    │            │
│      │                │                            │            │
│      │                ▼                            │            │
│      │  ┌─────────────────────────────────────┐    │            │
│      │  │   RAG Chain (LCEL)                  │    │            │
│      │  │   ChatPromptTemplate(context) | LLM │    │            │
│      │  └─────────────────────────────────────┘    │            │
│      │                                             │            │
│      └─── CHAT ────────────────────────────────────┤            │
│                                                    │            │
│         ┌─────────────────────────────────────┐    │            │
│         │   Conversation Chain (LCEL)         │    │            │
│         │   ChatPromptTemplate | LLM | Parser │    │            │
│         └─────────────────────────────────────┘    │            │
│                                                    │            │
│                          ▼                         │            │
│                    Response + Sources              │            │
│                                                    │            │
└─────────────────────────────────────────────────────────────────┘
```

## Composants LangChain

### 1. Embeddings (`src/rag/embeddings.py`)

Factory qui retourne un objet `Embeddings` selon le provider configuré :

```python
from src.rag.embeddings import get_embeddings

embeddings = get_embeddings()  # MistralAIEmbeddings ou HuggingFaceEmbeddings
```

| Provider | Classe LangChain | Dimension |
|----------|------------------|-----------|
| `mistral` | `MistralAIEmbeddings` | 1024 |
| `sentence-transformers` | `HuggingFaceEmbeddings` | 768 |

### 2. LLM (`src/rag/llm.py`)

Factory pour créer des instances `ChatMistralAI` :

```python
from src.rag.llm import get_llm

llm = get_llm()  # LLM par défaut (température 0.7)
classifier = get_llm(temperature=0, max_tokens=10)  # Classification déterministe
```

### 3. Vector Store (`src/rag/vectorstore.py`)

Fonctions pour gérer l'index FAISS via LangChain :

```python
from src.rag.vectorstore import load_vectorstore, build_vectorstore, save_vectorstore

# Charger un index existant
vectorstore = load_vectorstore(embeddings, index_dir)

# Construire un nouvel index
vectorstore = build_vectorstore(documents, embeddings, progress_callback)

# Sauvegarder
save_vectorstore(vectorstore, index_dir)
```

### 4. LCEL Chains

Le `RAGEngine` utilise 3 chaînes LCEL :

#### Classification Chain
```python
prompt = ChatPromptTemplate.from_messages([
    ("human", CLASSIFICATION_PROMPT_TEMPLATE),
])
chain = prompt | classification_llm | StrOutputParser()
```

#### Conversation Chain (mode CHAT)
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", CONVERSATION_SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{query}"),
])
chain = prompt | llm | StrOutputParser()
```

#### RAG Chain (mode SEARCH)
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", RAG_SYSTEM_PROMPT_TEMPLATE),  # Contient {context}
    MessagesPlaceholder(variable_name="history"),
    ("human", "{query}"),
])
chain = prompt | llm | StrOutputParser()
```

## Format d'index FAISS

LangChain utilise un format de sérialisation spécifique :

| Fichier | Description |
|---------|-------------|
| `index.faiss` | Index FAISS binaire |
| `index.pkl` | Métadonnées pickle (docstore, mapping) |
| `config.json` | Configuration (provider, dimension, etc.) |

### Migration depuis l'ancien format

L'ancien format (`events.index`, `embeddings.npy`, `metadata.json`) n'est pas compatible. Utilisez le script de migration :

```bash
uv run python scripts/migrate_index.py
```

Le `RAGEngine` supporte les deux formats avec fallback automatique pour une migration progressive.

## Interface publique (inchangée)

L'interface du `RAGEngine` reste identique :

```python
from src.rag.engine import RAGEngine

engine = RAGEngine()

# Classification automatique
result = engine.chat("Concerts ce weekend", top_k=5, history=history)
# Retourne: {"response": str, "sources": list, "query": str, "used_rag": bool}

# Recherche directe
results = engine.search("jazz", top_k=3)
# Retourne: [{"document": {...}, "similarity": float, "distance": float}]

# Classification explicite
needs_search = engine.needs_rag("Bonjour")  # False
needs_search = engine.needs_rag("Quels concerts?")  # True

# Propriétés
engine.num_documents  # Nombre de documents indexés
engine.embedding_dim  # Dimension des embeddings
```

## Dépendances LangChain

```toml
# pyproject.toml
dependencies = [
    "langchain>=0.3.0",
    "langchain-community>=0.3.0",
    "langchain-mistralai>=0.2.0",
    "langchain-huggingface>=0.1.0",
]
```

## Prompts

Les prompts sont définis dans `src/config/constants.py` :

- `CLASSIFICATION_PROMPT_TEMPLATE` : Classification SEARCH/CHAT (few-shot)
- `CONVERSATION_SYSTEM_PROMPT` : Personnalité pour le mode conversationnel
- `RAG_SYSTEM_PROMPT_TEMPLATE` : Prompt avec injection de contexte

## Gestion de l'historique

L'historique est converti automatiquement de `list[dict]` vers les messages LangChain :

```python
# Format d'entrée (API/UI)
history = [
    {"role": "user", "content": "Bonjour"},
    {"role": "assistant", "content": "Salut !"},
]

# Conversion interne
[HumanMessage(content="Bonjour"), AIMessage(content="Salut !")]
```

## Performance

- **Lazy imports** : Les providers d'embeddings sont importés à la demande
- **Batch processing** : L'`IndexBuilder` traite les documents par lots de 32
- **Caching** : Le `RAGEngine` est caché avec `@st.cache_resource` dans Streamlit
- **Fallback legacy** : Support des anciens index pour migration progressive

## Reconstruction de l'index

### Via script
```bash
uv run python scripts/migrate_index.py
```

### Via API
```bash
curl -X POST http://localhost:8000/rebuild \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

### Programmatiquement
```python
from src.rag.index_builder import IndexBuilder

builder = IndexBuilder(progress_callback=lambda msg, pct: print(f"{pct:.0%} {msg}"))
result = builder.rebuild()
```

## Avantages de l'architecture LangChain

1. **Abstraction** : Les providers (Mistral, HuggingFace) sont interchangeables
2. **LCEL** : Chaînes composables et testables
3. **Écosystème** : Accès aux outils LangChain (memory, agents, tools)
4. **Maintenance** : Les mises à jour des providers sont gérées par LangChain
5. **Observabilité** : Compatible avec LangSmith pour le tracing

## Limitations connues

- Le format d'index FAISS LangChain n'est pas compatible avec l'ancien format
- `allow_dangerous_deserialization=True` requis pour charger les index pickle
- Les scores de similarité peuvent différer légèrement de l'implémentation directe
