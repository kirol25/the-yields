from datetime import UTC, datetime


def current_year() -> int:
    return datetime.now(UTC).year
