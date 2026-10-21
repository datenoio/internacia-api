"""Tests for error mapping, startup and cross-cutting behavior."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from internacia import DatabaseError, NotFoundError, ValidationError

from app.config import settings
from app.main import app

SQL_ERROR = (
    'Query execution failed: Binder Error: Table "i" does not have a column named '
    '"translations"'
)


def test_sdk_validation_error_is_400(client: TestClient, mock_client: Mock):
    mock_client.search.fuzzy = Mock(side_effect=ValidationError("query must be a non-empty string"))

    response = client.get("/search?query=x")

    assert response.status_code == 400
    assert response.json()["error"] == "query must be a non-empty string"


def test_sdk_not_found_error_is_404(client: TestClient, mock_client: Mock):
    mock_client.intblocks.get_by_id = Mock(side_effect=NotFoundError("Block 'XX' not found"))

    response = client.get("/blocks/XX")

    assert response.status_code == 404
    assert response.json()["error"] == "Block 'XX' not found"


@pytest.mark.parametrize(
    "exc",
    [DatabaseError(SQL_ERROR), ValueError("The truth value of an array is ambiguous")],
)
def test_server_errors_are_generic_500(client: TestClient, mock_client: Mock, exc: Exception):
    """Server-side failures are 500 and never expose the underlying message."""
    mock_client.search.search_intblocks = Mock(side_effect=exc)

    response = client.get("/search/blocks?query=union")

    assert response.status_code == 500
    body = response.json()
    assert body["error"].startswith("Internal server error")
    assert str(exc) not in response.text
    assert "Binder" not in response.text


def test_unhandled_exception_is_generic_500(mock_client: Mock):
    """Exceptions outside the routers' handlers also hide their message."""
    from app.dependencies import get_internacia_client

    def broken_client():
        raise RuntimeError(SQL_ERROR)

    app.dependency_overrides[get_internacia_client] = broken_client
    try:
        response = TestClient(app, raise_server_exceptions=False).get("/countries/count")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    assert response.json() == {
        "error": "Internal server error",
        "status_code": 500,
        "path": "/countries/count",
    }


def test_cors_allows_any_origin_without_credentials(client: TestClient, mock_client: Mock):
    mock_client.countries.count = Mock(return_value=256)

    response = client.get("/countries/count", headers={"Origin": "https://example.org"})

    assert response.headers["access-control-allow-origin"] == "*"
    assert "access-control-allow-credentials" not in response.headers


def test_unknown_scope_category_passes_through(client: TestClient, mock_client: Mock):
    """Enum-like columns are open strings: new values from the data must not break responses."""
    block = {"id": "NEWBLOCK", "scope_category": "not_a_known_category", "status": "new-status"}
    mock_client.intblocks.get_by_id = Mock(return_value=block)
    mock_client.intblocks.get_by_status = Mock(return_value=[block])

    assert client.get("/blocks/NEWBLOCK").json()["data"] == block
    response = client.get("/blocks/status/new-status")
    assert response.status_code == 200
    assert response.json()["items"] == [block]


@pytest.mark.parametrize("make_path", [lambda tmp: tmp / "missing.duckdb", None])
def test_startup_fails_fast_without_database(tmp_path, monkeypatch, caplog, make_path):
    """The app refuses to start, and logs why, when the database cannot be opened."""
    if make_path is None:
        db_path = tmp_path / "not-a-database.duckdb"
        db_path.write_text("this is not a DuckDB file")
    else:
        db_path = make_path(tmp_path)
    monkeypatch.setattr(settings, "internacia_db_path", str(db_path))

    with pytest.raises(Exception):  # noqa: B017
        with TestClient(app):
            pass

    assert "Cannot open internacia-db" in caplog.text
    assert str(db_path) in caplog.text
