from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.api.finance.schemas import YearPayload
from app.core import settings


def current_year() -> int:
    return datetime.now(UTC).year


def assert_year_allowed(year: int, is_premium: bool) -> None:
    """Raise 403 if a free user attempts to access a non-current year."""
    if not is_premium and year != current_year():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Multi-year access requires a premium subscription",
        )


def assert_ticker_limit(payload: YearPayload, is_premium: bool) -> None:
    """Raise 403 if a free user's payload exceeds the per-section ticker limit."""
    if is_premium:
        return
    limit = settings.FREE_TIER_LIMIT
    over_limit = len(payload.dividends) > limit or len(payload.yields) > limit
    if over_limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Free plan: max {limit} tickers or accounts per section",
        )
