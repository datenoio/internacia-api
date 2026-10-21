"""Currency-related endpoints."""

from fastapi import APIRouter, HTTPException

from app.dependencies import InternaciaClientDep
from app.models.responses import ListResponse
from app.utils import handle_sdk_error

router = APIRouter(prefix="/currencies", tags=["currencies"])


@router.get("/{currency_code}/countries", response_model=ListResponse)
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
        countries = client.countries.get_by_currency(currency_code)

        return ListResponse(items=countries or [], count=len(countries) if countries else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving countries by currency") from e


@router.get("", response_model=ListResponse)
async def list_currencies(client: InternaciaClientDep):
    """
    List all unique currencies from all countries.

    Returns:
        List of all unique currencies
    """
    try:
        all_countries = client.countries.get_all()

        # Extract unique currencies
        currencies_map = {}
        for country in all_countries or []:
            for currency in country.get("currencies") or []:
                code = currency.get("code")
                if code and code not in currencies_map:
                    currencies_map[code] = currency

        currencies = list(currencies_map.values())

        return ListResponse(items=currencies, count=len(currencies))
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "listing currencies") from e


@router.get("/country/{country_code}", response_model=ListResponse)
async def get_currencies_by_country(
    country_code: str,
    client: InternaciaClientDep
):
    """
    Get currencies used by a specific country.

    Args:
        country_code: Country code (e.g., "US", "GB", "FR")

    Returns:
        List of currencies for the country
    """
    try:
        country = client.countries.get_by_code(country_code)

        if country is None:
            raise HTTPException(
                status_code=404,
                detail=f"Country with code '{country_code}' not found"
            )

        currencies = country.get("currencies") or []

        return ListResponse(items=currencies, count=len(currencies))
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving currencies by country") from e


@router.get("/{currency_code}", response_model=dict)
async def get_currency(
    currency_code: str,
    client: InternaciaClientDep
):
    """
    Get currency information by code.

    Args:
        currency_code: Currency code (e.g., "USD", "EUR", "GBP")

    Returns:
        Currency data from internacia-db
    """
    try:
        all_countries = client.countries.get_all()

        # Find currency in any country
        for country in all_countries or []:
            for currency in country.get("currencies") or []:
                if currency.get("code") == currency_code:
                    return {"data": currency}

        raise HTTPException(
            status_code=404,
            detail=f"Currency with code '{currency_code}' not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving currency") from e
