"""Tests for search-related endpoints."""

from unittest.mock import Mock

from fastapi.testclient import TestClient


def test_fuzzy_search_success(client: TestClient, mock_client: Mock):
    """Test fuzzy search endpoint successfully."""
    mock_results = [
        {"code": "US", "name": "United States", "type": "country"},
        {"id": "EU", "name": "European Union", "type": "intblock"}
    ]

    mock_client.search.fuzzy = Mock(return_value=mock_results)

    response = client.get("/search?query=united")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "count" in data
    assert "query" in data
    assert len(data["results"]) == 2
    assert data["count"] == 2
    assert data["query"] == "united"


def test_fuzzy_search_with_limit(client: TestClient, mock_client: Mock):
    """Test fuzzy search with limit parameter."""
    mock_results = [
        {"code": "US", "name": "United States"},
        {"code": "GB", "name": "United Kingdom"}
    ]

    mock_client.search.fuzzy = Mock(return_value=mock_results)

    response = client.get("/search?query=united&limit=2")

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2
    assert data["count"] == 2
    mock_client.search.fuzzy.assert_called_once_with(
        query="united",
        limit=2,
        search_countries=True,
        search_intblocks=True
    )


def test_fuzzy_search_with_search_options(client: TestClient, mock_client: Mock):
    """Test fuzzy search with search_countries and search_intblocks options."""
    mock_results = [{"code": "US", "name": "United States"}]

    mock_client.search.fuzzy = Mock(return_value=mock_results)

    response = client.get("/search?query=united&search_countries=true&search_intblocks=false")

    assert response.status_code == 200
    mock_client.search.fuzzy.assert_called_once_with(
        query="united",
        limit=10,
        search_countries=True,
        search_intblocks=False
    )


def test_fuzzy_search_empty_results(client: TestClient, mock_client: Mock):
    """Test fuzzy search when no results are found."""
    mock_client.search.fuzzy = Mock(return_value=[])

    response = client.get("/search?query=nonexistent")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "count" in data
    assert len(data["results"]) == 0
    assert data["count"] == 0
    assert data["query"] == "nonexistent"


def test_fuzzy_search_missing_query(client: TestClient, mock_client: Mock):
    """Test fuzzy search without query parameter."""
    response = client.get("/search")

    assert response.status_code == 422  # Validation error
    data = response.json()
    assert "detail" in data


def test_fuzzy_search_empty_query(client: TestClient, mock_client: Mock):
    """Test fuzzy search with empty query parameter."""
    response = client.get("/search?query=")

    assert response.status_code == 422  # Validation error
    data = response.json()
    assert "detail" in data


def test_fuzzy_search_invalid_limit(client: TestClient, mock_client: Mock):
    """Test fuzzy search with invalid limit parameter."""
    response = client.get("/search?query=test&limit=0")

    assert response.status_code == 422  # Validation error


def test_fuzzy_search_limit_too_high(client: TestClient, mock_client: Mock):
    """Test fuzzy search with limit exceeding maximum."""
    response = client.get("/search?query=test&limit=1001")

    assert response.status_code == 422  # Validation error


def test_fuzzy_search_sdk_error(client: TestClient, mock_client: Mock):
    """Test fuzzy search when SDK raises an error."""
    mock_client.search.fuzzy = Mock(side_effect=Exception("SDK error"))

    response = client.get("/search?query=test")

    assert response.status_code == 500
    data = response.json()
    assert "error" in data


def test_search_countries_success(client: TestClient, mock_client: Mock):
    """Test search countries endpoint successfully."""
    mock_results = [
        {"code": "US", "name": "United States", "type": "country"},
        {"code": "GB", "name": "United Kingdom", "type": "country"}
    ]

    mock_client.search.search_countries = Mock(return_value=mock_results)

    response = client.get("/search/countries?query=united")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2
    mock_client.search.search_countries.assert_called_once_with(query="united", limit=10)


def test_search_countries_with_limit(client: TestClient, mock_client: Mock):
    """Test search countries with limit."""
    mock_results = [{"code": "US", "name": "United States"}]

    mock_client.search.search_countries = Mock(return_value=mock_results)

    response = client.get("/search/countries?query=united&limit=5")

    assert response.status_code == 200
    mock_client.search.search_countries.assert_called_once_with(query="united", limit=5)


def test_search_blocks_success(client: TestClient, mock_client: Mock):
    """Test search blocks endpoint successfully."""
    mock_results = [
        {"id": "EU", "name": "European Union", "type": "intblock"}
    ]

    mock_client.search.search_intblocks = Mock(return_value=mock_results)

    response = client.get("/search/blocks?query=EU")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    mock_client.search.search_intblocks.assert_called_once_with(query="EU", limit=10)


def test_search_blocks_with_limit(client: TestClient, mock_client: Mock):
    """Test search blocks with limit."""
    mock_results = [{"id": "EU", "name": "European Union"}]

    mock_client.search.search_intblocks = Mock(return_value=mock_results)

    response = client.get("/search/blocks?query=EU&limit=5")

    assert response.status_code == 200
    mock_client.search.search_intblocks.assert_called_once_with(query="EU", limit=5)
