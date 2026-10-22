"""Smoke test: every route against a real internacia-db release DuckDB file.

Set ``INTERNACIA_TEST_DB_PATH`` to a release ``internacia.duckdb`` (see
``scripts/fetch_test_db.py``). Without it these tests are skipped locally and fail in CI.
Expected counts come from SQL against the same file (``SQL``), or are lower bounds, so the tests
pass unchanged against any 3.x release; the data-bump workflow relies on that.
"""

import os
from collections.abc import Callable, Iterator
from typing import Any

import duckdb
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

ENV_DB_PATH = "INTERNACIA_TEST_DB_PATH"

Check = Callable[[Any], None]


class SQL(str):
    """An expected count computed from the test database: ``SELECT count(*) ...``."""


def expected(n: int | SQL) -> int:
    if not isinstance(n, SQL):
        return n
    with duckdb.connect(os.environ[ENV_DB_PATH], read_only=True) as conn:
        return conn.execute(n).fetchone()[0]


@pytest.fixture(scope="module", params=[True, False], ids=["preloaded", "uncached"])
def api(request: pytest.FixtureRequest) -> Iterator[TestClient]:
    db_path = os.getenv(ENV_DB_PATH)
    if not db_path:
        if os.getenv("CI"):
            pytest.fail(f"{ENV_DB_PATH} must be set in CI")
        pytest.skip(f"{ENV_DB_PATH} is not set")
    if not os.path.isfile(db_path):
        pytest.fail(f"{ENV_DB_PATH}={db_path} does not exist")

    previous = settings.internacia_db_path, settings.preload_catalogs
    settings.internacia_db_path, settings.preload_catalogs = db_path, request.param
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        settings.internacia_db_path, settings.preload_catalogs = previous


def items(n: int | SQL | None = None, at_least: int = 1) -> Check:
    """A page whose whole list has ``n`` (or at least ``at_least``) items."""

    def check(body: Any) -> None:
        expected_count = min(body["total"] - body["offset"], body["limit"])
        assert body["count"] == len(body["items"]) == expected_count
        if n is None:
            assert body["total"] >= at_least
        else:
            assert body["total"] == expected(n)
        assert (body["next"] is None) == (body["offset"] + body["count"] >= body["total"])

    return check


def fields_only(*names: str) -> Check:
    def check(body: Any) -> None:
        rows = body["items"] if "items" in body else [body["data"]]
        assert rows and all(list(row) == list(names) for row in rows)

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


def count(n: int | SQL) -> Check:
    def check(body: Any) -> None:
        assert body == {"count": expected(n)}

    return check


def anything(body: Any) -> None:
    pass


ALL_COUNTRIES = SQL("SELECT count(*) FROM countries")
ALL_BLOCKS = SQL("SELECT count(*) FROM intblocks")
ECS_COUNTRIES = SQL("SELECT count(*) FROM countries WHERE region.id = 'ECS'")
UN_MEMBERS = SQL("SELECT count(*) FROM countries WHERE un_member")
ECONOMIC_BLOCKS = SQL("SELECT count(*) FROM intblocks WHERE list_contains(blocktype, 'economic')")
FORMAL_BLOCKS = SQL("SELECT count(*) FROM intblocks WHERE status = 'formal'")
REGIONAL_BLOCKS = SQL("SELECT count(*) FROM intblocks WHERE geographic_scope = 'regional'")
ALL_BLOCKTYPES = SQL("SELECT count(*) FROM blocktypes")

OK_ROUTES: list[tuple[str, Check]] = [
    ("/", anything),
    # countries
    ("/countries", items(ALL_COUNTRIES)),
    ("/countries?limit=5", items(ALL_COUNTRIES)),
    ("/countries/count", count(ALL_COUNTRIES)),
    ("/countries/code/US", data(code="US", iso3code="USA")),
    ("/countries/code/us", data(code="US")),
    ("/countries/iso3/USA", data(code="US")),
    ("/countries/numeric/840", data(code="US")),
    ("/countries/region/ECS", items(ECS_COUNTRIES)),
    ("/countries/income-level/LMC", items()),
    ("/countries/un-members", items(UN_MEMBERS)),
    ("/countries/independent", items(at_least=190)),
    ("/countries/continent/Europe", items(at_least=40)),
    ("/countries/currency/EUR", items(at_least=20)),
    ("/countries/language/fra", items()),
    ("/countries/alpha2/FR", data(code="FR")),
    ("/countries/alpha3/FRA", data(code="FR")),
    ("/countries/DE", data(code="DE")),
    ("/countries/code/AQ", data(code="AQ", currencies=None, languages=None)),
    # blocks
    ("/blocks", items(ALL_BLOCKS)),
    ("/blocks?limit=3", items(ALL_BLOCKS)),
    ("/blocks/count", count(ALL_BLOCKS)),
    ("/blocks/EU", data(id="EU")),
    ("/blocks/eu", data(id="EU")),
    ("/blocks/UNASUR", data(id="UNASUR")),
    ("/blocks/type/economic", items(ECONOMIC_BLOCKS)),
    ("/blocks/status/formal", items(FORMAL_BLOCKS)),
    ("/blocks/scope/regional", items(REGIONAL_BLOCKS)),
    ("/blocks/member/FR", items(at_least=300)),
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
    # currencies (some countries, such as AQ, have none)
    ("/currencies", items(at_least=100)),
    ("/currencies/EUR", data(code="EUR")),
    ("/currencies/EUR/countries", items(at_least=20)),
    ("/currencies/country/US", items()),
    ("/currencies/country/AQ", items(0)),
    # languages (some countries, such as AQ, have none)
    ("/languages", items(at_least=100)),
    ("/languages/fra", data(code="fra")),
    ("/languages/fra/countries", items()),
    ("/languages/country/CH", items(at_least=3)),
    ("/languages/country/AQ", items(0)),
    # regions
    ("/regions", items(at_least=7)),
    ("/regions/ECS", data(id="ECS")),
    ("/regions/ECS/countries", items(ECS_COUNTRIES)),
    ("/regions/country/US", data(id="NAC")),
    # timezones
    ("/timezones", items(at_least=300)),
    ("/timezones/country/RU", items(at_least=10)),
    ("/timezones/Europe/Paris", data(timezone="Europe/Paris")),
    # v3 surface
    ("/blocks/EU/members", items(at_least=20)),
    ("/blocks/eu/members?current=false", items(at_least=27)),
    ("/countries/US/memberships", items(at_least=300)),
    ("/countries/US/memberships?current=false", items(at_least=300)),
    ("/blocktypes", items(ALL_BLOCKTYPES)),
    ("/blocktypes/economic", data(id="economic")),
    ("/blocks/member/US?current=true", items(at_least=300)),
    # pagination and field selection
    ("/countries?limit=10&offset=250", items(ALL_COUNTRIES)),
    ("/blocks?fields=id,name&limit=5", fields_only("id", "name")),
    ("/countries/code/FR?fields=code,name", fields_only("code", "name")),
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


def test_pagination_walks_the_whole_list(api: TestClient) -> None:
    codes, url = [], "/countries?limit=100&fields=code"
    while url:
        body = api.get(url).json()
        codes += [row["code"] for row in body["items"]]
        url = body["next"]
    assert len(codes) == len(set(codes)) == 256


def test_retired_ids_redirect_when_the_database_has_aliases(api: TestClient) -> None:
    has_aliases = api.app.state.client._db_manager.has_relation("intblocks_aliases")
    response = api.get("/blocks/USAN/members?current=false", follow_redirects=False)
    if not has_aliases:
        assert response.status_code == 404
        return
    assert response.status_code == 301
    assert response.headers["location"].endswith("/blocks/UNASUR/members?current=false")
    assert api.get("/countries/code/KV", follow_redirects=False).headers["location"].endswith(
        "/countries/code/XK"
    )
    assert api.get("/blocks/USAN").json()["data"]["id"] == "UNASUR"
    assert api.get("/blocks/ASF").headers["X-Internacia-Disambiguated"] == "FSA"


def test_deprecated_routes_advertise_successors(api: TestClient) -> None:
    response = api.get("/currencies/EUR/countries")
    assert response.headers["Deprecation"] == "true"
    assert "/countries/currency/EUR" in response.headers["Link"]
