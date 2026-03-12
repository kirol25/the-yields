from typing import Any, Literal

from fastapi import HTTPException, status

from app.api.finance.schemas import YearPayload
from app.api.finance.utils import assert_ticker_limit, assert_year_allowed, current_year
from app.core.utils import YieldRepositoryType


class YieldService:
    """Business logic layer between the HTTP router and the data repository."""

    def __init__(self, repository: YieldRepositoryType) -> None:
        self.repository = repository

    def get_years(self, is_premium: bool) -> list[int]:
        """Return available years, filtered to the current year for free users."""
        years = self.repository.list_years()
        if not is_premium:
            years = [y for y in years if y == current_year()]
        return years

    def get_data(self, year: int, is_premium: bool) -> dict[str, Any]:
        """Retrieve dividend and yield data for *year*.

        Raises 403 if a free user requests a non-current year.
        """
        assert_year_allowed(year, is_premium)
        return self.repository.read_year(year)

    def save_data(
        self, year: int, payload: YearPayload, is_premium: bool
    ) -> dict[str, str]:
        """Persist dividend and yield data for *year*.

        Raises 403 if a free user exceeds the tier limits.
        """
        assert_year_allowed(year, is_premium)
        assert_ticker_limit(payload, is_premium)
        self.repository.write_year(year, payload.model_dump())
        return {"status": "ok"}

    def delete_all_data(self) -> dict[str, str]:
        """Permanently delete all data for the current user."""
        self.repository.delete_all_data()
        return {"status": "ok"}

    def get_settings(self) -> dict[str, Any]:
        """Retrieve user settings (goals, steuerfreibetrag)."""
        return self.repository.read_settings()

    def save_settings(self, payload: dict[str, Any]) -> dict[str, str]:
        """Persist user settings."""
        self.repository.write_settings(payload)
        return {"status": "ok"}

    def delete_entry(
        self,
        year: int,
        section: Literal["dividends", "yields"],
        key: str,
        is_premium: bool,
    ) -> dict[str, str]:
        """Delete *key* from *section* in *year*.

        Raises 403 if a free user requests a non-current year.
        Raises 404 if the entry does not exist.
        """
        assert_year_allowed(year, is_premium)
        if not self.repository.delete_entry(year, section, key):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entry '{key}' not found in {section} for {year}",
            )
        return {"status": "ok"}
