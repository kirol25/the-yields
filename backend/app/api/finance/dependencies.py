import re
from typing import Annotated

from cachetools import TTLCache
from fastapi import Depends, Header, HTTPException, status

from app.api.auth import verify_token
from app.api.finance.repository import YieldRepository
from app.api.finance.s3_repository import S3YieldRepository
from app.api.finance.service import YieldService
from app.core import settings
from app.core.config import Environment
from app.core.utils import YieldRepositoryType

# ── dependency factories ──────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

_PREMIUM_CACHE: TTLCache = TTLCache(maxsize=1024, ttl=300)


def _get_is_premium(sub: str) -> bool:
    """Read is_premium from the user's settings.json in S3, with a 5-min cache."""
    if sub in _PREMIUM_CACHE:
        return _PREMIUM_CACHE[sub]
    repo = S3YieldRepository(user_key=sub)
    is_premium = repo.read_settings().get("is_premium", False)
    _PREMIUM_CACHE[sub] = is_premium
    return is_premium


def invalidate_premium_cache(sub: str) -> None:
    _PREMIUM_CACHE.pop(sub, None)


def get_auth_context(
    authorization: Annotated[str | None, Header()] = None,
    x_user_email: Annotated[str | None, Header()] = None,
) -> dict:
    """Resolve ``{"email": str, "sub": str, "is_premium": bool}`` from the request.

    Production: verify the ID token, then read is_premium from settings.json.
    Dev mode (ALLOW_INSECURE_DEV_AUTH): trust X-User-Email, is_premium always False.
    """
    if settings.COGNITO_USER_POOL_ID and not settings.ALLOW_INSECURE_DEV_AUTH:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header with Bearer token is required",
            )
        ctx = verify_token(authorization.removeprefix("Bearer "))
        ctx["is_premium"] = _get_is_premium(ctx["sub"])
        return ctx

    if not settings.ALLOW_INSECURE_DEV_AUTH:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured on this server",
        )

    # Explicit dev mode — trust X-User-Email
    if not x_user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Email header is required",
        )
    if not _EMAIL_RE.match(x_user_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-User-Email header value",
        )
    return {"email": x_user_email, "sub": "", "is_premium": False}


def get_repository(
    ctx: Annotated[dict, Depends(get_auth_context)],
) -> YieldRepositoryType:
    """Return the appropriate repository scoped to the requesting user."""
    user_key = ctx.get("sub") or ctx["email"]

    if settings.ENVIRONMENT == Environment.PROD:
        return S3YieldRepository(user_key=user_key)
    return YieldRepository(user_email=ctx["email"])


def get_service(
    repo: Annotated[YieldRepositoryType, Depends(get_repository)],
) -> YieldService:
    """Instantiate a ``YieldService`` backed by the injected repository."""
    return YieldService(repo)


AuthContextDep = Annotated[dict, Depends(get_auth_context)]
ServiceDep = Annotated[YieldService, Depends(get_service)]
