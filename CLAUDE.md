# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a RAG (Retrieval-Augmented Generation) chatbot for discovering cultural events using natural language queries. The system retrieves events from the Open Agenda API, indexes them with FAISS vector embeddings, and uses Mistral AI to generate conversational responses.

**Stack**: Python 3.11+, Streamlit (UI), Mistral AI (LLM + Embeddings), FAISS (vector store), FastAPI (REST API), Open Agenda API (data)

**Package Manager**: This project uses `uv` (not pip). All dependency management and script execution should be done through `uv`.

**Architecture**: LangChain LCEL (LangChain Expression Language) for RAG orchestration, with Mistral AI (LLM + Embeddings) and FAISS (vector store).

## Implementation Status

✅ **Fully Implemented**:
- Core RAG pipeline with query classification (RAGEngine, IndexBuilder)
- Mistral AI integration (LLM + embeddings) with sentence-transformers fallback
- FAISS vector store with metadata persistence
- FastAPI REST API with session management and background tasks
- Streamlit chat interface with modern dark theme
- Complete test suite (unit, integration, e2e)
- Docker containerization with multi-mode support
- RAGAS evaluation framework
- Comprehensive documentation

📓 **Jupyter Notebook-based**:
- Data collection from Open Agenda API
- Data preprocessing and cleaning
- Index building and experimentation

⚠️ **Architectural Notes**:
- No separate retriever/generator/embeddings modules - consolidated in RAGEngine
- No standalone scripts for data pipeline - handled via notebooks + API `/rebuild` endpoint
- UI in root `app.py`, not `src/ui/` directory

## Common Commands

### Environment Setup
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies
uv sync

# Install with optional dependencies
uv sync --extra dev          # Development tools (testing, linting, notebooks)
uv sync --extra api          # FastAPI REST API
uv sync --extra evaluation   # RAG evaluation tools
uv sync --all-extras         # Everything
```

### Development Workflow
```bash
# 1. Fetch events and build index using Jupyter notebooks
uv run jupyter lab  # Run notebooks/01_data_collection.ipynb through 04_build_faiss_index.ipynb

# OR use the FastAPI rebuild endpoint:
# POST http://localhost:8000/rebuild with events data

# 2. Run Streamlit application
uv run streamlit run app.py

# 3. Run FastAPI server
uv run uvicorn src.api.main:app --reload

# 4. Test API endpoints
uv run python scripts/api_test.py
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test types
uv run pytest tests/unit/              # Unit tests only
uv run pytest tests/integration/ -m integration
uv run pytest tests/e2e/ -m e2e

# Exclude slow tests
uv run pytest -m "not slow"

# Run RAG evaluation
uv run python scripts/evaluate_rag.py --test-file tests/data/test_questions.json
```

### Code Quality
```bash
# Format code with Black
uv run black src tests scripts

# Lint with Ruff
uv run ruff check src tests scripts

# Type check with mypy
uv run mypy src

# Run pre-commit hooks
uv run pre-commit install
uv run pre-commit run --all-files
```

### Jupyter Notebooks
```bash
uv run jupyter lab
uv run jupyter notebook
```

### FastAPI Endpoints
The REST API (`src/api/main.py`) provides the following endpoints:

```bash
# Health check
GET /health

# Semantic search (no session)
POST /search
Body: {"query": "concerts ce weekend", "top_k": 5}

# Chat with session management
POST /chat
Body: {"query": "salut", "session_id": "optional-id"}

# Get session history
GET /session/{session_id}

# Delete session
DELETE /session/{session_id}

# Rebuild FAISS index (background task with progress tracking)
POST /rebuild
Headers: X-API-Key: <REBUILD_API_KEY>
Body: {"events": [...], "use_mistral_embeddings": true}
```

## Architecture

### RAG Pipeline Flow
```
User Query → Streamlit UI / FastAPI → RAGEngine
                                          ↓
                                    Query Classification
                                    (needs_rag() check)
                                          ↓
                        ┌─────────────────┴─────────────────┐
                        ↓                                   ↓
                   CHAT Mode                          SEARCH Mode (RAG)
            (conversation_response)                         ↓
                        ↓                          1. Encode query (Mistral/ST)
                Simple LLM chat                    2. FAISS semantic search (top-k)
                  (no context)                     3. Generate response with context
                        ↓                                   ↓
                        └───────────────┬─────────────────┘
                                        ↓
                              Response + Sources (if RAG)
```

### Module Organization

**src-layout pattern**: All source code lives in `src/` to avoid import issues.

- **src/config/**: ✅ Configuration management (fully implemented)
  - `settings.py`: Pydantic Settings with environment variable validation
    - API keys (MISTRAL_API_KEY, REBUILD_API_KEY, OPENAGENDA_API_KEY)
    - Embedding provider selection (mistral vs sentence-transformers)
    - LLM configuration (model, temperature, max_tokens)
    - Retrieval settings (top_k_results, min_similarity_score)
    - API and Streamlit configuration
  - `constants.py`: Application constants
    - Project paths (DATA_DIR, INDEXES_DIR, etc.)
    - Model names (MISTRAL_MODELS, EMBEDDING_MODELS)
    - Prompt templates (SYSTEM_PROMPT_TEMPLATE)
    - Validation constants and metrics thresholds
    - Event categories and file names

- **src/data/**: Data models and access
  - `models.py`: ✅ Pydantic models for Event, Location, DateRange, QueryResponse, EvaluationQuestion, EvaluationResult
  - Data fetching and preprocessing handled via Jupyter notebooks (`notebooks/01_data_collection.ipynb`, `notebooks/02_data_preprocessing.ipynb`)

- **src/rag/**: Core RAG logic (LangChain LCEL-based)
  - `engine.py`: ✅ RAGEngine class with LCEL chains
    - Query classification (`needs_rag()`) via classification chain
    - Conversational responses (`conversation_response()`) via conversation chain
    - Semantic search (`search()`) via LangChain FAISS vector store
    - Response generation (`generate_response()`) via RAG chain
    - Unified chat interface (`chat()`) - Complete pipeline with automatic RAG detection
  - `embeddings.py`: ✅ Factory `get_embeddings()` → `MistralAIEmbeddings` or `HuggingFaceEmbeddings`
  - `llm.py`: ✅ Factory `get_llm()` → `ChatMistralAI` with configurable parameters
  - `vectorstore.py`: ✅ Functions `load_vectorstore()`, `build_vectorstore()`, `save_vectorstore()`
  - `index_builder.py`: ✅ FAISS index construction with LangChain format
    - Uses `FAISS.from_documents()` and `save_local()` for LangChain-compatible serialization
    - Progress tracking, batch processing

- **src/api/**: ✅ FastAPI REST API (fully implemented)
  - `main.py`: Complete REST API with health checks, search, chat with session memory, and background index rebuilding

- **src/ui/**: UI implemented in root-level `app.py` (Streamlit)
  - Modern dark theme with chat interface, message history (max 5), sidebar controls, and streaming responses

- **src/utils/**: Minimal utilities (only `__init__.py`)

- **scripts/**: Standalone executable scripts
  - `evaluate_rag.py`: ✅ Complete RAG evaluation framework with RAGAS integration, keyword coverage metrics, and JSON report generation
  - `api_test.py`: ✅ API testing utilities

- **notebooks/**: Jupyter notebooks for data pipeline
  - `01_data_collection.ipynb`: Event fetching from Open Agenda API
  - `02_data_preprocessing.ipynb`: Data cleaning and HTML stripping
  - `03_create_embeddings_mistral.ipynb`: Embedding generation with Mistral
  - `04_build_faiss_index.ipynb`: FAISS index construction
  - `05_rag_chatbot_mistral.ipynb`: RAG experimentation and testing

- **tests/**: Test suite organized by type (unit, integration, e2e)

### Key Architectural Patterns

1. **Settings Management**: Uses Pydantic Settings with automatic `.env` loading and validation. Access via `from src.config.settings import settings`.

2. **Data Models**: All data uses Pydantic models for validation. The `Event` model includes helper methods:
   - `.to_search_text()`: Formats event for FAISS embedding
   - `.to_display_dict()`: Formats event for UI display
   - `.is_free`, `.is_upcoming`, `.is_past`, `.is_ongoing`: Computed properties

3. **Vector Store**: FAISS via LangChain wrapper (`langchain_community.vectorstores.FAISS`). Default embedding provider: **Mistral** (`mistral-embed`, 1024 dimensions). Also supports HuggingFace (`paraphrase-multilingual-mpnet-base-v2`, 768 dimensions) via settings.

4. **LLM Integration**: LangChain `ChatMistralAI` from `langchain_mistralai`. Uses `mistral-small-latest` model, temperature 0.7, with LCEL chains for orchestration.

5. **Testing Strategy**:
   - Uses pytest with custom markers (slow, integration, e2e, requires_api)
   - Shared fixtures in `tests/conftest.py` for sample events and mock data
   - Target metrics: latency < 3s, relevance > 80%, coverage > 70%

## Critical Implementation Details

### Architecture Note: LangChain LCEL Integration
**This project uses LangChain LCEL for RAG orchestration:**

```python
# LangChain components used
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# LCEL chain example
chain = ChatPromptTemplate | ChatMistralAI | StrOutputParser
```

See `docs/INTEGRATION_LANGCHAIN.md` for detailed architecture documentation.

### FAISS Index Management
FAISS indexes are managed through LangChain's `FAISS` wrapper:

```python
# Loading a FAISS index (LangChain format)
from langchain_community.vectorstores import FAISS
vectorstore = FAISS.load_local(folder_path, embeddings, allow_dangerous_deserialization=True)

# Files created by save_local():
# - index.faiss (FAISS binary index)
# - index.pkl (docstore and mapping)
# - config.json (custom metadata for compatibility)
```

**Migration**: Run `uv run python scripts/migrate_index.py` to convert legacy indexes to LangChain format.

### Embedding Provider Selection
The project supports two embedding providers via `settings.embedding_provider`:

```python
# Mistral embeddings (DEFAULT)
embedding_provider = "mistral"  # Uses mistral-embed (1024 dim)

# Sentence Transformers
embedding_provider = "sentence-transformers"  # Uses paraphrase-multilingual-mpnet-base-v2 (768 dim)
```

### API Keys
- **MISTRAL_API_KEY**: Required for LLM and Mistral embeddings
- **REBUILD_API_KEY**: Optional authentication for the `/rebuild` endpoint
- **OPENAGENDA_API_KEY**: May be required for Open Agenda API access
- All keys should be in `.env` file (never commit to git)
- Access via: `from src.config.settings import settings; settings.mistral_api_key`

### Prompt Template
The system prompt is defined in `src/config/constants.py` as `SYSTEM_PROMPT_TEMPLATE`. It instructs the LLM to:
- Respond in French conversationally
- Recommend 2-3 relevant events maximum
- Include practical info (date, location, price)
- Suggest alternatives if no exact matches
- Be concise but informative

### Data Directories
- `data/raw/`: Raw events from Open Agenda API
- `data/processed/`: Cleaned and structured events
- `data/indexes/`: FAISS vector indexes
- All data directories are in `.gitignore` (not versioned)

### Performance Targets
Per `src/config/constants.py`:
- `TARGET_LATENCY_SECONDS = 3.0`: Responses must be < 3 seconds
- `TARGET_RELEVANCE_SCORE = 0.8`: 80%+ keyword coverage in answers
- `TARGET_COVERAGE = 0.7`: 70%+ of test questions answered successfully

## Project-Specific Conventions

1. **All scripts should be run via `uv run`**, not `python` directly
2. **Type hints**: Use modern Python 3.11+ syntax (`list[str]` not `List[str]`)
3. **Line length**: 100 characters (enforced by Black and Ruff)
4. **String formatting**: Prefer f-strings over `.format()` or `%`
5. **Pydantic models**: Used extensively for data validation - always define field descriptions
6. **French language**: User-facing text and responses are in French
7. **Logging**: Use structured logging with `python-json-logger` for production

## Development Workflow

When implementing new features:

1. **Check configuration**: See if settings need to be added to `settings.py` or constants to `constants.py`
2. **Define models first**: If working with new data structures, add Pydantic models to `src/data/models.py`
3. **Write tests**: Add fixtures to `conftest.py` if needed, write tests before implementation
4. **Run formatters**: `uv run black .` and `uv run ruff check .` before committing
5. **Update evaluation**: If changing RAG behavior, update test questions in `tests/data/test_questions.json`

## Docker

✅ **Fully implemented** with multi-stage build and dual-mode support:

### Docker Setup
```bash
# Build image
docker build -t events-assistant .

# Run Streamlit (default)
docker run -p 8501:8501 --env-file .env -v $(pwd)/data:/app/data events-assistant

# Run FastAPI
docker run -p 8000:8000 --env-file .env -v $(pwd)/data:/app/data events-assistant api

# Using docker-compose
docker-compose up              # Starts both API and Streamlit services
docker-compose up api          # Only API
docker-compose up streamlit    # Only Streamlit
```

### Features
- Multi-stage build (base → dependencies → production)
- Python 3.11-slim base image
- Uses `uv` for dependency management
- Environment variable configuration (MISTRAL_API_KEY required)
- Volume mounting for `data/` persistence
- Built-in healthcheck
- Supports both Streamlit (8501) and FastAPI (8000) modes

## Performance Considerations

1. **Streamlit caching**: RAGEngine initialization uses `@st.cache_resource` for persistence across sessions
2. **FAISS index size**: Varies by embedding provider
   - Mistral embeddings: ~1024 dims × number of events
   - Sentence Transformers: ~768 dims × number of events
3. **Batch processing**: `DEFAULT_BATCH_SIZE = 32` for embedding generation (configurable in constants)
4. **API rate limits**: Respect Open Agenda and Mistral API rate limits
5. **Embedding model**: Default `mistral-embed` for quality multilingual support; `paraphrase-multilingual-mpnet-base-v2` available as alternative
6. **Query classification**: `needs_rag()` method reduces unnecessary FAISS searches for conversational queries
7. **Session memory**: Both API and Streamlit maintain conversation history (MAX_HISTORY = 5 messages)

## Additional Documentation

Comprehensive documentation is available in the `docs/` directory:

- **INTEGRATION_LANGCHAIN.md**: LangChain architecture, components, and migration guide
- **ARCHITECTURE.md**: Detailed system architecture and design decisions
- **COMPRENDRE_LE_RAG.md**: RAG concepts explained (in French)
- **GUIDE_DEMARRAGE.md**: Getting started guide (in French)
- **REFERENCE_API.md**: Complete API reference
- **Guide complet projet RAG.md**: Full project guide (in French)
- **guide-pyproject-toml.md**: pyproject.toml configuration guide

## Known Limitations

- **Manual index updates**: No automatic refresh from Open Agenda API (must use notebooks or `/rebuild` endpoint)
- **Limited conversation memory**: Only stores last 5 messages per session (configurable via MAX_HISTORY)
- **Default location**: Configured for Marseille (changeable via settings.default_location)
- **No user authentication**: API and Streamlit are open access
- **In-memory session storage**: API sessions stored in memory (lost on restart, no database persistence)
- **French language only**: All prompts and responses are in French
- **No conversation context across RAG/CHAT modes**: Mode switching doesn't preserve full conversation semantics
