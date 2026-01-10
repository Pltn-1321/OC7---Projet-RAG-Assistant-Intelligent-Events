# 🎯 GUIDE COMPLET - Projet RAG Assistant Intelligent Events

**Date limite démo : 24 janvier 2026 (14 jours)**  
**Porteur : Pierre**  
**Stack : Streamlit + LangChain + Mistral + Faiss**

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble du projet](#vue-densemble)
2. [Planning hebdomadaire](#planning)
3. [Checklist détaillée par étape](#checklist)
4. [Conseils techniques critiques](#conseils-techniques)
5. [Configuration environnement](#environnement)
6. [Structure du projet](#structure)
7. [Points de vigilance](#vigilance)
8. [Ressources et liens](#ressources)

---

## 🎯 VUE D'ENSEMBLE DU PROJET {#vue-densemble}

### Objectif
Créer un chatbot RAG (Retrieval-Augmented Generation) qui permet de découvrir des événements culturels via questions en langage naturel, basé sur les données Open Agenda.

### Métriques de succès
- ✅ Pertinence réponses > 80%
- ✅ Temps de réponse < 3 secondes
- ✅ Satisfaction démo > 4/5
- ✅ Couverture questions > 70%

### Livrables finaux
1. ✅ Application Streamlit fonctionnelle
2. ✅ API REST FastAPI (optionnelle mais recommandée)
3. ✅ Pipeline d'indexation automatisé
4. ✅ Index vectoriel Faiss
5. ✅ Tests fonctionnels avec jeu de questions
6. ✅ Documentation technique complète
7. ✅ Conteneurisation Docker
8. ✅ Présentation PowerPoint (10-15 slides)

---

## 📅 PLANNING DÉTAILLÉ (14 JOURS) {#planning}

### 🔵 SEMAINE 1 : DÉVELOPPEMENT CORE

#### **Jour 1-2 (10-11 janvier) : Fondations**
```
✅ Configuration environnement Python
✅ Installation dépendances (requirements.txt)
✅ Test connexion API Open Agenda
✅ Récupération première donnée test
✅ Structure projet créée
```

**Livrables J2 :**
- Environnement virtuel fonctionnel
- `requirements.txt` complet
- Premier script de test API
- README.md initial
- Git initialisé avec .gitignore

---

#### **Jour 3-4 (12-13 janvier) : Pipeline d'indexation**
```
✅ Script récupération événements Open Agenda
✅ Nettoyage et structuration données
✅ Génération embeddings (test sur 50 événements)
✅ Création index FAISS
✅ Tests unitaires pipeline
```

**Livrables J4 :**
- `scripts/fetch_events.py` fonctionnel
- `scripts/build_index.py` fonctionnel
- Index FAISS avec ~100-500 événements
- Dataset test sauvegardé (JSON)

---

#### **Jour 5-7 (14-16 janvier) : Système RAG**
```
✅ Implémentation retriever (recherche similarité)
✅ Intégration Mistral AI (génération réponses)
✅ Orchestration LangChain
✅ Tests end-to-end RAG
✅ Optimisation prompts
```

**Livrables J7 :**
- Module RAG fonctionnel
- 5 questions/réponses testées avec succès
- Temps de réponse < 3s validé
- Logs structurés

---

### 🟢 SEMAINE 2 : INTERFACE & FINITIONS

#### **Jour 8-10 (17-19 janvier) : Interface Streamlit + API**
```
✅ Interface Streamlit conversationnelle
✅ Affichage formaté des réponses
✅ Liens vers événements Open Agenda
✅ API REST FastAPI (si temps)
✅ Tests interface utilisateur
```

**Livrables J10 :**
- App Streamlit fonctionnelle
- Design épuré et professionnel
- Gestion d'erreurs robuste
- (Optionnel) API REST avec Swagger

---

#### **Jour 11-12 (20-21 janvier) : Tests & Évaluation**
```
✅ Jeu de test 30+ questions annotées
✅ Script d'évaluation automatique
✅ Calcul métriques (Recall, Precision, F1)
✅ Tests sur différents scénarios
✅ Correction bugs identifiés
```

**Livrables J12 :**
- `tests/test_questions.json` (30 questions)
- `scripts/evaluate_rag.py` fonctionnel
- Rapport métriques (CSV/JSON)
- Documentation tests

---

#### **Jour 13 (22 janvier) : Docker & Documentation**
```
✅ Dockerfile optimisé
✅ Docker Compose (optionnel)
✅ Tests build/run containers
✅ Documentation technique complète
✅ README final
```

**Livrables J13 :**
- `Dockerfile` fonctionnel
- `docker-compose.yml` (optionnel)
- Documentation installation
- Guide troubleshooting

---

#### **Jour 14 (23 janvier) : Présentation & Répétition**
```
✅ PowerPoint finalisé (10-15 slides)
✅ Scénarios démo préparés
✅ Vidéo backup enregistrée
✅ Répétition présentation
✅ Tests finaux
```

**Livrables J14 :**
- PowerPoint complet
- Script démo avec exemples
- Vidéo backup (au cas où)
- Système 100% opérationnel

---

#### **🎬 Jour 15 (24 janvier) : DÉMO**
```
✅ Présentation 20 minutes
✅ Démo live interactive
✅ Q&A
✅ Feedback équipes
```

---

## ✅ CHECKLIST DÉTAILLÉE PAR ÉTAPE {#checklist}

### 📦 ÉTAPE 1 : Configuration Environnement

#### Actions
```bash
# 1. Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 2. Créer requirements.txt
touch requirements.txt

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Tester imports critiques
python -c "import faiss; print('Faiss OK')"
python -c "from langchain_community.vectorstores import FAISS; print('LangChain OK')"
python -c "from mistralai import Mistral; print('Mistral OK')"
```

#### ✅ Checklist
- [ ] Environnement virtuel créé et activé
- [ ] `requirements.txt` complet (voir section Environnement)
- [ ] Toutes dépendances installées sans erreur
- [ ] Imports critiques testés
- [ ] `.env` créé avec clés API (non versionné)
- [ ] `.gitignore` configuré
- [ ] Git initialisé

#### Validation
```bash
# Tous ces imports doivent réussir
python << EOF
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from mistralai import Mistral
import streamlit
import pandas
import requests
print("✅ Environnement OK")
EOF
```

---

### 📡 ÉTAPE 2 : Récupération Données Open Agenda

#### Actions
```python
# scripts/fetch_events.py
import requests
import json
from datetime import datetime, timedelta

def fetch_open_agenda_events(location="paris", max_events=500):
    """
    Récupère événements depuis Open Agenda
    
    Args:
        location: ville/région (ex: "paris", "lyon", "marseille")
        max_events: nombre maximum d'événements
    
    Returns:
        list: événements structurés
    """
    base_url = "https://api.openagenda.com/v2/agendas/{agenda_uid}/events"
    
    # TODO: Obtenir votre agenda_uid
    # Documentation: https://openagenda.zendesk.com/hc/fr
    
    events = []
    # Implémenter pagination API
    # Filtrer par date (derniers 12 mois + futurs)
    # Nettoyer HTML descriptions
    
    return events

if __name__ == "__main__":
    events = fetch_open_agenda_events("paris", 1000)
    print(f"✅ {len(events)} événements récupérés")
    
    # Sauvegarder pour tests
    with open("data/events_raw.json", "w") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
```

#### ✅ Checklist
- [ ] Compte Open Agenda créé
- [ ] API key récupérée (si nécessaire)
- [ ] Documentation API lue
- [ ] Script `fetch_events.py` créé
- [ ] Test récupération 10 événements réussi
- [ ] Récupération complète (500-2000 événements)
- [ ] Données sauvegardées en JSON
- [ ] Nettoyage HTML effectué
- [ ] Validation structure données

#### Structure attendue (JSON)
```json
{
  "id": "12345",
  "title": "Concert de Jazz au Caveau",
  "description": "Soirée jazz manouche...",
  "location": {
    "city": "Paris",
    "address": "15 rue de la Huchette",
    "coordinates": {"lat": 48.85, "lon": 2.35}
  },
  "dates": {
    "start": "2026-01-20T20:00:00",
    "end": "2026-01-20T23:00:00"
  },
  "price": "15€",
  "category": "Concert",
  "url": "https://openagenda.com/event/12345"
}
```

#### Points de vigilance
- ⚠️ Gestion pagination API
- ⚠️ Rate limiting (respecter limites)
- ⚠️ Nettoyage HTML (BeautifulSoup ou regex)
- ⚠️ Validation données (éviter champs vides)
- ⚠️ Encodage UTF-8

---

### 🔍 ÉTAPE 3 : Indexation Vectorielle FAISS

#### Actions
```python
# scripts/build_index.py
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
import json

def build_faiss_index(events_file="data/events_raw.json"):
    """
    Construit index FAISS depuis événements
    
    Args:
        events_file: chemin fichier JSON événements
    
    Returns:
        FAISS: index vectoriel
    """
    # 1. Charger événements
    with open(events_file) as f:
        events = json.load(f)
    
    # 2. Créer embeddings model
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    # 3. Créer documents LangChain
    documents = []
    for event in events:
        # Combiner informations pour recherche sémantique
        content = f"""
        Titre: {event['title']}
        Description: {event['description']}
        Lieu: {event['location']['city']}
        Date: {event['dates']['start']}
        Prix: {event.get('price', 'Non spécifié')}
        Catégorie: {event.get('category', 'Événement')}
        """
        
        doc = Document(
            page_content=content,
            metadata={
                "title": event['title'],
                "city": event['location']['city'],
                "date": event['dates']['start'],
                "price": event.get('price'),
                "url": event['url'],
                "id": event['id']
            }
        )
        documents.append(doc)
    
    # 4. Créer index FAISS
    print(f"🔨 Indexation de {len(documents)} événements...")
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    # 5. Sauvegarder
    vectorstore.save_local("data/faiss_index")
    print("✅ Index sauvegardé dans data/faiss_index")
    
    return vectorstore

if __name__ == "__main__":
    index = build_faiss_index()
    
    # Test recherche
    results = index.similarity_search("concert jazz paris", k=3)
    for i, doc in enumerate(results, 1):
        print(f"\n{i}. {doc.metadata['title']}")
```

#### ✅ Checklist
- [ ] Script `build_index.py` créé
- [ ] Modèle embeddings téléchargé
- [ ] Documents LangChain créés correctement
- [ ] Index FAISS construit sans erreur
- [ ] Index sauvegardé sur disque
- [ ] Test recherche similarité réussi
- [ ] Temps indexation acceptable (< 5 min pour 1000 événements)

#### Validation
```python
# Test complet
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Charger index
vectorstore = FAISS.load_local(
    "data/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

# Test recherche
queries = [
    "concert jazz ce weekend",
    "exposition gratuite paris",
    "spectacle enfants dimanche"
]

for query in queries:
    results = vectorstore.similarity_search(query, k=3)
    print(f"\n🔍 Query: {query}")
    for doc in results:
        print(f"  - {doc.metadata['title']}")
```

#### Points de vigilance
- ⚠️ Taille modèle embeddings (choisir léger pour POC)
- ⚠️ Mémoire RAM (indexation peut consommer beaucoup)
- ⚠️ Format métadonnées (doit être JSON serializable)
- ⚠️ Persistence index (save_local/load_local)

---

### 🤖 ÉTAPE 4 : Système RAG (Retrieval + Generation)

#### Actions
```python
# rag/chatbot.py
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_mistralai import ChatMistralAI
from langchain.prompts import PromptTemplate
import os

class EventChatbot:
    def __init__(self, index_path="data/faiss_index"):
        # 1. Charger index FAISS
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        self.vectorstore = FAISS.load_local(
            index_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        
        # 2. Initialiser Mistral
        self.llm = ChatMistralAI(
            model="mistral-small-latest",
            mistral_api_key=os.getenv("MISTRAL_API_KEY"),
            temperature=0.3
        )
        
        # 3. Définir prompt
        template = """Tu es un assistant intelligent qui aide les utilisateurs à découvrir des événements culturels.
        
Contexte des événements trouvés :
{context}

Question de l'utilisateur : {question}

Instructions :
- Réponds en français de manière naturelle et conversationnelle
- Recommande 2-3 événements pertinents maximum
- Mentionne les informations pratiques (date, lieu, prix)
- Si aucun événement ne correspond, propose des alternatives
- Sois concis mais informatif

Réponse :"""
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # 4. Créer chaîne RAG
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 5}
            ),
            chain_type_kwargs={"prompt": self.prompt},
            return_source_documents=True
        )
    
    def ask(self, question):
        """
        Pose une question au chatbot
        
        Args:
            question: question utilisateur
        
        Returns:
            dict: {
                "answer": réponse générée,
                "sources": événements sources avec métadonnées
            }
        """
        result = self.qa_chain({"query": question})
        
        return {
            "answer": result["result"],
            "sources": [
                {
                    "title": doc.metadata["title"],
                    "url": doc.metadata["url"],
                    "date": doc.metadata["date"],
                    "city": doc.metadata["city"],
                    "price": doc.metadata.get("price", "Non spécifié")
                }
                for doc in result["source_documents"]
            ]
        }

if __name__ == "__main__":
    # Test
    chatbot = EventChatbot()
    
    test_questions = [
        "Quels concerts ce weekend à Paris ?",
        "Événements gratuits pour enfants dimanche ?",
        "Exposition d'art contemporain dans le Marais ?"
    ]
    
    for q in test_questions:
        print(f"\n🔵 Q: {q}")
        result = chatbot.ask(q)
        print(f"🤖 A: {result['answer']}")
        print(f"📚 Sources: {len(result['sources'])} événements")
```

#### ✅ Checklist
- [ ] Clé API Mistral configurée
- [ ] Module RAG créé (`rag/chatbot.py`)
- [ ] Retriever fonctionnel (top-k événements)
- [ ] LLM Mistral intégré
- [ ] Prompt optimisé (itérations)
- [ ] Tests avec 10 questions variées
- [ ] Temps de réponse < 3s
- [ ] Pertinence réponses validée

#### Validation
```python
# Test end-to-end
from rag.chatbot import EventChatbot
import time

chatbot = EventChatbot()

questions = [
    "Concert jazz pas cher ce weekend",
    "Activités en famille samedi",
    "Exposition photo gratuite"
]

for q in questions:
    start = time.time()
    result = chatbot.ask(q)
    latency = time.time() - start
    
    print(f"\n{'='*60}")
    print(f"Q: {q}")
    print(f"A: {result['answer'][:200]}...")
    print(f"⏱️ Latency: {latency:.2f}s")
    print(f"📊 Sources: {len(result['sources'])}")
    
    assert latency < 3.0, f"❌ Latence trop élevée: {latency}s"
    assert len(result['sources']) > 0, "❌ Pas de sources"
    
print("\n✅ Tous les tests passent")
```

#### Points de vigilance
- ⚠️ Coût tokens Mistral (limiter contexte)
- ⚠️ Qualité prompt (itérer jusqu'à satisfaction)
- ⚠️ Gestion erreurs API
- ⚠️ Température LLM (0.3 pour cohérence)
- ⚠️ Nombre de documents récupérés (k=5 recommandé)

---

### 🎨 ÉTAPE 5 : Interface Streamlit

#### Actions
```python
# app.py
import streamlit as st
from rag.chatbot import EventChatbot
import time

# Configuration page
st.set_page_config(
    page_title="Assistant Événements",
    page_icon="🎭",
    layout="wide"
)

# Titre
st.title("🎭 Assistant Intelligent Événements")
st.markdown("Découvrez des événements culturels en posant vos questions naturellement")

# Initialiser chatbot (cache)
@st.cache_resource
def load_chatbot():
    return EventChatbot()

chatbot = load_chatbot()

# Zone de saisie
question = st.text_input(
    "Posez votre question :",
    placeholder="Ex: Concerts jazz ce weekend à Paris pas cher"
)

if st.button("🔍 Rechercher") and question:
    with st.spinner("Recherche en cours..."):
        start = time.time()
        result = chatbot.ask(question)
        latency = time.time() - start
    
    # Afficher réponse
    st.markdown("### 💬 Réponse")
    st.write(result["answer"])
    
    # Afficher sources
    st.markdown("### 📚 Événements suggérés")
    for i, source in enumerate(result["sources"], 1):
        with st.expander(f"{i}. {source['title']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"📅 **Date:** {source['date']}")
                st.write(f"📍 **Lieu:** {source['city']}")
            with col2:
                st.write(f"💰 **Prix:** {source['price']}")
                st.write(f"🔗 [Voir sur Open Agenda]({source['url']})")
    
    # Métriques (optionnel)
    st.sidebar.metric("⏱️ Temps de réponse", f"{latency:.2f}s")
    st.sidebar.metric("📊 Sources", len(result["sources"]))

# Exemples (sidebar)
st.sidebar.markdown("### 💡 Exemples de questions")
st.sidebar.markdown("""
- Concerts ce weekend à Paris ?
- Événements gratuits pour enfants ?
- Exposition d'art dans le Marais ?
- Spectacles samedi soir pas cher ?
""")
```

#### ✅ Checklist
- [ ] `app.py` créé
- [ ] Interface conversationnelle fonctionnelle
- [ ] Affichage réponse formatée
- [ ] Sources avec liens cliquables
- [ ] Design épuré et professionnel
- [ ] Gestion erreurs (question vide, API down)
- [ ] Indicateurs de chargement
- [ ] Tests sur différents navigateurs

#### Lancement
```bash
streamlit run app.py
```

#### Points de vigilance
- ⚠️ Cache chatbot (@st.cache_resource)
- ⚠️ UX/UI simple et claire
- ⚠️ Messages d'erreur compréhensibles
- ⚠️ Responsive design (desktop priority)

---

### 🌐 ÉTAPE 6 : API REST FastAPI (OPTIONNEL)

#### Actions
```python
# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag.chatbot import EventChatbot
import time

app = FastAPI(
    title="API Assistant Événements",
    description="API REST pour système RAG événements culturels",
    version="1.0.0"
)

# Charger chatbot au démarrage
chatbot = None

@app.on_event("startup")
async def startup_event():
    global chatbot
    chatbot = EventChatbot()

class Question(BaseModel):
    query: str
    max_results: int = 5

class Answer(BaseModel):
    answer: str
    sources: list
    latency: float

@app.post("/ask", response_model=Answer)
async def ask_question(question: Question):
    """
    Pose une question au système RAG
    
    Args:
        question: objet Question avec query
    
    Returns:
        Answer avec réponse, sources et latence
    """
    if not question.query.strip():
        raise HTTPException(status_code=400, detail="Question vide")
    
    try:
        start = time.time()
        result = chatbot.ask(question.query)
        latency = time.time() - start
        
        return Answer(
            answer=result["answer"],
            sources=result["sources"][:question.max_results],
            latency=latency
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model": "mistral-small"}

@app.post("/rebuild")
async def rebuild_index():
    """Reconstruit l'index vectoriel (admin)"""
    # TODO: Implémenter si nécessaire
    return {"message": "Not implemented in POC"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### ✅ Checklist (si API implémentée)
- [ ] `api/main.py` créé
- [ ] Endpoints `/ask`, `/health` fonctionnels
- [ ] Swagger auto-généré accessible (/docs)
- [ ] Tests avec curl/Postman
- [ ] Gestion erreurs robuste
- [ ] Documentation OpenAPI complète

#### Test
```bash
# Lancer API
uvicorn api.main:app --reload

# Tester
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "concerts jazz paris"}'

# Swagger
open http://localhost:8000/docs
```

---

### ✅ ÉTAPE 7 : Tests & Évaluation

#### Actions
```python
# tests/test_questions.json
[
  {
    "id": 1,
    "question": "Quels concerts jazz ce weekend à Paris ?",
    "expected_keywords": ["concert", "jazz", "paris", "weekend"],
    "category": "recherche_simple"
  },
  {
    "id": 2,
    "question": "Événements gratuits pour enfants dimanche après-midi",
    "expected_keywords": ["gratuit", "enfants", "dimanche"],
    "category": "filtres_multiples"
  }
  // ... 30 questions total
]
```

```python
# scripts/evaluate_rag.py
import json
from rag.chatbot import EventChatbot
import time

def evaluate_rag(test_file="tests/test_questions.json"):
    """Évalue le système RAG sur jeu de test"""
    
    chatbot = EventChatbot()
    
    with open(test_file) as f:
        test_cases = json.load(f)
    
    results = []
    total_latency = 0
    
    for test in test_cases:
        print(f"\n🔍 Test {test['id']}: {test['question']}")
        
        start = time.time()
        result = chatbot.ask(test['question'])
        latency = time.time() - start
        total_latency += latency
        
        # Vérifier présence mots-clés
        answer_lower = result['answer'].lower()
        keywords_found = sum(
            1 for kw in test['expected_keywords']
            if kw.lower() in answer_lower
        )
        
        relevance = keywords_found / len(test['expected_keywords'])
        
        results.append({
            "id": test['id'],
            "question": test['question'],
            "answer": result['answer'],
            "latency": latency,
            "relevance_score": relevance,
            "sources_count": len(result['sources'])
        })
        
        print(f"  ⏱️ Latency: {latency:.2f}s")
        print(f"  📊 Relevance: {relevance:.0%}")
        print(f"  📚 Sources: {len(result['sources'])}")
    
    # Métriques globales
    avg_latency = total_latency / len(test_cases)
    avg_relevance = sum(r['relevance_score'] for r in results) / len(results)
    
    print(f"\n{'='*60}")
    print(f"📊 RÉSULTATS GLOBAUX")
    print(f"{'='*60}")
    print(f"Questions testées: {len(test_cases)}")
    print(f"Latence moyenne: {avg_latency:.2f}s")
    print(f"Pertinence moyenne: {avg_relevance:.0%}")
    print(f"Cible latence: < 3s ({'✅' if avg_latency < 3 else '❌'})")
    print(f"Cible pertinence: > 80% ({'✅' if avg_relevance > 0.8 else '❌'})")
    
    # Sauvegarder résultats
    with open("tests/evaluation_results.json", "w") as f:
        json.dump({
            "results": results,
            "metrics": {
                "avg_latency": avg_latency,
                "avg_relevance": avg_relevance,
                "total_tests": len(test_cases)
            }
        }, f, indent=2, ensure_ascii=False)
    
    return results

if __name__ == "__main__":
    evaluate_rag()
```

#### ✅ Checklist
- [ ] Jeu de test créé (30+ questions)
- [ ] Questions couvrent différents scénarios
- [ ] Script d'évaluation fonctionnel
- [ ] Métriques calculées automatiquement
- [ ] Résultats sauvegardés (JSON/CSV)
- [ ] Cibles atteintes (latence < 3s, pertinence > 80%)

---

### 🐳 ÉTAPE 8 : Conteneurisation Docker

#### Actions
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier code
COPY . .

# Télécharger modèle embeddings (cache)
RUN python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Port Streamlit
EXPOSE 8501

# Commande démarrage
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

```yaml
# docker-compose.yml (optionnel)
version: '3.8'

services:
  streamlit:
    build: .
    ports:
      - "8501:8501"
    environment:
      - MISTRAL_API_KEY=${MISTRAL_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
  
  api:  # Si API implémentée
    build: .
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - MISTRAL_API_KEY=${MISTRAL_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

#### ✅ Checklist
- [ ] `Dockerfile` créé et optimisé
- [ ] `docker-compose.yml` créé (optionnel)
- [ ] `.dockerignore` configuré
- [ ] Build image réussit (< 2GB)
- [ ] Container démarre sans erreur
- [ ] Application accessible (localhost:8501)
- [ ] Variables d'environnement fonctionnelles
- [ ] Tests dans container

#### Commandes
```bash
# Build
docker build -t rag-events .

# Run
docker run -p 8501:8501 \
  -e MISTRAL_API_KEY=$MISTRAL_API_KEY \
  -v $(pwd)/data:/app/data \
  rag-events

# Avec Docker Compose
docker-compose up -d

# Vérifier logs
docker-compose logs -f
```

---

### 📊 ÉTAPE 9 : Présentation PowerPoint

#### Structure (10-15 slides)

**Slide 1: Titre**
- Titre: "Assistant Intelligent Événements - POC RAG"
- Nom, Date, Logo école

**Slide 2: Contexte & Problématique**
- Difficulté actuelle: interfaces complexes, filtres multiples
- Besoin: recherche naturelle en langage courant
- Opportunité: IA conversationnelle

**Slide 3: Solution Proposée**
- Chatbot RAG basé sur Open Agenda
- Comprend langage naturel
- Répond avec événements pertinents

**Slide 4: Architecture Technique**
- Schéma: Utilisateur → Streamlit → RAG → FAISS + Mistral
- Stack: Python, LangChain, Faiss, Mistral

**Slide 5: Pipeline de Données**
- Récupération Open Agenda
- Nettoyage et structuration
- Vectorisation (embeddings)
- Indexation FAISS

**Slide 6-7: Démonstration Interface**
- Screenshots Streamlit
- Exemples questions/réponses
- Mise en avant UX

**Slide 8: Résultats & Métriques**
- Latence moyenne: X.Xs (< 3s ✅)
- Pertinence: XX% (> 80% ✅)
- XX événements indexés
- XX questions testées

**Slide 9: Exemple Conversations**
- 2-3 captures d'écran conversations réelles
- Montrer variété cas d'usage

**Slide 10: Limitations POC**
- Zone géographique limitée
- Pas d'historique persistant
- Mise à jour manuelle index
- Coût tokens

**Slide 11: Pistes d'Amélioration**
- **Court terme**: filtres avancés, plus de villes
- **Moyen terme**: personnalisation, historique
- **Long terme**: multimodal, réservation

**Slide 12: Recommandations**
- Go/No-go pour V1 production
- Ressources nécessaires
- Roadmap 6 mois

**Slide 13: Conclusion**
- POC valide la faisabilité
- Architecture scalable démontrée
- Prêt pour phase suivante

**Slide 14: Q&A**
- Questions ?
- Contact

#### ✅ Checklist
- [ ] PowerPoint créé (10-15 slides)
- [ ] Design professionnel et cohérent
- [ ] Screenshots application inclus
- [ ] Métriques et graphiques clairs
- [ ] Schémas architecture
- [ ] Pas de jargon excessif
- [ ] Lisible et épuré
- [ ] Répétition présentation (< 20 min)

---

## ⚙️ CONFIGURATION ENVIRONNEMENT {#environnement}

### requirements.txt COMPLET

```txt
# === CORE RAG ===
langchain==0.1.0
langchain-community==0.1.0
langchain-mistralai==0.0.5
mistralai==0.1.6

# === VECTOR STORE ===
faiss-cpu==1.7.4
sentence-transformers==2.3.1

# === INTERFACE ===
streamlit==1.29.0

# === API (Optionnel) ===
fastapi==0.109.0
uvicorn[standard]==0.25.0
pydantic==2.5.3

# === DATA PROCESSING ===
requests==2.31.0
python-dotenv==1.0.0
pandas==2.1.4
beautifulsoup4==4.12.2

# === TESTS & EVALUATION ===
pytest==7.4.3
ragas==0.1.0  # Optionnel pour évaluation avancée

# === UTILS ===
python-json-logger==2.0.7
```

### Fichier .env

```bash
# .env
MISTRAL_API_KEY=your_mistral_api_key_here
OPENAGENDA_API_KEY=your_openagenda_key_if_needed

# Optionnel
LOG_LEVEL=INFO
INDEX_PATH=data/faiss_index
```

### .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Data
data/
*.json
*.csv
!tests/test_questions.json

# Secrets
.env
*.key

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp

# Docker
.dockerignore
```

---

## 🗂️ STRUCTURE PROJET {#structure}

```
rag-events-poc/
│
├── README.md                   # Documentation principale
├── requirements.txt            # Dépendances Python
├── .env                        # Variables d'environnement (non versionné)
├── .gitignore                  # Fichiers ignorés Git
├── Dockerfile                  # Conteneurisation
├── docker-compose.yml          # Orchestration (optionnel)
│
├── app.py                      # Application Streamlit
│
├── scripts/                    # Scripts utilitaires
│   ├── fetch_events.py         # Récupération Open Agenda
│   ├── build_index.py          # Construction index FAISS
│   └── evaluate_rag.py         # Évaluation automatique
│
├── rag/                        # Module RAG
│   ├── __init__.py
│   ├── chatbot.py              # Classe principale chatbot
│   ├── retriever.py            # Logique retrieval (optionnel)
│   └── generator.py            # Logique generation (optionnel)
│
├── api/                        # API REST (optionnel)
│   ├── __init__.py
│   └── main.py                 # FastAPI app
│
├── data/                       # Données (non versionné)
│   ├── events_raw.json         # Événements bruts
│   ├── faiss_index/            # Index vectoriel
│   └── ...
│
├── tests/                      # Tests
│   ├── test_questions.json     # Jeu de test
│   ├── evaluation_results.json # Résultats évaluation
│   └── test_rag.py             # Tests unitaires
│
└── docs/                       # Documentation
    ├── presentation.pptx       # PowerPoint démo
    ├── rapport_technique.md    # Rapport technique
    └── architecture.png        # Schémas
```

---

## ⚠️ POINTS DE VIGILANCE CRITIQUES {#vigilance}

### 🔴 Erreurs fréquentes à éviter

#### 1. Imports LangChain (CRITIQUE)
```python
# ❌ FAUX - imports deprecated
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

# ✅ CORRECT - imports actuels
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
```

#### 2. Mistral API
```python
# ❌ FAUX
from mistral import MistralClient

# ✅ CORRECT
from mistralai import Mistral
# OU
from langchain_mistralai import ChatMistralAI  # Recommandé avec LangChain
```

#### 3. Clé API Mistral
- ⚠️ NE JAMAIS versionner dans Git
- ✅ Utiliser variable d'environnement
- ✅ Fichier `.env` avec `python-dotenv`

#### 4. Faiss deserialization
```python
# ✅ IMPORTANT: allow_dangerous_deserialization=True requis
vectorstore = FAISS.load_local(
    "data/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True  # REQUIS
)
```

#### 5. Rate Limiting API
- ⚠️ Open Agenda: respecter limites
- ⚠️ Mistral: surveiller quota tokens
- ✅ Implémenter retry logic
- ✅ Cacher résultats quand possible

#### 6. Mémoire RAM
- ⚠️ Indexation 1000+ événements = ~2GB RAM
- ✅ Surveiller consommation
- ✅ Batch processing si nécessaire

#### 7. Docker
- ⚠️ Image peut être lourde (1-2GB)
- ✅ .dockerignore pour exclure data/
- ✅ Multi-stage build si possible
- ✅ Variables d'environnement pour secrets

---

## 🎯 CONSEILS TECHNIQUES AVANCÉS {#conseils-techniques}

### Optimisation Performance

#### 1. Cache Streamlit
```python
@st.cache_resource
def load_chatbot():
    """Cache chatbot pour éviter rechargement"""
    return EventChatbot()
```

#### 2. Lazy Loading
```python
# Charger index seulement quand nécessaire
class EventChatbot:
    def __init__(self):
        self._vectorstore = None
    
    @property
    def vectorstore(self):
        if self._vectorstore is None:
            self._vectorstore = self._load_index()
        return self._vectorstore
```

#### 3. Réduire Taille Contexte
```python
# Limiter longueur descriptions dans embeddings
def truncate_text(text, max_words=100):
    words = text.split()
    return ' '.join(words[:max_words])
```

### Amélioration Qualité

#### 1. Prompt Engineering
```python
# Tester plusieurs formulations
prompts = [
    "Tu es un assistant...",
    "En tant qu'expert événements...",
    "Aide l'utilisateur à trouver..."
]

# A/B test et mesurer pertinence
```

#### 2. Hybrid Search (optionnel)
```python
# Combiner recherche sémantique + filtres métadonnées
def hybrid_search(query, filters=None):
    # 1. Recherche sémantique
    semantic_results = vectorstore.similarity_search(query, k=20)
    
    # 2. Filtrer par métadonnées
    if filters:
        filtered = [
            doc for doc in semantic_results
            if matches_filters(doc.metadata, filters)
        ]
        return filtered[:5]
    
    return semantic_results[:5]
```

#### 3. Reranking (optionnel)
```python
# Re-classer résultats par pertinence
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_results(query, documents):
    pairs = [[query, doc.page_content] for doc in documents]
    scores = reranker.predict(pairs)
    
    # Trier par score
    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )
    return [doc for doc, score in ranked]
```

### Monitoring

#### 1. Logs Structurés
```python
import logging
import json_logging

json_logging.init_fastapi(enable_json=True)
logger = logging.getLogger(__name__)

def ask(self, question):
    logger.info("query_received", extra={"query": question})
    
    start = time.time()
    result = self.qa_chain({"query": question})
    latency = time.time() - start
    
    logger.info("query_completed", extra={
        "query": question,
        "latency": latency,
        "sources_count": len(result["source_documents"])
    })
    
    return result
```

#### 2. Métriques Temps Réel
```python
# Streamlit sidebar
st.sidebar.metric("Questions totales", session_state.total_queries)
st.sidebar.metric("Latence moyenne", f"{session_state.avg_latency:.2f}s")
st.sidebar.metric("Taux succès", f"{session_state.success_rate:.0%}")
```

---

## 📚 RESSOURCES & LIENS {#ressources}

### Documentation Officielle

- **Open Agenda API**: https://openagenda.zendesk.com/hc/fr
- **Mistral AI**: https://docs.mistral.ai/
- **LangChain**: https://python.langchain.com/docs/get_started
- **Faiss**: https://github.com/facebookresearch/faiss/wiki
- **Streamlit**: https://docs.streamlit.io/
- **FastAPI**: https://fastapi.tiangolo.com/

### Tutoriels Recommandés

- LangChain RAG: https://python.langchain.com/docs/use_cases/question_answering/
- Mistral + LangChain: https://python.langchain.com/docs/integrations/chat/mistralai/
- Faiss Best Practices: https://github.com/facebookresearch/faiss/wiki/Faiss-building-blocks

### Modèles Embeddings

- **all-MiniLM-L6-v2** (recommandé POC): 384 dimensions, rapide
- **all-mpnet-base-v2**: 768 dimensions, plus précis mais plus lent
- **paraphrase-multilingual-MiniLM-L12-v2**: multilingue

### Outils Utiles

- **Postman**: tester API REST
- **DB Browser**: visualiser données
- **Weights & Biases**: tracking expériences (optionnel)

---

## 🚀 COMMANDES RAPIDES

### Setup Initial
```bash
# Créer environnement
python -m venv venv
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Configurer secrets
cp .env.example .env
# Éditer .env avec vos clés
```

### Développement
```bash
# Fetch data
python scripts/fetch_events.py

# Build index
python scripts/build_index.py

# Run Streamlit
streamlit run app.py

# Run API (si implémentée)
uvicorn api.main:app --reload
```

### Tests
```bash
# Tests unitaires
pytest tests/

# Évaluation RAG
python scripts/evaluate_rag.py
```

### Docker
```bash
# Build & Run
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## ✅ CHECKLIST FINALE AVANT DÉMO

### 48h Avant (22 janvier)
- [ ] Tous les scripts fonctionnent sans erreur
- [ ] Index vectoriel complet et testé
- [ ] Application Streamlit professionnelle
- [ ] 30+ questions testées avec succès
- [ ] Métriques validées (latence < 3s, pertinence > 80%)
- [ ] Docker build et run OK
- [ ] PowerPoint finalisé
- [ ] Documentation complète

### 24h Avant (23 janvier)
- [ ] Répétition présentation (timing)
- [ ] Scénarios démo préparés (3-5 exemples)
- [ ] Vidéo backup enregistrée
- [ ] Environnement démo testé (laptop/connexion)
- [ ] Plan B si problème technique
- [ ] Slides relues (typos, clarté)
- [ ] Réponses aux questions attendues préparées

### Jour J (24 janvier)
- [ ] ☕ Bien reposé
- [ ] Laptop chargé + chargeur
- [ ] Connexion Internet stable
- [ ] Docker containers pré-démarrés
- [ ] Slides ouverts
- [ ] Terminal prêt
- [ ] Enthousiasme et confiance !

---

## 🎓 CONCLUSION

Ce projet RAG est ambitieux mais réalisable en 14 jours avec une approche méthodique :

**Clés du succès :**
1. **Prioriser impitoyablement** : focus sur fonctionnalités core
2. **Tester tôt et souvent** : validation continue
3. **Documenter au fur et à mesure** : pas tout à la fin
4. **Préparer la démo dès J10** : ne pas attendre dernière minute
5. **Rester simple** : MVP > complexité prématurée

**Si manque de temps :**
- ❌ Sacrifier : API REST, tests unitaires exhaustifs, nice-to-have
- ✅ Garder : Streamlit, RAG core, démo fluide, présentation solide

**Bon courage Pierre ! 🚀**

N'oubliez pas : un POC bien présenté vaut mieux qu'un système parfait mal démontré.

---

**Version** : 1.0  
**Dernière mise à jour** : 10 janvier 2026  
**Auteur** : Claude (Assistant AI)
