"""Language endpoints, from the internacia-db `country_languages` view."""

from fastapi import APIRouter, HTTPException, Request, Response

from app.api import FieldsParam, Paging, mark_deprecated, page
from app.dependencies import InternaciaClientDep
from app.models.responses import Language, LanguageEntry, Page, Record, Single

router = APIRouter(prefix="/languages", tags=["languages"])


@router.get("", response_model=Page[LanguageEntry])
def list_languages(client: InternaciaClientDep, request: Request, paging: Paging):
    """Languages (ISO 639-3) listed for countries, with the number of countries each."""
    return page([dict(lang) for lang in client.countries.get_languages()], request, paging)


@router.get("/country/{country_code}", response_model=Page[Language])
def list_country_languages(
    country_code: str, client: InternaciaClientDep, request: Request, paging: Paging
):
    """Languages of one country (empty for countries without languages)."""
    if client.countries.get_by_code(country_code) is None:
        raise HTTPException(404, detail=f"Country with code '{country_code}' not found")
    rows = client.countries.get_country_languages(country_code)
    return page([dict(lang) for lang in rows], request, paging)


@router.get("/{language_code}/countries", response_model=Page[Record], deprecated=True)
def list_countries_by_language_legacy(
    language_code: str,
    client: InternaciaClientDep,
    request: Request,
    response: Response,
    paging: Paging,
    fields: FieldsParam = None,
):
    """Deprecated: use `/countries/language/{language_code}`."""
    mark_deprecated(response, f"/countries/language/{language_code}")
    rows = client.countries.get_by_language(language_code)
    return page([dict(r) for r in rows], request, paging, fields)


@router.get("/{language_code}", response_model=Single[LanguageEntry])
def get_language(language_code: str, client: InternaciaClientDep):
    """One language by ISO 639-3 code (e.g. `fra`)."""
    language = client.countries.get_language(language_code)
    if language is None:
        raise HTTPException(404, detail=f"Language with code '{language_code}' not found")
    return {"data": dict(language)}
