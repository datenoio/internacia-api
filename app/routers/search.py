"""Search-related endpoints."""

from fastapi import APIRouter, Query, HTTPException
from app.dependencies import InternaciaClientDep, StubClient
from app.utils import handle_sdk_error, convert_numpy_to_python
from app.models.responses import SearchResponse

router = APIRouter(prefix="/search", tags=["search"])


def _check_client(client):
    """Check if client is available."""
    if isinstance(client, StubClient):
        raise HTTPException(
            status_code=501,
            detail="SDK not available"
        )


@router.get("", response_model=SearchResponse)
async def fuzzy_search(
    client: InternaciaClientDep,
    query: str = Query(..., description="Search query string", min_length=1),
    limit: int = Query(10, description="Maximum number of results", ge=1, le=1000),
    include_countries: bool = Query(True, description="Whether to search countries"),
    include_blocks: bool = Query(True, description="Whether to search international blocks")
):
    """
    Perform fuzzy search across countries and international blocks.

    This function searches across:
    - Country names (in any language via native_names)
    - Country codes (ISO 3166-1 alpha-2, alpha-3, numeric)
    - International block names
    - Block translations (in any language)
    - Block acronyms (in any language)
    - Block IDs
    - Block tags

    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 10)
        include_countries: Whether to search countries (default: True)
        include_blocks: Whether to search international blocks (default: True)

    Returns:
        Search results from internacia-db
    """
    try:
        _check_client(client)
        results = client.search.fuzzy(
            query=query,
            limit=limit,
            search_countries=include_countries,
            search_intblocks=include_blocks
        )

        # Convert numpy arrays to Python lists for JSON serialization
        if results:
            results = [convert_numpy_to_python(result) for result in results]

        return SearchResponse(
            results=results or [],
            count=len(results) if results else 0,
            query=query
        )
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "performing search") from e


@router.get("/countries", response_model=SearchResponse)
async def search_countries(
    client: InternaciaClientDep,
    query: str = Query(..., description="Search query string", min_length=1),
    limit: int = Query(10, description="Maximum number of results", ge=1, le=1000)
):
    """
    Search only countries.

    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 10)

    Returns:
        Search results for countries only
    """
    try:
        _check_client(client)
        results = client.search.search_countries(query=query, limit=limit)

        # Convert numpy arrays to Python lists for JSON serialization
        if results:
            results = [convert_numpy_to_python(result) for result in results]

        return SearchResponse(
            results=results or [],
            count=len(results) if results else 0,
            query=query
        )
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "searching countries") from e


@router.get("/blocks", response_model=SearchResponse)
async def search_intblocks(
    client: InternaciaClientDep,
    query: str = Query(..., description="Search query string", min_length=1),
    limit: int = Query(10, description="Maximum number of results", ge=1, le=1000)
):
    """
    Search only international blocks.

    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 10)

    Returns:
        Search results for blocks only
    """
    try:
        _check_client(client)
        results = client.search.search_intblocks(query=query, limit=limit)

        # Convert numpy arrays to Python lists for JSON serialization
        if results:
            results = [convert_numpy_to_python(result) for result in results]

        return SearchResponse(
            results=results or [],
            count=len(results) if results else 0,
            query=query
        )
    except HTTPException:
        raise
    except Exception as e:
        raise handle_sdk_error(e, "searching blocks") from e
