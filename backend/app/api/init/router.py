"""Single-shot init endpoint — returns all startup data in one request."""

import uuid
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.depots.schemas import DepotOut
from app.api.finance.dependencies import AuthContextDep
from app.api.finance.repository import YieldRepository
from app.api.users.schemas import MeResponse
from app.api.users.service import UserService
from app.core.limiter import limiter
from app.db.models import Depot, User
from app.db.session import get_db

router = APIRouter(prefix="/api", tags=["init"])

DBDep = Annotated[Session, Depends(get_db)]


class InitResponse(BaseModel):
    me: MeResponse
    settings: dict[str, Any]
    depots: list[DepotOut]
    years: list[int]
    year_data: dict[str, Any]
    current_year: int
    depot_id: uuid.UUID | None


@router.get(
    "/init",
    response_model=InitResponse,
    status_code=status.HTTP_200_OK,
    summary="Bootstrap app data",
    description=(
        "Returns all data needed to hydrate the frontend on login: "
        "user identity, settings, depots, available years, and current-year data. "
        "Replaces 5 sequential API calls with a single round trip."
    ),
)
@limiter.limit("30/minute")
def get_init(
    request: Request,
    ctx: AuthContextDep,
    db: DBDep,
    depot_id: uuid.UUID | None = Query(default=None),
    year: int | None = Query(default=None, ge=2000, le=2100),
) -> InitResponse:
    current_year = year or datetime.now(UTC).year

    # Build a repo — creates user+depot if this is a brand-new account.
    # If depot_id is stale (deleted), fall back to the default depot.
    active_depot_id = depot_id
    try:
        repo = YieldRepository(
            sub=ctx["sub"], email=ctx["email"], session=db, depot_id=active_depot_id
        )
        settings_data = repo.read_settings()
    except HTTPException:
        active_depot_id = None
        repo = YieldRepository(sub=ctx["sub"], email=ctx["email"], session=db)
        settings_data = repo.read_settings()

    # Depots list (user guaranteed to exist after read_settings above)
    user = db.query(User).filter_by(sub=ctx["sub"]).first()
    depots: list[Depot] = (
        db.query(Depot).filter_by(user_id=user.id).order_by(Depot.created_at).all()
        if user
        else []
    )

    # If no depot_id was given (or it was stale), pin to the first depot
    if active_depot_id is None and depots:
        active_depot_id = depots[0].id
        repo = YieldRepository(
            sub=ctx["sub"], email=ctx["email"], session=db, depot_id=active_depot_id
        )

    years = repo.list_years()

    # Clamp current_year to what actually exists
    if years and current_year not in years:
        current_year = max(years)

    year_data = repo.read_year(current_year)

    return InitResponse(
        me=UserService().get_me(
            ctx["email"], ctx["is_premium"], ctx["subscription_plan"]
        ),
        settings=settings_data,
        depots=depots,
        years=years,
        year_data=year_data,
        current_year=current_year,
        depot_id=active_depot_id,
    )
