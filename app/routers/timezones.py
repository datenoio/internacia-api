"""Time zone endpoints, from the internacia-db `country_timezones` view."""

from fastapi import APIRouter, HTTPException, Request

from app.api import Paging, page
from app.dependencies import InternaciaClientDep
from app.models.responses import Page, Single, Timezone, TimezoneEntry

router = APIRouter(prefix="/timezones", tags=["timezones"])


@router.get("", response_model=Page[TimezoneEntry])
def list_timezones(client: InternaciaClientDep, request: Request, paging: Paging):
    """IANA time zones used by countries, with the number of countries using each."""
    return page([dict(t) for t in client.countries.get_timezones()], request, paging)


@router.get("/country/{country_code}", response_model=Page[TimezoneEntry])
def list_country_timezones(
    country_code: str, client: InternaciaClientDep, request: Request, paging: Paging
):
    """Time zones of one country, each with the number of countries using it."""
    if client.countries.get_by_code(country_code) is None:
        raise HTTPException(404, detail=f"Country with code '{country_code}' not found")
    counts = {t["timezone"]: t["country_count"] for t in client.countries.get_timezones()}
    rows = [
        {"timezone": tz, "country_count": counts.get(tz, 1)}
        for tz in client.countries.get_country_timezones(country_code)
    ]
    return page(rows, request, paging)


@router.get("/{timezone_name:path}", response_model=Single[Timezone])
def get_timezone(timezone_name: str, client: InternaciaClientDep):
    """One IANA time zone (e.g. `Europe/Paris`) with the countries that use it."""
    countries = [c["code"] for c in client.countries.get_by_timezone(timezone_name)]
    if not countries:
        raise HTTPException(404, detail=f"Timezone '{timezone_name}' not found")
    return {
        "data": {"timezone": timezone_name, "country_count": len(countries), "countries": countries}
    }
