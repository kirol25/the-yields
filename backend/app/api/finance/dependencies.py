from typing import Annotated

from fastapi import Depends

from app import settings
from app.api.finance.repository import YieldRepository
from app.api.finance.s3_repository import S3YieldRepository
from app.api.finance.service import YieldService
from app.utils import YieldRepositoryType

# ── dependency factories ──────────────────────────────────────────────────────


def get_repository() -> YieldRepositoryType:
    """Return the appropriate repository based on the STORAGE_BACKEND env var."""
    if settings.STORAGE_BACKEND == "s3":
        return S3YieldRepository()
    return YieldRepository()


def get_service(
    repo: Annotated[object, Depends(get_repository)],
) -> YieldService:
    """Instantiate a ``YieldService`` backed by the injected repository."""
    return YieldService(repo)


ServiceDep = Annotated[YieldService, Depends(get_service)]
