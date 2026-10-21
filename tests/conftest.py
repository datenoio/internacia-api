"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient
from typing import Generator
import sys

# Mock the internacia module before importing app
if 'internacia' not in sys.modules:
    mock_internacia = MagicMock()
    mock_internacia.InternaciaClient = Mock
    sys.modules['internacia'] = mock_internacia

from app.main import app
from app.dependencies import get_internacia_client


@pytest.fixture
def mock_client() -> Mock:
    """Create a mock InternaciaClient instance with sub-clients."""
    client = Mock()
    client.__class__.__name__ = "InternaciaClient"
    
    # Create sub-clients for countries, intblocks, and search
    client.countries = Mock()
    client.intblocks = Mock()
    client.search = Mock()
    
    return client


@pytest.fixture
def override_get_client(mock_client: Mock) -> Generator:
    """Override the dependency to return a mock client."""
    app.dependency_overrides[get_internacia_client] = lambda: mock_client
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_client) -> TestClient:
    """Create a test client with mocked dependencies."""
    return TestClient(app)
