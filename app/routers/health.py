"""Health check endpoints."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config import settings
from app.dependencies import InternaciaClientDep
from app.models.responses import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "",
    response_model=HealthResponse,
    responses={503: {"model": HealthResponse, "description": "Database is not readable"}},
)
def health_check(client: InternaciaClientDep):
    """
    Health check endpoint.

    Runs a query against the database. Returns 200 when it succeeds and 503 otherwise,
    so it can be used as a readiness probe.
    """
    try:
        client.countries.count()
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("Health check failed")
        body = HealthResponse(status="unhealthy", sdk_connected=False, version=settings.api_version)
        return JSONResponse(status_code=503, content=body.model_dump())

    return HealthResponse(status="healthy", sdk_connected=True, version=settings.api_version)
