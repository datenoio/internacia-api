"""Tests for timezone-related endpoints."""

from unittest.mock import Mock

from fastapi.testclient import TestClient


def test_get_timezone_not_found(client: TestClient, mock_client: Mock):
    """Test getting a timezone that doesn't exist (timezones not in SDK yet)."""
    response = client.get("/timezones/America/New_York")

    assert response.status_code == 404
    data = response.json()
    assert "error" in data or "detail" in data
    if "error" in data:
        assert "not found" in data["error"].lower() or "not available" in data["error"].lower()


def test_list_timezones_empty(client: TestClient, mock_client: Mock):
    """Test listing timezones returns empty list (timezones not in SDK yet)."""
    response = client.get("/timezones")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 0
    assert data["count"] == 0


def test_get_timezones_by_country_empty(client: TestClient, mock_client: Mock):
    """Test getting timezones by country returns empty list (timezones not in SDK yet)."""
    response = client.get("/timezones/country/US")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 0
    assert data["count"] == 0
