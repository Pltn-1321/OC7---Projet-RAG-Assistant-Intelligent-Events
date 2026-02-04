"""Application constants."""

from pathlib import Path

# =============================================================================
# PROJECT PATHS
# =============================================================================
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
INDEXES_DIR = DATA_DIR / "indexes"
LOGS_DIR = PROJECT_ROOT / "logs"
TESTS_DATA_DIR = PROJECT_ROOT / "tests" / "data"

# =============================================================================
# API ENDPOINTS
# =============================================================================
OPENAGENDA_BASE_URL = "https://api.openagenda.com/v2"
OPENAGENDA_EVENTS_ENDPOINT = "/agendas/{agenda_uid}/events"

# =============================================================================
# MODEL NAMES AND VERSIONS
# =============================================================================
# Mistral models
MISTRAL_EMBEDDING_MODEL = "mistral-embed"  # 1024 dimensions

MISTRAL_LLM_MODELS = {
    "small": "mistral-small-latest",
    "medium": "mistral-medium-latest",
    "large": "mistral-large-latest",
}

# =============================================================================
# DEFAULT CONFIGURATIONS
# =============================================================================
DEFAULT_CHUNK_SIZE = 500  # For text chunking
DEFAULT_CHUNK_OVERLAP = 50  # Overlap between chunks
DEFAULT_BATCH_SIZE = 32  # For embedding generation
DEFAULT_REQUEST_TIMEOUT = 30  # API request timeout in seconds
DEFAULT_MAX_RETRIES = 3  # Maximum retries for failed requests

# =============================================================================
# PROMPT TEMPLATES
# =============================================================================
# Legacy template (kept for backward compatibility)
SYSTEM_PROMPT_TEMPLATE = """Tu es un assistant intelligent qui aide les utilisateurs à découvrir des événements culturels.

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

# =============================================================================
# LANGCHAIN PROMPT TEMPLATES
# =============================================================================
# Classification prompt (for query routing: SEARCH vs CHAT)
CLASSIFICATION_PROMPT_TEMPLATE = """Analyse cette requête et réponds uniquement par "SEARCH" ou "CHAT".

SEARCH = L'utilisateur cherche des événements, concerts, expos, spectacles, activités, sorties
CHAT = Salutations, remerciements, questions générales, bavardage

Exemples:
- "Bonjour" -> CHAT
- "Merci beaucoup !" -> CHAT
- "Comment ça marche ?" -> CHAT
- "Tu peux m'aider ?" -> CHAT
- "Concerts à Paris" -> SEARCH
- "Que faire ce weekend ?" -> SEARCH
- "Des expos intéressantes ?" -> SEARCH
- "Y a quoi comme festivals ?" -> SEARCH

Requête: "{query}"
Réponse:"""

# Conversation system prompt (non-RAG mode)
CONVERSATION_SYSTEM_PROMPT = """Tu es un assistant sympa spécialisé dans les événements culturels.

Personnalité :
- Tutoie l'utilisateur, sois chaleureux
- Réponds de façon concise
- Si on te demande ce que tu peux faire, explique que tu aides à trouver des événements (concerts, expos, spectacles, etc.)
- Encourage l'utilisateur à poser des questions sur les événements"""

# RAG system prompt (with context injection)
RAG_SYSTEM_PROMPT_TEMPLATE = """Tu es un assistant sympa qui aide à trouver des événements culturels.

Personnalité :
- Tutoie l'utilisateur, sois chaleureux et enthousiaste
- Réponds de façon concise (2-3 phrases max par événement)
- Si l'utilisateur pose une question de suivi, réfère-toi à la conversation précédente
- Si aucun événement ne correspond, propose des alternatives ou demande plus de précisions

{context}"""

# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================
MIN_QUERY_LENGTH = 3  # Minimum query length in characters
MAX_QUERY_LENGTH = 500  # Maximum query length in characters
MIN_EVENTS_TO_INDEX = 10  # Minimum events required for indexing
MAX_EVENTS_PER_REQUEST = 100  # Maximum events per API request

# =============================================================================
# CATEGORIES
# =============================================================================
EVENT_CATEGORIES = [
    "Concert",
    "Exposition",
    "Théâtre",
    "Cinéma",
    "Spectacle",
    "Festival",
    "Conférence",
    "Atelier",
    "Sport",
    "Autre",
]

# =============================================================================
# FILE NAMES
# =============================================================================
RAW_EVENTS_FILE = "events_raw.json"
PROCESSED_EVENTS_FILE = "events_processed.json"
FAISS_INDEX_FILE = "index.faiss"
FAISS_METADATA_FILE = "index.pkl"
TEST_QUESTIONS_FILE = "test_questions.json"
EVALUATION_RESULTS_FILE = "evaluation_results.json"

# =============================================================================
# METRICS THRESHOLDS
# =============================================================================
TARGET_LATENCY_SECONDS = 3.0  # Target response time
TARGET_RELEVANCE_SCORE = 0.8  # Target relevance score (80%)
TARGET_COVERAGE = 0.7  # Target question coverage (70%)

# =============================================================================
# LOGGING
# =============================================================================
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# =============================================================================
# CACHE
# =============================================================================
CACHE_TTL_SECONDS = 3600  # Cache time-to-live (1 hour)
MAX_CACHE_SIZE = 1000  # Maximum cache entries
