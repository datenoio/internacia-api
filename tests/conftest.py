"""Pytest configuration and shared fixtures."""

from collections.abc import Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_internacia_client
from app.main import app


@pytest.fixture
def mock_client() -> Mock:
    """Create a mock InternaciaClient instance with sub-clients."""
    client = Mock()
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
    """
    Create a test client with mocked dependencies.

    Not used as a context manager, so the startup hook that opens the real database
    does not run.
    """
    return TestClient(app)
