"""International block (intblock) endpoints."""

from typing import Any

from fastapi import APIRouter, Query, Request, Response

from app.api import FieldsParam, Paging, not_found_or_moved, page, single
from app.dependencies import InternaciaClientDep
from app.models.responses import Count, Membership, Page, Record, Single

router = APIRouter(prefix="/blocks", tags=["blocks"])


def _block(client: InternaciaClientDep, block_id: str, request: Request) -> Record:
    block = client.intblocks.get_by_id(block_id)
    if block is None:
        raise not_found_or_moved(client.intblocks.resolve_id(block_id), request, "Block", block_id)
    return dict(block)


def _list(rows: list[Any], request: Request, paging: Paging, fields: str | None) -> dict:
    return page([dict(r) for r in rows], request, paging, fields)


@router.get("", response_model=Page[Record])
def list_blocks(
    client: InternaciaClientDep, request: Request, paging: Paging, fields: FieldsParam = None
):
    """All international organizations and groups. Use `fields` to keep pages small."""
    return _list(client.intblocks.get_all(), request, paging, fields)


@router.get("/count", response_model=Count)
def count_blocks(client: InternaciaClientDep):
    """Number of blocks."""
    return {"count": client.intblocks.count()}


@router.get("/type/{blocktype}", response_model=Page[Record])
def list_blocks_by_type(
    blocktype: str,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    fields: FieldsParam = None,
):
    """Blocks with a block type (see `/blocktypes`)."""
    return _list(client.intblocks.get_by_blocktype(blocktype), request, paging, fields)


@router.get("/status/{status}", response_model=Page[Record])
def list_blocks_by_status(
    status: str,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    fields: FieldsParam = None,
):
    """Blocks with a status (open enum, e.g. `formal`, `informal`, `historical`)."""
    return _list(client.intblocks.get_by_status(status), request, paging, fields)


@router.get("/scope/{scope}", response_model=Page[Record])
def list_blocks_by_scope(
    scope: str,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    fields: FieldsParam = None,
):
    """Blocks with a geographic scope (open enum, e.g. `global`, `regional`)."""
    return _list(client.intblocks.get_by_geographic_scope(scope), request, paging, fields)


@router.get("/member/{country_code}", response_model=Page[Record])
def list_blocks_by_member(
    country_code: str,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    fields: FieldsParam = None,
    current: bool = Query(False, description="Only blocks where the membership is current"),
):
    """Blocks that list a country (alpha-2) in `includes`; former memberships unless `current`."""
    rows = client.intblocks.get_by_member(country_code, current_only=current)
    return _list(rows, request, paging, fields)


@router.get("/acronym/{acronym}", response_model=Page[Record])
def list_blocks_by_acronym(
    acronym: str,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    fields: FieldsParam = None,
):
    """Blocks with an acronym in any language (e.g. `NATO`)."""
    return _list(client.intblocks.get_by_acronym(acronym), request, paging, fields)


@router.get("/tag/{tag}", response_model=Page[Record])
def list_blocks_by_tag(
    tag: str,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    fields: FieldsParam = None,
):
    """Blocks with a tag (e.g. `trade`)."""
    return _list(client.intblocks.get_by_tag(tag), request, paging, fields)


@router.get("/topic/{topic_key}", response_model=Page[Record])
def list_blocks_by_topic(
    topic_key: str,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    fields: FieldsParam = None,
):
    """Blocks with a topic key (e.g. `economy`)."""
    return _list(client.intblocks.get_by_topic(topic_key), request, paging, fields)


@router.get("/founded/{year}", response_model=Page[Record])
def list_blocks_by_founded_year(
    year: int,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    fields: FieldsParam = None,
):
    """Blocks founded in a year."""
    return _list(client.intblocks.get_by_founded_year(year), request, paging, fields)


@router.get("/{block_id}/members", response_model=Page[Membership])
def list_block_members(
    block_id: str,
    client: InternaciaClientDep,
    request: Request,
    paging: Paging,
    current: bool = Query(True, description="Only current memberships (see the data contract)"),
):
    """
    Membership edges of a block, ordered by country code. With `current=true` (default) former
    members and edges with a `left` date are excluded; filter `status` for full members.
    """
    block = _block(client, block_id, request)
    rows = client.memberships.get_by_intblock(block["id"], current_only=current)
    return page([dict(r) for r in rows], request, paging)


@router.get("/{block_id}", response_model=Single[Record])
def get_block(
    block_id: str,
    client: InternaciaClientDep,
    request: Request,
    response: Response,
    fields: FieldsParam = None,
):
    """
    A block by id (case-insensitive). Merged or renamed ids redirect with 301 (e.g. `USAN` →
    `UNASUR`); retired ids return 410. When the id now names a different organization than it
    used to, `X-Internacia-Disambiguated` names the id the previous one moved to.
    """
    block = _block(client, block_id, request)
    previous = client.intblocks.resolve_id(block_id).get("disambiguated")
    if previous:
        response.headers["X-Internacia-Disambiguated"] = previous
    return single(block, fields)
