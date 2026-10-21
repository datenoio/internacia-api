"""Response models for API endpoints."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service status")
    sdk_connected: bool = Field(..., description="Whether SDK is connected")
    version: str = Field(..., description="API version")


class CountryResponse(BaseModel):
    """Country data response model."""

    # Using flexible model to handle various SDK response structures
    data: Dict[str, Any] = Field(..., description="Country data from SDK")


class BlockResponse(BaseModel):
    """International block data response model."""

    data: Dict[str, Any] = Field(..., description="Block data from SDK")


class SearchResponse(BaseModel):
    """Search results response model."""

    results: List[Dict[str, Any]] = Field(..., description="Search results")
    count: int = Field(..., description="Number of results returned")
    query: str = Field(..., description="Original search query")


class ListResponse(BaseModel):
    """Generic list response model."""

    items: List[Dict[str, Any]] = Field(..., description="List of items")
    count: int = Field(..., description="Total number of items")
