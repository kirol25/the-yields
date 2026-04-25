from fastapi import APIRouter, Request, status

from app.api.finance.dependencies import AuthContextDep
from app.api.users.schemas import MeResponse
from app.api.users.service import UserService
from app.core.limiter import limiter

router = APIRouter(prefix="/api", tags=["users"])


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "User context retrieved successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required."},
    },
    response_model=MeResponse,
    summary="Authenticated user context",
    description="Returns the current user's identity.",
)
@limiter.limit("30/minute")
def get_me(request: Request, ctx: AuthContextDep) -> MeResponse:
    return UserService().get_me(ctx["email"])
