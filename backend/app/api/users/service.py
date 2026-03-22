from app.api.users.schemas import MeResponse
from app.core import settings


class UserService:
    def get_me(
        self, email: str, is_premium: bool, subscription_plan: str | None
    ) -> MeResponse:
        return MeResponse(
            email=email,
            is_premium=is_premium,
            subscription_plan=subscription_plan,
            free_tier_limit=settings.FREE_TIER_LIMIT,
        )
