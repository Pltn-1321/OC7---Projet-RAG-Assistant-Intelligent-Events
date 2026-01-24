# Plan d'intégration LangChain - RAG Events Assistant

## Objectif
Migrer le pipeline RAG de l'intégration directe SDK (Mistral + FAISS) vers LangChain LCEL, tout en conservant l'interface publique identique (API, UI, tests).

---

## Étapes d'implémentation

### Étape 1 : Dépendances (`pyproject.toml`)
- Ajouter `langchain-huggingface>=0.1.0` (remplacement de sentence-transformers direct)
- Les autres dépendances LangChain sont déjà présentes
- Exécuter `uv sync`

### Étape 2 : Module Embeddings - NOUVEAU `src/rag/embeddings.py`
Factory qui retourne un objet `Embeddings` LangChain selon le provider configuré :
- `"mistral"` → `MistralAIEmbeddings` (depuis `langchain_mistralai`)
- `"sentence-transformers"` → `HuggingFaceEmbeddings` (depuis `langchain_huggingface`)

### Étape 3 : Module LLM - NOUVEAU `src/rag/llm.py`
Factory `get_llm()` qui retourne un `ChatMistralAI` configuré avec les settings (model, temperature, max_tokens).

### Étape 4 : Module VectorStore - NOUVEAU `src/rag/vectorstore.py`
- `load_vectorstore(embeddings, index_dir)` → charge via `FAISS.load_local()`
- `build_vectorstore(documents, embeddings, progress_callback)` → construit via `FAISS.from_documents()` avec batch processing pour le suivi de progression

### Étape 5 : Prompts LangChain (`src/config/constants.py`)
Ajouter 3 templates de prompts compatibles LangChain :
- `CLASSIFICATION_PROMPT_TEMPLATE` : classifie SEARCH vs CHAT (few-shot)
- `CONVERSATION_SYSTEM_PROMPT` : personnalité pour le mode conversationnel
- `RAG_SYSTEM_PROMPT_TEMPLATE` : prompt avec `{context}` pour le mode RAG

### Étape 6 : Réécriture RAGEngine (`src/rag/engine.py`)
Réécrire avec LCEL tout en gardant la **même interface publique** :

**Composants internes :**
- `_classification_chain` : `ChatPromptTemplate | ChatMistralAI(temp=0) | StrOutputParser`
- `_conversation_chain` : `ChatPromptTemplate(system + history + query) | ChatMistralAI | StrOutputParser`
- `_rag_chain` : `ChatPromptTemplate(system/context + history + query) | ChatMistralAI | StrOutputParser`

**Méthodes publiques inchangées :**
| Méthode | Signature | Retour |
|---------|-----------|--------|
| `needs_rag(query)` | `str → bool` | Inchangé |
| `encode_query(query)` | `str → np.ndarray` | Inchangé (compat.) |
| `search(query, top_k)` | → `list[dict]` avec `document`, `similarity`, `distance` | Inchangé |
| `generate_response(query, results, history)` | → `str` | Inchangé |
| `conversation_response(query, history)` | → `str` | Inchangé |
| `chat(query, top_k, history)` | → `{"response", "sources", "query", "used_rag"}` | Inchangé |
| `num_documents` (property) | → `int` | Inchangé |
| `embedding_dim` (property) | → `int` | Inchangé |

**Conversions internes :**
- `_convert_history(list[dict])` → `list[HumanMessage | AIMessage]`
- `_format_context(results)` → `str` (formatage des événements)

### Étape 7 : Réécriture IndexBuilder (`src/rag/index_builder.py`)
- `load_documents()` → retourne `list[Document]` (LangChain)
- `build_and_save(documents)` → `FAISS.from_documents()` + `save_local()` + `config.json`
- `rebuild()` → pipeline complet avec stats (interface retour identique)
- Progress callback préservé via batch processing

### Étape 8 : Script de migration - NOUVEAU `scripts/migrate_index.py`
Script one-shot pour reconstruire l'index au format LangChain depuis `rag_documents.json`.

### Étape 9 : Mise à jour des tests
**`tests/unit/test_rag_engine.py`** :
- Changer les cibles de mock : `MistralAIEmbeddings`, `ChatMistralAI`, `FAISS.load_local`
- Vérifier les formats de retour identiques

**NOUVEAU `tests/unit/test_langchain_components.py`** :
- Tests factory embeddings (mistral + huggingface)
- Tests vectorstore loader
- Tests IndexBuilder avec format LangChain

**Tests integration/e2e** : aucun changement (même interface publique)

### Étape 10 : Intégration API/UI
- `src/api/main.py` : aucun changement nécessaire (même interface RAGEngine)
- `app.py` : aucun changement nécessaire

### Étape 11 : Documentation complète
- **NOUVEAU** `docs/INTEGRATION_LANGCHAIN.md` : architecture LangChain, composants utilisés, diagrammes de flux, guide de migration
- **MAJ** `CLAUDE.md` : remplacer les mentions "NOT LangChain" par la nouvelle architecture
- **MAJ** `docs/ARCHITECTURE.md` : mettre à jour diagrammes et descriptions

### Étape 12 : Vérification et nettoyage
- Supprimer les imports directs `mistralai` dans engine.py
- Supprimer les anciens fichiers d'index si présents
- Exécuter la suite de tests complète

---

## Fichiers critiques à modifier/créer

| Fichier | Action |
|---------|--------|
| `src/rag/embeddings.py` | CRÉER |
| `src/rag/llm.py` | CRÉER |
| `src/rag/vectorstore.py` | CRÉER |
| `src/rag/engine.py` | RÉÉCRIRE |
| `src/rag/index_builder.py` | RÉÉCRIRE |
| `src/config/constants.py` | MODIFIER (ajouter prompts) |
| `pyproject.toml` | MODIFIER (ajouter langchain-huggingface) |
| `scripts/migrate_index.py` | CRÉER |
| `tests/unit/test_rag_engine.py` | MODIFIER |
| `tests/unit/test_langchain_components.py` | CRÉER |
| `docs/INTEGRATION_LANGCHAIN.md` | CRÉER |
| `CLAUDE.md` | MODIFIER |

---

## Composants LangChain utilisés

| Besoin | Classe LangChain | Import |
|--------|------------------|--------|
| LLM | `ChatMistralAI` | `langchain_mistralai` |
| Embeddings Mistral | `MistralAIEmbeddings` | `langchain_mistralai` |
| Embeddings HuggingFace | `HuggingFaceEmbeddings` | `langchain_huggingface` |
| Vector Store | `FAISS` | `langchain_community.vectorstores` |
| Documents | `Document` | `langchain_core.documents` |
| Prompts | `ChatPromptTemplate`, `MessagesPlaceholder` | `langchain_core.prompts` |
| Messages | `HumanMessage`, `AIMessage`, `SystemMessage` | `langchain_core.messages` |
| Output | `StrOutputParser` | `langchain_core.output_parsers` |
| Runnables | `RunnablePassthrough`, `RunnableLambda` | `langchain_core.runnables` |

---

## Point d'attention : Format d'index FAISS

Le format de sérialisation change :
- **Ancien** : `events.index` + `config.json` + `embeddings.npy` + `metadata.json`
- **Nouveau** : `index.faiss` + `index.pkl` (format LangChain `save_local`/`load_local`)

Un **re-indexing** est requis après migration. La source (`rag_documents.json`) reste identique.

---

## Vérification end-to-end

1. `uv sync` — installer les dépendances
2. `uv run python scripts/migrate_index.py` — reconstruire l'index au format LangChain
3. `uv run pytest tests/unit/` — tests unitaires
4. `uv run streamlit run app.py` — vérifier l'interface Streamlit
5. `uv run uvicorn src.api.main:app --reload` — vérifier l'API FastAPI
6. Tester manuellement : poser une question événementielle + une question conversationnelle
7. `uv run pytest` — suite de tests complète
