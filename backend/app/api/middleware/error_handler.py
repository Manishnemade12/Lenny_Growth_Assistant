"""Global exception handler for consistent structured error responses.

Catches all unhandled exceptions and returns a standardised JSON error body
matching the ErrorResponse schema defined in CONVENTIONS.md Rule 6.
"""

import logging
from datetime import datetime, timezone

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.api.errors")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all exception handler.

    Maps known exception types to appropriate HTTP status codes and error
    codes.  Unknown exceptions are treated as 500 INTERNAL_ERROR.

    Args:
        request: The incoming FastAPI request.
        exc: The unhandled exception.

    Returns:
        JSONResponse with structured error body.
    """
    error_mapping: dict[type, tuple[int, str, str]] = {
        ConnectionError: (503, "LLM_UNAVAILABLE", "LLM provider is unavailable"),
        TimeoutError: (504, "LLM_TIMEOUT", "LLM request timed out"),
        ValueError: (422, "VALIDATION_ERROR", str(exc)),
        PermissionError: (403, "FORBIDDEN", "Insufficient permissions"),
        FileNotFoundError: (404, "NOT_FOUND", "Resource not found"),
    }

    status_code, error_code, message = error_mapping.get(
        type(exc),
        (500, "INTERNAL_ERROR", "An unexpected error occurred"),
    )

    logger.error(
        "Unhandled exception: %s",
        type(exc).__name__,
        extra={
            "error_code": error_code,
            "path": request.url.path,
            "method": request.method,
            "detail": str(exc),
        },
        exc_info=True,
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "error": message,
            "code": error_code,
            "detail": str(exc) if status_code != 500 else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
