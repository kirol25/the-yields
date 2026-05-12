from enum import StrEnum


class Environment(StrEnum):
    LOCAL = "local"
    PROD = "prod"


class AuthMode(StrEnum):
    COGNITO = "cognito"
    LOCAL = "local"
