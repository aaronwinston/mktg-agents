from __future__ import annotations

import json
import logging
import time
from typing import Callable, Optional

import jwt

from audit import clear_audit_context, set_audit_context
from config import settings


logger = logging.getLogger("forgeos.request")


def _get_header(scope, name: bytes) -> Optional[bytes]:
    for k, v in scope.get("headers", []):
        if k.lower() == name:
            return v
    return None


def _decode_auth(scope) -> tuple[Optional[str], Optional[str]]:
    """Best-effort extraction of user/org from cookie or Authorization header."""

    token = None

    cookie = _get_header(scope, b"cookie")
    if cookie:
        try:
            cookie_str = cookie.decode("latin-1")
            for part in cookie_str.split(";"):
                part = part.strip()
                if part.startswith("auth_token="):
                    token = part.split("=", 1)[1]
                    break
        except Exception:
            pass

    if not token:
        auth = _get_header(scope, b"authorization")
        if auth:
            try:
                auth_str = auth.decode("latin-1")
                if auth_str.startswith("Bearer "):
                    token = auth_str[7:]
            except Exception:
                pass

    if not token:
        return None, None

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub"), payload.get("org_id")
    except Exception:
        return None, None


class RequestLoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()

        method = scope.get("method")
        path = scope.get("path")

        content_length = _get_header(scope, b"content-length")
        req_size = int(content_length.decode("latin-1")) if content_length else 0

        user_id, org_id = _decode_auth(scope)
        set_audit_context(user_id=user_id, org_id=org_id, request_method=method, request_path=path)

        status_code = 500
        resp_size = 0

        async def send_wrapper(message):
            nonlocal status_code, resp_size
            if message["type"] == "http.response.start":
                status_code = message["status"]
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                if body:
                    resp_size += len(body)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            latency_ms = (time.perf_counter() - start) * 1000
            logger.info(
                json.dumps(
                    {
                        "method": method,
                        "path": path,
                        "status": status_code,
                        "latency_ms": round(latency_ms, 2),
                        "user_id": user_id,
                        "org_id": org_id,
                        "request_bytes": req_size,
                        "response_bytes": resp_size,
                    }
                )
            )
            clear_audit_context()
