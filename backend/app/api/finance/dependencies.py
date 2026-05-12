from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

# ── dependency factories ──────────────────────────────────────────────────────
from sqlalchemy.orm import Session

from app.api.auth import verify_token
from app.api.finance.repository import YieldRepository
from app.api.finance.service import YieldService
from app.core import settings
from app.core.enums import AuthMode
from app.db.session import get_db


def get_auth_context(
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    """Verify the ID token and return context with email and sub.

    When ``AUTH_MODE=local`` the token is ignored and a fixed dev user is
    returned, so new contributors can `docker compose up` without setting up
    Cognito. Otherwise raises 503 if Cognito is not configured, 401 if the
    token is missing or invalid.
    """
    if settings.AUTH_MODE == AuthMode.LOCAL:
        return {"sub": settings.LOCAL_AUTH_SUB, "email": settings.LOCAL_AUTH_EMAIL}
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
    return ctx


def get_repository(
    ctx: Annotated[dict, Depends(get_auth_context)],
    db: Annotated[Session, Depends(get_db)],
) -> YieldRepository:
    """Return a YieldRepository scoped to the requesting user.

    FastAPI caches ``get_db`` per request, so ``ctx`` and ``repo`` share
    the same session and commit/rollback together.
    """
    return YieldRepository(sub=ctx["sub"], email=ctx["email"], session=db)


def get_service(
    repo: Annotated[YieldRepository, Depends(get_repository)],
) -> YieldService:
    """Instantiate a YieldService backed by the injected repository."""
    return YieldService(repo)


AuthContextDep = Annotated[dict, Depends(get_auth_context)]
ServiceDep = Annotated[YieldService, Depends(get_service)]
