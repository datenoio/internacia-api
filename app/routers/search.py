"""Search endpoints."""

from fastapi import APIRouter, Query

from app.dependencies import InternaciaClientDep
from app.models.responses import SearchResponse

router = APIRouter(prefix="/search", tags=["search"])

QueryParam = Query(..., description="Search query string", min_length=1)
LimitParam = Query(10, description="Maximum number of results", ge=1, le=1000)


@router.get("", response_model=SearchResponse)
def fuzzy_search(
    client: InternaciaClientDep,
    query: str = QueryParam,
    limit: int = LimitParam,
    include_countries: bool = Query(True, description="Whether to search countries"),
    include_blocks: bool = Query(True, description="Whether to search international blocks"),
):
    """
    Fuzzy search across countries (names in any language, ISO codes) and international blocks
    (names in any language, acronyms, ids). Each result has `type` `country` or `intblock`.
    """
    results = client.search.fuzzy(
        query=query,
        limit=limit,
        search_countries=include_countries,
        search_intblocks=include_blocks,
    )
    return {"results": results, "count": len(results), "query": query}


@router.get("/countries", response_model=SearchResponse)
def search_countries(client: InternaciaClientDep, query: str = QueryParam, limit: int = LimitParam):
    """Search countries only."""
    results = client.search.search_countries(query=query, limit=limit)
    return {"results": results, "count": len(results), "query": query}


@router.get("/blocks", response_model=SearchResponse)
def search_blocks(client: InternaciaClientDep, query: str = QueryParam, limit: int = LimitParam):
    """Search international blocks only."""
    results = client.search.search_intblocks(query=query, limit=limit)
    return {"results": results, "count": len(results), "query": query}
