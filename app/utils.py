"""Utility functions for SDK integration."""

import logging

from fastapi import HTTPException
from internacia import NotFoundError
from internacia import ValidationError as SDKValidationError

logger = logging.getLogger(__name__)


def handle_sdk_error(e: Exception, operation: str) -> HTTPException:
    """
    Convert an SDK exception to an HTTP exception.

    Input validation errors become 400 and not-found errors 404, with the SDK message.
    Everything else is logged and becomes a generic 500 so that internal details such
    as SQL text never reach the client.

    Args:
        e: Exception from SDK
        operation: Description of the operation that failed

    Returns:
        HTTPException with appropriate status code
    """
    if isinstance(e, HTTPException):
        return e
    if isinstance(e, SDKValidationError):
        return HTTPException(status_code=400, detail=str(e))
    if isinstance(e, NotFoundError):
        return HTTPException(status_code=404, detail=str(e))

    logger.error("Error %s", operation, exc_info=e)
    return HTTPException(status_code=500, detail=f"Internal server error while {operation}")
