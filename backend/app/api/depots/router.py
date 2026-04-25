"""Depot management + depot-scoped finance routes.

Depot CRUD:
  GET    /api/depots               - list user's depots
  POST   /api/depots               - create depot
  PATCH  /api/depots/{depot_id}    - rename depot
  DELETE /api/depots/{depot_id}    - delete depot (not allowed if it's the only one)

Finance sub-routes (scoped to a specific depot):
  GET    /api/depots/{depot_id}/years
  GET    /api/depots/{depot_id}/data/{year}
  PUT    /api/depots/{depot_id}/data/{year}
  DELETE /api/depots/{depot_id}/data/{year}/{section}/{key}
"""

import uuid
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from sqlalchemy.orm import Session

from app.api.depots.schemas import CreateDepotRequest, DepotOut, RenameDepotRequest
from app.api.finance.dependencies import AuthContextDep
from app.api.finance.repository import YieldRepository
from app.api.finance.schemas import YearPayload
from app.api.finance.service import YieldService
from app.core.limiter import limiter
from app.db.models import Depot, User
from app.db.session import get_db

router = APIRouter(prefix="/api/depots", tags=["depots"])

DBDep = Annotated[Session, Depends(get_db)]

YearPath = Annotated[int, Path(ge=2000, le=2100, description="Four-digit year")]
KeyPath = Annotated[
    str,
    Path(
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z0-9 .&+_\-]+$",
        description="Ticker symbol or account name",
    ),
]


def _get_or_create_user(ctx: dict, db: Session) -> User:
    user = db.query(User).filter_by(sub=ctx["sub"]).first()
    if not user:
        user = User(sub=ctx["sub"], email=ctx["email"])
        db.add(user)
        db.flush()
    return user


def _get_depot_or_404(depot_id: uuid.UUID, user: User, db: Session) -> Depot:
    depot = db.query(Depot).filter_by(id=depot_id, user_id=user.id).first()
    if not depot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Depot not found"
        )
    return depot


def _make_service(depot_id: uuid.UUID, ctx: dict, db: Session) -> YieldService:
    repo = YieldRepository(
        sub=ctx["sub"], email=ctx["email"], session=db, depot_id=depot_id
    )
    return YieldService(repo)


# ── Depot CRUD ─────────────────────────────────────────────────────────────────


@router.get(
    "",
    response_model=list[DepotOut],
    status_code=status.HTTP_200_OK,
    summary="List depots",
    description="Returns all depots owned by the authenticated user.",
)
def list_depots(ctx: AuthContextDep, db: DBDep) -> list[Depot]:
    user = db.query(User).filter_by(sub=ctx["sub"]).first()
    if not user:
        return []
    return db.query(Depot).filter_by(user_id=user.id).order_by(Depot.created_at).all()


@router.post(
    "",
    response_model=DepotOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create depot",
    description="Creates a new depot.",
    responses={
        status.HTTP_409_CONFLICT: {"description": "Depot name already exists"},
    },
)
def create_depot(payload: CreateDepotRequest, ctx: AuthContextDep, db: DBDep) -> Depot:
    user = _get_or_create_user(ctx, db)

    duplicate = db.query(Depot).filter_by(user_id=user.id, name=payload.name).first()
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A depot named '{payload.name}' already exists",
        )

    depot = Depot(user_id=user.id, name=payload.name)
    db.add(depot)
    db.flush()
    return depot


@router.patch(
    "/{depot_id}",
    response_model=DepotOut,
    status_code=status.HTTP_200_OK,
    summary="Rename depot",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Depot not found"},
        status.HTTP_409_CONFLICT: {"description": "Depot name already exists"},
    },
)
def rename_depot(
    depot_id: uuid.UUID, payload: RenameDepotRequest, ctx: AuthContextDep, db: DBDep
) -> Depot:
    user = _get_or_create_user(ctx, db)
    depot = _get_depot_or_404(depot_id, user, db)

    duplicate = db.query(Depot).filter_by(user_id=user.id, name=payload.name).first()
    if duplicate and duplicate.id != depot_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A depot named '{payload.name}' already exists",
        )

    depot.name = payload.name
    db.flush()
    return depot


@router.delete(
    "/{depot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete depot",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Cannot delete the only depot"},
        status.HTTP_404_NOT_FOUND: {"description": "Depot not found"},
    },
)
def delete_depot(depot_id: uuid.UUID, ctx: AuthContextDep, db: DBDep) -> None:
    user = _get_or_create_user(ctx, db)
    depot = _get_depot_or_404(depot_id, user, db)

    depot_count = db.query(Depot).filter_by(user_id=user.id).count()
    if depot_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the only depot",
        )

    db.delete(depot)
    db.flush()


# ── Finance sub-routes (scoped to a specific depot) ────────────────────────────


@router.get(
    "/{depot_id}/years",
    status_code=status.HTTP_200_OK,
    summary="List years for depot",
)
@limiter.limit("60/minute")
def get_years_for_depot(
    request: Request, depot_id: uuid.UUID, ctx: AuthContextDep, db: DBDep
) -> list[int]:
    service = _make_service(depot_id, ctx, db)
    return service.get_years()


@router.get(
    "/{depot_id}/data/{year}",
    status_code=status.HTTP_200_OK,
    summary="Get year data for depot",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Depot not found"},
    },
)
@limiter.limit("120/minute")
def get_data_for_depot(
    request: Request,
    depot_id: uuid.UUID,
    year: YearPath,
    ctx: AuthContextDep,
    db: DBDep,
) -> dict[str, Any]:
    service = _make_service(depot_id, ctx, db)
    return service.get_data(year)


@router.put(
    "/{depot_id}/data/{year}",
    status_code=status.HTTP_200_OK,
    summary="Save year data for depot",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Depot not found"},
    },
)
@limiter.limit("120/minute")
def put_data_for_depot(
    request: Request,
    depot_id: uuid.UUID,
    year: YearPath,
    payload: YearPayload,
    ctx: AuthContextDep,
    db: DBDep,
) -> dict[str, str]:
    service = _make_service(depot_id, ctx, db)
    return service.save_data(year, payload)


@router.delete(
    "/{depot_id}/data/{year}/{section}/{key}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Delete an entry for depot",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Entry not found"},
    },
)
@limiter.limit("60/minute")
def delete_entry_for_depot(
    request: Request,
    depot_id: uuid.UUID,
    year: YearPath,
    section: Literal["dividends", "yields"],
    key: KeyPath,
    ctx: AuthContextDep,
    db: DBDep,
) -> dict[str, str]:
    service = _make_service(depot_id, ctx, db)
    return service.delete_entry(year, section, key)
