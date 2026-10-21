"""FastAPI dependencies for dependency injection."""

import logging
from pathlib import Path
from typing import Annotated

from fastapi import Depends, Request
from internacia import InternaciaClient

from app.config import settings

logger = logging.getLogger(__name__)


def create_client() -> InternaciaClient:
    """
    Open the internacia-db database and check that it can be queried.

    Called once at application startup. Any failure is logged and re-raised so the
    server refuses to start instead of serving errors.
    """
    db_path = Path(settings.internacia_db_path) if settings.internacia_db_path else None
    try:
        client = InternaciaClient(db_path=db_path)
        client.countries.count()
    except Exception:
        logger.critical(
            "Cannot open internacia-db (INTERNACIA_DB_PATH=%s); refusing to start",
            settings.internacia_db_path or "<unset, using SDK cache>",
            exc_info=True,
        )
        raise
    return client


def get_internacia_client(request: Request) -> InternaciaClient:
    """Return the client created at startup."""
    return request.app.state.client


InternaciaClientDep = Annotated[InternaciaClient, Depends(get_internacia_client)]
