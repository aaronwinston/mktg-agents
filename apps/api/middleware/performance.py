"""Performance monitoring middleware for tracking endpoint latencies."""

import time
import logging
from typing import Callable
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from personal_mode import is_personal

logger = logging.getLogger(__name__)

# Thresholds for performance warnings
SLOW_ENDPOINT_THRESHOLD_MS = 500
VERY_SLOW_ENDPOINT_THRESHOLD_MS = 1000


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Logs endpoint response times to help identify performance bottlenecks.
    
    In personal mode, logs endpoints exceeding thresholds for debugging.
    In multi-tenant mode, logs all times for analytics.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip benchmark endpoint itself
        if request.url.path == "/api/__benchmark":
            return await call_next(request)

        start_time = time.time()

        try:
            response = await call_next(request)
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.warning(
                f"[PERF] {request.method} {request.url.path} errored after {elapsed_ms:.1f}ms: {e}"
            )
            raise

        elapsed_ms = (time.time() - start_time) * 1000

        # Log slow endpoints
        if is_personal():
            if elapsed_ms > VERY_SLOW_ENDPOINT_THRESHOLD_MS:
                logger.warning(
                    f"[PERF] VERY SLOW: {request.method} {request.url.path} took {elapsed_ms:.1f}ms"
                )
            elif elapsed_ms > SLOW_ENDPOINT_THRESHOLD_MS:
                logger.debug(
                    f"[PERF] SLOW: {request.method} {request.url.path} took {elapsed_ms:.1f}ms"
                )
        else:
            # In multi-tenant, just log at debug level
            logger.debug(
                f"[PERF] {request.method} {request.url.path} took {elapsed_ms:.1f}ms"
            )

        # Add timing header for debugging
        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.1f}"

        return response
