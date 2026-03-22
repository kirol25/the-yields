from pydantic import BaseModel, EmailStr, Field

from app.core import settings
from app.core.enums import SubscriptionPlan


class MeResponse(BaseModel):
    email: EmailStr = Field(description="The authenticated user's email address")
    is_premium: bool = Field(
        description="Whether the user has an active premium subscription"
    )
    subscription_plan: SubscriptionPlan | None = Field(
        None,
        description="Active plan: 'monthly' or 'yearly'. Null when not premium.",
    )
    free_tier_limit: int = Field(
        settings.FREE_TIER_LIMIT,
        description="The maximum number of tickers/accounts allowed in the free tier",
    )
