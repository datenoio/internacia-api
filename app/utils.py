"""Utility functions for SDK integration."""

from typing import Any

from fastapi import HTTPException

from app.dependencies import StubClient


def convert_numpy_to_python(obj: Any) -> Any:
    """
    Recursively convert numpy arrays and other numpy types to Python native types.

    This function handles the case where DuckDB/pandas returns numpy arrays
    that FastAPI cannot serialize.

    Args:
        obj: Object that may contain numpy arrays

    Returns:
        Object with numpy arrays converted to Python lists
    """
    try:
        import numpy as np

        # Convert numpy arrays to lists
        if isinstance(obj, np.ndarray):
            return obj.tolist()

        # Convert numpy scalars to Python types
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()

        # Convert numpy bool to Python bool
        if isinstance(obj, np.bool_):
            return bool(obj)

    except ImportError:
        # numpy not available, skip conversion
        pass

    # Recursively process dictionaries
    if isinstance(obj, dict):
        return {key: convert_numpy_to_python(value) for key, value in obj.items()}

    # Recursively process lists
    if isinstance(obj, list):
        return [convert_numpy_to_python(item) for item in obj]

    # Return as-is for other types
    return obj


def handle_sdk_error(e: Exception, operation: str) -> HTTPException:
    """
    Convert SDK exceptions to HTTP exceptions.

    Args:
        e: Exception from SDK
        operation: Description of the operation that failed

    Returns:
        HTTPException with appropriate status code
    """
    if isinstance(e, HTTPException):
        raise e

    # Check for SDK-specific exceptions
    error_type = type(e).__name__

    # Map SDK exceptions to HTTP status codes
    if "ValidationError" in error_type or "ValueError" in error_type:
        status_code = 400
    elif "NotFoundError" in error_type or "FileNotFoundError" in error_type:
        status_code = 404
    elif "DatabaseError" in error_type:
        status_code = 500
    else:
        status_code = 500

    return HTTPException(
        status_code=status_code,
        detail=f"Error {operation}: {str(e)}"
    )


def check_stub_client(client: Any) -> None:
    """
    Check if client is a stub and raise appropriate error.

    Args:
        client: Client instance to check

    Raises:
        HTTPException: If client is a stub (SDK not available)
    """
    if isinstance(client, StubClient):
        raise HTTPException(
            status_code=501,
            detail="SDK not available"
        )
