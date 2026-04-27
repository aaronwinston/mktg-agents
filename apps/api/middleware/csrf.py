"""
CSRF Protection Middleware for FastAPI
Validates CSRF tokens on state-changing requests (POST, PUT, DELETE, PATCH)
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

CSRF_HEADER_NAME = "X-CSRF-Token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate CSRF tokens on state-changing requests.
    Tokens should be sent in the X-CSRF-Token header for POST/PUT/DELETE/PATCH requests.
    """

    def __init__(self, app, exempt_paths: list = None):
        super().__init__(app)
        # Paths that don't require CSRF protection (e.g., login, public APIs)
        self.exempt_paths = exempt_paths or [
            "/api/auth/signin",
            "/api/auth/signup",
            "/api/auth/signout",
            "/api/health",
        ]

    async def dispatch(self, request: Request, call_next):
        # Skip CSRF check for safe methods
        if request.method in SAFE_METHODS:
            return await call_next(request)

        # Skip CSRF check for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)

        # For state-changing requests, validate CSRF token
        csrf_token = request.headers.get(CSRF_HEADER_NAME)

        if not csrf_token:
            logger.warning(
                f"Missing CSRF token for {request.method} {request.url.path} from {request.client}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Missing CSRF token",
            )

        # Token validation: in production, compare with server-stored token
        # For now, we just verify it exists and is not empty
        if not csrf_token.strip() or len(csrf_token) < 32:
            logger.warning(
                f"Invalid CSRF token for {request.method} {request.url.path} from {request.client}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid CSRF token",
            )

        logger.debug(
            f"CSRF token validated for {request.method} {request.url.path}"
        )

        return await call_next(request)


def validate_csrf_token(request: Request) -> bool:
    """
    Dependency function to validate CSRF tokens on specific endpoints
    Can be used as: auth: AuthContext = Depends(validate_csrf_token)
    """
    if request.method in SAFE_METHODS:
        return True

    csrf_token = request.headers.get(CSRF_HEADER_NAME)

    if not csrf_token or not csrf_token.strip() or len(csrf_token) < 32:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token",
        )

    return True
