from typing import Annotated

from fastapi import Depends

from app.api.finance.repository import YieldRepository
from app.api.finance.service import YieldService

# ── dependency factories ──────────────────────────────────────────────────────


def get_repository() -> YieldRepository:
    """Instantiate a ``YieldRepository`` for the current request."""
    return YieldRepository()


def get_service(
    repo: Annotated[YieldRepository, Depends(get_repository)],
) -> YieldService:
    """Instantiate a ``YieldService`` backed by the injected repository."""
    return YieldService(repo)


ServiceDep = Annotated[YieldService, Depends(get_service)]
