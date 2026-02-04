# =============================================================================
# RAG Events Assistant - Dockerfile
# =============================================================================
# Image Docker pour l'application RAG Events Assistant
# Supporte deux modes: API (FastAPI) et UI (Streamlit)
#
# Build:
#   docker build -t rag-events .
#
# Run API:
#   docker run -p 8000:8000 -e MISTRAL_API_KEY=xxx rag-events
#
# Run Streamlit:
#   docker run -p 8501:8501 -e MISTRAL_API_KEY=xxx rag-events streamlit
# =============================================================================

FROM python:3.11-slim AS base

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Installer les dependances systeme
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Installer uv
RUN pip install uv

# =============================================================================
# Stage de build des dependances
# =============================================================================
FROM base AS dependencies

# Copier les fichiers de dependances
COPY pyproject.toml uv.lock* ./

# Installer les dependances (sans dev)
RUN uv sync --frozen --no-dev --extra api

# =============================================================================
# Stage de production
# =============================================================================
FROM base AS production

# Copier l'environnement virtuel depuis le stage dependencies
COPY --from=dependencies /app/.venv /app/.venv

# Ajouter l'environnement virtuel au PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copier le code source
COPY src/ src/
COPY app.py .
COPY scripts/ scripts/

# Creer les repertoires de donnees
RUN mkdir -p data/processed data/indexes data/raw

# Exposer les ports
EXPOSE 8000 8501

# Variables d'environnement par defaut
ENV API_HOST=0.0.0.0 \
    API_PORT=8000 \
    STREAMLIT_PORT=8501

# Script d'entrypoint
COPY <<'EOF' /app/entrypoint.sh
#!/bin/bash
set -e

if [ "$1" = "streamlit" ]; then
    echo "Demarrage de Streamlit..."
    exec streamlit run app.py \
        --server.port=${STREAMLIT_PORT} \
        --server.address=0.0.0.0 \
        --server.headless=true
elif [ "$1" = "api" ] || [ -z "$1" ]; then
    echo "Demarrage de l'API FastAPI..."
    exec uvicorn src.api.main:app \
        --host ${API_HOST} \
        --port ${API_PORT}
else
    exec "$@"
fi
EOF

RUN chmod +x /app/entrypoint.sh

# Healthcheck pour l'API
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${API_PORT}/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["api"]
