"""API FastAPI - Endpoints REST pour le RAG avec memoire conversationnelle."""

import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.config.settings import settings
from src.rag.engine import RAGEngine

MAX_HISTORY = 5  # Nombre de messages user en mémoire


# Modèles Pydantic
class Message(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)


class DocumentResult(BaseModel):
    title: str
    content: str
    metadata: dict
    similarity: float
    distance: float


class SearchResponse(BaseModel):
    results: list[DocumentResult]
    query: str


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    session_id: str | None = Field(None, description="ID de session pour la mémoire")
    top_k: int = Field(5, ge=1, le=20)


class ChatResponse(BaseModel):
    response: str
    sources: list[DocumentResult]
    query: str
    session_id: str


# Stockage des sessions (en mémoire)
sessions: dict[str, list[dict]] = defaultdict(list)


@lru_cache
def get_rag_engine() -> RAGEngine:
    return RAGEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_rag_engine()
    yield
    sessions.clear()


app = FastAPI(
    title="Events RAG API",
    description="API chatbot avec mémoire pour événements culturels",
    version="1.0.0",
    lifespan=lifespan,
)

if settings.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health")
async def health_check():
    try:
        rag = get_rag_engine()
        return {
            "status": "healthy",
            "documents": rag.num_documents,
            "embedding_dim": rag.embedding_dim,
            "active_sessions": len(sessions),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    try:
        rag = get_rag_engine()
        results = rag.search(request.query, top_k=request.top_k)
        return SearchResponse(
            results=[
                DocumentResult(
                    title=r["document"]["title"],
                    content=r["document"]["content"],
                    metadata=r["document"]["metadata"],
                    similarity=r["similarity"],
                    distance=r["distance"],
                )
                for r in results
            ],
            query=request.query,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat avec mémoire des 5 derniers échanges."""
    try:
        rag = get_rag_engine()

        # Gérer la session
        session_id = request.session_id or str(uuid.uuid4())
        history = sessions[session_id]

        # Appel RAG avec historique
        result = rag.chat(request.query, top_k=request.top_k, history=history)

        # Mettre à jour l'historique (garder les 5 derniers échanges = 10 messages)
        history.append({"role": "user", "content": request.query})
        history.append({"role": "assistant", "content": result["response"]})

        # Limiter à MAX_HISTORY échanges (user + assistant)
        if len(history) > MAX_HISTORY * 2:
            sessions[session_id] = history[-(MAX_HISTORY * 2) :]

        return ChatResponse(
            response=result["response"],
            sources=[
                DocumentResult(
                    title=r["document"]["title"],
                    content=r["document"]["content"],
                    metadata=r["document"]["metadata"],
                    similarity=r["similarity"],
                    distance=r["distance"],
                )
                for r in result["sources"]
            ],
            query=result["query"],
            session_id=session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Efface l'historique d'une session."""
    if session_id in sessions:
        del sessions[session_id]
        return {"status": "cleared", "session_id": session_id}
    raise HTTPException(status_code=404, detail="Session non trouvée")


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Recupere l'historique d'une session."""
    if session_id in sessions:
        return {"session_id": session_id, "history": sessions[session_id]}
    raise HTTPException(status_code=404, detail="Session non trouvee")


# =============================================================================
# REBUILD ENDPOINT
# =============================================================================

# Stockage du statut des taches de reconstruction
rebuild_tasks: dict[str, dict] = {}


class RebuildResponse(BaseModel):
    """Reponse de demarrage de reconstruction."""

    status: str = Field(..., description="Statut de la requete (accepted)")
    message: str = Field(..., description="Message descriptif")
    task_id: str = Field(..., description="ID de la tache pour suivre la progression")


class RebuildStatusResponse(BaseModel):
    """Reponse de statut de reconstruction."""

    status: str = Field(..., description="Statut (in_progress, completed, failed)")
    progress: float | None = Field(None, description="Progression (0.0 a 1.0)")
    message: str | None = Field(None, description="Message de progression")
    documents_processed: int | None = Field(None, description="Nombre de documents traites")
    embedding_dimension: int | None = Field(None, description="Dimension des embeddings")
    index_vectors: int | None = Field(None, description="Nombre de vecteurs dans l'index")
    elapsed_seconds: float | None = Field(None, description="Temps ecoule en secondes")
    error: str | None = Field(None, description="Message d'erreur si echec")


def verify_rebuild_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")) -> str:
    """
    Verifie la cle API pour l'endpoint /rebuild.

    Args:
        x_api_key: Cle API fournie dans le header X-API-Key.

    Returns:
        La cle API validee.

    Raises:
        HTTPException: Si la cle est invalide ou manquante.
    """
    if not settings.rebuild_api_key:
        raise HTTPException(
            status_code=500,
            detail="REBUILD_API_KEY non configuree sur le serveur",
        )
    if not x_api_key or x_api_key != settings.rebuild_api_key:
        raise HTTPException(
            status_code=401,
            detail="Cle API invalide ou manquante",
        )
    return x_api_key


@app.post("/rebuild", response_model=RebuildResponse)
async def rebuild_index(
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_rebuild_api_key),
):
    """
    Reconstruit l'index FAISS a partir des documents sources.

    Necessite le header X-API-Key avec une cle valide (REBUILD_API_KEY).
    La reconstruction s'execute en arriere-plan.
    Utilisez GET /rebuild/{task_id} pour suivre la progression.
    """
    from src.rag.index_builder import IndexBuilder

    task_id = str(uuid.uuid4())
    rebuild_tasks[task_id] = {"status": "in_progress", "progress": 0.0, "message": "Demarrage"}

    def progress_callback(message: str, percentage: float) -> None:
        rebuild_tasks[task_id]["progress"] = percentage
        rebuild_tasks[task_id]["message"] = message

    def run_rebuild() -> None:
        try:
            builder = IndexBuilder(progress_callback=progress_callback)
            result = builder.rebuild()

            rebuild_tasks[task_id] = {
                "status": "completed",
                "progress": 1.0,
                "message": "Reconstruction terminee",
                **result,
            }

            # Vider le cache du RAG engine pour recharger l'index
            get_rag_engine.cache_clear()

        except Exception as e:
            rebuild_tasks[task_id] = {
                "status": "failed",
                "progress": rebuild_tasks[task_id].get("progress", 0),
                "message": "Echec de la reconstruction",
                "error": str(e),
            }

    background_tasks.add_task(run_rebuild)

    return RebuildResponse(
        status="accepted",
        message="Reconstruction de l'index demarree en arriere-plan",
        task_id=task_id,
    )


@app.get("/rebuild/{task_id}", response_model=RebuildStatusResponse)
async def get_rebuild_status(task_id: str):
    """
    Recupere le statut d'une tache de reconstruction.

    Args:
        task_id: ID de la tache retourne par POST /rebuild.
    """
    if task_id not in rebuild_tasks:
        raise HTTPException(status_code=404, detail="Tache non trouvee")
    return RebuildStatusResponse(**rebuild_tasks[task_id])
