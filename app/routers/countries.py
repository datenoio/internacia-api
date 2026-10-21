"""Country-related endpoints."""

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import InternaciaClientDep, StubClient
from app.models.responses import CountryResponse, ListResponse
from app.utils import convert_numpy_to_python, handle_sdk_error

router = APIRouter(prefix="/countries", tags=["countries"])


def _check_client(client):
    """Check if client is available."""
    if isinstance(client, StubClient):
        raise HTTPException(
            status_code=501,
            detail="SDK not available"
        )


@router.get("/code/{code}", response_model=CountryResponse)
async def get_country_by_code(
    code: str,
    client: InternaciaClientDep
):
    """
    Get a country by its ISO 3166-1 alpha-2 code.

    Args:
        code: Two-letter country code (e.g., "US", "FR", "GB")

    Returns:
        Country data from internacia-db
    """
    try:
        _check_client(client)
        country = client.countries.get_by_code(code)

        if country is None:
            raise HTTPException(
                status_code=404,
                detail=f"Country with code '{code}' not found"
            )

        # Convert numpy arrays to Python lists for JSON serialization
        country = convert_numpy_to_python(country)
        return CountryResponse(data=country)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving country by code") from e


@router.get("/iso3/{iso3code}", response_model=CountryResponse)
async def get_country_by_iso3(
    iso3code: str,
    client: InternaciaClientDep
):
    """
    Get a country by its ISO 3166-1 alpha-3 code.

    Args:
        iso3code: Three-letter country code (e.g., "USA", "FRA", "GBR")

    Returns:
        Country data from internacia-db
    """
    try:
        _check_client(client)
        country = client.countries.get_by_iso3(iso3code)

        if country is None:
            raise HTTPException(
                status_code=404,
                detail=f"Country with ISO3 code '{iso3code}' not found"
            )

        # Convert numpy arrays to Python lists for JSON serialization
        country = convert_numpy_to_python(country)
        return CountryResponse(data=country)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving country by ISO3 code") from e


@router.get("/numeric/{numeric_code}", response_model=CountryResponse)
async def get_country_by_numeric_code(
    numeric_code: str,
    client: InternaciaClientDep
):
    """
    Get a country by its ISO 3166-1 numeric code.

    Args:
        numeric_code: Three-digit numeric code (e.g., "840", "250", "826")

    Returns:
        Country data from internacia-db
    """
    try:
        _check_client(client)
        country = client.countries.get_by_numeric_code(numeric_code)

        if country is None:
            raise HTTPException(
                status_code=404,
                detail=f"Country with numeric code '{numeric_code}' not found"
            )

        # Convert numpy arrays to Python lists for JSON serialization
        country = convert_numpy_to_python(country)
        return CountryResponse(data=country)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving country by numeric code") from e


@router.get("", response_model=ListResponse)
async def get_all_countries(
    client: InternaciaClientDep,
    limit: int | None = Query(None, description="Maximum number of results", ge=1)
):
    """
    Get all countries.

    Args:
        limit: Optional maximum number of results to return

    Returns:
        List of all countries from internacia-db
    """
    try:
        _check_client(client)
        countries = client.countries.get_all(limit=limit)

        # Convert numpy arrays to Python lists for JSON serialization
        if countries:
            countries = [convert_numpy_to_python(country) for country in countries]
        return ListResponse(items=countries or [], count=len(countries) if countries else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "listing countries") from e


@router.get("/region/{region_id}", response_model=ListResponse)
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

        # Convert numpy arrays to Python lists for JSON serialization
        if countries:
            countries = [convert_numpy_to_python(country) for country in countries]
        return ListResponse(items=countries or [], count=len(countries) if countries else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving countries by region") from e


@router.get("/income-level/{income_level_id}", response_model=ListResponse)
async def get_countries_by_income_level(
    income_level_id: str,
    client: InternaciaClientDep
):
    """
    Get countries by World Bank income level.

    Args:
        income_level_id: Income level ID (e.g., "OEC", "HIC", "LIC")

    Returns:
        List of countries with the specified income level
    """
    try:
        _check_client(client)
        countries = client.countries.get_by_income_level(income_level_id)

        # Convert numpy arrays to Python lists for JSON serialization
        if countries:
            countries = [convert_numpy_to_python(country) for country in countries]
        return ListResponse(items=countries or [], count=len(countries) if countries else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving countries by income level") from e


@router.get("/un-members", response_model=ListResponse)
async def get_un_members(client: InternaciaClientDep):
    """
    Get all UN member countries.

    Returns:
        List of UN member countries
    """
    try:
        _check_client(client)
        countries = client.countries.get_un_members()

        # Convert numpy arrays to Python lists for JSON serialization
        if countries:
            countries = [convert_numpy_to_python(country) for country in countries]
        return ListResponse(items=countries or [], count=len(countries) if countries else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving UN members") from e


@router.get("/independent", response_model=ListResponse)
async def get_independent_countries(client: InternaciaClientDep):
    """
    Get all independent countries.

    Returns:
        List of independent countries
    """
    try:
        _check_client(client)
        countries = client.countries.get_independent()

        # Convert numpy arrays to Python lists for JSON serialization
        if countries:
            countries = [convert_numpy_to_python(country) for country in countries]
        return ListResponse(items=countries or [], count=len(countries) if countries else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving independent countries") from e


@router.get("/continent/{continent}", response_model=ListResponse)
async def get_countries_by_continent(
    continent: str,
    client: InternaciaClientDep
):
    """
    Get countries by continent.

    Args:
        continent: Continent name (e.g., "North America", "Europe", "Asia")

    Returns:
        List of countries on the specified continent
    """
    try:
        _check_client(client)
        countries = client.countries.get_by_continent(continent)

        # Convert numpy arrays to Python lists for JSON serialization
        if countries:
            countries = [convert_numpy_to_python(country) for country in countries]
        return ListResponse(items=countries or [], count=len(countries) if countries else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving countries by continent") from e


@router.get("/currency/{currency_code}", response_model=ListResponse)
async def get_countries_by_currency(
    currency_code: str,
    client: InternaciaClientDep
):
    """
    Get countries that use a specific currency.

    Args:
        currency_code: Currency code (e.g., "USD", "EUR", "GBP")

    Returns:
        List of countries using the specified currency
    """
    try:
        _check_client(client)
        countries = client.countries.get_by_currency(currency_code)

        # Convert numpy arrays to Python lists for JSON serialization
        if countries:
            countries = [convert_numpy_to_python(country) for country in countries]
        return ListResponse(items=countries or [], count=len(countries) if countries else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving countries by currency") from e


@router.get("/language/{language_code}", response_model=ListResponse)
async def get_countries_by_language(
    language_code: str,
    client: InternaciaClientDep
):
    """
    Get countries where a specific language is spoken.

    Args:
        language_code: Language code (e.g., "eng", "fra", "spa")

    Returns:
        List of countries where the language is spoken
    """
    try:
        _check_client(client)
        countries = client.countries.get_by_language(language_code)

        # Convert numpy arrays to Python lists for JSON serialization
        if countries:
            countries = [convert_numpy_to_python(country) for country in countries]
        return ListResponse(items=countries or [], count=len(countries) if countries else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving countries by language") from e


@router.get("/count", response_model=dict)
async def get_countries_count(client: InternaciaClientDep):
    """
    Get the total number of countries.

    Returns:
        Total count of countries
    """
    try:
        _check_client(client)
        count = client.countries.count()

        return {"count": count}
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "counting countries") from e


# Legacy endpoints for backward compatibility (must be after specific routes)
@router.get("/alpha2/{alpha2_code}", response_model=CountryResponse)
async def get_country_by_alpha2_legacy(
    alpha2_code: str,
    client: InternaciaClientDep
):
    """Legacy endpoint - redirects to /code/{code}"""
    return await get_country_by_code(alpha2_code, client)


@router.get("/alpha3/{alpha3_code}", response_model=CountryResponse)
async def get_country_by_alpha3_legacy(
    alpha3_code: str,
    client: InternaciaClientDep
):
    """Legacy endpoint - redirects to /iso3/{iso3code}"""
    return await get_country_by_iso3(alpha3_code, client)


@router.get("/{country_code}", response_model=CountryResponse)
async def get_country_legacy(
    country_code: str,
    client: InternaciaClientDep
):
    """Legacy endpoint - redirects to /code/{code}"""
    return await get_country_by_code(country_code, client)
