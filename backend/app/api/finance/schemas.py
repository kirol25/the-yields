from pydantic import BaseModel, ConfigDict, Field


class DividendEntry(BaseModel):
    name: str = Field(
        description="Display name of the dividend instrument",
        max_length=200,
    )
    months: dict[str, float] = Field(
        description="Monthly amounts keyed by zero-padded month number (e.g. '01')"
    )


class YieldEntry(BaseModel):
    months: dict[str, float] = Field(
        description="Monthly amounts keyed by zero-padded month number (e.g. '01')"
    )


class YearPayload(BaseModel):
    """Validated body for PUT /api/data/{year}."""

    model_config = ConfigDict(extra="forbid")

    dividends: dict[str, DividendEntry] = Field(
        default={},
        description="Dividend entries keyed by ticker symbol (e.g. 'AAPL')",
    )
    yields: dict[str, YieldEntry] = Field(
        default={},
        description="Yield entries keyed by account name (e.g. 'TradeRepublic')",
    )


class SettingsPayload(BaseModel):
    """Validated body for PUT /api/settings."""

    model_config = ConfigDict(extra="ignore")

    dividendGoal: dict[str, float] = Field(
        default={},
        description="Annual dividend income goals keyed by year (e.g. {'2024': 1200.0})",  # noqa: E501
    )
    yieldGoal: dict[str, float] = Field(
        default={},
        description="Annual yield income goals keyed by year (e.g. {'2024': 500.0})",
    )
    steuerfreibetrag: dict[str, float] = Field(
        default={},
        description="Tax-free allowance per year keyed by year (e.g. {'2024': 801.0})",
    )
