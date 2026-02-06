# Soutenance - Questions/Réponses Techniques
## RAG Chatbot Événements Culturels

> **Sheetcode ultra-condensé pour préparation orale**
> Focus : Backend, RAG, FAISS, Embeddings, Architecture

---

## 📐 SECTION 1 : ARCHITECTURE RAG & PIPELINE

### **Q1 : Qu'est-ce que le RAG et pourquoi avoir choisi cette architecture ?**

→ **RAG** (Retrieval-Augmented Generation) = technique qui combine recherche sémantique (retrieval) + génération LLM. Au lieu de fine-tuner un modèle (coûteux, statique), on injecte du **contexte externe** (événements) dans le prompt du LLM à chaque requête.
→ **Avantages** : Données actualisables en temps réel, traçabilité des sources (pas d'hallucinations), coût réduit vs fine-tuning. Idéal pour événements culturels changeants (Open Agenda).

---

### **Q2 : Comment fonctionne votre pipeline dual-mode (CHAT vs SEARCH) ?**

→ **Classification intelligente** : Chaque requête passe d'abord par `needs_rag()` qui utilise un LLM (température 0 = déterministe) pour détecter si c'est une recherche d'événements (**SEARCH**) ou conversation générale (**CHAT**).
→ **CHAT** : Réponse directe LLM sans recherche FAISS (ex: "Bonjour", "Merci").
→ **SEARCH** : Pipeline RAG complet → encode query → FAISS search (top-k=5) → inject context → LLM generate.
→ **Performance** : Économise 50-70% appels FAISS pour queries non-RAG, maintient UX conversationnelle naturelle.

---

### **Q3 : Pourquoi utiliser LangChain LCEL plutôt qu'une implémentation custom ?**

→ **LCEL** (LangChain Expression Language) = syntaxe déclarative pour composer des chaînes : `chain = prompt | llm | parser`.
→ **Avantages** : Portabilité (changement provider facile), abstractions standardisées (MessagesPlaceholder pour historique), support natif vectorstores (FAISS, Pinecone).
→ **Inconvénient** : Overhead performance ~10% vs custom, dépendance externe.
→ **3 chaînes LCEL** : `_classification_chain`, `_conversation_chain`, `_rag_chain` (voir `engine.py:96-126`).

---

### **Q4 : Décrivez le flux complet d'une requête /chat**

→ **Étapes** :
1. **FastAPI** reçoit POST /chat (query, session_id, top_k)
2. **Session management** : Récupère ou crée session PostgreSQL, charge historique (MAX_HISTORY=5 derniers messages)
3. **RAGEngine.chat()** :
   - Classification `needs_rag()` → SEARCH ou CHAT
   - Si SEARCH : encode query (Mistral-embed) → FAISS search (top-k=5) → format context → RAG chain
   - Si CHAT : conversation chain direct (pas de FAISS)
4. **Response** : Génération LLM (température 0.7) + sources (si RAG)
5. **Persistence** : Sauvegarde user + assistant messages en DB avec latency_ms, sources JSON

---

### **Q5 : Comment fonctionne la classification de requêtes (needs_rag) ?**

→ **Prompt CLASSIFICATION_PROMPT_TEMPLATE** : "Analyse cette requête et réponds uniquement par 'SEARCH' ou 'CHAT'". Exemples fournis ("Bonjour" → CHAT, "Concerts Paris" → SEARCH).
→ **LLM config** : `ChatMistralAI(temperature=0, max_tokens=10)` = déterministe, réponse binaire.
→ **Chaîne LCEL** : `prompt | classification_llm | StrOutputParser()` → détecte "SEARCH" dans output.
→ **Accuracy** : 100% sur dataset test (12/12 questions correctement classées).

---

### **Q6 : Comment gérez-vous l'historique conversationnel ?**

→ **Stockage** : PostgreSQL avec modèle `MessageModel` (session_id, role, content, created_at, sources JSON).
→ **Limite** : `MAX_HISTORY = 5` paires user+assistant (10 messages max) pour éviter dépassement tokens.
→ **Conversion** : Fonction `_convert_history()` transforme `{"role": "user", "content": "..."}` → `HumanMessage` / `AIMessage` (format LangChain).
→ **Injection LCEL** : `MessagesPlaceholder(variable_name="history")` dans prompts conversation/RAG injecte historique dans contexte LLM.

---

## 🔍 SECTION 2 : FAISS & EMBEDDINGS

### **Q7 : Qu'est-ce que FAISS et pourquoi l'utiliser vs Pinecone/ChromaDB ?**

→ **FAISS** (Facebook AI Similarity Search) = bibliothèque C++ optimisée pour recherche vectorielle haute performance. IndexFlatL2 = recherche exhaustive avec distance L2 euclidienne.
→ **Avantages** : Gratuit, local (pas de cloud), ultra-rapide (50-100ms pour 497 docs), contrôle total données.
→ **vs Pinecone** : Cloud, payant, scalable (millions vecteurs) mais vendor lock-in.
→ **vs ChromaDB** : Plus simple mais moins performant (~2x plus lent).
→ **Choix** : Pour 497 événements, FAISS in-memory largement suffisant.

---

### **Q8 : Quelle est la structure de votre index FAISS ?**

→ **Type** : `IndexFlatL2` = exhaustive search (pas de quantization), garantit précision maximale.
→ **Format LangChain** : 3 fichiers créés par `save_local()` :
   - `index.faiss` : Index binaire FAISS
   - `index.pkl` : Docstore + mapping (pickle serialization)
   - `config.json` : Métadonnées custom (nombre docs, timestamp, provider)
→ **Dimension** : 1024d (mistral-embed)
→ **Normalisation** : Vecteurs normalisés L2 (`faiss.normalize_L2()`) pour conversion distance → similarité cosinus.

---

### **Q9 : Pourquoi mistral-embed 1024d plutôt que sentence-transformers 768d ?**

→ **mistral-embed** : Modèle Mistral AI spécialisé français, 1024 dimensions, **sémantique riche** (contexte culturel français natif).
→ **vs sentence-transformers** : 768d, multilingue généraliste mais moins performant sur nuances françaises.
→ **Trade-off** : 1024d = +33% mémoire vs 768d, mais qualité sémantique supérieure pour événements culturels français.
→ **API unifiée** : Mistral embed + LLM même provider (simplification gestion clés API).

---

### **Q10 : Comment calculez-vous le score de similarité affiché dans le chat ?**

→ **FAISS retourne distance L2** (plus petit = plus proche). Formule conversion : `similarity = 1 - distance_L2`.
→ **Exemple** : distance=0.2 → similarity=0.8 = **80%** affiché.
→ **Normalisation L2** : Pour vecteurs normalisés, distance L2 ∈ [0, 2]. En pratique résultats pertinents < 1 donc similarity > 0%.
→ **Code** (`engine.py:232`) : `"similarity": float(1 - score)  # L2 distance to similarity`.
→ **Frontend** : `formatSimilarity(score) = (score * 100).toFixed(1) + "%"`.

---

### **Q11 : Pourquoi normaliser les vecteurs avec faiss.normalize_L2() ?**

→ **Sans normalisation** : Distance L2 biaisée par magnitude (vecteurs longs > courts même si sémantiquement proches).
→ **Avec normalisation** : `||a|| = ||b|| = 1` → distance L2 équivalente à **similarité cosinus** : `||a-b||² = 2 - 2·cos(θ)`.
→ **Avantage** : Comparaison purement sémantique (angle entre vecteurs), indépendante de la longueur texte.
→ **Application** : `encode_query()` (ligne 204) normalise query, `IndexBuilder` normalise documents avant indexation.

---

### **Q12 : Comment fonctionne le rebuild de l'index FAISS ?**

→ **Endpoint** : POST `/rebuild` avec authentification `X-API-Key` (header).
→ **BackgroundTask** : Opération longue (30-60s) exécutée en async, retour immédiat 202 Accepted + task_id.
→ **Pipeline** :
   1. `IndexBuilder.load_documents()` → charge `rag_documents.json`
   2. Batch embedding (32 docs/batch) avec progress callbacks (0-100%)
   3. `FAISS.from_documents()` + `add_documents()` (batching)
   4. `save_local()` → index.faiss + index.pkl + config.json
   5. `get_rag_engine.cache_clear()` → reload index dans RAGEngine
→ **Sécurité** : Vérifie REBUILD_API_KEY (HTTPException 401 si invalide).

---

## 🤖 SECTION 3 : LLM & API

### **Q13 : Quel LLM utilisez-vous et pourquoi Mistral vs OpenAI ?**

→ **LLM** : `mistral-small-latest` (ChatMistralAI wrapper LangChain).
→ **Avantages Mistral** :
   - Français natif (meilleure qualité réponses culturelles)
   - Prix : ~2x moins cher qu'OpenAI GPT-4
   - Souveraineté européenne (RGPD, données EU)
   - API unifiée embeddings + LLM (gestion simplifiée)
→ **vs OpenAI GPT-4** : Plus cher, américain, mais écosystème plus mature.
→ **Alternative Mistral** : `mistral-large` (plus précis, +50% coût).

---

### **Q14 : Pourquoi température 0.7 pour génération et 0 pour classification ?**

→ **Température** = paramètre randomness LLM (0 = déterministe, 2 = très créatif).
→ **Classification (temp=0)** : Sortie binaire "SEARCH"/"CHAT" doit être **reproductible**, pas de créativité nécessaire.
→ **Génération (temp=0.7)** : Réponses conversationnelles **variées** mais contrôlées (évite hallucinations > 1.0, évite répétitif < 0.5).
→ **Code** : `get_llm(temperature=0.7, max_tokens=1000)` pour RAG/conversation, `get_llm(temperature=0, max_tokens=10)` pour classification.

---

### **Q15 : Comment injectez-vous le contexte RAG dans le prompt ?**

→ **Méthode** : `_format_context(results)` transforme résultats FAISS en string structuré :
```
Événements pertinents :

Événement 1 :
[page_content du Document]

Événement 2 :
...
```
→ **Template RAG** : `RAG_SYSTEM_PROMPT_TEMPLATE` contient placeholder `{context}`. LangChain remplace dynamiquement.
→ **Chaîne LCEL** : `ChatPromptTemplate([system, history, human]) | llm | parser` → inject variables `{"context": formatted, "query": query, "history": messages}`.
→ **Top-k=5** : Limite contexte à 5 événements (évite dépassement tokens, focus pertinence).

---

### **Q16 : Quels sont les endpoints FastAPI principaux ?**

→ **7 endpoints REST** :
   - `GET /health` : Health check + stats (nb docs, sessions actives)
   - `POST /search` : Recherche sémantique stateless (sans session)
   - `POST /chat` : Chat conversationnel avec session persistence
   - `GET /session/{id}` : Récupère historique session
   - `DELETE /session/{id}` : Supprime session + messages
   - `POST /rebuild` : Rebuild index FAISS (background, auth requise)
   - `GET /events` : Liste événements indexés (pagination)
→ **Documentation auto** : Swagger UI à `/docs`, ReDoc à `/redoc`.

---

### **Q17 : Comment gérez-vous les sessions avec PostgreSQL ?**

→ **Repository pattern** : `SessionRepository`, `MessageRepository` (async SQLAlchemy).
→ **Modèles** :
   - `SessionModel` : id (UUID), created_at, updated_at, messages (relation)
   - `MessageModel` : id (auto), session_id (FK), role, content, sources (JSONB), latency_ms, top_k
→ **Async** : `AsyncSession` (asyncpg driver) = requêtes DB non-bloquantes, FastAPI traite N requêtes parallèles.
→ **Cleanup** : Pas d'auto-expiration actuellement (amélioration future : TTL 24h).
→ **Connection pool** : 10 connexions (`pool_size=10`), `pool_pre_ping=True` (health checks).

---

## ⚖️ SECTION 4 : CHOIX TECHNIQUES & TRADE-OFFS

### **Q18 : Quels sont les avantages/limites du pipeline dual-mode ?**

→ **✅ Avantages** :
   - Performance : Évite FAISS inutile (salutations, remerciements) → économie 50-70% requêtes vectorstore
   - UX : Réponses conversationnelles naturelles (pas de "désolé, pas d'événement" pour "Bonjour")
   - Flexibilité : Gestion différenciée prompts (CONVERSATION vs RAG)
→ **❌ Limites** :
   - Complexité : 2 prompts à maintenir (drift possible)
   - Classification peut échouer (~5% edge cases théoriques, 0% observé sur test)
   - Latence ajoutée : +50-100ms pour classification (acceptable < 3s total)

---

### **Q19 : LangChain LCEL : avantages/inconvénients vs implémentation custom ?**

→ **✅ Avantages** :
   - Portabilité : Changement provider facile (Mistral → OpenAI = 3 lignes)
   - Abstractions : MessagesPlaceholder, Document, StrOutputParser standardisés
   - Communauté : Ecosystem LangChain (FAISS, Pinecone, agents...)
→ **❌ Inconvénients** :
   - Overhead : ~10% latence vs appels API directs
   - Dépendance : Breaking changes LangChain (migration mistral → 0.1.x récente)
   - Courbe apprentissage : LCEL syntax non intuitive débutants
→ **Trade-off** : Gain maintenabilité > perte performance mineure.

---

### **Q20 : FAISS vs Pinecone : pourquoi ce choix pour votre projet ?**

→ **FAISS choisi** :
   - ✅ Gratuit, auto-hébergé (pas de coût cloud)
   - ✅ Ultra-rapide pour petits datasets (<10k docs)
   - ✅ Contrôle total données (RGPD, offline)
   - ❌ Scalabilité limitée RAM (~1M docs max)
   - ❌ Pas de distribution (single server)
→ **Pinecone alternative** :
   - ✅ Scalable (milliards vecteurs)
   - ✅ Managed (updates, backups auto)
   - ❌ Coût (~$70/mois minimum)
   - ❌ Vendor lock-in
→ **Décision** : 497 événements → FAISS largement suffisant, évite complexité cloud.

---

### **Q21 : Quelles métriques d'évaluation utilisez-vous (RAGAS, latence) ?**

→ **3 métriques principales** :
   1. **Latence** : Temps total encode+search+generate. **Cible <3.0s**, **résultat 2.41s** ✅ (mesure `time.time()`, stockée `MessageModel.latency_ms`)
   2. **Couverture mots-clés** : % mots attendus présents dans réponse. **Cible >80%**, **résultat 81.5%** ✅ (annotation manuelle 12 questions)
   3. **Classification accuracy** : Détection SEARCH/CHAT correcte. **Résultat 100%** (12/12) ✅
→ **RAGAS** (future) : `context_precision`, `context_recall`, `answer_relevancy`, `faithfulness` (framework evaluation RAG).
→ **Dataset test** : `test-questions-annote.json` (12 questions, 5 catégories).

---

### **Q22 : Quelles sont les limitations actuelles et améliorations futures ?**

→ **Limitations** :
   - Scalabilité : FAISS in-memory (limite ~10k événements)
   - Mise à jour manuelle : Pas d'auto-sync Open Agenda (rebuild manuel via /rebuild)
   - Mono-langue : Français uniquement (prompts, embeddings)
   - Session volatility : PostgreSQL mais pas de TTL auto (accumulation sessions)
   - Pas d'auth utilisateur : API publique (rate limiting futur)
→ **Améliorations prioritaires** :
   - Court terme : Cache Redis sessions, authentification JWT, monitoring Prometheus
   - Moyen terme : Auto-sync Open Agenda (CRON), multi-langue (English), recommandations personnalisées
   - Long terme : Fine-tuning Mistral, migration Pinecone (si >10k events), interface vocale

---

## 📊 ANNEXE : CHIFFRES CLÉS À MÉMORISER

### Architecture
- **Pipeline** : Dual-mode (CHAT / SEARCH)
- **LCEL chains** : 3 chaînes (classification, conversation, RAG)
- **Classification** : Température 0, max_tokens=10, accuracy 100%

### Données & Index
- **Événements indexés** : 497 (Open Agenda API)
- **Embedding dimension** : 1024d (mistral-embed)
- **Index FAISS** : IndexFlatL2, normalisation L2
- **Format LangChain** : index.faiss + index.pkl + config.json

### Performance
- **Latence moyenne** : 2.41s (cible <3.0s) ✅
- **Couverture mots-clés** : 81.5% (cible >80%) ✅
- **Classification accuracy** : 100% (12/12 questions)
- **Temps rebuild index** : ~30-60s (background task)

### Stack Technique
- **Embeddings** : MistralAIEmbeddings (mistral-embed, 1024d)
- **LLM** : ChatMistralAI (mistral-small-latest, temp=0.7, max_tokens=1000)
- **Vectorstore** : FAISS IndexFlatL2 (LangChain wrapper)
- **API** : FastAPI (async/await, ASGI, 7 endpoints)
- **Database** : PostgreSQL (async SQLAlchemy, asyncpg)
- **Session management** : MAX_HISTORY=5 messages, repository pattern

### Tests & Évaluation
- **Dataset test** : 12 questions annotées (5 catégories)
- **Métriques** : Latence, couverture, classification accuracy
- **Framework** : RAGAS (context_precision, answer_relevancy)
- **Coverage code** : 85% (pytest-cov)

### Configuration
- **Température génération** : 0.7 (créatif contrôlé)
- **Température classification** : 0 (déterministe)
- **Top-k retrieval** : 5 événements max
- **MAX_HISTORY** : 5 paires (10 messages max)
- **Batch size embeddings** : 32 documents
- **Target latency** : <3.0s
- **Target relevance** : >80% coverage

---

## 🎯 CONSEILS SOUTENANCE

**Questions probables examinateur** :
1. "Pourquoi RAG vs fine-tuning ?" → Coût, actualisation temps réel, traçabilité
2. "Comment gérez-vous l'historique ?" → PostgreSQL, MAX_HISTORY=5, MessagesPlaceholder
3. "Expliquez calcul similarité" → 1 - L2_distance, normalisation vecteurs
4. "Pourquoi dual-mode ?" → Performance (évite FAISS inutile), UX conversationnelle
5. "Limitations ?" → Scalabilité FAISS, pas auto-sync, mono-langue

**Réflexes techniques** :
- Toujours citer chiffres précis (2.41s, 81.5%, 1024d, 497 events)
- Justifier choix architecturaux (Mistral = français natif + prix, FAISS = gratuit + contrôle)
- Montrer conscience trade-offs (LCEL overhead 10% vs portabilité)
- Proposer améliorations (cache Redis, JWT auth, multi-langue)

**Temps révision** : 15-20 minutes lecture complète + 5 minutes mémorisation chiffres = prêt pour soutenance ! 🚀
