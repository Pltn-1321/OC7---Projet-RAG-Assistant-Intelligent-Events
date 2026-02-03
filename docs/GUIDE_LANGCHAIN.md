# Guide Pédagogique LangChain - Cas Pratique RAG Events

Ce guide explique LangChain en utilisant ce projet de chatbot RAG comme exemple concret.

---

## Table des matières

1. [Qu'est-ce que LangChain ?](#1-quest-ce-que-langchain-)
2. [Pourquoi migrer vers LangChain ?](#2-pourquoi-migrer-vers-langchain-)
3. [L'architecture de LangChain](#3-larchitecture-de-langchain)
4. [LCEL - LangChain Expression Language](#4-lcel---langchain-expression-language)
   - [4.bis LCEL en profondeur](#4bis-lcel-en-profondeur)
5. [Les composants dans ce projet](#5-les-composants-dans-ce-projet)
6. [Comparaison Avant/Après](#6-comparaison-avantaprès)
7. [Construire des chaînes LCEL](#7-construire-des-chaînes-lcel)
8. [Erreurs courantes et pièges](#8-erreurs-courantes-et-pièges-à-éviter)
9. [Glossaire](#9-glossaire)

---

## 1. Qu'est-ce que LangChain ?

### En une phrase
LangChain est un **framework** qui standardise la façon de connecter des LLMs à des sources de données et des outils.

### L'analogie des briques LEGO

Imagine que tu construis un pipeline de données :

```
Sans LangChain (code SDK direct) :
┌──────────────────────────────────────────────────────────────┐
│  Code "à la main" - chaque pièce est faite sur mesure       │
│                                                              │
│  mistralai.Mistral() ──► API call manuel ──► Parse réponse  │
│  faiss.read_index() ──► .search() ──► Format résultats      │
│  sentence_transformers ──► encode() ──► normalise numpy     │
└──────────────────────────────────────────────────────────────┘

Avec LangChain :
┌──────────────────────────────────────────────────────────────┐
│  Briques standardisées qui s'emboîtent                       │
│                                                              │
│  [Embeddings] ──► [VectorStore] ──► [LLM] ──► [OutputParser]│
│       │                │              │              │       │
│   Interface         Interface      Interface      Interface  │
│   commune            commune        commune        commune    │
└──────────────────────────────────────────────────────────────┘
```

**Le principe clé** : Chaque composant respecte une **interface standard**. Tu peux remplacer `MistralAIEmbeddings` par `HuggingFaceEmbeddings` sans changer le reste du code.

---

## 2. Pourquoi migrer vers LangChain ?

### Les avantages concrets pour ce projet

| Aspect | Code SDK direct | Avec LangChain |
|--------|-----------------|----------------|
| **Changer de LLM** | Réécrire toute la logique d'appel | Changer une ligne (le modèle) |
| **Changer d'embeddings** | Gérer 2 APIs différentes manuellement | Factory avec interface commune |
| **Combiner des étapes** | Code impératif, beaucoup de glue code | Opérateur `|` (pipe) composable |
| **Streaming** | Implémenter manuellement | `.stream()` intégré |
| **Debugging** | print/logs manuels | LangSmith tracing intégré |
| **Tests** | Mock complexe de chaque API | Mock d'interfaces standard |

### Ce que LangChain n'est PAS

- ❌ **Pas une API de plus** : C'est une couche d'abstraction au-dessus des APIs
- ❌ **Pas obligatoire** : Le code SDK direct fonctionne très bien
- ❌ **Pas magique** : Tu dois quand même comprendre ce qui se passe

---

## 3. L'architecture de LangChain

### Les packages principaux

```
langchain-core          ← Interfaces de base (Embeddings, LLM, Runnable)
├── langchain-mistralai ← Implémentations Mistral (ChatMistralAI, MistralAIEmbeddings)
├── langchain-huggingface ← Implémentations HuggingFace (HuggingFaceEmbeddings)
└── langchain-community ← Intégrations communauté (FAISS, etc.)
```

### Les composants fondamentaux

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPOSANTS LANGCHAIN                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ╔═══════════════╗    Convertit texte → vecteurs numériques    │
│  ║  Embeddings   ║    Ex: MistralAIEmbeddings, HuggingFaceEmb  │
│  ╚═══════════════╝                                              │
│         │                                                       │
│         ▼                                                       │
│  ╔═══════════════╗    Stocke et recherche dans les vecteurs    │
│  ║  VectorStore  ║    Ex: FAISS, Chroma, Pinecone              │
│  ╚═══════════════╝                                              │
│         │                                                       │
│         ▼                                                       │
│  ╔═══════════════╗    Génère du texte à partir d'un prompt     │
│  ║  Chat Model   ║    Ex: ChatMistralAI, ChatOpenAI            │
│  ╚═══════════════╝                                              │
│         │                                                       │
│         ▼                                                       │
│  ╔═══════════════╗    Formate la sortie du LLM                 │
│  ║ OutputParser  ║    Ex: StrOutputParser, JsonOutputParser    │
│  ╚═══════════════╝                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. LCEL - LangChain Expression Language

### Le concept central

LCEL est la syntaxe qui permet de **chaîner des composants** avec l'opérateur `|` (pipe).

```python
# Syntaxe LCEL
chain = prompt | llm | output_parser

# Équivalent "à la main"
prompt_text = prompt.format(query=query)
llm_response = llm.invoke(prompt_text)
result = output_parser.parse(llm_response)
```

### Comment ça marche ?

Chaque composant LangChain implémente l'interface `Runnable` :

```python
class Runnable:
    def invoke(self, input) -> output:    # Exécution synchrone
        ...
    def stream(self, input) -> Iterator:  # Exécution en streaming
        ...
    def batch(self, inputs) -> list:      # Exécution par lots
        ...
```

L'opérateur `|` connecte la sortie d'un `Runnable` à l'entrée du suivant :

```
┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
│ Prompt │ ──► │  LLM   │ ──► │ Parser │ ──► │ Résult │
└────────┘     └────────┘     └────────┘     └────────┘
    │              │              │              │
   str      ChatPromptValue   AIMessage        str
  (input)      (→ LLM)        (→ Parser)    (output)
```

### Exemple concret

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_mistralai import ChatMistralAI

# 1. Définir le prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant pour événements culturels."),
    ("human", "{query}")
])

# 2. Créer le LLM
llm = ChatMistralAI(model="mistral-small-latest", temperature=0.7)

# 3. Créer le parser (extrait le texte de AIMessage)
parser = StrOutputParser()

# 4. CHAÎNER avec LCEL
chain = prompt | llm | parser

# 5. Utiliser
response = chain.invoke({"query": "Que faire ce weekend ?"})
```

---

## 4.bis. LCEL en profondeur

### Comment fonctionne l'opérateur `|` ?

Quand tu écris `a | b`, Python appelle `a.__or__(b)`. LangChain surcharge cet opérateur pour créer une `RunnableSequence` :

```python
# Ce que tu écris
chain = prompt | llm | parser

# Ce que Python fait réellement
chain = RunnableSequence(steps=[prompt, llm, parser])
```

La `RunnableSequence` exécute chaque étape dans l'ordre, passant la sortie de l'une à l'entrée de la suivante.

### Visualisation du flux de données

Prenons une chaîne de classification comme exemple :

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FLUX DE DONNÉES - Classification                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ENTRÉE                                                                  │
│  {"query": "concerts ce weekend"}                                        │
│         │                                                                │
│         ▼                                                                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ ChatPromptTemplate                                                │   │
│  │                                                                   │   │
│  │ Prend: dict avec clé "query"                                     │   │
│  │ Retourne: ChatPromptValue (liste de messages formatés)           │   │
│  │                                                                   │   │
│  │ Template: "Analyse cette requête: {query}..."                    │   │
│  │ Résultat: [HumanMessage("Analyse cette requête: concerts...")]   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│         │                                                                │
│         ▼ ChatPromptValue                                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ ChatMistralAI (temperature=0)                                     │   │
│  │                                                                   │   │
│  │ Prend: ChatPromptValue ou list[BaseMessage]                      │   │
│  │ Retourne: AIMessage                                               │   │
│  │                                                                   │   │
│  │ Appelle l'API Mistral avec les messages                          │   │
│  │ Résultat: AIMessage(content="SEARCH")                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│         │                                                                │
│         ▼ AIMessage                                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ StrOutputParser                                                   │   │
│  │                                                                   │   │
│  │ Prend: AIMessage                                                 │   │
│  │ Retourne: str                                                     │   │
│  │                                                                   │   │
│  │ Extrait: message.content                                         │   │
│  │ Résultat: "SEARCH"                                               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│         │                                                                │
│         ▼                                                                │
│  SORTIE                                                                  │
│  "SEARCH"                                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Les types de données entre chaque étape

C'est **crucial** de comprendre quel type circule :

```python
# Prompt → Chat Model
ChatPromptTemplate.invoke({"query": "..."})
# Retourne: ChatPromptValue (convertible en List[BaseMessage])

# Chat Model → Parser
ChatMistralAI.invoke(messages)
# Retourne: AIMessage(content="...", ...)

# Parser → Résultat
StrOutputParser.invoke(ai_message)
# Retourne: str (juste le content)
```

### RunnableLambda : Transformer les données

Quand tu as besoin de logique personnalisée entre les étapes :

```python
from langchain_core.runnables import RunnableLambda

# Exemple : transformer la sortie avant de la passer au LLM
def add_context(inputs: dict) -> dict:
    """Ajoute le contexte des événements aux inputs."""
    events = inputs.get("events", [])
    context = "\n".join(f"- {e['title']}" for e in events)
    return {**inputs, "context": context}

# Utilisation dans une chaîne
chain = (
    RunnableLambda(add_context)  # Transforme inputs → inputs avec context
    | prompt                      # Utilise {context} dans le template
    | llm
    | parser
)
```

### RunnablePassthrough : Préserver des données

Parfois tu veux garder l'input original tout en ajoutant des choses :

```python
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

# Pattern : garder la query ET ajouter les résultats de recherche
chain = RunnableParallel(
    query=RunnablePassthrough(),           # Garde l'input tel quel
    results=retriever,                      # Cherche dans le vectorstore
) | prompt | llm | parser

# Quand tu appelles chain.invoke("concerts weekend")
# Le prompt reçoit: {"query": "concerts weekend", "results": [Document, ...]}
```

### Pattern complet : Classification + Routing

Voici comment implémenter un pipeline `chat()` avec LCEL :

```python
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough

class RAGEngine:
    def __init__(self):
        # Chaîne 1 : Classification
        self._classification_chain = (
            ChatPromptTemplate.from_template(CLASSIFICATION_PROMPT)
            | get_llm(temperature=0, max_tokens=10)
            | StrOutputParser()
        )

        # Chaîne 2 : Mode conversationnel (sans RAG)
        self._conversation_chain = (
            ChatPromptTemplate.from_messages([
                ("system", CONVERSATION_SYSTEM_PROMPT),
                MessagesPlaceholder("history", optional=True),
                ("human", "{query}")
            ])
            | get_llm()
            | StrOutputParser()
        )

        # Chaîne 3 : Mode RAG
        self._rag_chain = (
            ChatPromptTemplate.from_messages([
                ("system", RAG_SYSTEM_PROMPT),  # Inclut {context}
                MessagesPlaceholder("history", optional=True),
                ("human", "{query}")
            ])
            | get_llm()
            | StrOutputParser()
        )

    def chat(self, query: str, top_k: int = 5, history: list | None = None) -> dict:
        # Étape 1 : Classifier
        classification = self._classification_chain.invoke({"query": query})
        use_rag = "SEARCH" in classification.upper()

        # Étape 2 : Router vers la bonne chaîne
        if use_rag:
            # Recherche + génération
            results = self._vectorstore.similarity_search_with_score(query, k=top_k)
            context = self._format_context(results)
            response = self._rag_chain.invoke({
                "query": query,
                "context": context,
                "history": self._convert_history(history or [])
            })
            sources = self._format_sources(results)
        else:
            # Conversation simple
            response = self._conversation_chain.invoke({
                "query": query,
                "history": self._convert_history(history or [])
            })
            sources = []

        return {
            "response": response,
            "sources": sources,
            "query": query,
            "used_rag": use_rag
        }
```

### Alternative : Tout en une chaîne avec RunnableBranch

Pour les puristes LCEL (plus complexe, moins lisible) :

```python
def _route_query(inputs: dict) -> str:
    """Détermine quelle chaîne utiliser."""
    classification = self._classification_chain.invoke({"query": inputs["query"]})
    return "rag" if "SEARCH" in classification.upper() else "chat"

# Chaîne unique avec routing
self._unified_chain = RunnableBranch(
    (
        lambda x: _route_query(x) == "rag",
        self._prepare_rag_context | self._rag_chain
    ),
    self._conversation_chain  # Default: chat
)
```

**Conseil** : La version explicite (if/else) est plus claire. LCEL brille pour les pipelines linéaires, pas pour la logique métier complexe.

### Streaming avec LCEL

Le streaming fonctionne automatiquement si le LLM le supporte :

```python
# Au lieu de .invoke(), utilise .stream()
for chunk in self._rag_chain.stream({"query": query, "context": context}):
    print(chunk, end="", flush=True)  # Affiche token par token

# Dans Streamlit
with st.chat_message("assistant"):
    response = st.write_stream(self._rag_chain.stream(inputs))
```

### Debugging des chaînes

**Méthode 1 : Inspecter les étapes**

```python
# Voir les étapes d'une chaîne
print(chain.steps)  # Liste des Runnables

# Voir le schéma d'input/output
print(chain.input_schema.schema())
print(chain.output_schema.schema())
```

**Méthode 2 : Callback handlers**

```python
from langchain_core.callbacks import StdOutCallbackHandler

# Affiche tout ce qui se passe
chain.invoke(inputs, config={"callbacks": [StdOutCallbackHandler()]})
```

**Méthode 3 : LangSmith (recommandé pour production)**

```bash
# Dans .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
```

### Tester les chaînes LCEL

```python
import pytest
from unittest.mock import Mock, patch

def test_classification_chain():
    """Test que la chaîne de classification retourne SEARCH ou CHAT."""
    engine = RAGEngine()

    # Mock le LLM pour contrôler la sortie
    with patch.object(engine._classification_chain, 'invoke') as mock_invoke:
        mock_invoke.return_value = "SEARCH"

        result = engine.needs_rag("concerts ce weekend")

        assert result is True
        mock_invoke.assert_called_once()

def test_rag_chain_formatting():
    """Test que le contexte est bien injecté."""
    engine = RAGEngine()

    # On peut tester le prompt template isolément
    prompt_value = engine._rag_chain.first.invoke({
        "query": "test",
        "context": "Event 1: Concert",
        "history": []
    })

    # Vérifie que le contexte apparaît dans les messages
    messages = prompt_value.to_messages()
    system_msg = messages[0].content
    assert "Event 1: Concert" in system_msg
```

---

## 5. Les composants dans ce projet

### 5.1 Embeddings (`src/rag/embeddings.py`)

```python
# Pattern Factory pour les embeddings
def get_embeddings() -> Embeddings:
    if settings.embedding_provider == "mistral":
        return MistralAIEmbeddings(model="mistral-embed", api_key=...)
    else:
        return HuggingFaceEmbeddings(model_name="paraphrase-multilingual-mpnet-base-v2")
```

**Pourquoi c'est bien** :
- Interface commune `Embeddings` avec méthode `.embed_query(text)` et `.embed_documents(texts)`
- Le reste du code ne sait pas quel provider est utilisé
- Changement de provider = changement dans settings, pas dans le code

### 5.2 LLM (`src/rag/llm.py`)

```python
def get_llm(temperature=None, max_tokens=None) -> ChatMistralAI:
    return ChatMistralAI(
        model=settings.llm_model,
        temperature=temperature or settings.llm_temperature,
        max_tokens=max_tokens or settings.max_tokens,
    )
```

**Méthodes disponibles** :
- `.invoke(messages)` → Réponse complète
- `.stream(messages)` → Générateur token par token
- `.batch([messages1, messages2])` → Plusieurs requêtes en parallèle

### 5.3 VectorStore (`src/rag/vectorstore.py`)

```python
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Charger un index existant
def load_vectorstore(embeddings, index_dir):
    return FAISS.load_local(
        str(index_dir),
        embeddings,
        allow_dangerous_deserialization=True  # Requis pour pickle
    )

# Créer un nouvel index
def build_vectorstore(documents: list[Document], embeddings):
    return FAISS.from_documents(documents, embeddings)
```

**Méthodes importantes** :
- `.similarity_search(query, k=5)` → Retourne les k documents les plus similaires
- `.similarity_search_with_score(query, k=5)` → Avec les scores de distance
- `.save_local(path)` / `.load_local(path)` → Persistance

### 5.4 Documents LangChain

```python
from langchain_core.documents import Document

# Un Document LangChain a deux attributs
doc = Document(
    page_content="Concert de jazz au Dôme ce samedi...",  # Le texte à indexer
    metadata={"id": "evt_123", "category": "concert"}     # Métadonnées
)
```

### 5.5 Prompts et Messages

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Template simple
prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant événements."),
    ("human", "{query}")
])

# Template avec historique dynamique
prompt_with_history = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant événements."),
    MessagesPlaceholder("history"),  # ← Injecté dynamiquement
    ("human", "{query}")
])

# Utilisation
messages = prompt_with_history.invoke({
    "query": "Et pour dimanche ?",
    "history": [
        HumanMessage(content="Que faire samedi ?"),
        AIMessage(content="Je te recommande le concert au Dôme...")
    ]
})
```

---

## 6. Comparaison Avant/Après

### Classification de requête (SEARCH vs CHAT)

**AVANT (SDK direct)** :

```python
def needs_rag(self, query: str) -> bool:
    classification_prompt = """Analyse cette requête..."""

    # Appel SDK Mistral direct
    response = self.mistral_client.chat.complete(
        model=settings.llm_model,
        messages=[{"role": "user", "content": classification_prompt.format(query=query)}],
        temperature=0,
        max_tokens=10,
    )
    result = response.choices[0].message.content.strip().upper()
    return "SEARCH" in result
```

**APRÈS (avec LCEL)** :

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def __init__(self):
    # Chaîne de classification (température 0 = déterministe)
    self._classification_chain = (
        ChatPromptTemplate.from_template(CLASSIFICATION_PROMPT_TEMPLATE)
        | get_llm(temperature=0, max_tokens=10)
        | StrOutputParser()
    )

def needs_rag(self, query: str) -> bool:
    result = self._classification_chain.invoke({"query": query})
    return "SEARCH" in result.upper()
```

**Ce qui change** :
- Le prompt est un objet réutilisable (`ChatPromptTemplate`)
- La logique de chaînage est déclarative (pas d'appel `.chat.complete()` manuel)
- Plus facile à tester (mock de `_classification_chain`)

---

### Recherche sémantique

**AVANT (SDK direct)** :

```python
def search(self, query: str, top_k: int = 5) -> list[dict]:
    # Encoder manuellement
    query_embedding = self.encode_query(query)

    # Appel FAISS direct
    distances, indices = self.index.search(query_embedding, top_k)

    # Formater les résultats manuellement
    results = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx < len(self.documents):
            results.append({
                "document": self.documents[idx],
                "similarity": float(1 - dist),
                "distance": float(dist),
            })
    return results
```

**APRÈS (avec LangChain FAISS)** :

```python
def __init__(self):
    embeddings = get_embeddings()
    self._vectorstore = FAISS.load_local(index_dir, embeddings)

def search(self, query: str, top_k: int = 5) -> list[dict]:
    # Une seule ligne !
    docs_with_scores = self._vectorstore.similarity_search_with_score(query, k=top_k)

    # Même format de retour pour compatibilité
    return [
        {
            "document": {"content": doc.page_content, **doc.metadata},
            "similarity": float(1 - score),
            "distance": float(score),
        }
        for doc, score in docs_with_scores
    ]
```

**Ce qui change** :
- Pas besoin de gérer `encode_query()` manuellement (le VectorStore le fait)
- Pas de manipulation numpy/FAISS directe
- Format `Document` standardisé avec `page_content` et `metadata`

---

### Génération de réponse RAG

**AVANT (SDK direct)** :

```python
def generate_response(self, query, results, history=None):
    # Construire le contexte manuellement
    context = "Événements pertinents :\n\n"
    for i, result in enumerate(results, 1):
        context += f"Événement {i}:\n{result['document']['content']}\n\n"

    system_prompt = f"""Tu es un assistant... {context}"""

    # Construire messages manuellement
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": query})

    # Appel SDK direct
    response = self.mistral_client.chat.complete(
        model=settings.llm_model,
        messages=messages,
        temperature=settings.llm_temperature,
    )
    return response.choices[0].message.content
```

**APRÈS (avec LCEL)** :

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda

def __init__(self):
    self._rag_chain = (
        ChatPromptTemplate.from_messages([
            ("system", RAG_SYSTEM_PROMPT_TEMPLATE),  # Contient {context}
            MessagesPlaceholder("history", optional=True),
            ("human", "{query}")
        ])
        | get_llm()
        | StrOutputParser()
    )

def generate_response(self, query, results, history=None):
    context = self._format_context(results)
    lc_history = self._convert_history(history or [])

    return self._rag_chain.invoke({
        "query": query,
        "context": context,
        "history": lc_history
    })
```

---

## 7. Construire des chaînes LCEL

### Pattern 1 : Chaîne linéaire simple

```python
chain = prompt | llm | parser
```

### Pattern 2 : Avec transformation intermédiaire

```python
from langchain_core.runnables import RunnableLambda

# Fonction de transformation
def format_output(text: str) -> dict:
    return {"response": text, "length": len(text)}

chain = prompt | llm | parser | RunnableLambda(format_output)
```

### Pattern 3 : Branches conditionnelles

```python
from langchain_core.runnables import RunnableBranch

# Chaîne avec routing
chain = RunnableBranch(
    (lambda x: x["type"] == "search", rag_chain),    # Si type=search → RAG
    (lambda x: x["type"] == "chat", chat_chain),     # Si type=chat → Chat
    default_chain                                     # Sinon → défaut
)
```

### Pattern 4 : Parallélisation

```python
from langchain_core.runnables import RunnableParallel

# Exécuter plusieurs chaînes en parallèle
chain = RunnableParallel(
    classification=classification_chain,
    embedding=embedding_chain,
)
# Retourne {"classification": ..., "embedding": ...}
```

---

## 8. Erreurs courantes et pièges à éviter

### Piège 1 : Mauvais type d'input

```python
# ❌ ERREUR : passer une string au lieu d'un dict
chain.invoke("ma question")

# ✅ CORRECT : le template attend un dict avec les clés
chain.invoke({"query": "ma question"})
```

### Piège 2 : Oublier que les chaînes sont immutables

```python
# ❌ ERREUR : on ne peut pas modifier une chaîne après création
chain = prompt | llm
chain.add(parser)  # N'existe pas !

# ✅ CORRECT : créer une nouvelle chaîne
chain = prompt | llm | parser
```

### Piège 3 : Confondre ChatPromptTemplate et PromptTemplate

```python
# ❌ ERREUR : PromptTemplate retourne une string, pas des messages
prompt = PromptTemplate.from_template("Question: {query}")
chain = prompt | llm  # Le LLM attend des messages !

# ✅ CORRECT : ChatPromptTemplate pour les Chat Models
prompt = ChatPromptTemplate.from_messages([
    ("human", "Question: {query}")
])
```

### Piège 4 : MessagesPlaceholder vide

```python
# ❌ ERREUR : si history est None, ça plante
prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant."),
    MessagesPlaceholder("history"),  # Obligatoire !
    ("human", "{query}")
])
prompt.invoke({"query": "test", "history": None})  # KeyError !

# ✅ CORRECT : marquer comme optionnel
prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant."),
    MessagesPlaceholder("history", optional=True),  # ← Ajouter optional=True
    ("human", "{query}")
])
```

### Piège 5 : Format des messages d'historique

```python
# ❌ ERREUR : dict au lieu de BaseMessage
history = [
    {"role": "user", "content": "Bonjour"},
    {"role": "assistant", "content": "Salut !"}
]

# ✅ CORRECT : utiliser les classes LangChain
from langchain_core.messages import HumanMessage, AIMessage

history = [
    HumanMessage(content="Bonjour"),
    AIMessage(content="Salut !")
]
```

### Piège 6 : FAISS allow_dangerous_deserialization

```python
# ❌ ERREUR : par défaut, load_local refuse le pickle
vectorstore = FAISS.load_local(index_dir, embeddings)
# ValueError: allow_dangerous_deserialization must be True

# ✅ CORRECT : activer explicitement (après avoir vérifié la source)
vectorstore = FAISS.load_local(
    index_dir,
    embeddings,
    allow_dangerous_deserialization=True  # ⚠️ Seulement pour fichiers de confiance
)
```

### Piège 7 : Dimensions d'embeddings incompatibles

```python
# ❌ ERREUR : l'index a été créé avec Mistral (1024 dims)
# mais tu charges avec HuggingFace (768 dims)
embeddings = HuggingFaceEmbeddings(...)  # 768 dimensions
vectorstore = FAISS.load_local(index_dir, embeddings)
# RuntimeError: dimension mismatch

# ✅ CORRECT : utiliser le même provider qu'à la création
# Vérifier config.json pour connaître le provider original
```

---

## 9. Glossaire

| Terme | Définition |
|-------|------------|
| **LCEL** | LangChain Expression Language - syntaxe déclarative avec `\|` |
| **Runnable** | Interface de base de tous les composants LangChain |
| **RunnableSequence** | Chaîne créée par l'opérateur `\|`, exécute les étapes en série |
| **RunnableParallel** | Exécute plusieurs Runnables en parallèle, retourne un dict |
| **RunnableLambda** | Wraps une fonction Python pour l'utiliser dans une chaîne |
| **RunnablePassthrough** | Passe l'input tel quel (utile avec RunnableParallel) |
| **RunnableBranch** | Routing conditionnel entre plusieurs chaînes |
| **Chain** | Séquence de Runnables connectés |
| **Embeddings** | Classe qui convertit texte → vecteurs |
| **VectorStore** | Base de données de vecteurs (FAISS, Chroma, etc.) |
| **Chat Model** | LLM avec format messages (system/human/assistant) |
| **Document** | Objet avec `page_content` et `metadata` |
| **ChatPromptTemplate** | Template qui produit une liste de messages |
| **MessagesPlaceholder** | Emplacement pour injecter un historique dynamique |
| **StrOutputParser** | Extrait le texte brut d'un AIMessage |
| **BaseMessage** | Classe parente de HumanMessage, AIMessage, SystemMessage |

---

## Ressources

- [Documentation officielle LCEL](https://python.langchain.com/docs/expression_language/)
- [LangChain Mistral Integration](https://python.langchain.com/docs/integrations/chat/mistral/)
- [FAISS VectorStore](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
