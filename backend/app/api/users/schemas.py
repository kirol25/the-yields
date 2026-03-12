from pydantic import BaseModel, EmailStr, Field

from app import settings


class MeResponse(BaseModel):
    email: EmailStr = Field(description="The authenticated user's email address")
    is_premium: bool = Field(
        description="Whether the user has an active premium subscription"
    )
    free_tier_limit: int = Field(
        settings.FREE_TIER_LIMIT,
        description="The maximum number of tickers/accounts allowed in the free tier",
    )
