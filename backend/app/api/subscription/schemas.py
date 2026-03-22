from enum import Enum

from pydantic import BaseModel


class SubscriptionPlan(str, Enum):
    monthly = "monthly"
    yearly = "yearly"


class CheckoutRequest(BaseModel):
    plan: SubscriptionPlan
