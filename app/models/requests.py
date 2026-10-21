"""Request models for API endpoints."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request model for search operations."""

    query: str = Field(..., description="Search query string", min_length=1)
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional search filters")
    limit: Optional[int] = Field(None, description="Maximum number of results", ge=1, le=1000)


class AdvancedSearchRequest(BaseModel):
    """Request model for advanced search with filters."""

    query: str = Field(..., description="Search query string", min_length=1)
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    limit: Optional[int] = Field(100, description="Maximum number of results", ge=1, le=1000)
    offset: Optional[int] = Field(0, description="Number of results to skip", ge=0)
