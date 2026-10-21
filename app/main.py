"""FastAPI application main entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from internacia import InternaciaError

from app.caching import EXPOSED_HEADERS, DataVersionMiddleware, data_identity
from app.config import settings
from app.dependencies import create_client
from app.routers import (
    blocks,
    blocktypes,
    countries,
    currencies,
    health,
    languages,
    meta,
    regions,
    search,
    timezones,
)
from app.utils import handle_sdk_error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Open the database before serving; startup fails if it cannot be opened."""
    app.state.client = create_client()
    app.state.data_identity = data_identity(app.state.client.meta())
    yield


# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
    expose_headers=EXPOSED_HEADERS,
)

app.add_middleware(DataVersionMiddleware)

# Register routers
app.include_router(health.router)
app.include_router(meta.router)
app.include_router(countries.router)
app.include_router(blocks.router)
app.include_router(blocktypes.router)
app.include_router(search.router)
app.include_router(currencies.router)
app.include_router(languages.router)
app.include_router(regions.router)
app.include_router(timezones.router)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path),
        },
        headers=exc.headers,
    )


@app.exception_handler(InternaciaError)
async def sdk_exception_handler(request: Request, exc: InternaciaError):
    """SDK validation errors are 400, not-found 404, anything else a logged generic 500."""
    error = handle_sdk_error(exc, f"handling {request.url.path}")
    return await http_exception_handler(request, error)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
