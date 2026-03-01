from typing import Annotated, Any

from fastapi import APIRouter, Depends

from backend.app.repository import YieldRepository
from backend.app.service import YieldService

router = APIRouter(prefix="/api", tags=["data"])


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


# ── routes ────────────────────────────────────────────────────────────────────

@router.get(
    "/years",
    summary="List available years",
    description="Scans the data directory and returns a sorted list of years for which a `YYYY.json` file exists.",
)
def get_years(service: ServiceDep) -> list[int]:
    """Return all years that have a corresponding data file on disk."""
    return service.get_years()


@router.get(
    "/data/{year}",
    summary="Get year data",
    description="Reads and returns the dividend and yield data for the given year. Returns empty collections if no file exists yet.",
)
def get_data(year: int, service: ServiceDep) -> dict[str, Any]:
    """Load and return the JSON data for *year*, or an empty scaffold if the file is missing."""
    return service.get_data(year)


@router.put(
    "/data/{year}",
    summary="Save year data",
    description="Writes the provided dividend and yield payload to `YYYY.json`, creating the file if it does not exist.",
)
def put_data(year: int, payload: dict[str, Any], service: ServiceDep) -> dict[str, str]:
    """Persist *payload* as the data file for *year* and confirm success."""
    return service.save_data(year, payload)
