"""Startup cache of the full lists and catalogs.

The database is read-only and fixed for the life of the process, so the results of the
argument-free list calls (all countries, all blocks, block types, currencies, languages,
time zones, regions) and ``meta()`` are loaded once at startup and served from memory.
Every other call goes to the SDK. Cached results are shared between requests: routers must
copy records before changing them.
"""

import logging
import time
from typing import Any

from internacia import InternaciaClient

logger = logging.getLogger(__name__)

CACHED_CALLS: dict[str, tuple[str, ...]] = {
    "countries": ("get_all", "get_currencies", "get_languages", "get_timezones", "get_regions"),
    "intblocks": ("get_all",),
    "blocktypes": ("get_all",),
}


class _CachedSubClient:
    def __init__(self, inner: Any, methods: tuple[str, ...]):
        self._inner = inner
        self._results = {name: getattr(inner, name)() for name in methods}

    def __getattr__(self, name: str) -> Any:
        method = getattr(self._inner, name)
        if name not in self._results:
            return method
        result = self._results[name]

        def call(*args: Any, **kwargs: Any) -> Any:
            return method(*args, **kwargs) if args or kwargs else result

        return call


class CachedClient:
    """An ``InternaciaClient`` whose argument-free list calls are answered from memory."""

    def __init__(self, client: InternaciaClient):
        started = time.perf_counter()
        self.client = client
        self._meta = client.meta()
        self._sub_clients = {
            name: _CachedSubClient(getattr(client, name), methods)
            for name, methods in CACHED_CALLS.items()
        }
        logger.info("Preloaded catalogs in %.0f ms", (time.perf_counter() - started) * 1000)

    def meta(self) -> dict[str, Any]:
        return self._meta

    def __getattr__(self, name: str) -> Any:
        if name in self._sub_clients:
            return self._sub_clients[name]
        return getattr(self.client, name)
