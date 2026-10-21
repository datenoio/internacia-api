"""Application configuration settings."""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # API Settings
    api_title: str = "Internacia API"
    api_version: str = "0.1.0"
    api_description: str = "REST API for internacia-db using the internacia Python SDK"

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Allowed CORS origins, e.g. CORS_ORIGINS='["https://example.org"]'
    cors_origins: list[str] = ["*"]

    # Path to internacia.duckdb; when unset the SDK falls back to its download cache
    internacia_db_path: str | None = None

    # Expected internacia-db version (e.g. "3.0.0"); startup fails if the database differs.
    # The Docker image sets it to the version it bakes in.
    internacia_db_version: str | None = None

    # Cache-Control max-age for successful responses, in seconds (0 disables caching headers)
    cache_max_age: int = 3600


# Global settings instance
settings = Settings()
