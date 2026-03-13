import re
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.api.auth import verify_access_token
from app.api.finance.repository import YieldRepository
from app.api.finance.s3_repository import S3YieldRepository
from app.api.finance.service import YieldService
from app.core import settings
from app.core.utils import YieldRepositoryType

# ── dependency factories ──────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


def get_auth_context(
    authorization: Annotated[str | None, Header()] = None,
    x_user_email: Annotated[str | None, Header()] = None,
) -> dict:
    """Resolve ``{"email": str, "is_premium": bool}`` from the request.

    Production (COGNITO_REGION set): verify the ``Authorization: Bearer``
    token against Cognito via GetUser.

    Dev mode is only enabled when ``ALLOW_INSECURE_DEV_AUTH`` is true.
    In that mode, trust the ``X-User-Email`` header after format validation;
    ``is_premium`` is always ``False``.
    """
    if settings.COGNITO_REGION and not settings.ALLOW_INSECURE_DEV_AUTH:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header with Bearer token is required",
            )
        return verify_access_token(authorization.removeprefix("Bearer "))

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
    return {"email": x_user_email, "is_premium": False}


def get_repository(
    ctx: Annotated[dict, Depends(get_auth_context)],
) -> YieldRepositoryType:
    """Return the appropriate repository scoped to the requesting user."""
    user_email = ctx["email"]
    if settings.STORAGE_BACKEND == "s3":
        return S3YieldRepository(user_email=user_email)
    return YieldRepository(user_email=user_email)


def get_service(
    repo: Annotated[YieldRepositoryType, Depends(get_repository)],
) -> YieldService:
    """Instantiate a ``YieldService`` backed by the injected repository."""
    return YieldService(repo)


AuthContextDep = Annotated[dict, Depends(get_auth_context)]
ServiceDep = Annotated[YieldService, Depends(get_service)]
