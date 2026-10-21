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

    # Path to internacia.duckdb; when unset the SDK falls back to its download cache
    internacia_db_path: str | None = None


# Global settings instance
settings = Settings()
