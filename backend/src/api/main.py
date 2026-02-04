"""API FastAPI - Endpoints REST pour le RAG avec memoire conversationnelle."""

# Fix OpenMP duplicate library error on macOS
import os

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import time
import uuid
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.database.connection import close_db, get_db, init_db
from src.database.repository import MessageRepository, SessionRepository
from src.rag.engine import RAGEngine

MAX_HISTORY = 5  # Nombre de messages (paires user+assistant) à conserver en DB


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


@lru_cache
def get_rag_engine() -> RAGEngine:
    return RAGEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize RAG engine
    get_rag_engine()
    # Initialize database tables
    await init_db()
    yield
    # Close database connections
    await close_db()


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
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        rag = get_rag_engine()

        # Test database connection and count sessions
        from src.database.models import SessionModel

        stmt = select(SessionModel)
        result = await db.execute(stmt)
        active_sessions = len(list(result.scalars().all()))

        return {
            "status": "healthy",
            "document_count": rag.num_documents,
            "embedding_dimension": rag.embedding_dim,
            "active_sessions": active_sessions,
            "database": "connected",
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
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Chat avec mémoire des 5 derniers échanges."""
    try:
        rag = get_rag_engine()
        session_repo = SessionRepository(db)
        message_repo = MessageRepository(db)

        # Parse or generate session_id
        if request.session_id:
            try:
                session_id = uuid.UUID(request.session_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid session_id format")
        else:
            session_id = uuid.uuid4()

        # Get or create session
        session = await session_repo.get_by_id(session_id)
        if not session:
            session = await session_repo.create(session_id=session_id)

        # Get conversation history (limited to MAX_HISTORY * 2 messages)
        history = await message_repo.get_session_history(
            session_id=session_id,
            limit=MAX_HISTORY * 2,
        )

        # Track latency
        start_time = time.time()

        # Appel RAG avec historique
        result = rag.chat(request.query, top_k=request.top_k, history=history)

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000

        # Save user message
        await message_repo.create(
            session_id=session_id,
            role="user",
            content=request.query,
            query_type="chat",
        )

        # Convert sources to list for JSON serialization
        sources_json = [
            {
                "title": r["document"]["title"],
                "content": r["document"]["content"],
                "metadata": r["document"]["metadata"],
                "similarity": r["similarity"],
                "distance": r["distance"],
            }
            for r in result["sources"]
        ]

        # Save assistant message with metadata
        await message_repo.create(
            session_id=session_id,
            role="assistant",
            content=result["response"],
            sources=sources_json,
            latency_ms=latency_ms,
            top_k=request.top_k,
            query_type="chat",
        )

        # Update session timestamp
        await session_repo.update_timestamp(session_id)

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
            session_id=str(session_id),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/session/{session_id}")
async def clear_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Efface l'historique d'une session."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    session_repo = SessionRepository(db)
    deleted = await session_repo.delete(session_uuid)

    if not deleted:
        raise HTTPException(status_code=404, detail="Session non trouvée")

    return {"status": "cleared", "session_id": session_id}


@app.get("/session/{session_id}")
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Recupere l'historique d'une session."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    session_repo = SessionRepository(db)
    session = await session_repo.get_by_id(session_uuid)

    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvee")

    # Convert messages to dict format
    history = [msg.to_dict() for msg in session.messages]

    return {
        "session_id": session_id,
        "history": history,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
    }


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


# =============================================================================
# EVENTS ENDPOINT
# =============================================================================


class Location(BaseModel):
    """Localisation d'un evenement."""

    city: str
    address: str | None = None
    postal_code: str | None = None


class DateRange(BaseModel):
    """Plage de dates d'un evenement."""

    start: str
    end: str


class Event(BaseModel):
    """Evenement culturel."""

    title: str
    description: str
    location: Location
    date_range: DateRange
    category: str | None = None
    price: float | None = None
    is_free: bool | None = None
    url: str | None = None
    image_url: str | None = None


class EventsListResponse(BaseModel):
    """Reponse de la liste des evenements."""

    events: list[Event]
    total: int
    skip: int
    limit: int


def _extract_description(content: str) -> str:
    """Extrait la description du contenu formaté."""
    lines = content.split("\n")
    for line in lines:
        if line.startswith("Description: "):
            return line[len("Description: ") :]
    return content


@app.get("/events", response_model=EventsListResponse)
async def list_events(skip: int = 0, limit: int = 100):
    """
    Liste tous les evenements indexes.

    Args:
        skip: Nombre d'evenements a sauter (pagination).
        limit: Nombre maximum d'evenements a retourner.

    Returns:
        Liste paginee des evenements.
    """
    try:
        rag = get_rag_engine()
        events = []

        for doc in rag.documents:
            metadata = doc.get("metadata", {})
            events.append(
                Event(
                    title=doc.get("title", ""),
                    description=_extract_description(doc.get("content", "")),
                    location=Location(
                        city=metadata.get("city", ""),
                        address=metadata.get("address"),
                    ),
                    date_range=DateRange(
                        start=metadata.get("start_date", ""),
                        end=metadata.get("end_date", ""),
                    ),
                    url=metadata.get("url"),
                )
            )

        total = len(events)
        paginated = events[skip : skip + limit]

        return EventsListResponse(
            events=paginated,
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
