"""Shared fixtures for the test suite.

Strategy
--------
- `get_auth_context` is overridden to skip real JWT/Cognito calls.
- `get_service` is overridden to use an in-process `YieldRepository` backed
  by a per-test `tmp_path`, so tests never touch S3 or the real data dir.
- `free_client` / `premium_client` expose the two tiers used across suites.
"""

import pytest
from fastapi.testclient import TestClient

from app.api.finance.dependencies import get_auth_context, get_service
from app.api.finance.repository import YieldRepository
from app.api.finance.service import YieldService
from app.main import app

TEST_EMAIL = "test@example.com"


# ---------------------------------------------------------------------------
# Auth context fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def free_ctx() -> dict:
    return {"email": TEST_EMAIL, "is_premium": False}


@pytest.fixture
def premium_ctx() -> dict:
    return {"email": TEST_EMAIL, "is_premium": True}


# ---------------------------------------------------------------------------
# Repository + service backed by tmp_path
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_repo(tmp_path) -> YieldRepository:
    return YieldRepository(user_email=TEST_EMAIL, data_dir=tmp_path)


@pytest.fixture
def tmp_service(tmp_repo) -> YieldService:
    return YieldService(tmp_repo)


# ---------------------------------------------------------------------------
# HTTP test clients
# ---------------------------------------------------------------------------


def _make_client(auth_ctx: dict, service: YieldService) -> TestClient:
    """Build a TestClient with dependency overrides for auth + storage."""
    app.dependency_overrides[get_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_service] = lambda: service
    client = TestClient(app, raise_server_exceptions=True)
    return client


@pytest.fixture
def free_client(free_ctx, tmp_service):
    client = _make_client(free_ctx, tmp_service)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def premium_client(premium_ctx, tmp_service):
    client = _make_client(premium_ctx, tmp_service)
    yield client
    app.dependency_overrides.clear()
