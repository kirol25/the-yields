from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app import settings
from app.api.finance.repository import YieldRepository
from app.api.finance.s3_repository import S3YieldRepository
from app.api.finance.service import YieldService
from app.utils import YieldRepositoryType

# ── dependency factories ──────────────────────────────────────────────────────


def get_user_email(x_user_email: Annotated[str | None, Header()] = None) -> str:
    """Extract the user email from the X-User-Email request header."""
    if not x_user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Email header is required",
        )
    return x_user_email


def get_repository(
    user_email: Annotated[str, Depends(get_user_email)],
) -> YieldRepositoryType:
    """Return the appropriate repository scoped to the requesting user."""
    if settings.STORAGE_BACKEND == "s3":
        return S3YieldRepository(user_email=user_email)
    return YieldRepository(user_email=user_email)


def get_service(
    repo: Annotated[object, Depends(get_repository)],
) -> YieldService:
    """Instantiate a ``YieldService`` backed by the injected repository."""
    return YieldService(repo)


ServiceDep = Annotated[YieldService, Depends(get_service)]
