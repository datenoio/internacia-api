"""Health check endpoints."""

from fastapi import APIRouter
from app.dependencies import InternaciaClientDep, StubClient
from app.models.responses import HealthResponse
from app.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check(client: InternaciaClientDep):
    """
    Health check endpoint.

    Returns the health status of the API and SDK connection.
    """
    # Check if we have a stub client (SDK not available)
    if isinstance(client, StubClient):
        sdk_connected = False
    else:
        try:
            # Try to perform a simple operation to check health
            if hasattr(client, 'health_check'):
                sdk_connected = client.health_check()
            elif hasattr(client, 'ping'):
                sdk_connected = client.ping()
            else:
                # If no health check method, assume healthy if client exists
                sdk_connected = client is not None
        except Exception:  # pylint: disable=broad-exception-caught
            # Catch all exceptions for health check to gracefully degrade
            sdk_connected = False

    return HealthResponse(
        status="healthy" if sdk_connected else "degraded",
        sdk_connected=sdk_connected,
        version=settings.api_version
    )
