"""Tests for region-related endpoints."""

from fastapi.testclient import TestClient
from unittest.mock import Mock


def test_get_region_success(client: TestClient, mock_client: Mock):
    """Test getting a region by ID successfully."""
    mock_countries = [
        {
            "code": "US",
            "name": "United States",
            "region": {"id": "NAC", "value": "North America"}
        }
    ]
    
    mock_client.countries.get_by_region = Mock(return_value=mock_countries)
    
    response = client.get("/regions/NAC")
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["id"] == "NAC"
    assert data["data"]["value"] == "North America"


def test_get_region_not_found(client: TestClient, mock_client: Mock):
    """Test getting a region that doesn't exist."""
    mock_client.countries.get_by_region = Mock(return_value=[])
    
    response = client.get("/regions/XXX")
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "Region 'XXX' not found" in data["error"]


def test_get_region_sdk_error(client: TestClient, mock_client: Mock):
    """Test getting a region when SDK raises an error."""
    mock_client.countries.get_by_region = Mock(side_effect=Exception("SDK error"))
    
    response = client.get("/regions/NAC")
    
    assert response.status_code == 500
    data = response.json()
    assert "error" in data


def test_list_regions_success(client: TestClient, mock_client: Mock):
    """Test listing all regions successfully."""
    mock_countries = [
        {
            "code": "US",
            "region": {"id": "NAC", "value": "North America"}
        },
        {
            "code": "BR",
            "region": {"id": "LCN", "value": "Latin America and Caribbean"}
        },
        {
            "code": "FR",
            "region": {"id": "ECS", "value": "Europe and Central Asia"}
        }
    ]
    
    mock_client.countries.get_all = Mock(return_value=mock_countries)
    
    response = client.get("/regions")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 3
    assert data["count"] == 3


def test_list_regions_empty(client: TestClient, mock_client: Mock):
    """Test listing regions when no regions are available."""
    mock_client.countries.get_all = Mock(return_value=[])
    
    response = client.get("/regions")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 0
    assert data["count"] == 0


def test_list_regions_sdk_error(client: TestClient, mock_client: Mock):
    """Test listing regions when SDK raises an error."""
    mock_client.countries.get_all = Mock(side_effect=Exception("SDK error"))
    
    response = client.get("/regions")
    
    assert response.status_code == 500
    data = response.json()
    assert "error" in data


def test_get_region_by_country_success(client: TestClient, mock_client: Mock):
    """Test getting region by country successfully."""
    mock_country = {
        "code": "US",
        "name": "United States",
        "region": {"id": "NAC", "value": "North America"}
    }
    
    mock_client.countries.get_by_code = Mock(return_value=mock_country)
    
    response = client.get("/regions/country/US")
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["id"] == "NAC"
    assert data["data"]["value"] == "North America"


def test_get_region_by_country_not_found(client: TestClient, mock_client: Mock):
    """Test getting region by country when country doesn't exist."""
    mock_client.countries.get_by_code = Mock(return_value=None)
    
    response = client.get("/regions/country/XX")
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "Country with code 'XX' not found" in data["error"]


def test_get_region_by_country_no_region(client: TestClient, mock_client: Mock):
    """Test getting region by country when country has no region."""
    mock_country = {
        "code": "XX",
        "name": "Test Country",
        "region": None
    }
    
    mock_client.countries.get_by_code = Mock(return_value=mock_country)
    
    response = client.get("/regions/country/XX")
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


def test_get_region_by_country_sdk_error(client: TestClient, mock_client: Mock):
    """Test getting region by country when SDK raises an error."""
    mock_client.countries.get_by_code = Mock(side_effect=Exception("SDK error"))
    
    response = client.get("/regions/country/US")
    
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
