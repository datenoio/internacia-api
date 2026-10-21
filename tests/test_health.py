"""Tests for health check endpoints."""

from unittest.mock import Mock

from fastapi.testclient import TestClient
from internacia import DatabaseError


def test_health_check_healthy(client: TestClient, mock_client: Mock):
    """Health is 200 when the database answers a query."""
    mock_client.countries.count = Mock(return_value=256)

    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["sdk_connected"] is True
    assert isinstance(data["version"], str)
    mock_client.countries.count.assert_called_once_with()


def test_health_check_database_error(client: TestClient, mock_client: Mock):
    """Health is 503 when the database query fails."""
    mock_client.countries.count = Mock(
        side_effect=DatabaseError("Query execution failed: IO Error: Cannot open file")
    )

    response = client.get("/health")

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["sdk_connected"] is False
    assert "IO Error" not in response.text


def test_health_check_unexpected_exception(client: TestClient, mock_client: Mock):
    """Health is 503 for any failure, not only SDK errors."""
    mock_client.countries.count = Mock(side_effect=RuntimeError("boom"))

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["status"] == "unhealthy"
