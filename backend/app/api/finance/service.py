from typing import Any

from app.api.finance.repository import YieldRepository


class YieldService:
    """Business logic layer between the HTTP router and the data repository."""

    def __init__(self, repository: YieldRepository) -> None:
        """Initialise the service with a repository instance.

        Args:
            repository: The repository responsible for reading and writing data.
        """
        self.repository = repository

    def get_years(self) -> list[int]:
        """Return all years for which data is available.

        Returns:
            Sorted list of integer years.
        """
        return self.repository.list_years()

    def get_data(self, year: int) -> dict[str, Any]:
        """Retrieve dividend and yield data for the given year.

        Args:
            year: The four-digit year to retrieve.

        Returns:
            Parsed year data, or an empty scaffold if nothing is recorded yet.
        """
        return self.repository.read_year(year)

    def save_data(self, year: int, payload: dict[str, Any]) -> dict[str, str]:
        """Persist dividend and yield data for the given year.

        Args:
            year: The four-digit year to save.
            payload: The full dividend/yield mapping to write.

        Returns:
            A status confirmation dict.
        """
        self.repository.write_year(year, payload)
        return {"status": "ok"}
