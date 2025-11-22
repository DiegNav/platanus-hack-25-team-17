"""Logging middleware for request/response tracking."""

import time
from collections.abc import Callable

from fastapi import Request, Response

from app.core.logging import get_logger

logger = get_logger(__name__)


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """Log all incoming requests and outgoing responses.

    Args:
        request: FastAPI request object
        call_next: Next middleware or route handler

    Returns:
        Response: Response from the route handler
    """
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Duration: {process_time:.3f}s"
    )

    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)

    return response
