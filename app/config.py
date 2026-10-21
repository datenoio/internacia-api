"""Application configuration settings."""

from typing import Optional

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
    api_version: str = "1.0.0"
    api_description: str = "REST API for internacia-db using internacia-python SDK"

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # SDK Configuration
    # Add any SDK-specific configuration here
    # For example, database connection strings, API keys, etc.
    internacia_db_url: Optional[str] = None
    internacia_db_path: Optional[str] = None


# Global settings instance
settings = Settings()
