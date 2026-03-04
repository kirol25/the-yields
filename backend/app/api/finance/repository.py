import json
import re
import shutil
from pathlib import Path
from typing import Any

PROJECT_ROOT: Path = Path(__file__).resolve().parents[4]
DATA_DIR: Path = PROJECT_ROOT / "data"


class YieldRepository:
    """Handles all file-system access for year-based JSON data files."""

    def __init__(self, user_email: str, data_dir: Path = DATA_DIR) -> None:
        """Initialise the repository scoped to a specific user.

        Args:
            user_email: The authenticated user's email address, used as the
                        subdirectory under ``data_dir``.
            data_dir: Root data directory. Defaults to the project-level
                      ``data/`` folder.
        """
        self.data_dir = data_dir / user_email

    # ── private ──────────────────────────────────────────────────────────────

    def _ensure_dir(self) -> None:
        """Create the user data directory if it does not already exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    # ── public ───────────────────────────────────────────────────────────────

    def list_years(self) -> list[int]:
        """Return a sorted list of years that have a corresponding data file.

        Returns:
            Sorted list of integer years found in the user's data directory.
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

    def delete_entry(self, year: int, section: str, key: str) -> bool:
        """Remove a single entry from a section of the given year's data.

        Args:
            year: The four-digit year to modify.
            section: Either ``"dividends"`` or ``"yields"``.
            key: The ticker symbol or account name to remove.

        Returns:
            ``True`` if the entry was found and removed, ``False`` otherwise.
        """
        data = self.read_year(year)
        if key not in data.get(section, {}):
            return False
        del data[section][key]
        self.write_year(year, data)
        return True

    def delete_all_data(self) -> None:
        """Delete the entire user data directory and all its contents.

        This is a destructive, irreversible operation used when a user
        permanently deletes their account.
        """
        if self.data_dir.exists():
            shutil.rmtree(self.data_dir)

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
