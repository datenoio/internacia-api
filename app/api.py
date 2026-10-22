"""Shared request handling: pagination, field selection, ID redirects, deprecation."""

from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Query, Request, Response
from internacia import IdResolution

MAX_LIMIT = 1000
DEFAULT_LIMIT = 100


class PageParams:
    """``limit``/``offset`` query parameters."""

    def __init__(
        self,
        limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT, description="Page size"),
        offset: int = Query(0, ge=0, description="Number of items to skip"),
    ):
        self.limit = limit
        self.offset = offset


Paging = Annotated[PageParams, Depends()]

FieldsParam = Annotated[
    str | None,
    Query(
        description="Comma-separated top-level fields to return, e.g. `code,name,region`",
        examples=["code,name"],
    ),
]


def select_fields(record: dict[str, Any], fields: str | None) -> dict[str, Any]:
    """Keep only the requested top-level fields (all fields when ``fields`` is empty)."""
    if not fields:
        return record
    wanted = [f.strip() for f in fields.split(",") if f.strip()]
    return {name: record.get(name) for name in wanted}


def page(
    items: Sequence[Any], request: Request, paging: PageParams, fields: str | None = None
) -> dict[str, Any]:
    """Slice ``items`` into one page with ``total`` and a ``next`` link."""
    window = list(items[paging.offset : paging.offset + paging.limit])
    if fields:
        window = [select_fields(item, fields) for item in window]
    end = paging.offset + len(window)
    next_url = (
        str(request.url.include_query_params(offset=end, limit=paging.limit))
        if end < len(items)
        else None
    )
    return {
        "items": window,
        "count": len(window),
        "total": len(items),
        "limit": paging.limit,
        "offset": paging.offset,
        "next": next_url,
    }


def single(record: dict[str, Any], fields: str | None = None) -> dict[str, Any]:
    return {"data": select_fields(record, fields)}


def not_found_or_moved(
    resolution: IdResolution, request: Request, kind: str, segment: str
) -> HTTPException:
    """
    The error for an ID with no record: 301 to its replacement (renamed or merged), 410 if
    it was retired, 404 otherwise.

    ``segment`` is the path segment holding the requested ID; the redirect replaces it and
    keeps the rest of the path and the query string.
    """
    status, target = resolution["status"], resolution["id"]
    if status in ("renamed", "merged") and target:
        parts = request.url.path.split("/")
        location_path = "/".join(target if part == segment else part for part in parts)
        location = request.url.replace(path=location_path)
        return HTTPException(
            status_code=301,
            detail=f"{kind} '{resolution['input']}' was {status} into '{target}'",
            headers={"Location": str(location)},
        )
    if status == "retired":
        note = f": {resolution['note']}" if resolution.get("note") else ""
        return HTTPException(
            status_code=410, detail=f"{kind} '{resolution['input']}' was retired{note}"
        )
    return HTTPException(status_code=404, detail=f"{kind} '{segment}' not found")


def mark_deprecated(response: Response, successor: str) -> None:
    """RFC 8594/9745 deprecation headers pointing at the successor route."""
    response.headers["Deprecation"] = "true"
    response.headers["Link"] = f'<{successor}>; rel="successor-version"'
