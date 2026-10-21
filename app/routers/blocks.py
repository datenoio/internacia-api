"""International block-related endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import InternaciaClientDep, StubClient
from app.models.responses import BlockResponse, ListResponse
from app.utils import handle_sdk_error, convert_numpy_to_python

router = APIRouter(prefix="/blocks", tags=["blocks"])


def _check_client(client):
    """Check if client is available."""
    if isinstance(client, StubClient):
        raise HTTPException(
            status_code=501,
            detail="SDK not available"
        )


@router.get("/count", response_model=dict)
async def get_blocks_count(client: InternaciaClientDep):
    """
    Get the total number of international blocks.

    Returns:
        Total count of blocks
    """
    try:
        _check_client(client)
        count = client.intblocks.count()

        return {"count": count}
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "counting blocks") from e


@router.get("/{block_id}", response_model=BlockResponse)
async def get_block_by_id(
    block_id: str,
    client: InternaciaClientDep
):
    """
    Get an international block by its ID.

    Args:
        block_id: Block identifier (e.g., "EU", "UN", "NATO")

    Returns:
        Block data from internacia-db
    """
    try:
        _check_client(client)
        block = client.intblocks.get_by_id(block_id)

        if block is None:
            raise HTTPException(
                status_code=404,
                detail=f"International block '{block_id}' not found"
            )

        # Convert numpy arrays to Python lists for JSON serialization
        block = convert_numpy_to_python(block)
        return BlockResponse(data=block)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving block") from e


@router.get("", response_model=ListResponse)
async def get_all_blocks(
    client: InternaciaClientDep,
    limit: Optional[int] = Query(None, description="Maximum number of results", ge=1)
):
    """
    Get all international blocks.

    Args:
        limit: Optional maximum number of results to return

    Returns:
        List of all international blocks from internacia-db
    """
    try:
        _check_client(client)
        blocks = client.intblocks.get_all(limit=limit)

        # Convert numpy arrays to Python lists for JSON serialization
        if blocks:
            blocks = [convert_numpy_to_python(block) for block in blocks]
        return ListResponse(items=blocks or [], count=len(blocks) if blocks else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "listing blocks") from e


@router.get("/type/{blocktype}", response_model=ListResponse)
async def get_blocks_by_type(
    blocktype: str,
    client: InternaciaClientDep
):
    """
    Get blocks by type.

    Args:
        blocktype: Block type (e.g., "economic", "political", "military")

    Returns:
        List of blocks of the specified type
    """
    try:
        _check_client(client)
        blocks = client.intblocks.get_by_blocktype(blocktype)

        # Convert numpy arrays to Python lists for JSON serialization
        if blocks:
            blocks = [convert_numpy_to_python(block) for block in blocks]
        return ListResponse(items=blocks or [], count=len(blocks) if blocks else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving blocks by type") from e


@router.get("/status/{status}", response_model=ListResponse)
async def get_blocks_by_status(
    status: str,
    client: InternaciaClientDep
):
    """
    Get blocks by status.

    Args:
        status: Status (e.g., "formal", "informal", "de-facto")

    Returns:
        List of blocks with the specified status
    """
    try:
        _check_client(client)
        blocks = client.intblocks.get_by_status(status)

        # Convert numpy arrays to Python lists for JSON serialization
        if blocks:
            blocks = [convert_numpy_to_python(block) for block in blocks]
        return ListResponse(items=blocks or [], count=len(blocks) if blocks else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving blocks by status") from e


@router.get("/scope/{scope}", response_model=ListResponse)
async def get_blocks_by_geographic_scope(
    scope: str,
    client: InternaciaClientDep
):
    """
    Get blocks by geographic scope.

    Args:
        scope: Geographic scope (e.g., "global", "regional", "sub-regional")

    Returns:
        List of blocks with the specified geographic scope
    """
    try:
        _check_client(client)
        blocks = client.intblocks.get_by_geographic_scope(scope)

        # Convert numpy arrays to Python lists for JSON serialization
        if blocks:
            blocks = [convert_numpy_to_python(block) for block in blocks]
        return ListResponse(items=blocks or [], count=len(blocks) if blocks else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving blocks by geographic scope") from e


@router.get("/member/{country_code}", response_model=ListResponse)
async def get_blocks_by_member(
    country_code: str,
    client: InternaciaClientDep
):
    """
    Get blocks that include a specific country as a member.

    Args:
        country_code: Two-letter country code (e.g., "US", "FR", "DE")

    Returns:
        List of blocks that include the specified country
    """
    try:
        _check_client(client)
        blocks = client.intblocks.get_by_member(country_code)

        # Convert numpy arrays to Python lists for JSON serialization
        if blocks:
            blocks = [convert_numpy_to_python(block) for block in blocks]
        return ListResponse(items=blocks or [], count=len(blocks) if blocks else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving blocks by member") from e


@router.get("/acronym/{acronym}", response_model=ListResponse)
async def get_blocks_by_acronym(
    acronym: str,
    client: InternaciaClientDep
):
    """
    Get blocks by acronym.

    Args:
        acronym: Acronym (e.g., "EU", "UN", "NATO")

    Returns:
        List of blocks with the specified acronym
    """
    try:
        _check_client(client)
        blocks = client.intblocks.get_by_acronym(acronym)

        # Convert numpy arrays to Python lists for JSON serialization
        if blocks:
            blocks = [convert_numpy_to_python(block) for block in blocks]
        return ListResponse(items=blocks or [], count=len(blocks) if blocks else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving blocks by acronym") from e


@router.get("/tag/{tag}", response_model=ListResponse)
async def get_blocks_by_tag(
    tag: str,
    client: InternaciaClientDep
):
    """
    Get blocks by tag.

    Args:
        tag: Tag keyword

    Returns:
        List of blocks with the specified tag
    """
    try:
        _check_client(client)
        blocks = client.intblocks.get_by_tag(tag)

        # Convert numpy arrays to Python lists for JSON serialization
        if blocks:
            blocks = [convert_numpy_to_python(block) for block in blocks]
        return ListResponse(items=blocks or [], count=len(blocks) if blocks else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving blocks by tag") from e


@router.get("/topic/{topic_key}", response_model=ListResponse)
async def get_blocks_by_topic(
    topic_key: str,
    client: InternaciaClientDep
):
    """
    Get blocks by topic key.

    Args:
        topic_key: Topic key (e.g., "economy", "political", "trade")

    Returns:
        List of blocks with the specified topic
    """
    try:
        _check_client(client)
        blocks = client.intblocks.get_by_topic(topic_key)

        # Convert numpy arrays to Python lists for JSON serialization
        if blocks:
            blocks = [convert_numpy_to_python(block) for block in blocks]
        return ListResponse(items=blocks or [], count=len(blocks) if blocks else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving blocks by topic") from e


@router.get("/founded/{year}", response_model=ListResponse)
async def get_blocks_by_founded_year(
    year: int,
    client: InternaciaClientDep
):
    """
    Get blocks founded in a specific year.

    Args:
        year: Foundation year (e.g., 1993, 1945)

    Returns:
        List of blocks founded in the specified year
    """
    try:
        _check_client(client)
        blocks = client.intblocks.get_by_founded_year(year)

        # Convert numpy arrays to Python lists for JSON serialization
        if blocks:
            blocks = [convert_numpy_to_python(block) for block in blocks]
        return ListResponse(items=blocks or [], count=len(blocks) if blocks else 0)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "retrieving blocks by founded year") from e
