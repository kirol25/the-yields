from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.tickers.schemas import TickerOut
from app.db.models import Ticker
from app.db.session import get_db

router = APIRouter(prefix="/api/tickers", tags=["tickers"])


@router.get(
    "",
    response_model=list[TickerOut],
    responses={status.HTTP_200_OK: {"description": "List of known tickers"}},
    summary="List all known tickers",
    description="Returns the reference list of known stock/ETF symbols. "
    "No authentication required.",
)
def list_tickers(db: Annotated[Session, Depends(get_db)]) -> list[Ticker]:
    """Returns the reference list of known stock/ETF symbols."""
    return db.query(Ticker).order_by(Ticker.symbol).all()
