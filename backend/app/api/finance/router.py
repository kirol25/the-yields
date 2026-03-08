from typing import Annotated, Any, Literal

from fastapi import APIRouter, Path, Request, status

from app import settings
from app.api.finance.dependencies import AuthContextDep, ServiceDep
from app.api.finance.schemas import SettingsPayload, YearPayload
from app.limiter import limiter

router = APIRouter(prefix="/api", tags=["finance"])

YearPath = Annotated[int, Path(ge=2000, le=2100, description="Four-digit year")]
KeyPath = Annotated[
    str,
    Path(
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z0-9 .&+_\-]+$",
        description="Ticker symbol or account name",
    ),
]

# ── routes ────────────────────────────────────────────────────────────────────


@router.get(
    "/years",
    responses={
        status.HTTP_200_OK: {"description": "Years retrieved successfully"},
    },
    status_code=status.HTTP_200_OK,
    summary="List available years",
    description="Returns a sorted list of years for which data exists."
    " Free users only receive the current year.",
)
def get_years(ctx: AuthContextDep, service: ServiceDep) -> list[int]:
    return service.get_years(ctx["is_premium"])


@router.get(
    "/data/{year}",
    responses={
        status.HTTP_200_OK: {"description": "Data retrieved successfully"},
        status.HTTP_403_FORBIDDEN: {"description": "Premium subscription required"},
        status.HTTP_404_NOT_FOUND: {"description": "Year not found"},
    },
    status_code=status.HTTP_200_OK,
    summary="Get year data",
    description="Returns dividend and yield data for the given year."
    " Free users may only access the current year.",
)
def get_data(
    year: YearPath, ctx: AuthContextDep, service: ServiceDep
) -> dict[str, Any]:
    return service.get_data(year, ctx["is_premium"])


@router.put(
    "/data/{year}",
    responses={
        status.HTTP_200_OK: {"description": "Data saved successfully"},
        status.HTTP_403_FORBIDDEN: {"description": "Premium subscription required"},
    },
    status_code=status.HTTP_200_OK,
    summary="Save year data",
    description="Writes the provided dividend and yield payload to `YYYY.json`."
    " Free users are restricted to the current year and up to"
    f" {settings.FREE_TIER_LIMIT} tickers/accounts per section.",
)
@limiter.limit("120/minute")
def put_data(
    request: Request,
    year: YearPath,
    payload: YearPayload,
    ctx: AuthContextDep,
    service: ServiceDep,
) -> dict[str, str]:
    return service.save_data(year, payload, ctx["is_premium"])


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
@limiter.limit("20/minute")
def put_settings(
    request: Request,
    payload: SettingsPayload,
    service: ServiceDep,
) -> dict[str, str]:
    return service.save_settings(payload.model_dump())


@router.delete(
    "/data",
    responses={
        status.HTTP_200_OK: {"description": "All user data deleted successfully"},
    },
    status_code=status.HTTP_200_OK,
    summary="Delete all user data",
    description="Permanently deletes all data files for the authenticated user.",
)
def delete_all_data(service: ServiceDep) -> dict[str, str]:
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
@limiter.limit("60/minute")
def delete_entry(
    request: Request,
    year: YearPath,
    section: Literal["dividends", "yields"],
    key: KeyPath,
    ctx: AuthContextDep,
    service: ServiceDep,
) -> dict[str, str]:
    return service.delete_entry(year, section, key, ctx["is_premium"])
