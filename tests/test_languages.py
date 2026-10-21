"""Tests for language-related endpoints."""

from unittest.mock import Mock

from fastapi.testclient import TestClient


def test_get_language_success(client: TestClient, mock_client: Mock):
    """Test getting a language by code successfully."""
    mock_countries = [
        {
            "code": "US",
            "name": "United States",
            "languages": [{"code": "eng", "name": "English"}]
        }
    ]

    mock_client.countries.get_all = Mock(return_value=mock_countries)

    response = client.get("/languages/eng")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["code"] == "eng"
    assert data["data"]["name"] == "English"


def test_get_language_not_found(client: TestClient, mock_client: Mock):
    """Test getting a language that doesn't exist."""
    mock_client.countries.get_all = Mock(return_value=[])

    response = client.get("/languages/xx")

    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "Language with code 'xx' not found" in data["error"]


def test_get_language_sdk_error(client: TestClient, mock_client: Mock):
    """Test getting a language when SDK raises an error."""
    mock_client.countries.get_all = Mock(side_effect=Exception("SDK error"))

    response = client.get("/languages/eng")

    assert response.status_code == 500
    data = response.json()
    assert "error" in data


def test_list_languages_success(client: TestClient, mock_client: Mock):
    """Test listing all languages successfully."""
    mock_countries = [
        {
            "code": "US",
            "languages": [{"code": "eng", "name": "English"}]
        },
        {
            "code": "FR",
            "languages": [{"code": "fra", "name": "French"}]
        },
        {
            "code": "ES",
            "languages": [{"code": "spa", "name": "Spanish"}]
        }
    ]

    mock_client.countries.get_all = Mock(return_value=mock_countries)

    response = client.get("/languages")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 3
    assert data["count"] == 3


def test_list_languages_empty(client: TestClient, mock_client: Mock):
    """Test listing languages when no languages are available."""
    mock_client.countries.get_all = Mock(return_value=[])

    response = client.get("/languages")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 0
    assert data["count"] == 0


def test_list_languages_sdk_error(client: TestClient, mock_client: Mock):
    """Test listing languages when SDK raises an error."""
    mock_client.countries.get_all = Mock(side_effect=Exception("SDK error"))

    response = client.get("/languages")

    assert response.status_code == 500
    data = response.json()
    assert "error" in data


def test_get_languages_by_country_success(client: TestClient, mock_client: Mock):
    """Test getting languages by country successfully."""
    mock_country = {
        "code": "US",
        "name": "United States",
        "languages": [
            {"code": "eng", "name": "English"},
            {"code": "spa", "name": "Spanish"}
        ]
    }

    mock_client.countries.get_by_code = Mock(return_value=mock_country)

    response = client.get("/languages/country/US")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 2
    assert data["items"][0]["code"] == "eng"


def test_get_languages_by_country_empty(client: TestClient, mock_client: Mock):
    """Test getting languages by country when country has no languages."""
    mock_country = {
        "code": "XX",
        "name": "Test Country",
        "languages": []
    }

    mock_client.countries.get_by_code = Mock(return_value=mock_country)

    response = client.get("/languages/country/XX")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 0
    assert data["count"] == 0


def test_get_languages_by_country_not_found(client: TestClient, mock_client: Mock):
    """Test getting languages by country when country doesn't exist."""
    mock_client.countries.get_by_code = Mock(return_value=None)

    response = client.get("/languages/country/XX")

    assert response.status_code == 404
    data = response.json()
    assert "error" in data


def test_get_languages_by_country_sdk_error(client: TestClient, mock_client: Mock):
    """Test getting languages by country when SDK raises an error."""
    mock_client.countries.get_by_code = Mock(side_effect=Exception("SDK error"))

    response = client.get("/languages/country/US")

    assert response.status_code == 500
    data = response.json()
    assert "error" in data
