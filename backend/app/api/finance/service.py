from typing import Any, Literal

from fastapi import HTTPException, status

from app.api.finance.repository import YieldRepository
from app.api.finance.schemas import YearPayload
from app.core.logging_config import logger


class YieldService:
    """Business logic layer between the HTTP router and the data repository."""

    def __init__(self, repository: YieldRepository) -> None:
        self.repository = repository

    def get_years(self) -> list[int]:
        """Return all available years."""
        return self.repository.list_years()

    def get_data(self, year: int) -> dict[str, Any]:
        """Retrieve dividend and yield data for *year*."""
        return self.repository.read_year(year)

    def save_data(self, year: int, payload: YearPayload) -> dict[str, str]:
        """Persist dividend and yield data for *year*."""
        self.repository.write_year(year, payload.model_dump())
        logger.info(
            "data_saved",
            year=year,
            dividends=len(payload.dividends),
            yields=len(payload.yields),
        )
        return {"status": "ok"}

    def delete_all_data(self) -> dict[str, str]:
        """Permanently delete all data for the current user."""
        self.repository.delete_all_data()
        logger.info("all_data_deleted")
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
    ) -> dict[str, str]:
        """Delete *key* from *section* in *year*.

        Raises 404 if the entry does not exist.
        """
        if not self.repository.delete_entry(year, section, key):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entry '{key}' not found in {section} for {year}",
            )
        logger.info("entry_deleted", year=year, section=section, key=key)
        return {"status": "ok"}
