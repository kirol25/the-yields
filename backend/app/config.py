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
    CORS_ORIGINS: str = Field(
        "http://localhost:5173",
        description="Comma-separated list of allowed CORS origins",
    )


@lru_cache
def get_settings() -> Settings:
    """Load and return the application settings."""
    return Settings()


# --- App description for API docs ---
_description = """
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
