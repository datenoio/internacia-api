"""Tests for country-related endpoints."""

from fastapi.testclient import TestClient
from unittest.mock import Mock


def test_get_country_by_code_success(client: TestClient, mock_client: Mock):
    """Test getting a country by code successfully."""
    mock_country_data = {
        "code": "US",
        "name": "United States",
        "iso3code": "USA",
        "numeric_code": "840"
    }
    
    # Mock the SDK method
    mock_client.countries.get_by_code = Mock(return_value=mock_country_data)
    
    response = client.get("/countries/code/US")
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["code"] == "US"
    assert data["data"]["name"] == "United States"


def test_get_country_by_code_legacy(client: TestClient, mock_client: Mock):
    """Test legacy endpoint /countries/{code} redirects to /code/{code}."""
    mock_country_data = {"code": "GB", "name": "United Kingdom"}
    
    mock_client.countries.get_by_code = Mock(return_value=mock_country_data)
    
    response = client.get("/countries/GB")
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["code"] == "GB"


def test_get_country_not_found(client: TestClient, mock_client: Mock):
    """Test getting a country that doesn't exist."""
    mock_client.countries.get_by_code = Mock(return_value=None)
    
    response = client.get("/countries/code/XX")
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "Country with code 'XX' not found" in data["error"]


def test_get_country_sdk_error(client: TestClient, mock_client: Mock):
    """Test getting a country when SDK raises an error."""
    mock_client.countries.get_by_code = Mock(side_effect=Exception("SDK error"))
    
    response = client.get("/countries/code/US")
    
    assert response.status_code == 500
    data = response.json()
    assert "error" in data


def test_list_countries_success(client: TestClient, mock_client: Mock):
    """Test listing all countries successfully."""
    mock_countries = [
        {"code": "US", "name": "United States"},
        {"code": "GB", "name": "United Kingdom"},
        {"code": "FR", "name": "France"}
    ]
    
    mock_client.countries.get_all = Mock(return_value=mock_countries)
    
    response = client.get("/countries")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 3
    assert data["count"] == 3
    assert data["items"][0]["code"] == "US"


def test_list_countries_with_limit(client: TestClient, mock_client: Mock):
    """Test listing countries with limit."""
    mock_countries = [
        {"code": "US", "name": "United States"},
        {"code": "GB", "name": "United Kingdom"}
    ]
    
    mock_client.countries.get_all = Mock(return_value=mock_countries)
    
    response = client.get("/countries?limit=2")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    mock_client.countries.get_all.assert_called_once_with(limit=2)


def test_list_countries_empty(client: TestClient, mock_client: Mock):
    """Test listing countries when no countries are available."""
    mock_client.countries.get_all = Mock(return_value=[])
    
    response = client.get("/countries")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 0
    assert data["count"] == 0


def test_get_country_by_iso3_success(client: TestClient, mock_client: Mock):
    """Test getting a country by ISO3 code successfully."""
    mock_country_data = {
        "code": "US",
        "name": "United States",
        "iso3code": "USA"
    }
    
    mock_client.countries.get_by_iso3 = Mock(return_value=mock_country_data)
    
    response = client.get("/countries/iso3/USA")
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["iso3code"] == "USA"


def test_get_country_by_iso3_not_found(client: TestClient, mock_client: Mock):
    """Test getting a country by ISO3 that doesn't exist."""
    mock_client.countries.get_by_iso3 = Mock(return_value=None)
    
    response = client.get("/countries/iso3/XXX")
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


def test_get_country_by_numeric_code_success(client: TestClient, mock_client: Mock):
    """Test getting a country by numeric code successfully."""
    mock_country_data = {
        "code": "US",
        "name": "United States",
        "numeric_code": "840"
    }
    
    mock_client.countries.get_by_numeric_code = Mock(return_value=mock_country_data)
    
    response = client.get("/countries/numeric/840")
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["numeric_code"] == "840"


def test_get_country_by_numeric_code_not_found(client: TestClient, mock_client: Mock):
    """Test getting a country by numeric code that doesn't exist."""
    mock_client.countries.get_by_numeric_code = Mock(return_value=None)
    
    response = client.get("/countries/numeric/999")
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


def test_get_countries_by_region(client: TestClient, mock_client: Mock):
    """Test getting countries by region."""
    mock_countries = [
        {"code": "US", "name": "United States"},
        {"code": "CA", "name": "Canada"}
    ]
    
    mock_client.countries.get_by_region = Mock(return_value=mock_countries)
    
    response = client.get("/countries/region/NAC")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2


def test_get_countries_by_income_level(client: TestClient, mock_client: Mock):
    """Test getting countries by income level."""
    mock_countries = [{"code": "US", "name": "United States"}]
    
    mock_client.countries.get_by_income_level = Mock(return_value=mock_countries)
    
    response = client.get("/countries/income-level/HIC")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_un_members(client: TestClient, mock_client: Mock):
    """Test getting UN member countries."""
    mock_countries = [{"code": "US", "name": "United States"}]
    
    mock_client.countries.get_un_members = Mock(return_value=mock_countries)
    
    response = client.get("/countries/un-members")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_independent_countries(client: TestClient, mock_client: Mock):
    """Test getting independent countries."""
    mock_countries = [{"code": "US", "name": "United States"}]
    
    mock_client.countries.get_independent = Mock(return_value=mock_countries)
    
    response = client.get("/countries/independent")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_countries_by_continent(client: TestClient, mock_client: Mock):
    """Test getting countries by continent."""
    mock_countries = [{"code": "US", "name": "United States"}]
    
    mock_client.countries.get_by_continent = Mock(return_value=mock_countries)
    
    response = client.get("/countries/continent/North America")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_countries_by_currency(client: TestClient, mock_client: Mock):
    """Test getting countries by currency."""
    mock_countries = [{"code": "US", "name": "United States"}]
    
    mock_client.countries.get_by_currency = Mock(return_value=mock_countries)
    
    response = client.get("/countries/currency/USD")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_countries_by_language(client: TestClient, mock_client: Mock):
    """Test getting countries by language."""
    mock_countries = [{"code": "US", "name": "United States"}]
    
    mock_client.countries.get_by_language = Mock(return_value=mock_countries)
    
    response = client.get("/countries/language/eng")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_countries_count(client: TestClient, mock_client: Mock):
    """Test getting countries count."""
    mock_client.countries.count = Mock(return_value=195)
    
    response = client.get("/countries/count")
    
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 195


def test_get_country_by_alpha2_legacy(client: TestClient, mock_client: Mock):
    """Test legacy endpoint /countries/alpha2/{code}."""
    mock_country_data = {"code": "US", "name": "United States"}
    
    mock_client.countries.get_by_code = Mock(return_value=mock_country_data)
    
    response = client.get("/countries/alpha2/US")
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["code"] == "US"


def test_get_country_by_alpha3_legacy(client: TestClient, mock_client: Mock):
    """Test legacy endpoint /countries/alpha3/{code}."""
    mock_country_data = {"code": "US", "name": "United States", "iso3code": "USA"}
    
    mock_client.countries.get_by_iso3 = Mock(return_value=mock_country_data)
    
    response = client.get("/countries/alpha3/USA")
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["iso3code"] == "USA"
