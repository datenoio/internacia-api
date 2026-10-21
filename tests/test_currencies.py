"""Tests for currency-related endpoints."""

from fastapi.testclient import TestClient
from unittest.mock import Mock


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
