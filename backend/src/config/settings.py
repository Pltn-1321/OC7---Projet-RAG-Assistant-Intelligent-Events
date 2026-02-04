"""Application settings module using Pydantic Settings."""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        # Monorepo: try root .env first, then local .env
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =============================================================================
    # API KEYS (REQUIRED)
    # =============================================================================
    mistral_api_key: str | None = Field(None, description="Mistral AI API key")
    rebuild_api_key: str | None = Field(
        None, description="API key for /rebuild endpoint authentication"
    )

    # =============================================================================
    # APPLICATION CONFIGURATION
    # =============================================================================
    log_level: str = Field("INFO", description="Logging level")
    index_path: Path = Field(
        Path("data/indexes/faiss_index"), description="Path to FAISS index directory"
    )
    max_events: int = Field(10000, description="Maximum number of events to fetch")
    default_location: str | None = Field(
        "marseille", description="Default location for event search"
    )

    # =============================================================================
    # EMBEDDING CONFIGURATION
    # =============================================================================
    mistral_embedding_model: str = Field(
        "mistral-embed", description="Mistral embedding model name (dimension: 1024)"
    )

    # =============================================================================
    # LLM CONFIGURATION
    # =============================================================================
    llm_model: str = Field("mistral-small-latest", description="Mistral LLM model name")
    llm_temperature: float = Field(0.7, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(1000, ge=1, le=4096, description="Maximum tokens for LLM response")

    # =============================================================================
    # RETRIEVAL SETTINGS
    # =============================================================================
    top_k_results: int = Field(5, ge=1, le=20, description="Number of documents to retrieve")
    min_similarity_score: float = Field(
        0.3, ge=0.0, le=1.0, description="Minimum similarity score threshold"
    )

    # =============================================================================
    # API CONFIGURATION (if using FastAPI)
    # =============================================================================
    api_host: str = Field("0.0.0.0", description="API host address")
    api_port: int = Field(8000, ge=1, le=65535, description="API port")
    enable_cors: bool = Field(True, description="Enable CORS")
    cors_origins: str = Field(
        "http://localhost:3000,http://localhost:5173,http://localhost:8501",
        description="Allowed CORS origins",
    )

    # =============================================================================
    # STREAMLIT CONFIGURATION
    # =============================================================================
    streamlit_port: int = Field(8501, ge=1, le=65535, description="Streamlit port")
    streamlit_server_address: str = Field("0.0.0.0", description="Streamlit server address")

    # =============================================================================
    # DATABASE CONFIGURATION (POSTGRESQL)
    # =============================================================================
    postgres_host: str = Field("localhost", description="PostgreSQL host address")
    postgres_port: int = Field(5432, ge=1, le=65535, description="PostgreSQL port")
    postgres_user: str = Field("postgres", description="PostgreSQL username")
    postgres_password: str = Field("", description="PostgreSQL password")
    postgres_db: str = Field("rag_events", description="PostgreSQL database name")
    postgres_pool_size: int = Field(10, ge=1, le=100, description="Connection pool size")
    postgres_max_overflow: int = Field(20, ge=0, le=100, description="Max overflow connections")

    # =============================================================================
    # DEVELOPMENT SETTINGS
    # =============================================================================
    debug: bool = Field(False, description="Enable debug mode")
    enable_profiling: bool = Field(False, description="Enable profiling")
    cache_embeddings: bool = Field(True, description="Cache embeddings")

    @field_validator("postgres_password")
    @classmethod
    def validate_postgres_config(cls, v: str, info) -> str:
        """
        Validate PostgreSQL configuration (optional for development).

        For production, ensure all PostgreSQL variables are set in environment.
        For development without database, password can be empty.
        """
        # Warn if password is empty but allow it for development
        if not v and info.data.get("debug") is False:
            import warnings

            warnings.warn(
                "POSTGRES_PASSWORD is empty. This is only acceptable for local development.",
                UserWarning,
            )
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
        return v_upper

    @field_validator("index_path")
    @classmethod
    def validate_index_path(cls, v: Path) -> Path:
        """Ensure index path is a Path object."""
        if isinstance(v, str):
            return Path(v)
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def embedding_model(self) -> str:
        """Get the Mistral embedding model name."""
        return self.mistral_embedding_model

    @property
    def embedding_dimension(self) -> int:
        """Get Mistral embedding dimension (1024)."""
        return 1024

    @property
    def database_url(self) -> str:
        """Get PostgreSQL database URL with asyncpg driver."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


# Global settings instance
settings = Settings()


# Convenience function
def get_settings() -> Settings:
    """Get application settings instance."""
    return settings
