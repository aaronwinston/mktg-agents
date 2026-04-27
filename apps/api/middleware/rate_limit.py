from __future__ import annotations

from typing import Optional

import jwt
from fastapi import Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import JSONResponse, Response

from config import settings


def _get_client_ip(request: Request) -> str:
    if settings.RATE_LIMIT_TRUST_X_FORWARDED_FOR:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            ip = xff.split(",")[0].strip()
            if ip:
                return ip

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def _get_bearer_token(request: Request) -> Optional[str]:
    token = request.cookies.get("auth_token")
    if token:
        return token

    authz = request.headers.get("authorization")
    if authz and authz.lower().startswith("bearer "):
        return authz.split(" ", 1)[1].strip()

    return None


def rate_limit_key(request: Request) -> str:
    """Rate limit key:

    - Authenticated: per-user key (JWT `sub`)
    - Unauthenticated: per-IP key

    This prevents brute-force and provides fair usage per authenticated user.
    """

    token = _get_bearer_token(request)
    if token:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_exp": False},
            )
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except Exception:
            # Fall back to IP-based limiting if the token can't be decoded.
            pass

    return f"ip:{_get_client_ip(request)}"


def global_rate_limit_key(_: Optional[Request] = None) -> str:
    return "global"


limiter = Limiter(
    key_func=rate_limit_key,
    default_limits=[settings.RATE_LIMIT_INTERNAL],
    headers_enabled=True,
    enabled=settings.RATE_LIMIT_ENABLED,
    storage_uri=settings.RATE_LIMIT_STORAGE_URI,
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    response = JSONResponse(
        {
            "detail": "Too Many Requests",
            "error": f"Rate limit exceeded: {exc.detail}",
        },
        status_code=429,
    )
    return request.app.state.limiter._inject_headers(response, request.state.view_rate_limit)


def setup_rate_limiting(app) -> None:
    """Wire slowapi into the FastAPI app."""

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
