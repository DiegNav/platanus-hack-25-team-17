"""Global error handling middleware."""

import traceback
from collections.abc import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


async def error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """Handle all unhandled exceptions globally.

    Args:
        request: FastAPI request object
        call_next: Next middleware or route handler

    Returns:
        Response: JSON response with error details
    """
    try:
        return await call_next(request)
    except ValueError as exc:
        logger.warning(f"Validation error: {exc!s}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc), "error": "validation_error"},
        )
    except Exception as exc:
        logger.error(f"Unhandled exception: {exc!s}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "error": "internal_error",
            },
        )
