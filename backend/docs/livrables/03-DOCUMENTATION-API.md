# Reference de l'API REST

Documentation complete des endpoints de l'API RAG Events Assistant.

**URL de base**: `http://localhost:8000`

**Documentation interactive**: Disponible a `/docs` (Swagger UI) et `/redoc` (ReDoc)

---

## Endpoints

### GET /health

Verifie l'etat de sante de l'API.

**Requete**:
```bash
curl http://localhost:8000/health
```

**Reponse 200 (OK)**:
```json
{
    "status": "healthy",
    "documents": 497,
    "embedding_dim": 1024,
    "active_sessions": 2
}
```

**Reponse 503 (Service Unavailable)**:
```json
{
    "detail": "Index FAISS non trouve: data/processed/faiss_index/events.index"
}
```

---

### POST /search

Effectue une recherche semantique dans les evenements.

**Headers**:
```
Content-Type: application/json
```

**Corps de la requete**:
```json
{
    "query": "concert de jazz a Paris",
    "top_k": 5
}
```

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `query` | string | Oui | Requete de recherche (min 1 caractere) |
| `top_k` | integer | Non | Nombre de resultats (1-20, defaut: 5) |

**Requete curl**:
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "exposition art contemporain", "top_k": 3}'
```

**Reponse 200**:
```json
{
    "results": [
        {
            "title": "Exposition d'art contemporain",
            "content": "Titre: Exposition d'art contemporain\nVille: Marseille\nDate: 15/01/2025...",
            "metadata": {
                "city": "Marseille",
                "url": "https://openagenda.com/event/123",
                "category": "Exposition"
            },
            "similarity": 0.531,
            "distance": 0.469
        }
    ],
    "query": "exposition art contemporain"
}
```

**Reponse 422 (Validation Error)**:
```json
{
    "detail": [
        {
            "type": "string_too_short",
            "loc": ["body", "query"],
            "msg": "String should have at least 1 character",
            "input": ""
        }
    ]
}
```

---

### POST /chat

Envoie un message au chatbot avec memoire conversationnelle.

**Corps de la requete**:
```json
{
    "query": "Quels concerts sont prevus ce weekend ?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "top_k": 5
}
```

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `query` | string | Oui | Message de l'utilisateur |
| `session_id` | string | Non | ID de session (auto-genere si absent) |
| `top_k` | integer | Non | Nombre de resultats (1-20, defaut: 5) |

**Requete curl (nouvelle session)**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Bonjour !"}'
```

**Requete curl (session existante)**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Des concerts ce weekend ?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Reponse 200**:
```json
{
    "response": "Salut ! Je suis la pour t'aider a trouver des evenements...",
    "sources": [
        {
            "title": "Concert Jazz Manouche",
            "content": "...",
            "metadata": {"city": "Paris", "url": "..."},
            "similarity": 0.72,
            "distance": 0.28
        }
    ],
    "query": "Des concerts ce weekend ?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Notes**:
- Si `session_id` n'est pas fourni, un nouvel ID est genere (UUID v4)
- L'historique est limite a 5 echanges (10 messages)
- Les sources sont vides si la requete est conversationnelle (salutation, remerciement)

---

### GET /session/{session_id}

Recupere l'historique d'une session.

**Parametres de chemin**:
| Parametre | Type | Description |
|-----------|------|-------------|
| `session_id` | string | ID de la session |

**Requete curl**:
```bash
curl http://localhost:8000/session/550e8400-e29b-41d4-a716-446655440000
```

**Reponse 200**:
```json
{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "history": [
        {"role": "user", "content": "Bonjour !"},
        {"role": "assistant", "content": "Salut ! Comment puis-je t'aider ?"},
        {"role": "user", "content": "Des concerts ce weekend ?"},
        {"role": "assistant", "content": "Voici quelques concerts..."}
    ]
}
```

**Reponse 404**:
```json
{
    "detail": "Session non trouvee"
}
```

---

### DELETE /session/{session_id}

Supprime une session et son historique.

**Requete curl**:
```bash
curl -X DELETE http://localhost:8000/session/550e8400-e29b-41d4-a716-446655440000
```

**Reponse 200**:
```json
{
    "status": "cleared",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Reponse 404**:
```json
{
    "detail": "Session non trouvee"
}
```

---

### POST /rebuild

Reconstruit l'index FAISS a partir des documents sources.

**Authentification requise**: Header `X-API-Key`

**Headers**:
```
Content-Type: application/json
X-API-Key: votre_cle_api_rebuild
```

**Requete curl**:
```bash
curl -X POST http://localhost:8000/rebuild \
  -H "X-API-Key: votre_cle_api_rebuild"
```

**Reponse 200 (Accepted)**:
```json
{
    "status": "accepted",
    "message": "Reconstruction de l'index demarree en arriere-plan",
    "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

**Reponse 401 (Unauthorized)**:
```json
{
    "detail": "Cle API invalide ou manquante"
}
```

**Reponse 500 (Server Error)**:
```json
{
    "detail": "REBUILD_API_KEY non configuree sur le serveur"
}
```

**Notes**:
- La reconstruction s'execute en arriere-plan
- Utilisez `GET /rebuild/{task_id}` pour suivre la progression
- Le cache du RAGEngine est invalide automatiquement apres succes

---

### GET /rebuild/{task_id}

Recupere le statut d'une tache de reconstruction.

**Parametres de chemin**:
| Parametre | Type | Description |
|-----------|------|-------------|
| `task_id` | string | ID de la tache (retourne par POST /rebuild) |

**Requete curl**:
```bash
curl http://localhost:8000/rebuild/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

**Reponse 200 (En cours)**:
```json
{
    "status": "in_progress",
    "progress": 0.45,
    "message": "Generation embeddings: 150/300"
}
```

**Reponse 200 (Termine)**:
```json
{
    "status": "completed",
    "progress": 1.0,
    "message": "Reconstruction terminee",
    "documents_processed": 497,
    "embedding_dimension": 1024,
    "index_vectors": 497,
    "elapsed_seconds": 45.23
}
```

**Reponse 200 (Echec)**:
```json
{
    "status": "failed",
    "progress": 0.32,
    "message": "Echec de la reconstruction",
    "error": "Documents non trouves: data/processed/rag_documents.json"
}
```

**Reponse 404**:
```json
{
    "detail": "Tache non trouvee"
}
```

---

## Codes de Reponse

| Code | Signification | Cas d'usage |
|------|---------------|-------------|
| 200 | OK | Requete reussie |
| 401 | Unauthorized | Cle API manquante ou invalide (/rebuild) |
| 404 | Not Found | Session ou tache non trouvee |
| 422 | Validation Error | Parametres invalides |
| 500 | Internal Server Error | Erreur serveur |
| 503 | Service Unavailable | Index non disponible |

---

## Modeles de Donnees

### SearchRequest
```json
{
    "query": "string (min: 1)",
    "top_k": "integer (1-20, default: 5)"
}
```

### ChatRequest
```json
{
    "query": "string (min: 1)",
    "session_id": "string | null",
    "top_k": "integer (1-20, default: 5)"
}
```

### DocumentResult
```json
{
    "title": "string",
    "content": "string",
    "metadata": {
        "city": "string",
        "url": "string",
        "category": "string"
    },
    "similarity": "float (0-1)",
    "distance": "float"
}
```

### Message
```json
{
    "role": "user | assistant",
    "content": "string"
}
```

---

## Exemples d'Integration

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# Recherche
response = requests.post(
    f"{BASE_URL}/search",
    json={"query": "concert jazz", "top_k": 3}
)
results = response.json()

# Chat avec session
session_id = None
for message in ["Bonjour", "Des concerts ce soir ?", "Merci !"]:
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"query": message, "session_id": session_id}
    )
    data = response.json()
    session_id = data["session_id"]
    print(f"Bot: {data['response']}")
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000";

// Recherche
async function search(query) {
    const response = await fetch(`${BASE_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 5 })
    });
    return response.json();
}

// Chat
async function chat(query, sessionId = null) {
    const response = await fetch(`${BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, session_id: sessionId })
    });
    return response.json();
}
```

### cURL (Bash)

```bash
# Fonction de chat avec session
SESSION_ID=""

chat() {
    RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$1\", \"session_id\": $SESSION_ID}")

    echo "$RESPONSE" | jq -r '.response'
    SESSION_ID=$(echo "$RESPONSE" | jq -r '.session_id')
}

chat "Bonjour !"
chat "Quels concerts ce soir ?"
chat "Merci !"
```
