from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    STORAGE_BACKEND: str = Field(
        "local", description="Storage backend to use: 'local' or 's3'"
    )
    S3_BUCKET: str = Field("the-yield-data", description="S3 bucket name")
    S3_PREFIX: str = Field("test-user", description="S3 prefix for storing data")


@lru_cache
def get_settings() -> Settings:
    """Load and return the application settings."""
    return Settings()
