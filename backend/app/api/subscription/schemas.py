from pydantic import BaseModel

from app.core.enums import SubscriptionPlan


class CheckoutRequest(BaseModel):
    plan: SubscriptionPlan
