from typing import Annotated

from cachetools import TTLCache
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import verify_token
from app.api.finance.db_repository import DBYieldRepository
from app.api.finance.service import YieldService
from app.core import settings
from app.core.logging_config import logger
from app.db.models import User
from app.db.session import get_db

# ── dependency factories ──────────────────────────────────────────────────────

_PREMIUM_CACHE: TTLCache = TTLCache(maxsize=1024, ttl=300)


def _get_is_premium(sub: str, db: Session) -> bool:
    """Read is_premium from the User row, with a 5-minute in-process cache."""
    if sub in _PREMIUM_CACHE:
        return _PREMIUM_CACHE[sub]
    try:
        user = db.query(User).filter_by(sub=sub).first()
        is_premium = user.is_premium if user else False
    except Exception:
        logger.warning("premium_check_failed_fallback", user=sub)
        return False
    _PREMIUM_CACHE[sub] = is_premium
    return is_premium


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
    ctx["is_premium"] = _get_is_premium(ctx["sub"], db)
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
