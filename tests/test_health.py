"""Tests for health check endpoints."""

from fastapi.testclient import TestClient
from unittest.mock import Mock


def test_health_check_healthy(client: TestClient, mock_client: Mock):
    """Test health check endpoint when SDK is healthy."""
    # Mock the health check to return True
    mock_client.health_check = Mock(return_value=True)
    mock_client.ping = Mock(return_value=True)
    
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["sdk_connected"] is True
    assert "version" in data
    assert isinstance(data["version"], str)


def test_health_check_degraded(client: TestClient, mock_client: Mock):
    """Test health check endpoint when SDK is not connected."""
    # Mock the health check to return False
    mock_client.health_check = Mock(return_value=False)
    mock_client.ping = Mock(return_value=False)
    
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["sdk_connected"] is False
    assert "version" in data


def test_health_check_no_methods(client: TestClient, mock_client: Mock):
    """Test health check when SDK has no health check methods."""
    # Remove health check methods
    delattr(mock_client, 'health_check')
    delattr(mock_client, 'ping')
    
    response = client.get("/health")
    
    # Should still return healthy if client exists
    assert response.status_code == 200
    data = response.json()
    assert data["sdk_connected"] is True


def test_health_check_exception(client: TestClient, mock_client: Mock):
    """Test health check when SDK raises an exception."""
    # Mock the health check to raise an exception
    mock_client.health_check = Mock(side_effect=Exception("Connection error"))
    mock_client.ping = Mock(side_effect=Exception("Connection error"))
    
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["sdk_connected"] is False

