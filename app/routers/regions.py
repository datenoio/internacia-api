"""World Bank region endpoints."""

from fastapi import APIRouter, HTTPException, Request, Response

from app.api import FieldsParam, Paging, mark_deprecated, page
from app.dependencies import InternaciaClientDep
from app.models.responses import Page, Record, Region, RegionEntry, Single

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("", response_model=Page[RegionEntry])
def list_regions(client: InternaciaClientDep, request: Request, paging: Paging):
    """World Bank regions with the number of countries in each."""
    return page([dict(r) for r in client.countries.get_regions()], request, paging)


@router.get("/country/{country_code}", response_model=Single[Region])
def get_country_region(country_code: str, client: InternaciaClientDep):
    """The World Bank region of one country."""
    country = client.countries.get_by_code(country_code)
    if country is None:
        raise HTTPException(404, detail=f"Country with code '{country_code}' not found")
    region = country.get("region") or {}
    if not region.get("id"):
        raise HTTPException(404, detail=f"Region for country '{country_code}' not found")
    return {"data": {"id": region["id"], "value": region.get("value")}}


@router.get("/{region_id}/countries", response_model=Page[Record], deprecated=True)
def list_countries_by_region_legacy(
    region_id: str,
    client: InternaciaClientDep,
    request: Request,
    response: Response,
    paging: Paging,
    fields: FieldsParam = None,
):
    """Deprecated: use `/countries/region/{region_id}`."""
    mark_deprecated(response, f"/countries/region/{region_id}")
    rows = client.countries.get_by_region(region_id)
    return page([dict(r) for r in rows], request, paging, fields)


@router.get("/{region_id}", response_model=Single[RegionEntry])
def get_region(region_id: str, client: InternaciaClientDep):
    """One World Bank region by id (e.g. `ECS`)."""
    region = client.countries.get_region(region_id)
    if region is None:
        raise HTTPException(404, detail=f"Region '{region_id}' not found")
    return {"data": dict(region)}
