"""Application settings module using Pydantic Settings."""

from pathlib import Path
from typing import Optional

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
    mistral_api_key: str = Field(..., description="Mistral AI API key")
    openagenda_api_key: Optional[str] = Field(
        None, description="Open Agenda API key (if required)"
    )

    # =============================================================================
    # APPLICATION CONFIGURATION
    # =============================================================================
    log_level: str = Field("INFO", description="Logging level")
    index_path: Path = Field(
        Path("data/indexes/faiss_index"), description="Path to FAISS index directory"
    )
    max_events: int = Field(1000, description="Maximum number of events to fetch")
    default_location: str = Field("paris", description="Default location for event search")

    # =============================================================================
    # MODEL CONFIGURATION
    # =============================================================================
    embedding_model: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace embedding model name",
    )
    llm_model: str = Field("mistral-small-latest", description="Mistral LLM model name")
    llm_temperature: float = Field(0.3, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(500, ge=1, le=4096, description="Maximum tokens for LLM response")

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

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()


# Convenience function
def get_settings() -> Settings:
    """Get application settings instance."""
    return settings
