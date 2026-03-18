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
) -> dict:
    """Verify the ID token and return context with email, sub, and is_premium.

    Raises 503 if Cognito is not configured, 401 if the token is missing or invalid.
    """
    if not settings.COGNITO_USER_POOL_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured on this server",
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header with Bearer token is required",
        )
    ctx = verify_token(authorization.removeprefix("Bearer "))
    ctx["is_premium"] = _get_is_premium(ctx["sub"])
    return ctx


def get_repository(
    ctx: Annotated[dict, Depends(get_auth_context)],
) -> YieldRepositoryType:
    """Return the appropriate repository scoped to the requesting user."""
    if settings.ENVIRONMENT == Environment.PROD:
        return S3YieldRepository(user_key=ctx["sub"])
    return YieldRepository(user_email=ctx["email"])


def get_service(
    repo: Annotated[YieldRepositoryType, Depends(get_repository)],
) -> YieldService:
    """Instantiate a ``YieldService`` backed by the injected repository."""
    return YieldService(repo)


AuthContextDep = Annotated[dict, Depends(get_auth_context)]
ServiceDep = Annotated[YieldService, Depends(get_service)]
