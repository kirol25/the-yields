from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Free tier ---
    FREE_TIER_LIMIT: int = Field(
        5,
        description="Max tickers/accounts per section for free users",
    )

    # --- CORS settings ---
    CORS_ORIGINS: str = Field(
        "http://localhost:5173",
        description="Comma-separated list of allowed CORS origins",
    )

    # --- Storage settings ---
    STORAGE_BACKEND: str = Field(
        "local", description="Storage backend to use: 'local' or 's3'"
    )
    S3_BUCKET: str = Field("the-yields-data", description="S3 bucket name")
    S3_PREFIX: str = Field("test-user", description="S3 prefix for storing data")

    # --- Cognito / Auth settings ---
    COGNITO_REGION: str = Field(
        "",
        description="AWS Cognito region (e.g. eu-central-1). "
        "Leave empty to skip JWT verification in dev mode.",
    )
    COGNITO_USER_POOL_ID: str = Field(
        "",
        description="Cognito User Pool ID — required to update custom:is_premium "
        "on subscription events.",
    )
    ALLOW_INSECURE_DEV_AUTH: bool = Field(
        False,
        description="Allow trusting X-User-Email instead of JWTs when Cognito "
        "is not configured. Intended for local development only.",
    )

    # --- Stripe settings ---
    STRIPE_SECRET_KEY: str = Field(
        "",
        description="Stripe secret key (sk_live_... or sk_test_...). "
        "Leave empty to disable Stripe endpoints.",
    )
    STRIPE_WEBHOOK_SECRET: str = Field(
        "",
        description="Stripe webhook signing secret (whsec_...) for verifying events.",
    )
    STRIPE_PRICE_ID_MONTHLY: str = Field(
        "",
        description="Stripe Price ID for the monthly plan.",
    )
    STRIPE_PRICE_ID_YEARLY: str = Field(
        "",
        description="Stripe Price ID for the yearly plan.",
    )
    APP_URL: str = Field(
        "http://localhost:5173",
        description="Public frontend URL used for Stripe success/cancel redirects.",
    )

    # --- Feedback email settings ---
    AWS_REGION: str = Field(
        "eu-central-1",
        description="AWS region used for SES",
    )
    FEEDBACK_FROM_EMAIL: str = Field(
        "support@the-yields.com",
        description="Verified SES sender address for feedback emails",
    )
    FEEDBACK_TO_EMAIL: str = Field(
        "lorikbajrami25@gmail.com",
        description="Recipient address for feedback submissions",
    )


@lru_cache
def get_settings() -> Settings:
    """Load and return the application settings."""
    return Settings()


# --- App description for API docs ---
description = """
# The Yield API

## Overview

Enterprise-grade RESTful API for comprehensive dividend and investment yield management.
This service provides robust financial data tracking capabilities with real-time analytics
and portfolio performance monitoring.

## Core Capabilities

### Dividend Management
- Track dividend income across multiple investment instruments
- Historical dividend data aggregation and analysis
- Automated dividend calculation and forecasting

### Yield Analytics
- Real-time yield calculation and tracking
- Multi-period performance analysis (monthly, quarterly, yearly)
- Comparative yield metrics and benchmarking

### Portfolio Intelligence
- Comprehensive investment performance insights
- Data-driven portfolio optimization recommendations
- Advanced reporting and visualization support

## Technical Specifications

- **Architecture**: RESTful API design principles
- **Security**: Industry-standard authentication and authorization
- **Performance**: Optimized for high-throughput operations
- **Scalability**: Cloud-native, horizontally scalable infrastructure

## API Documentation

Complete endpoint documentation, request/response schemas, and integration examples
are available through the interactive documentation below.
"""  # noqa: E501
