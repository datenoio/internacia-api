"""Region-related endpoints."""

from fastapi import APIRouter, HTTPException

from app.dependencies import InternaciaClientDep, StubClient
from app.models.responses import ListResponse
from app.utils import handle_sdk_error

router = APIRouter(prefix="/regions", tags=["regions"])


def _check_client(client):
    """Check if client is available."""
    if isinstance(client, StubClient):
        raise HTTPException(
            status_code=501,
            detail="SDK not available"
        )


@router.get("/{region_id}/countries", response_model=ListResponse)
async def get_countries_by_region(
    region_id: str,
    client: InternaciaClientDep
):
    """
    Get countries by World Bank region ID.

    Args:
        region_id: Region ID (e.g., "NAC", "ECS", "SSF")

    Returns:
        List of countries in the specified region
    """
    try:
        _check_client(client)
        countries = client.countries.get_by_region(region_id)

        return ListResponse(items=countries or [], count=len(countries) if countries else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving countries by region") from e


@router.get("", response_model=ListResponse)
async def list_regions(client: InternaciaClientDep):
    """
    List all unique regions from all countries.

    Returns:
        List of all unique regions
    """
    try:
        _check_client(client)
        all_countries = client.countries.get_all()

        # Extract unique regions
        regions_map = {}
        for country in all_countries or []:
            region = country.get("region")
            if region:
                region_id = region.get("id")
                if region_id and region_id not in regions_map:
                    regions_map[region_id] = region

        regions = list(regions_map.values())

        return ListResponse(items=regions, count=len(regions))
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "listing regions") from e


@router.get("/country/{country_code}", response_model=dict)
async def get_region_by_country(
    country_code: str,
    client: InternaciaClientDep
):
    """
    Get region information for a specific country.

    Args:
        country_code: Country code (e.g., "US", "GB", "FR")

    Returns:
        Region data for the country
    """
    try:
        _check_client(client)
        country = client.countries.get_by_code(country_code)

        if country is None:
            raise HTTPException(
                status_code=404,
                detail=f"Country with code '{country_code}' not found"
            )

        region = country.get("region")
        if region:
            return {"data": region}

        raise HTTPException(
            status_code=404,
            detail=f"Region for country '{country_code}' not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving region by country") from e


@router.get("/{region_id}", response_model=dict)
async def get_region(
    region_id: str,
    client: InternaciaClientDep
):
    """
    Get region information by ID.

    Args:
        region_id: Region ID (e.g., "NAC", "ECS", "SSF")

    Returns:
        Region data from internacia-db
    """
    try:
        _check_client(client)
        countries = client.countries.get_by_region(region_id)

        if not countries:
            raise HTTPException(
                status_code=404,
                detail=f"Region '{region_id}' not found"
            )

        # Get region data from first country
        region = countries[0].get("region")
        if region:
            return {"data": region}

        raise HTTPException(
            status_code=404,
            detail=f"Region '{region_id}' not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving region") from e
