from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    LOCAL = "local"
    PROD = "prod"


BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App / Environment ---
    ENVIRONMENT: Environment = Field(
        Environment.LOCAL,
        description="Deployment environment. Controls doc exposure and dev-only features.",  # noqa: E501
    )
    APP_URL: str = Field(
        "http://localhost:5173",
        description="Public frontend URL used for Stripe success/cancel redirects.",
    )
    CORS_ORIGINS: str = Field(
        "http://localhost:5173",
        description="Comma-separated list of allowed CORS origins",
    )

    # --- Auth (Cognito) ---
    COGNITO_REGION: str = Field(
        "eu-central-1",
        description="Cognito region for JWT verification (e.g. 'eu-central-1'). "
        "Leave empty to disable JWT verification and use dev mode.",
    )
    COGNITO_USER_POOL_ID: str = Field(
        "",
        description="Cognito User Pool ID — required to update custom:is_premium "
        "on subscription events.",
    )
    # --- Storage ---
    S3_BUCKET: str = Field("the-yields-data", description="S3 bucket name")

    # --- Stripe / Billing ---
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

    # --- Email (SES) ---
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

    # --- Feature flags ---
    FREE_TIER_LIMIT: int = Field(
        5,
        description="Max tickers/accounts per section for free users",
    )

    @property
    def docs_enabled(self) -> bool:
        """Expose API docs only outside of production."""
        return self.ENVIRONMENT != Environment.PROD


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
