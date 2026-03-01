import json
import re
from pathlib import Path
from typing import Any

from backend.app.utils import DATA_DIR


class YieldRepository:
    """Handles all file-system access for year-based JSON data files."""

    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        """Initialise the repository with the path to the data directory.

        Args:
            data_dir: Directory where ``YYYY.json`` files are stored.
                      Defaults to the project-level ``data/`` folder.
        """
        self.data_dir = data_dir

    # ── private ──────────────────────────────────────────────────────────────

    def _ensure_dir(self) -> None:
        """Create the data directory if it does not already exist."""
        self.data_dir.mkdir(exist_ok=True)

    # ── public ───────────────────────────────────────────────────────────────

    def list_years(self) -> list[int]:
        """Return a sorted list of years that have a corresponding data file.

        Returns:
            Sorted list of integer years found in the data directory.
        """
        self._ensure_dir()
        return sorted(
            int(p.stem)
            for p in self.data_dir.glob("*.json")
            if re.fullmatch(r"\d{4}", p.stem)
        )

    def read_year(self, year: int) -> dict[str, Any]:
        """Read and return the data for the given year.

        Args:
            year: The four-digit year to read.

        Returns:
            Parsed JSON content, or an empty scaffold if the file is missing.
        """
        self._ensure_dir()
        path = self.data_dir / f"{year}.json"
        if not path.exists():
            return {"dividends": {}, "yields": {}}
        with open(path) as f:
            return json.load(f)  # type: ignore[no-any-return]

    def write_year(self, year: int, data: dict[str, Any]) -> None:
        """Persist data for the given year, creating the file if needed.

        Args:
            year: The four-digit year to write.
            data: The full dividend/yield payload to serialise.
        """
        self._ensure_dir()
        path = self.data_dir / f"{year}.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
