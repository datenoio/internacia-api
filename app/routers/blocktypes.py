"""Block type taxonomy endpoints."""

from fastapi import APIRouter, HTTPException, Request

from app.api import Paging, page
from app.dependencies import InternaciaClientDep
from app.models.responses import Blocktype, Page, Single

router = APIRouter(prefix="/blocktypes", tags=["blocktypes"])


@router.get("", response_model=Page[Blocktype])
def list_blocktypes(client: InternaciaClientDep, request: Request, paging: Paging):
    """All block types (the values used in `intblocks.blocktype`), ordered by id."""
    return page([dict(b) for b in client.blocktypes.get_all()], request, paging)


@router.get("/{blocktype_id}", response_model=Single[Blocktype])
def get_blocktype(blocktype_id: str, client: InternaciaClientDep):
    """One block type with its names in other languages."""
    blocktype = client.blocktypes.get_by_id(blocktype_id)
    if blocktype is None:
        raise HTTPException(404, detail=f"Block type '{blocktype_id}' not found")
    return {"data": dict(blocktype)}
