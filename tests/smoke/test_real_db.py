"""Smoke test: every route against a real internacia-db release DuckDB file.

Set ``INTERNACIA_TEST_DB_PATH`` to a release ``internacia.duckdb`` (see
``scripts/fetch_test_db.py``). Without it these tests are skipped locally and fail in CI.
Expected counts are for internacia-db 3.0.0; update them when bumping the tested release.
"""

import os
from collections.abc import Callable, Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

ENV_DB_PATH = "INTERNACIA_TEST_DB_PATH"

Check = Callable[[Any], None]


@pytest.fixture(scope="module")
def api() -> Iterator[TestClient]:
    db_path = os.getenv(ENV_DB_PATH)
    if not db_path:
        if os.getenv("CI"):
            pytest.fail(f"{ENV_DB_PATH} must be set in CI")
        pytest.skip(f"{ENV_DB_PATH} is not set")
    if not os.path.isfile(db_path):
        pytest.fail(f"{ENV_DB_PATH}={db_path} does not exist")

    previous = settings.internacia_db_path
    settings.internacia_db_path = db_path
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        settings.internacia_db_path = previous


def items(n: int | None = None, at_least: int = 1) -> Check:
    def check(body: Any) -> None:
        assert body["count"] == len(body["items"])
        if n is None:
            assert body["count"] >= at_least
        else:
            assert body["count"] == n

    return check


def data(**expected: Any) -> Check:
    def check(body: Any) -> None:
        for key, value in expected.items():
            assert body["data"][key] == value

    return check


def results(at_least: int = 1, only_type: str | None = None) -> Check:
    def check(body: Any) -> None:
        assert body["count"] == len(body["results"]) >= at_least
        if only_type:
            assert {r["type"] for r in body["results"]} == {only_type}

    return check


def count(n: int) -> Check:
    def check(body: Any) -> None:
        assert body == {"count": n}

    return check


def anything(body: Any) -> None:
    pass


OK_ROUTES: list[tuple[str, Check]] = [
    ("/", anything),
    # countries
    ("/countries", items(256)),
    ("/countries?limit=5", items(5)),
    ("/countries/count", count(256)),
    ("/countries/code/US", data(code="US", iso3code="USA")),
    ("/countries/code/us", data(code="US")),
    ("/countries/iso3/USA", data(code="US")),
    ("/countries/numeric/840", data(code="US")),
    ("/countries/region/ECS", items(64)),
    ("/countries/income-level/LMC", items()),
    ("/countries/un-members", items(193)),
    ("/countries/independent", items(at_least=190)),
    ("/countries/continent/Europe", items(55)),
    ("/countries/currency/EUR", items(35)),
    ("/countries/language/fra", items()),
    ("/countries/alpha2/FR", data(code="FR")),
    ("/countries/alpha3/FRA", data(code="FR")),
    ("/countries/DE", data(code="DE")),
    ("/countries/code/AQ", data(code="AQ", currencies=None, languages=None)),
    # blocks
    ("/blocks", items(1269)),
    ("/blocks?limit=3", items(3)),
    ("/blocks/count", count(1269)),
    ("/blocks/EU", data(id="EU")),
    ("/blocks/eu", data(id="EU")),
    ("/blocks/UNASUR", data(id="UNASUR")),
    ("/blocks/type/economic", items(62)),
    ("/blocks/status/formal", items(1097)),
    ("/blocks/scope/regional", items(603)),
    ("/blocks/member/FR", items(508)),
    ("/blocks/acronym/NATO", items()),
    ("/blocks/tag/trade", items()),
    ("/blocks/topic/economy", items()),
    ("/blocks/founded/1945", items()),
    # search
    ("/search?query=united", results()),
    ("/search?query=europe", results()),
    ("/search?query=Европа", results()),
    ("/search?query=union&include_countries=false", results(only_type="intblock")),
    ("/search?query=france&include_blocks=false", results(only_type="country")),
    ("/search/countries?query=france", results(only_type="country")),
    ("/search/blocks?query=union", results(only_type="intblock")),
    ("/search?query=zzqqxxnotfound", results(at_least=0)),
    # currencies (10 countries have NULL currencies in 3.0.0)
    ("/currencies", items(at_least=100)),
    ("/currencies/EUR", data(code="EUR")),
    ("/currencies/EUR/countries", items(35)),
    ("/currencies/country/US", items()),
    ("/currencies/country/AQ", items(0)),
    # languages (8 countries have NULL languages in 3.0.0)
    ("/languages", items(at_least=100)),
    ("/languages/fra", data(code="fra")),
    ("/languages/fra/countries", items()),
    ("/languages/country/CH", items(at_least=3)),
    ("/languages/country/AQ", items(0)),
    # regions
    ("/regions", items(at_least=7)),
    ("/regions/ECS", data(id="ECS")),
    ("/regions/ECS/countries", items(64)),
    ("/regions/country/US", data(id="NAC")),
    # timezones (placeholder until the SDK exposes them)
    ("/timezones", items(0)),
]

ERROR_ROUTES: list[tuple[str, int]] = [
    ("/countries/code/XX", 404),
    ("/blocks/NOSUCHBLOCK", 404),
    ("/currencies/XXX", 404),
    ("/languages/xxx", 404),
    ("/regions/XXX", 404),
    ("/blocks/founded/999", 400),
    ("/search?query=", 422),
]


def test_health(api: TestClient) -> None:
    response = api.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.parametrize(("path", "check"), OK_ROUTES, ids=[p for p, _ in OK_ROUTES])
def test_route_ok(api: TestClient, path: str, check: Check) -> None:
    response = api.get(path)
    assert response.status_code == 200, response.text[:500]
    check(response.json())


@pytest.mark.parametrize(("path", "status"), ERROR_ROUTES, ids=[p for p, _ in ERROR_ROUTES])
def test_route_error(api: TestClient, path: str, status: int) -> None:
    response = api.get(path)
    assert response.status_code == status, response.text[:500]
    assert "Error:" not in response.text


def test_meta_and_cache_headers(api: TestClient) -> None:
    meta = api.get("/meta").json()["data"]
    assert meta["version"].startswith("3.")
    assert meta["contract_version"].startswith("3.")
    assert meta["datasets"]["countries"]["row_count"] == 256
    response = api.get("/blocks/EU")
    assert response.headers["X-Internacia-Version"] == meta["version"]
    cached = api.get("/blocks/EU", headers={"If-None-Match": response.headers["ETag"]})
    assert cached.status_code == 304
