"""FastAPI dependencies for dependency injection."""

from functools import lru_cache
from typing import Annotated, Optional
from pathlib import Path
from fastapi import Depends

try:
    from internacia import InternaciaClient
    SDK_AVAILABLE = True
except ImportError:
    # Fallback if import fails - will be caught at runtime
    InternaciaClient = None
    SDK_AVAILABLE = False

from app.config import settings


class StubClient:
    """Stub client used when SDK is not available."""


@lru_cache()
def get_internacia_client():
    """
    Create and return a singleton InternaciaClient instance.

    Uses LRU cache to ensure only one instance is created.
    Returns a stub client if SDK is not available.

    The SDK accepts db_path as a Path object (not a string).
    """
    if not SDK_AVAILABLE or InternaciaClient is None:
        # Return a stub client instead of raising an error
        # This allows the API to run and return proper 501 errors
        return StubClient()

    # Initialize client with configuration from settings
    # SDK expects db_path as Path, not url or path strings
    try:
        if settings.internacia_db_path:
            db_path = Path(settings.internacia_db_path)
            return InternaciaClient(db_path=db_path)
        # Use default initialization (will look for database in default locations)
        return InternaciaClient()
    except Exception:  # pylint: disable=broad-exception-caught
        # If client creation fails, return stub
        # We catch all exceptions here to gracefully fall back to stub client
        return StubClient()


# Dependency annotation for use in route handlers
# Use Optional type to handle stub client case
InternaciaClientDep = Annotated[Optional[object], Depends(get_internacia_client)]
