from typing import Any, Literal

from fastapi import APIRouter, status

from app.api.finance.dependencies import ServiceDep

router = APIRouter(prefix="/api", tags=["finance"])


# ── routes ────────────────────────────────────────────────────────────────────


@router.get(
    "/years",
    responses={
        status.HTTP_200_OK: {"description": "Years retrieved successfully"},
    },
    status_code=status.HTTP_200_OK,
    summary="List available years",
    description="Scans the data directory and returns a sorted list of years for which"
    " a `YYYY.json` file exists.",
)
def get_years(service: ServiceDep) -> list[int]:
    """Return all years that have a corresponding data file on disk."""
    return service.get_years()


@router.get(
    "/data/{year}",
    responses={
        status.HTTP_200_OK: {"description": "Data retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Year not found"},
    },
    status_code=status.HTTP_200_OK,
    summary="Get year data",
    description="Reads and returns the dividend and yield data for the given year."
    " Returns empty collections if no file exists yet.",
)
def get_data(year: int, service: ServiceDep) -> dict[str, Any]:
    """Load and return the JSON data for *year* or an empty scaffold
    if the file is missing."""
    return service.get_data(year)


@router.put(
    "/data/{year}",
    responses={
        status.HTTP_200_OK: {"description": "Data saved successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Year not found"},
    },
    status_code=status.HTTP_200_OK,
    summary="Save year data",
    description="Writes the provided dividend and yield payload to `YYYY.json`,"
    "creating the file if it does not exist.",
)
def put_data(year: int, payload: dict[str, Any], service: ServiceDep) -> dict[str, str]:
    """Persist *payload* as the data file for *year* and confirm success."""
    return service.save_data(year, payload)


@router.delete(
    "/data",
    responses={
        status.HTTP_200_OK: {"description": "All user data deleted successfully"},
    },
    status_code=status.HTTP_200_OK,
    summary="Delete all user data",
    description="Permanently deletes all data files for the authenticated user."
    " Called as part of the account deletion flow.",
)
def delete_all_data(service: ServiceDep) -> dict[str, str]:
    """Permanently delete all data for the authenticated user."""
    return service.delete_all_data()


@router.delete(
    "/data/{year}/{section}/{key}",
    responses={
        status.HTTP_202_ACCEPTED: {"description": "Entry deleted successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Entry not found"},
    },
    status_code=status.HTTP_202_ACCEPTED,
    summary="Delete an entry",
    description="Removes a single dividend or yield entry from the given year's data file.",  # noqa: E501
)
def delete_entry(
    year: int,
    section: Literal["dividends", "yields"],
    key: str,
    service: ServiceDep,
) -> dict[str, str]:
    """Delete *key* from *section* in the data file for *year*."""
    return service.delete_entry(year, section, key)
