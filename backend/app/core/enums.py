from enum import StrEnum


class Environment(StrEnum):
    LOCAL = "local"
    PROD = "prod"


class SubscriptionPlan(StrEnum):
    monthly = "monthly"
    yearly = "yearly"
