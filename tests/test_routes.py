"""API-layer behavior of the routers with a mocked SDK: pagination, field selection,
redirects, deprecation, 404s and the SDK calls made. Data behavior is covered by the smoke
test against a real database (tests/smoke)."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from internacia import ValidationError

COUNTRIES = [
    {"code": c, "name": f"Country {c}", "region": {"id": "ECS", "value": "Europe"}} for c in "ABCDE"
]


def resolution(value, status, target=None, note=None, disambiguated=None):
    return {
        "input": value,
        "id": target,
        "status": status,
        "since": "3.0.0",
        "note": note,
        "disambiguated": disambiguated,
    }


class TestPagination:
    def test_page_window_total_and_next(self, client: TestClient, mock_client: Mock):
        mock_client.countries.get_all = Mock(return_value=COUNTRIES)
        body = client.get("/countries?limit=2&offset=1").json()
        assert [c["code"] for c in body["items"]] == ["B", "C"]
        assert (body["count"], body["total"], body["limit"], body["offset"]) == (2, 5, 2, 1)
        assert body["next"].endswith("/countries?offset=3&limit=2")
        assert client.get("/countries?limit=2&offset=3").json()["next"] is None

    def test_default_and_maximum_limit(self, client: TestClient, mock_client: Mock):
        mock_client.countries.get_all = Mock(return_value=COUNTRIES * 50)
        assert client.get("/countries").json()["count"] == 100
        assert client.get("/countries?limit=1001").status_code == 422
        assert client.get("/countries?offset=-1").status_code == 422

    def test_fields(self, client: TestClient, mock_client: Mock):
        mock_client.countries.get_all = Mock(return_value=COUNTRIES)
        mock_client.countries.get_by_code = Mock(return_value=COUNTRIES[0])
        assert client.get("/countries?fields=code").json()["items"][0] == {"code": "A"}
        assert client.get("/countries/code/A?fields=name, code").json()["data"] == {
            "name": "Country A",
            "code": "A",
        }


class TestRedirects:
    def test_renamed_country_redirects_keeping_the_query(
        self, client: TestClient, mock_client: Mock
    ):
        mock_client.countries.get_by_code = Mock(return_value=None)
        mock_client.countries.resolve_code = Mock(return_value=resolution("KV", "renamed", "XK"))
        response = client.get("/countries/code/KV?fields=code", follow_redirects=False)
        assert response.status_code == 301
        assert response.headers["location"].endswith("/countries/code/XK?fields=code")
        assert response.json()["error"] == "Country 'KV' was renamed into 'XK'"

    def test_merged_block_redirects_sub_routes(self, client: TestClient, mock_client: Mock):
        mock_client.intblocks.get_by_id = Mock(return_value=None)
        mock_client.intblocks.resolve_id = Mock(return_value=resolution("USAN", "merged", "UNASUR"))
        response = client.get("/blocks/usan/members?current=false", follow_redirects=False)
        assert response.status_code == 301
        assert response.headers["location"].endswith("/blocks/UNASUR/members?current=false")

    def test_retired_block_is_gone(self, client: TestClient, mock_client: Mock):
        mock_client.intblocks.get_by_id = Mock(return_value=None)
        mock_client.intblocks.resolve_id = Mock(
            return_value=resolution("TELESUR", "retired", note="Not an intergovernmental body")
        )
        response = client.get("/blocks/TELESUR")
        assert response.status_code == 410
        assert "retired: Not an intergovernmental body" in response.json()["error"]

    def test_unknown_ids_are_404(self, client: TestClient, mock_client: Mock):
        mock_client.intblocks.get_by_id = Mock(return_value=None)
        mock_client.countries.get_by_code = Mock(return_value=None)
        mock_client.countries.get_by_iso3 = Mock(return_value=None)
        assert client.get("/blocks/NOPE").status_code == 404
        assert client.get("/countries/code/QQ/memberships").status_code == 404
        assert (
            client.get("/countries/iso3/QQQ").json()["error"]
            == "Country with ISO3 code 'QQQ' not found"
        )

    def test_disambiguated_header(self, client: TestClient, mock_client: Mock):
        mock_client.intblocks.get_by_id = Mock(
            return_value={"id": "ASF", "name": "African Standby Force"}
        )
        mock_client.intblocks.resolve_id = Mock(
            return_value=resolution("ASF", "current", "ASF", disambiguated="FSA")
        )
        assert client.get("/blocks/ASF").headers["X-Internacia-Disambiguated"] == "FSA"


class TestMemberships:
    def test_block_members_default_current(self, client: TestClient, mock_client: Mock):
        mock_client.intblocks.get_by_id = Mock(return_value={"id": "NATO"})
        edge = {
            "intblock_id": "NATO",
            "country_code": "FR",
            "include_type": "country",
            "status": "member",
            "joined": "1949",
            "left": None,
        }
        mock_client.memberships.get_by_intblock = Mock(return_value=[edge])
        body = client.get("/blocks/nato/members").json()
        assert body["items"] == [edge]
        mock_client.memberships.get_by_intblock.assert_called_once_with("NATO", current_only=True)
        client.get("/blocks/NATO/members?current=false")
        mock_client.memberships.get_by_intblock.assert_called_with("NATO", current_only=False)

    def test_country_memberships(self, client: TestClient, mock_client: Mock):
        mock_client.countries.get_by_code = Mock(return_value={"code": "US"})
        mock_client.memberships.get_by_country = Mock(return_value=[])
        assert client.get("/countries/us/memberships?current=false").json()["total"] == 0
        mock_client.memberships.get_by_country.assert_called_once_with("US", current_only=False)

    def test_blocks_by_member_current_flag(self, client: TestClient, mock_client: Mock):
        mock_client.intblocks.get_by_member = Mock(return_value=[])
        client.get("/blocks/member/US?current=true")
        mock_client.intblocks.get_by_member.assert_called_once_with("US", current_only=True)


class TestDeprecation:
    @pytest.mark.parametrize(
        ("path", "successor", "setup"),
        [
            ("/countries/FR", "/countries/code/FR", "get_by_code"),
            ("/countries/alpha2/FR", "/countries/code/FR", "get_by_code"),
            ("/countries/alpha3/FRA", "/countries/iso3/FRA", "get_by_iso3"),
            ("/currencies/EUR/countries", "/countries/currency/EUR", "get_by_currency"),
            ("/languages/fra/countries", "/countries/language/fra", "get_by_language"),
            ("/regions/ECS/countries", "/countries/region/ECS", "get_by_region"),
        ],
    )
    def test_deprecated_routes(self, client: TestClient, mock_client: Mock, path, successor, setup):
        value = COUNTRIES[0] if setup in ("get_by_code", "get_by_iso3") else COUNTRIES
        setattr(mock_client.countries, setup, Mock(return_value=value))
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers["Deprecation"] == "true"
        assert response.headers["Link"] == f'<{successor}>; rel="successor-version"'


class TestCatalogs:
    def test_currencies(self, client: TestClient, mock_client: Mock):
        eur = {"code": "EUR", "name": "Euro", "symbol": "€", "country_count": 35}
        mock_client.countries.get_currencies = Mock(return_value=[eur])
        mock_client.countries.get_currency = Mock(side_effect=lambda c: eur if c == "EUR" else None)
        assert client.get("/currencies").json()["items"] == [eur]
        assert client.get("/currencies/EUR").json()["data"] == eur
        assert client.get("/currencies/XXX").status_code == 404

    def test_country_currencies_and_languages(self, client: TestClient, mock_client: Mock):
        mock_client.countries.get_by_code = Mock(
            side_effect=lambda c: {"code": c} if c == "CH" else None
        )
        mock_client.countries.get_country_currencies = Mock(return_value=[])
        mock_client.countries.get_country_languages = Mock(
            return_value=[{"code": "deu", "name": "German", "official": None}]
        )
        assert client.get("/currencies/country/CH").json()["total"] == 0
        assert client.get("/languages/country/CH").json()["items"][0]["code"] == "deu"
        assert client.get("/currencies/country/QQ").status_code == 404

    def test_regions(self, client: TestClient, mock_client: Mock):
        mock_client.countries.get_region = Mock(return_value=None)
        mock_client.countries.get_by_code = Mock(return_value=COUNTRIES[0])
        assert client.get("/regions/XXX").status_code == 404
        assert client.get("/regions/country/A").json()["data"] == {"id": "ECS", "value": "Europe"}

    def test_timezones(self, client: TestClient, mock_client: Mock):
        mock_client.countries.get_by_code = Mock(return_value={"code": "FR"})
        mock_client.countries.get_timezones = Mock(
            return_value=[{"timezone": "Europe/Paris", "country_count": 2}]
        )
        mock_client.countries.get_country_timezones = Mock(return_value=["Europe/Paris"])
        mock_client.countries.get_by_timezone = Mock(
            side_effect=lambda tz: [{"code": "FR"}, {"code": "MC"}] if tz == "Europe/Paris" else []
        )
        assert client.get("/timezones/country/FR").json()["items"] == [
            {"timezone": "Europe/Paris", "country_count": 2}
        ]
        assert client.get("/timezones/Europe/Paris").json()["data"]["countries"] == ["FR", "MC"]
        assert client.get("/timezones/Mars/Olympus").status_code == 404

    def test_blocktypes(self, client: TestClient, mock_client: Mock):
        mock_client.blocktypes.get_all = Mock(return_value=[{"id": "economic", "name": "Economic"}])
        mock_client.blocktypes.get_by_id = Mock(return_value=None)
        assert client.get("/blocktypes").json()["items"][0]["id"] == "economic"
        assert client.get("/blocktypes/nope").status_code == 404


def test_sdk_validation_error_is_400(client: TestClient, mock_client: Mock):
    mock_client.countries.get_by_code = Mock(side_effect=ValidationError("code must be a 2-letter"))
    response = client.get("/countries/code/USA")
    assert response.status_code == 400
    assert response.json()["error"] == "code must be a 2-letter"


def test_founded_year_must_be_an_integer(client: TestClient):
    assert client.get("/blocks/founded/abc").status_code == 422
