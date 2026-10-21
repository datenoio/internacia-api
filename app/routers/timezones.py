"""Timezone-related endpoints."""

from fastapi import APIRouter, HTTPException

from app.dependencies import InternaciaClientDep
from app.models.responses import ListResponse
from app.utils import handle_sdk_error

router = APIRouter(prefix="/timezones", tags=["timezones"])


@router.get("", response_model=ListResponse)
async def list_timezones(client: InternaciaClientDep):
    """
    List all timezones.

    Note: Timezone functionality is not currently available in the SDK.
    This endpoint returns an empty list.

    Returns:
        List of all timezones (currently empty)
    """
    try:
        # Timezones are not available in the SDK yet
        return ListResponse(items=[], count=0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "listing timezones") from e


@router.get("/country/{country_code}", response_model=ListResponse)
async def get_timezones_by_country(
    country_code: str,
    client: InternaciaClientDep
):
    """
    Get timezones used in a specific country.

    Note: Timezone functionality is not currently available in the SDK.
    This endpoint returns an empty list.

    Args:
        country_code: Country code (e.g., 'US', 'GB', 'FR')

    Returns:
        List of timezones for the country (currently empty)
    """
    try:
        # Timezones are not available in the SDK yet
        # country_code is part of the API contract but not currently used
        _ = country_code  # Suppress unused argument warning
        return ListResponse(items=[], count=0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving timezones by country") from e


@router.get("/{timezone_name:path}", response_model=dict)
async def get_timezone(
    timezone_name: str,
    client: InternaciaClientDep
):
    """
    Get timezone information by name.

    Note: Timezone functionality is not currently available in the SDK.
    This endpoint returns a 404 error.

    Args:
        timezone_name: Timezone name (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo')

    Returns:
        Timezone data (currently not available)
    """
    try:
        # Timezones are not available in the SDK yet
        raise HTTPException(
            status_code=404,
            detail=(
                f"Timezone '{timezone_name}' not found. "
                "Timezone functionality is not available in the SDK."
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving timezone") from e
