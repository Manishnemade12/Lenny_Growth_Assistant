"""Structured JSON logging middleware for FastAPI.

Logs every incoming request and outgoing response with timing,
method, path, status code, and client information.
"""

import logging
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.api.access")


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs structured JSON for each HTTP request/response.

    Logs include request_id, method, path, status, latency, and client IP.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request and log structured details."""
        request_id = str(uuid4())[:8]
        start_time = time.perf_counter()

        # Attach request_id to request state for downstream use
        request.state.request_id = request_id

        response = await call_next(request)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            "HTTP %s %s → %s (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            latency_ms,
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "client_ip": request.client.host if request.client else "unknown",
            },
        )

        response.headers["X-Request-ID"] = request_id
        return response
