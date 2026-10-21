"""Response models for API endpoints.

Country and block records are open dictionaries: their fields are the internacia-db columns,
which grow with MINOR data releases (see the data contract). Everything the API derives
itself has a typed model.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

Record = dict[str, Any]


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    path: str = Field(..., description="Request path")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service status")
    sdk_connected: bool = Field(..., description="Whether the database answered a query")
    version: str = Field(..., description="API version")


class Page(BaseModel, Generic[T]):
    """One page of a list."""

    items: list[T] = Field(..., description="Items on this page")
    count: int = Field(..., description="Number of items on this page")
    total: int = Field(..., description="Number of items in the whole list")
    limit: int = Field(..., description="Page size")
    offset: int = Field(..., description="Index of the first item on this page")
    next: str | None = Field(None, description="URL of the next page, if any")


class Single(BaseModel, Generic[T]):
    """One item."""

    data: T


class Count(BaseModel):
    count: int


class SearchResponse(BaseModel):
    """Search results response model."""

    results: list[Record] = Field(..., description="Search results")
    count: int = Field(..., description="Number of results returned")
    query: str = Field(..., description="Original search query")


class Membership(BaseModel):
    """A membership edge between a block and a country."""

    intblock_id: str
    country_code: str
    include_type: str | None = None
    status: str | None = Field(None, description="Open enum, e.g. member, observer, former_member")
    joined: str | None = None
    left: str | None = None


class Blocktype(BaseModel):
    id: str
    name: str | None = None
    other_names: list[dict[str, Any]] | None = None


class Currency(BaseModel):
    code: str
    name: str | None = None
    symbol: str | None = None


class CurrencyEntry(Currency):
    country_count: int


class Language(BaseModel):
    code: str
    name: str | None = None
    official: bool | None = None


class LanguageEntry(BaseModel):
    code: str
    name: str | None = None
    country_count: int


class TimezoneEntry(BaseModel):
    timezone: str
    country_count: int


class Timezone(TimezoneEntry):
    countries: list[str] = Field(..., description="Alpha-2 codes of the countries using it")


class Region(BaseModel):
    id: str
    value: str | None = None


class RegionEntry(Region):
    country_count: int
