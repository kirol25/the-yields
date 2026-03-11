from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    plan: str  # "monthly" | "yearly"
