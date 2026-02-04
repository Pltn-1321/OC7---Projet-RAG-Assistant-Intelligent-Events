# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **monorepo** containing a RAG (Retrieval-Augmented Generation) chatbot for discovering cultural events using natural language queries. The system retrieves events from the Open Agenda API, indexes them with FAISS vector embeddings, and uses Mistral AI to generate conversational responses.

## Monorepo Structure

```
.
├── backend/                 # Python API + RAG Engine
│   ├── src/                 # Source code
│   │   ├── api/             # FastAPI REST API
│   │   ├── rag/             # RAG engine (LangChain LCEL)
│   │   ├── config/          # Settings & constants
│   │   └── data/            # Pydantic models
│   ├── tests/               # Unit, integration, e2e tests
│   ├── notebooks/           # Jupyter notebooks (data pipeline)
│   ├── scripts/             # Utility scripts
│   ├── docs/                # Backend documentation
│   ├── data/                # Data files (not versioned)
│   ├── app.py               # Streamlit UI (alternative)
│   ├── pyproject.toml       # Python dependencies (uv)
│   └── Dockerfile           # Backend Docker image
│
├── frontend/                # React application
│   ├── src/                 # TypeScript source code
│   ├── docs/                # Frontend documentation
│   ├── package.json         # Node.js dependencies
│   └── Dockerfile           # Frontend Docker image
│
├── docker-compose.yml       # Service orchestration
├── .gitignore               # Monorepo gitignore
├── LICENSE                  # MIT License
└── README.md                # Project overview
```

## Tech Stack

### Backend
- **Python 3.11+** with **uv** package manager
- **LangChain LCEL** for RAG orchestration
- **Mistral AI** (LLM + Embeddings)
- **FAISS** vector store
- **FastAPI** REST API
- **Streamlit** alternative UI

### Frontend
- **React 18+** with **TypeScript**
- **Vite** build tool
- **Tailwind CSS** + **shadcn/ui**

## Common Commands

### Backend (from `backend/` directory)

```bash
# Install dependencies
uv sync --all-extras

# Run FastAPI server
uv run uvicorn src.api.main:app --reload

# Run Streamlit
uv run streamlit run app.py

# Run tests
uv run pytest --cov=src

# Format & lint
uv run black src tests && uv run ruff check src tests
```

### Frontend (from `frontend/` directory)

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

### Docker (from root)

```bash
# Start all services
docker-compose up

# Start specific services
docker-compose up api frontend
docker-compose up api streamlit

# Build images
docker-compose build
```

## Implementation Status

✅ **Fully Implemented**:
- Core RAG pipeline with query classification (RAGEngine, IndexBuilder)
- Mistral AI integration (LLM + embeddings)
- FAISS vector store with metadata persistence
- FastAPI REST API with session management and background tasks
- Streamlit chat interface with modern dark theme
- React frontend with TypeScript
- Complete test suite (unit, integration, e2e)
- Docker containerization with multi-mode support
- RAGAS evaluation framework
- Comprehensive documentation

📓 **Jupyter Notebook-based**:
- Data collection from Open Agenda API
- Data preprocessing and cleaning
- Index building and experimentation

## Architecture

### RAG Pipeline Flow
```
User Query → Frontend React / Streamlit → FastAPI → RAGEngine
                                                        ↓
                                                  Query Classification
                                                  (needs_rag() check)
                                                        ↓
                              ┌─────────────────────────┴─────────────────────────┐
                              ↓                                                   ↓
                         CHAT Mode                                          SEARCH Mode (RAG)
                  (conversation_response)                                         ↓
                              ↓                                    1. Encode query (Mistral)
                      Simple LLM chat                              2. FAISS semantic search (top-k)
                        (no context)                               3. Generate response with context
                              ↓                                                   ↓
                              └───────────────────────┬───────────────────────────┘
                                                      ↓
                                            Response + Sources (if RAG)
```

### Backend Module Organization

All backend code lives in `backend/src/` following the src-layout pattern:

- **src/config/**: Configuration management
  - `settings.py`: Pydantic Settings with environment variable validation
  - `constants.py`: Application constants (prompts, paths, thresholds)

- **src/data/**: Data models
  - `models.py`: Pydantic models (Event, Location, QueryResponse, etc.)

- **src/rag/**: Core RAG logic (LangChain LCEL-based)
  - `engine.py`: RAGEngine class with LCEL chains
  - `embeddings.py`: Mistral embeddings factory
  - `llm.py`: Factory for LLM
  - `vectorstore.py`: FAISS vector store management
  - `index_builder.py`: FAISS index construction

- **src/api/**: FastAPI REST API
  - `main.py`: Complete REST API with session management

### Key Files

| File | Description |
|------|-------------|
| `backend/src/rag/engine.py` | RAGEngine with LCEL chains |
| `backend/src/api/main.py` | FastAPI endpoints |
| `backend/src/config/settings.py` | Pydantic Settings |
| `backend/app.py` | Streamlit interface |
| `frontend/src/App.tsx` | Main React component |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/search` | POST | Semantic search (no session) |
| `/chat` | POST | Chat with session |
| `/session/{id}` | GET/DELETE | Session management |
| `/rebuild` | POST | Rebuild FAISS index |

## Environment Variables

Required at root level (`.env`):

| Variable | Description | Required |
|----------|-------------|----------|
| `MISTRAL_API_KEY` | Mistral AI API key | Yes |
| `REBUILD_API_KEY` | API key for /rebuild endpoint | No |

## Testing

```bash
# Backend tests (from backend/)
uv run pytest
uv run pytest --cov=src --cov-report=html

# Frontend tests (from frontend/)
npm run test
```

## Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Project overview |
| [backend/README.md](backend/README.md) | Full backend documentation |
| [backend/docs/](backend/docs/) | Architecture, API, guides |
| [frontend/README.md](frontend/README.md) | Frontend documentation |
| [frontend/docs/](frontend/docs/) | Implementation details |

## Development Conventions

1. **Backend commands via `uv run`** from `backend/` directory
2. **Frontend commands via `npm`** from `frontend/` directory
3. **Type hints**: Modern Python 3.11+ syntax (`list[str]` not `List[str]`)
4. **Line length**: 100 characters (Black + Ruff)
5. **French language**: User-facing text in French
6. **Commits**: Conventional Commits format

## Critical Implementation Details

### LangChain LCEL Integration

```python
# LangChain components used
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# LCEL chain example
chain = ChatPromptTemplate | ChatMistralAI | StrOutputParser
```

### FAISS Index Management

```python
# Loading a FAISS index (LangChain format)
from langchain_community.vectorstores import FAISS
vectorstore = FAISS.load_local(folder_path, embeddings, allow_dangerous_deserialization=True)

# Files created by save_local():
# - index.faiss (FAISS binary index)
# - index.pkl (docstore and mapping)
# - config.json (custom metadata)
```

### Data Directories (in `backend/`)
- `data/raw/`: Raw events from Open Agenda API
- `data/processed/`: Cleaned and structured events
- `data/indexes/`: FAISS vector indexes
- All data directories are in `.gitignore` (not versioned)

### Performance Targets
- `TARGET_LATENCY_SECONDS = 3.0`: Responses must be < 3 seconds
- `TARGET_RELEVANCE_SCORE = 0.8`: 80%+ keyword coverage in answers
- `TARGET_COVERAGE = 0.7`: 70%+ of test questions answered successfully

## Known Limitations

- **Manual index updates**: No automatic refresh from Open Agenda API
- **Limited conversation memory**: Only stores last 5 messages per session
- **Default location**: Configured for Marseille
- **No user authentication**: API and Streamlit are open access
- **In-memory session storage**: Sessions lost on restart
- **French language only**: All prompts and responses are in French
