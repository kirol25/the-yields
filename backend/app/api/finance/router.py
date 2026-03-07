from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, status

from app.api.finance.dependencies import AuthContextDep, ServiceDep

router = APIRouter(prefix="/api", tags=["finance"])

FREE_TIER_LIMIT = 5  # max tickers/accounts per section for free users


def _current_year() -> int:
    return datetime.now(UTC).year


def _assert_year_allowed(year: int, is_premium: bool) -> None:
    """Raise 403 if a free user attempts to access a non-current year."""
    if not is_premium and year != _current_year():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Multi-year access requires a premium subscription",
        )


def _assert_ticker_limit(payload: dict[str, Any], is_premium: bool) -> None:
    """Raise 403 if a free user's payload exceeds the per-section ticker limit."""
    if is_premium:
        return
    dividends = payload.get("dividends", {})
    yields = payload.get("yields", {})
    if len(dividends) > FREE_TIER_LIMIT or len(yields) > FREE_TIER_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Free plan: max {FREE_TIER_LIMIT} tickers or accounts per section",
        )


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
def get_years(ctx: AuthContextDep, service: ServiceDep) -> list[int]:
    """Return all years that have a corresponding data file on disk.

    Free users only receive the current year even if past files exist.
    """
    years = service.get_years()
    if not ctx["is_premium"]:
        current = _current_year()
        years = [y for y in years if y == current]
    return years


@router.get(
    "/data/{year}",
    responses={
        status.HTTP_200_OK: {"description": "Data retrieved successfully"},
        status.HTTP_403_FORBIDDEN: {"description": "Premium subscription required"},
        status.HTTP_404_NOT_FOUND: {"description": "Year not found"},
    },
    status_code=status.HTTP_200_OK,
    summary="Get year data",
    description="Reads and returns the dividend and yield data for the given year."
    " Returns empty collections if no file exists yet."
    " Free users may only access the current year.",
)
def get_data(year: int, ctx: AuthContextDep, service: ServiceDep) -> dict[str, Any]:
    """Load and return the JSON data for *year* or an empty scaffold if the file
    is missing. Free users are restricted to the current year."""
    _assert_year_allowed(year, ctx["is_premium"])
    return service.get_data(year)


@router.put(
    "/data/{year}",
    responses={
        status.HTTP_200_OK: {"description": "Data saved successfully"},
        status.HTTP_403_FORBIDDEN: {"description": "Premium subscription required"},
        status.HTTP_404_NOT_FOUND: {"description": "Year not found"},
    },
    status_code=status.HTTP_200_OK,
    summary="Save year data",
    description="Writes the provided dividend and yield payload to `YYYY.json`,"
    " creating the file if it does not exist."
    " Free users are restricted to the current year and up to"
    f" {FREE_TIER_LIMIT} tickers/accounts per section.",
)
def put_data(
    year: int,
    payload: dict[str, Any],
    ctx: AuthContextDep,
    service: ServiceDep,
) -> dict[str, str]:
    """Persist *payload* as the data file for *year* and confirm success."""
    _assert_year_allowed(year, ctx["is_premium"])
    _assert_ticker_limit(payload, ctx["is_premium"])
    return service.save_data(year, payload)


@router.get(
    "/settings",
    status_code=status.HTTP_200_OK,
    summary="Get user settings",
    description="Returns the user's saved goals and steuerfreibetrag.",
)
def get_settings(service: ServiceDep) -> dict[str, Any]:
    return service.get_settings()


@router.put(
    "/settings",
    status_code=status.HTTP_200_OK,
    summary="Save user settings",
    description="Persists the user's goals and steuerfreibetrag.",
)
def put_settings(payload: dict[str, Any], service: ServiceDep) -> dict[str, str]:
    return service.save_settings(payload)


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
        status.HTTP_403_FORBIDDEN: {"description": "Premium subscription required"},
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
    ctx: AuthContextDep,
    service: ServiceDep,
) -> dict[str, str]:
    """Delete *key* from *section* in the data file for *year*."""
    _assert_year_allowed(year, ctx["is_premium"])
    return service.delete_entry(year, section, key)
