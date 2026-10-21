"""Startup cache of the full lists and catalogs."""

from unittest.mock import Mock

from app.catalog import CACHED_CALLS, CachedClient


def _client() -> Mock:
    client = Mock()
    client.meta.return_value = {"version": "3.0.0"}
    client.intblocks.get_all.return_value = [{"id": "NATO"}]
    client.countries.get_all.return_value = [{"code": "FR"}]
    return client


def test_list_calls_are_loaded_once():
    inner = _client()
    cached = CachedClient(inner)
    for _ in range(3):
        assert cached.intblocks.get_all() == [{"id": "NATO"}]
        assert cached.countries.get_all() == [{"code": "FR"}]
        assert cached.meta() == {"version": "3.0.0"}
    inner.intblocks.get_all.assert_called_once_with()
    inner.countries.get_all.assert_called_once_with()
    inner.meta.assert_called_once_with()
    for name, methods in CACHED_CALLS.items():
        for method in methods:
            getattr(getattr(inner, name), method).assert_called_once_with()


def test_calls_with_arguments_and_other_methods_go_to_the_sdk():
    inner = _client()
    cached = CachedClient(inner)
    inner.intblocks.get_all.return_value = [{"id": "EU"}]
    assert cached.intblocks.get_all(limit=1) == [{"id": "EU"}]
    inner.intblocks.get_all.assert_called_with(limit=1)

    inner.countries.count.return_value = 256
    assert cached.countries.count() == 256
    assert cached.countries.count() == 256
    assert inner.countries.count.call_count == 2

    inner.memberships.get_by_country.return_value = []
    assert cached.memberships.get_by_country("FR") == []
    inner.memberships.get_by_country.assert_called_once_with("FR")
