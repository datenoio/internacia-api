"""Data version headers, ETags and Cache-Control.

Responses depend only on the request URL, the API version and the internacia-db build being
served, so the ETag is derived from those and checked before the route runs: a matching
``If-None-Match`` is answered with 304 without querying the database.
"""

import hashlib
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.config import settings

UNCACHED_PATHS = ("/health",)
EXPOSED_HEADERS = ["ETag", "X-Internacia-Version", "X-Internacia-Contract"]


def data_identity(meta: dict[str, Any]) -> dict[str, str]:
    """Header values and ETag seed for one database build."""
    datasets = meta.get("datasets") or {}
    seed = "|".join(
        [
            settings.api_version,
            str(meta.get("version")),
            str(meta.get("build_date")),
            str(meta.get("git_commit")),
            *(f"{name}:{info.get('schema_hash')}" for name, info in sorted(datasets.items())),
        ]
    )
    return {
        "version": str(meta.get("version")),
        "contract": str(meta.get("contract_version")),
        "seed": seed,
    }


def _etag(seed: str, request: Request) -> str:
    url = f"{request.url.path}?{request.url.query}"
    return 'W/"' + hashlib.sha256(f"{seed}|{url}".encode()).hexdigest()[:32] + '"'


class DataVersionMiddleware(BaseHTTPMiddleware):
    """Adds X-Internacia-Version/-Contract to every response; ETag and Cache-Control to
    successful GETs; answers matching If-None-Match with 304."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        identity: dict[str, str] | None = getattr(request.app.state, "data_identity", None)
        if identity is None:
            return await call_next(request)
        headers = {
            "X-Internacia-Version": identity["version"],
            "X-Internacia-Contract": identity["contract"],
        }
        cacheable = request.method in ("GET", "HEAD") and request.url.path not in UNCACHED_PATHS
        if cacheable:
            etag = _etag(identity["seed"], request)
            headers["ETag"] = etag
            if settings.cache_max_age > 0:
                headers["Cache-Control"] = f"public, max-age={settings.cache_max_age}"
            match = request.headers.get("if-none-match", "")
            if etag in {tag.strip() for tag in match.split(",")} or match.strip() == "*":
                return Response(status_code=304, headers=headers)
        response = await call_next(request)
        if cacheable and response.status_code == 200:
            response.headers.update(headers)
        else:
            versions = {k: v for k, v in headers.items() if k.startswith("X-Internacia")}
            response.headers.update(versions)
        if request.url.path in UNCACHED_PATHS:
            response.headers["Cache-Control"] = "no-store"
        return response
