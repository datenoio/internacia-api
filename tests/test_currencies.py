"""Tests for currency-related endpoints."""

from unittest.mock import Mock

from fastapi.testclient import TestClient


def test_get_currency_success(client: TestClient, mock_client: Mock):
    """Test getting a currency by code successfully."""
    mock_countries = [
        {
            "code": "US",
            "name": "United States",
            "currencies": [{"code": "USD", "name": "US Dollar", "symbol": "$"}]
        }
    ]

    mock_client.countries.get_all = Mock(return_value=mock_countries)

    response = client.get("/currencies/USD")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["code"] == "USD"
    assert data["data"]["name"] == "US Dollar"


def test_get_currency_not_found(client: TestClient, mock_client: Mock):
    """Test getting a currency that doesn't exist."""
    mock_client.countries.get_all = Mock(return_value=[])

    response = client.get("/currencies/XXX")

    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "Currency with code 'XXX' not found" in data["error"]


def test_get_currency_sdk_error(client: TestClient, mock_client: Mock):
    """Test getting a currency when SDK raises an error."""
    mock_client.countries.get_all = Mock(side_effect=Exception("SDK error"))

    response = client.get("/currencies/USD")

    assert response.status_code == 500
    data = response.json()
    assert "error" in data


def test_list_currencies_success(client: TestClient, mock_client: Mock):
    """Test listing all currencies successfully."""
    mock_countries = [
        {
            "code": "US",
            "currencies": [{"code": "USD", "name": "US Dollar"}]
        },
        {
            "code": "GB",
            "currencies": [{"code": "GBP", "name": "British Pound"}]
        },
        {
            "code": "FR",
            "currencies": [{"code": "EUR", "name": "Euro"}]
        }
    ]

    mock_client.countries.get_all = Mock(return_value=mock_countries)

    response = client.get("/currencies")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 3
    assert data["count"] == 3


def test_list_currencies_empty(client: TestClient, mock_client: Mock):
    """Test listing currencies when no currencies are available."""
    mock_client.countries.get_all = Mock(return_value=[])

    response = client.get("/currencies")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 0
    assert data["count"] == 0


def test_list_currencies_sdk_error(client: TestClient, mock_client: Mock):
    """Test listing currencies when SDK raises an error."""
    mock_client.countries.get_all = Mock(side_effect=Exception("SDK error"))

    response = client.get("/currencies")

    assert response.status_code == 500
    data = response.json()
    assert "error" in data


def test_get_currencies_by_country_success(client: TestClient, mock_client: Mock):
    """Test getting currencies by country successfully."""
    mock_country = {
        "code": "US",
        "name": "United States",
        "currencies": [{"code": "USD", "name": "US Dollar"}]
    }

    mock_client.countries.get_by_code = Mock(return_value=mock_country)

    response = client.get("/currencies/country/US")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["code"] == "USD"


def test_get_currencies_by_country_empty(client: TestClient, mock_client: Mock):
    """Test getting currencies by country when country has no currencies."""
    mock_country = {
        "code": "XX",
        "name": "Test Country",
        "currencies": []
    }

    mock_client.countries.get_by_code = Mock(return_value=mock_country)

    response = client.get("/currencies/country/XX")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 0
    assert data["count"] == 0


def test_get_currencies_by_country_not_found(client: TestClient, mock_client: Mock):
    """Test getting currencies by country when country doesn't exist."""
    mock_client.countries.get_by_code = Mock(return_value=None)

    response = client.get("/currencies/country/XX")

    assert response.status_code == 404
    data = response.json()
    assert "error" in data


def test_get_currencies_by_country_sdk_error(client: TestClient, mock_client: Mock):
    """Test getting currencies by country when SDK raises an error."""
    mock_client.countries.get_by_code = Mock(side_effect=Exception("SDK error"))

    response = client.get("/currencies/country/US")

    assert response.status_code == 500
    data = response.json()
    assert "error" in data


def test_currencies_null_column_is_treated_as_empty(client: TestClient, mock_client: Mock):
    """A NULL `currencies` column (10 countries in internacia-db 3.0.0) is treated as empty."""
    mock_countries = [
        {"code": "AQ", "currencies": None},
        {"code": "FR", "currencies": [{"code": "EUR", "name": "Euro"}]},
    ]
    mock_client.countries.get_all = Mock(return_value=mock_countries)
    mock_client.countries.get_by_code = Mock(return_value=mock_countries[0])

    response = client.get("/currencies")
    assert response.status_code == 200
    assert response.json() == {"items": [{"code": "EUR", "name": "Euro"}], "count": 1}

    response = client.get("/currencies/EUR")
    assert response.status_code == 200
    assert response.json() == {"data": {"code": "EUR", "name": "Euro"}}

    response = client.get("/currencies/country/AQ")
    assert response.status_code == 200
    assert response.json() == {"items": [], "count": 0}
