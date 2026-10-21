"""Tests for main application endpoints."""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test the root endpoint returns API information."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "description" in data
    assert "docs_url" in data
    assert "redoc_url" in data
    assert data["docs_url"] == "/docs"
    assert data["redoc_url"] == "/redoc"


def test_root_endpoint_structure(client: TestClient):
    """Test root endpoint returns correct structure."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["name"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["description"], str)

