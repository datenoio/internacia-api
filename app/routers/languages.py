"""Language-related endpoints."""

from fastapi import APIRouter, HTTPException
from app.dependencies import InternaciaClientDep, StubClient
from app.utils import handle_sdk_error
from app.models.responses import ListResponse

router = APIRouter(prefix="/languages", tags=["languages"])


def _check_client(client):
    """Check if client is available."""
    if isinstance(client, StubClient):
        raise HTTPException(
            status_code=501,
            detail="SDK not available"
        )


@router.get("/{language_code}/countries", response_model=ListResponse)
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

        return ListResponse(items=countries or [], count=len(countries) if countries else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving countries by language") from e


@router.get("", response_model=ListResponse)
async def list_languages(client: InternaciaClientDep):
    """
    List all unique languages from all countries.

    Returns:
        List of all unique languages
    """
    try:
        _check_client(client)
        all_countries = client.countries.get_all()

        # Extract unique languages
        languages_map = {}
        for country in all_countries or []:
            for language in country.get("languages", []):
                code = language.get("code")
                if code and code not in languages_map:
                    languages_map[code] = language

        languages = list(languages_map.values())

        return ListResponse(items=languages, count=len(languages))
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "listing languages") from e


@router.get("/country/{country_code}", response_model=ListResponse)
async def get_languages_by_country(
    country_code: str,
    client: InternaciaClientDep
):
    """
    Get languages spoken in a specific country.

    Args:
        country_code: Country code (e.g., "US", "GB", "FR")

    Returns:
        List of languages for the country
    """
    try:
        _check_client(client)
        country = client.countries.get_by_code(country_code)

        if country is None:
            raise HTTPException(
                status_code=404,
                detail=f"Country with code '{country_code}' not found"
            )

        languages = country.get("languages", [])

        return ListResponse(items=languages, count=len(languages))
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving languages by country") from e


@router.get("/{language_code}", response_model=dict)
async def get_language(
    language_code: str,
    client: InternaciaClientDep
):
    """
    Get language information by code.

    Args:
        language_code: Language code (e.g., "eng", "fra", "spa")

    Returns:
        Language data from internacia-db
    """
    try:
        _check_client(client)
        all_countries = client.countries.get_all()

        # Find language in any country
        for country in all_countries or []:
            for language in country.get("languages", []):
                if language.get("code") == language_code:
                    return {"data": language}

        raise HTTPException(
            status_code=404,
            detail=f"Language with code '{language_code}' not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving language") from e
