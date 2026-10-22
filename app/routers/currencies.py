"""Currency endpoints, from the internacia-db `country_currencies` view."""

from fastapi import APIRouter, HTTPException, Request, Response

from app.api import FieldsParam, Paging, mark_deprecated, page
from app.dependencies import InternaciaClientDep
from app.models.responses import Currency, CurrencyEntry, Page, Record, Single

router = APIRouter(prefix="/currencies", tags=["currencies"])


@router.get("", response_model=Page[CurrencyEntry])
def list_currencies(client: InternaciaClientDep, request: Request, paging: Paging):
    """Currencies used by countries, with the number of countries using each."""
    return page([dict(c) for c in client.countries.get_currencies()], request, paging)


@router.get("/country/{country_code}", response_model=Page[Currency])
def list_country_currencies(
    country_code: str, client: InternaciaClientDep, request: Request, paging: Paging
):
    """Currencies of one country (empty for countries without currencies)."""
    if client.countries.get_by_code(country_code) is None:
        raise HTTPException(404, detail=f"Country with code '{country_code}' not found")
    rows = client.countries.get_country_currencies(country_code)
    return page([dict(c) for c in rows], request, paging)


@router.get("/{currency_code}/countries", response_model=Page[Record], deprecated=True)
def list_countries_by_currency_legacy(
    currency_code: str,
    client: InternaciaClientDep,
    request: Request,
    response: Response,
    paging: Paging,
    fields: FieldsParam = None,
):
    """Deprecated: use `/countries/currency/{currency_code}`."""
    mark_deprecated(response, f"/countries/currency/{currency_code}")
    rows = client.countries.get_by_currency(currency_code)
    return page([dict(r) for r in rows], request, paging, fields)


@router.get("/{currency_code}", response_model=Single[CurrencyEntry])
def get_currency(currency_code: str, client: InternaciaClientDep):
    """One currency by ISO 4217 code."""
    currency = client.countries.get_currency(currency_code)
    if currency is None:
        raise HTTPException(404, detail=f"Currency with code '{currency_code}' not found")
    return {"data": dict(currency)}
