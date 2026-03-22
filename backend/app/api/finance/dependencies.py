from typing import Annotated

from backend.app.api.finance.repository import DBYieldRepository
from cachetools import TTLCache
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import verify_token
from app.api.finance.service import YieldService
from app.core import settings
from app.core.logging_config import logger
from app.db.models import User
from app.db.session import get_db

# ── dependency factories ──────────────────────────────────────────────────────

_PREMIUM_CACHE: TTLCache = TTLCache(maxsize=1024, ttl=300)


def _get_user_subscription(sub: str, db: Session) -> tuple[bool, str | None]:
    """Return (is_premium, subscription_plan) from the User row, 5-minute cache."""
    if sub in _PREMIUM_CACHE:
        return _PREMIUM_CACHE[sub]
    try:
        user = db.query(User).filter_by(sub=sub).first()
        result = (user.is_premium, user.subscription_plan) if user else (False, None)
    except Exception:
        logger.warning("premium_check_failed_fallback", user=sub)
        return (False, None)
    _PREMIUM_CACHE[sub] = result
    return result


def invalidate_premium_cache(sub: str) -> None:
    _PREMIUM_CACHE.pop(sub, None)


def get_auth_context(
    authorization: Annotated[str | None, Header()] = None,
    db: Annotated[Session, Depends(get_db)] = None,  # type: ignore[assignment]
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
    is_premium, subscription_plan = _get_user_subscription(ctx["sub"], db)
    ctx["is_premium"] = is_premium
    ctx["subscription_plan"] = subscription_plan
    return ctx


def get_repository(
    ctx: Annotated[dict, Depends(get_auth_context)],
    db: Annotated[Session, Depends(get_db)],
) -> DBYieldRepository:
    """Return a DBYieldRepository scoped to the requesting user.

    FastAPI caches ``get_db`` per request, so ``ctx`` and ``repo`` share
    the same session and commit/rollback together.
    """
    return DBYieldRepository(sub=ctx["sub"], email=ctx["email"], session=db)


def get_service(
    repo: Annotated[DBYieldRepository, Depends(get_repository)],
) -> YieldService:
    """Instantiate a YieldService backed by the injected repository."""
    return YieldService(repo)


AuthContextDep = Annotated[dict, Depends(get_auth_context)]
ServiceDep = Annotated[YieldService, Depends(get_service)]
