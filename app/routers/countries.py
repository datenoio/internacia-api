"""Country endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request, Response

from app.api import FieldsParam, Paging, mark_deprecated, not_found_or_moved, page, single
from app.dependencies import InternaciaClientDep
from app.models.responses import Count, Membership, Page, Record, Single

router = APIRouter(prefix="/countries", tags=["countries"])


def _country(client: InternaciaClientDep, code: str, request: Request) -> Record:
    country = client.countries.get_by_code(code)
    if country is None:
        raise not_found_or_moved(client.countries.resolve_code(code), request, "Country", code)
    return dict(country)


def _list(rows: list[Any], request: Request, paging: Paging, fields: str | None) -> dict:
    return page([dict(r) for r in rows], request, paging, fields)


@router.get("", response_model=Page[Record])
def list_countries(
    client: InternaciaClientDep, request: Request, paging: Paging, fields: FieldsParam = None
):
    """All countries and territories, ordered as stored."""
    return _list(client.countries.get_all(), request, paging, fields)


@router.get("/count", response_model=Count)
def count_countries(client: InternaciaClientDep):
    """Number of countries and territories."""
    return {"count": client.countries.count()}


@router.get("/code/{code}", response_model=Single[Record])
def get_country_by_code(
    code: str, client: InternaciaClientDep, request: Request, fields: FieldsParam = None
):
    """
    A country by ISO 3166-1 alpha-2 code (e.g. `US`). Renamed codes redirect with 301
    (e.g. `KV` → `XK`).
    """
    return single(_country(client, code, request), fields)


@router.get("/iso3/{iso3code}", response_model=Single[Record])
def get_country_by_iso3(iso3code: str, client: InternaciaClientDep, fields: FieldsParam = None):
    """A country by ISO 3166-1 alpha-3 code (e.g. `USA`)."""
    country = client.countries.get_by_iso3(iso3code)
    if country is None:
        raise HTTPException(404, detail=f"Country with ISO3 code '{iso3code}' not found")
    return single(dict(country), fields)


@router.get("/numeric/{numeric_code}", response_model=Single[Record])
def get_country_by_numeric_code(
    numeric_code: str, client: InternaciaClientDep, fields: FieldsParam = None
):
    """A country by ISO 3166-1 numeric code (e.g. `840`)."""
    country = client.countries.get_by_numeric_code(numeric_code)
    if country is None:
        raise HTTPException(404, detail=f"Country with numeric code '{numeric_code}' not found")
    return single(dict(country), fields)


@router.get("/region/{region_id}", response_model=Page[Record])
def list_countries_by_region(
    region_id: str,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    fields: FieldsParam = None,
):
    """Countries in a World Bank region (e.g. `ECS`)."""
    return _list(client.countries.get_by_region(region_id), request, paging, fields)


@router.get("/income-level/{income_level_id}", response_model=Page[Record])
def list_countries_by_income_level(
    income_level_id: str,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    fields: FieldsParam = None,
):
    """
    Countries in a World Bank income level (e.g. `LMC`, `UMC`, `LIC`; high income is split
    into `NOC` and `OEC`).
    """
    return _list(client.countries.get_by_income_level(income_level_id), request, paging, fields)


@router.get("/un-members", response_model=Page[Record])
def list_un_members(
    client: InternaciaClientDep, request: Request, paging: Paging, fields: FieldsParam = None
):
    """UN member states."""
    return _list(client.countries.get_un_members(), request, paging, fields)


@router.get("/independent", response_model=Page[Record])
def list_independent_countries(
    client: InternaciaClientDep, request: Request, paging: Paging, fields: FieldsParam = None
):
    """Independent countries."""
    return _list(client.countries.get_independent(), request, paging, fields)


@router.get("/continent/{continent}", response_model=Page[Record])
def list_countries_by_continent(
    continent: str,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    fields: FieldsParam = None,
):
    """Countries on a continent (e.g. `Europe`)."""
    return _list(client.countries.get_by_continent(continent), request, paging, fields)


@router.get("/currency/{currency_code}", response_model=Page[Record])
def list_countries_by_currency(
    currency_code: str,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    fields: FieldsParam = None,
):
    """Countries that use a currency (ISO 4217, e.g. `EUR`)."""
    return _list(client.countries.get_by_currency(currency_code), request, paging, fields)


@router.get("/language/{language_code}", response_model=Page[Record])
def list_countries_by_language(
    language_code: str,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    fields: FieldsParam = None,
):
    """Countries that list a language (ISO 639-3, e.g. `fra`)."""
    return _list(client.countries.get_by_language(language_code), request, paging, fields)


@router.get("/{code}/memberships", response_model=Page[Membership])
def list_country_memberships(
    code: str,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    current: bool = Query(True, description="Only current memberships (see the data contract)"),
):
    """
    Membership edges of a country, ordered by block id. With `current=true` (default) former
    members, edges with a `left` date and dissolved blocks are excluded.
    """
    country = _country(client, code, request)
    rows = client.memberships.get_by_country(country["code"], current_only=current)
    return page([dict(r) for r in rows], request, paging)


@router.get("/alpha2/{alpha2_code}", response_model=Single[Record], deprecated=True)
def get_country_by_alpha2_legacy(
    alpha2_code: str,
    client: InternaciaClientDep,
    request: Request,
    response: Response,
    fields: FieldsParam = None,
):
    """Deprecated: use `/countries/code/{code}`."""
    mark_deprecated(response, f"/countries/code/{alpha2_code}")
    return single(_country(client, alpha2_code, request), fields)


@router.get("/alpha3/{alpha3_code}", response_model=Single[Record], deprecated=True)
def get_country_by_alpha3_legacy(
    alpha3_code: str, client: InternaciaClientDep, response: Response, fields: FieldsParam = None
):
    """Deprecated: use `/countries/iso3/{iso3code}`."""
    mark_deprecated(response, f"/countries/iso3/{alpha3_code}")
    return get_country_by_iso3(alpha3_code, client, fields)


@router.get("/{country_code}", response_model=Single[Record], deprecated=True)
def get_country_legacy(
    country_code: str,
    client: InternaciaClientDep,
    request: Request,
    response: Response,
    fields: FieldsParam = None,
):
    """Deprecated: use `/countries/code/{code}`."""
    mark_deprecated(response, f"/countries/code/{country_code}")
    return single(_country(client, country_code, request), fields)
