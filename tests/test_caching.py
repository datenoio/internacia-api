"""Data version headers, ETags, Cache-Control and /meta."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.caching import data_identity
from app.config import settings
from app.main import app

META = {
    "version": "3.0.0",
    "contract_version": "3.0",
    "build_date": "2026-10-16T14:30:59Z",
    "git_commit": "cd96e13",
    "data_license": "CC-BY-4.0",
    "datasets": {"countries": {"row_count": 256, "schema_hash": "abc"}},
}


@pytest.fixture
def api(client: TestClient, mock_client: Mock):
    mock_client.meta = Mock(return_value=META)
    mock_client.countries.count = Mock(return_value=256)
    app.state.data_identity = data_identity(META)
    yield client
    del app.state.data_identity


def test_meta_endpoint(api: TestClient):
    body = api.get("/meta").json()
    assert body["api_version"] == settings.api_version
    assert body["data"]["version"] == "3.0.0"
    assert body["sdk_version"]


def test_success_headers(api: TestClient):
    response = api.get("/countries/count")
    assert response.headers["X-Internacia-Version"] == "3.0.0"
    assert response.headers["X-Internacia-Contract"] == "3.0"
    assert response.headers["ETag"].startswith('W/"')
    assert response.headers["Cache-Control"] == f"public, max-age={settings.cache_max_age}"
    assert api.get("/countries/count?x=1").headers["ETag"] != response.headers["ETag"]


def test_if_none_match_returns_304_without_running_the_route(api: TestClient, mock_client: Mock):
    etag = api.get("/countries/count").headers["ETag"]
    mock_client.countries.count.reset_mock()
    response = api.get("/countries/count", headers={"If-None-Match": f'"other", {etag}'})
    assert response.status_code == 304
    assert response.content == b""
    assert response.headers["ETag"] == etag
    mock_client.countries.count.assert_not_called()


def test_etag_changes_with_the_data_build(api: TestClient):
    etag = api.get("/countries/count").headers["ETag"]
    app.state.data_identity = data_identity({**META, "git_commit": "0000000"})
    assert api.get("/countries/count", headers={"If-None-Match": etag}).status_code == 200


def test_errors_and_health_are_not_cached(api: TestClient, mock_client: Mock):
    mock_client.intblocks.get_by_id = Mock(return_value=None)
    missing = api.get("/blocks/NOPE")
    assert missing.status_code == 404
    assert missing.headers["X-Internacia-Version"] == "3.0.0"
    assert "ETag" not in missing.headers and "Cache-Control" not in missing.headers
    health = api.get("/health")
    assert health.headers["Cache-Control"] == "no-store"
    assert "ETag" not in health.headers


def test_cors_exposes_version_headers(api: TestClient):
    response = api.get("/countries/count", headers={"Origin": "https://example.org"})
    exposed = response.headers["access-control-expose-headers"]
    assert "ETag" in exposed and "X-Internacia-Version" in exposed


def test_startup_rejects_unexpected_data_version(monkeypatch, caplog):
    from app.dependencies import create_client

    fake = Mock()
    fake.meta.return_value = META
    monkeypatch.setattr("app.dependencies.InternaciaClient", Mock(return_value=fake))
    monkeypatch.setattr(settings, "internacia_db_version", "v3.1.0")
    with pytest.raises(RuntimeError, match="does not match"):
        create_client()
    monkeypatch.setattr(settings, "internacia_db_version", "v3.0.0")
    assert create_client() is fake
