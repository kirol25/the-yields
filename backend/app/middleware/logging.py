import time

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging_config import logger

_HEALTH_PATH = "/monitoring/health"


def _extract_user(request: Request) -> str:
    """Best-effort extraction of user email from the request for log context."""
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        try:
            claims = jwt.decode(
                auth.removeprefix("Bearer "),
                options={"verify_signature": False},
                algorithms=["RS256"],
            )
            email = claims.get("username") or claims.get("cognito:username", "")
            if email:
                return email
        except Exception:
            pass
    return request.headers.get("x-user-email", "anonymous")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with method, path, status, duration, and user."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip health checks to avoid log noise
        if request.url.path == _HEALTH_PATH:
            return await call_next(request)

        start = time.perf_counter()
        user = _extract_user(request)

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        status_code = response.status_code

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
