from pydantic import BaseModel


class TickerOut(BaseModel):
    symbol: str
    name: str
    sector: str | None
    exchange: str | None
    currency: str | None

    model_config = {"from_attributes": True}
