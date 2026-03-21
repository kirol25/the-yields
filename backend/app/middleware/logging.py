import asyncio
import time

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging_config import logger

_HEALTH_PATH = "/monitoring/health"


def _extract_user(request: Request) -> str:
    """Best-effort extraction of user sub from the ID token for log context."""
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        try:
            claims = jwt.decode(
                auth.removeprefix("Bearer "),
                options={"verify_signature": False},
                algorithms=["RS256"],
            )
            sub = claims.get("sub", "")
            if sub:
                return sub
        except Exception:
            pass
    return "anonymous"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with method, path, status, duration, and user."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip health checks to avoid log noise
        if request.url.path == _HEALTH_PATH:
            return await call_next(request)

        start = time.perf_counter()
        user = _extract_user(request)
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
        except asyncio.CancelledError:
            # Server is shutting down while this request was in-flight;
            # re-raise immediately so the event loop can clean up.
            raise
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            log = logger.bind(
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=duration_ms,
                user=user,
            )
            if status_code >= 500:
                log.error("request_error")
            elif status_code >= 400:
                log.warning("request_warning")
            else:
                log.info("request")

        return response
