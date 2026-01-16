"""Application settings module using Pydantic Settings."""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =============================================================================
    # API KEYS (REQUIRED)
    # =============================================================================
    mistral_api_key: str | None = Field(None, description="Mistral AI API key")
    rebuild_api_key: str | None = Field(None, description="API key for /rebuild endpoint authentication")

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
    embedding_provider: str = Field(
        "mistral", description="Embedding provider: 'mistral' or 'sentence-transformers'"
    )

    mistral_embedding_model: str = Field(
        "mistral-embed", description="Mistral embedding model name (dimension: 1024)"
    )

    sentence_transformer_model: str = Field(
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        description="HuggingFace embedding model name (dimension: 768)",
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
        "http://localhost:3000,http://localhost:8501", description="Allowed CORS origins"
    )

    # =============================================================================
    # STREAMLIT CONFIGURATION
    # =============================================================================
    streamlit_port: int = Field(8501, ge=1, le=65535, description="Streamlit port")
    streamlit_server_address: str = Field("0.0.0.0", description="Streamlit server address")

    # =============================================================================
    # DEVELOPMENT SETTINGS
    # =============================================================================
    debug: bool = Field(False, description="Enable debug mode")
    enable_profiling: bool = Field(False, description="Enable profiling")
    cache_embeddings: bool = Field(True, description="Cache embeddings")

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

    @field_validator("embedding_provider")
    @classmethod
    def validate_embedding_provider(cls, v: str) -> str:
        """Validate embedding provider."""
        valid_providers = ["mistral", "sentence-transformers"]
        if v not in valid_providers:
            raise ValueError(f"Invalid provider. Must be one of {valid_providers}")
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def embedding_model(self) -> str:
        """Get the appropriate embedding model based on provider."""
        if self.embedding_provider == "mistral":
            return self.mistral_embedding_model
        return self.sentence_transformer_model

    @property
    def embedding_dimension(self) -> int:
        """Get embedding dimension based on provider."""
        if self.embedding_provider == "mistral":
            return 1024  # Mistral embed dimension
        return 768  # Sentence-transformers paraphrase-multilingual-mpnet


# Global settings instance
settings = Settings()


# Convenience function
def get_settings() -> Settings:
    """Get application settings instance."""
    return settings
