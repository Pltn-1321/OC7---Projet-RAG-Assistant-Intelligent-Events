# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a RAG (Retrieval-Augmented Generation) chatbot for discovering cultural events using natural language queries. The system retrieves events from the Open Agenda API, indexes them with FAISS vector embeddings, and uses Mistral AI to generate conversational responses.

**Stack**: Python 3.11+, Streamlit (UI), LangChain (RAG), Mistral AI (LLM), FAISS (vector store), Open Agenda API (data)

**Package Manager**: This project uses `uv` (not pip). All dependency management and script execution should be done through `uv`.

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
# 1. Fetch events from Open Agenda API
uv run python scripts/fetch_events.py --location paris --max-events 1000

# 2. Build FAISS vector index
uv run python scripts/build_index.py --input data/processed/events.json

# 3. Run Streamlit application
uv run streamlit run app.py

# 4. Run FastAPI server (if implemented)
uv run uvicorn src.api.main:app --reload
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

## Architecture

### RAG Pipeline Flow
```
User Query → Streamlit UI → RAG Chatbot → FAISS Retriever (top-k events)
                                        ↓
                                   LangChain Chain
                                        ↓
                                   Mistral LLM (with context)
                                        ↓
                                   Response + Sources
```

### Module Organization

**src-layout pattern**: All source code lives in `src/` to avoid import issues.

- **src/config/**: Configuration management
  - `settings.py`: Pydantic Settings for environment variables (validates all config on load)
  - `constants.py`: Application constants (paths, prompts, thresholds, model names)

- **src/data/**: Data models and access
  - `models.py`: Pydantic models for Event, Location, DateRange, QueryResponse, etc.
  - `fetcher.py`: Client for Open Agenda API (to be implemented)
  - `preprocessor.py`: Data cleaning and HTML stripping (to be implemented)

- **src/rag/**: Core RAG logic
  - `chatbot.py`: Main chatbot orchestrator (EventChatbot class)
  - `retriever.py`: FAISS vector search wrapper (to be implemented)
  - `generator.py`: LLM generation logic (to be implemented)
  - `embeddings.py`: Embedding model management (to be implemented)
  - `prompts.py`: Prompt templates (to be implemented)
  - `index_manager.py`: FAISS index operations (to be implemented)

- **src/api/**: FastAPI REST endpoints (optional)
- **src/ui/**: Streamlit UI components (to be implemented)
- **src/utils/**: Shared utilities (logging, caching, etc.)

- **scripts/**: Standalone executable scripts
  - `fetch_events.py`: Fetch events from Open Agenda
  - `build_index.py`: Build FAISS index from events
  - `evaluate_rag.py`: Evaluate RAG system performance

- **tests/**: Test suite organized by type (unit, integration, e2e)

### Key Architectural Patterns

1. **Settings Management**: Uses Pydantic Settings with automatic `.env` loading and validation. Access via `from src.config.settings import settings`.

2. **Data Models**: All data uses Pydantic models for validation. The `Event` model includes helper methods:
   - `.to_search_text()`: Formats event for FAISS embedding
   - `.to_display_dict()`: Formats event for UI display
   - `.is_free`, `.is_upcoming`, `.is_past`, `.is_ongoing`: Computed properties

3. **Vector Store**: FAISS with HuggingFace embeddings (sentence-transformers). Default model: `all-MiniLM-L6-v2` (384 dimensions, fast).

4. **LLM Integration**: LangChain + Mistral AI using `ChatMistralAI`. Default model: `mistral-small-latest` with temperature 0.3.

5. **Testing Strategy**:
   - Uses pytest with custom markers (slow, integration, e2e, requires_api)
   - Shared fixtures in `tests/conftest.py` for sample events and mock data
   - Target metrics: latency < 3s, relevance > 80%, coverage > 70%

## Critical Implementation Details

### LangChain Imports (IMPORTANT)
**Always use the modern imports from `langchain_community`, not the deprecated `langchain` imports:**

```python
# ✅ CORRECT
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI

# ❌ WRONG (deprecated)
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
```

### FAISS Deserialization
When loading FAISS indexes, you must set `allow_dangerous_deserialization=True`:

```python
vectorstore = FAISS.load_local(
    "data/indexes/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True  # Required
)
```

### API Keys
- MISTRAL_API_KEY: Required for LLM
- OPENAGENDA_API_KEY: May be required for API access
- Both should be in `.env` file (never commit to git)
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

The project is designed to be containerized:
- Dockerfile should use Python 3.11 slim base
- MISTRAL_API_KEY must be passed as environment variable
- Mount `data/` volume for persistence
- Expose ports 8501 (Streamlit) and 8000 (FastAPI)

## Performance Considerations

1. **Streamlit caching**: Use `@st.cache_resource` for chatbot initialization
2. **FAISS index size**: ~2GB RAM for 1000 events with 384-dim embeddings
3. **Batch processing**: Use `DEFAULT_BATCH_SIZE = 32` for embedding generation
4. **API rate limits**: Respect Open Agenda and Mistral API rate limits
5. **Embedding model**: `all-MiniLM-L6-v2` is chosen for speed over accuracy (POC priority)

## Known Limitations (POC Phase)

- No conversation history/memory
- Manual index updates (no auto-refresh)
- Single location support (Paris-focused)
- No user authentication
- In-memory only (no database persistence)
- French language only
