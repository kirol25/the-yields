"""Shared fixtures for the test suite.

Strategy (HTTP tests)
---------------------
- `get_auth_context` is overridden to skip real JWT/Cognito calls.
- `get_service` is overridden to use an in-process `YieldRepository` backed
  by a per-test `tmp_path`, so tests never touch S3 or the real data dir.
- `free_client` / `premium_client` expose the two tiers used across suites.

Strategy (DB / model tests)
----------------------------
- `db_engine` (session-scoped): connects to the test database, creates all
  tables once, and drops them after the session ends.
- `db_session` (function-scoped): wraps each test in an outer transaction +
  a SAVEPOINT. Both are rolled back on teardown, so tests never persist data
  and IntegrityError assertions don't abort the outer connection.
- `user`, `depot`, `dividend_entry` are convenience fixtures that pre-insert
  common rows and are automatically rolled back with the session.

The test database URL defaults to:
    postgresql://postgres:postgres@localhost:5432/the_yields_test
Override it with the TEST_DATABASE_URL environment variable.
"""

import os

import pytest
from backend.app.api.finance.repository import YieldRepository
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.orm import Session

from app.api.finance.dependencies import get_auth_context, get_service
from app.api.finance.service import YieldService
from app.db import models  # noqa: F401 — ensures all models are registered
from app.db.base import Base
from app.db.models import Depot, DividendEntry, User
from app.main import app

TEST_EMAIL = "test@example.com"
TEST_SUB = "test-sub-uuid"

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/the_yields_test",
)


# ---------------------------------------------------------------------------
# Auth context fixtures (HTTP suite)
# ---------------------------------------------------------------------------


@pytest.fixture
def free_ctx() -> dict:
    return {"email": TEST_EMAIL, "sub": TEST_SUB, "is_premium": False}


@pytest.fixture
def premium_ctx() -> dict:
    return {"email": TEST_EMAIL, "sub": TEST_SUB, "is_premium": True}


# ---------------------------------------------------------------------------
# Repository + service backed by tmp_path (HTTP suite)
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_repo(tmp_path) -> YieldRepository:
    return YieldRepository(user_email=TEST_EMAIL, data_dir=tmp_path)


@pytest.fixture
def tmp_service(tmp_repo) -> YieldService:
    return YieldService(tmp_repo)


# ---------------------------------------------------------------------------
# HTTP test clients (HTTP suite)
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


# ---------------------------------------------------------------------------
# Database engine — session-scoped (DB suite)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def db_engine() -> Engine:
    """Create the test schema once per pytest session and tear it down after.

    Skips automatically if the test database is not reachable, so the
    HTTP suite can run in CI without a Postgres instance.
    """
    try:
        engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
        # Verify connectivity before creating tables
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        Base.metadata.create_all(engine)
    except Exception as exc:
        pytest.skip(f"Test database unavailable — skipping DB tests: {exc}")
        return  # unreachable, satisfies type checker

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


# ---------------------------------------------------------------------------
# Database session — function-scoped with automatic rollback (DB suite)
# ---------------------------------------------------------------------------


@pytest.fixture
def db_session(db_engine: Engine) -> Session:
    """Yield an ORM session isolated inside a transaction + SAVEPOINT.

    Isolation strategy:
    - An outer ``BEGIN`` wraps the entire test.
    - A SAVEPOINT is created immediately so that ``IntegrityError`` tests can
      roll back to the savepoint (via ``session.rollback()``) without aborting
      the outer connection.
    - The event listener re-creates the SAVEPOINT after each sub-transaction
      ends so the session is always in a clean, usable state.
    - The outer ``BEGIN`` is rolled back unconditionally after the test, so
      no data ever reaches the database.
    """
    connection = db_engine.connect()
    outer_transaction = connection.begin()
    session = Session(bind=connection)

    # Create the first SAVEPOINT
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session: Session, transaction) -> None:  # type: ignore[type-arg]
        nonlocal nested
        # Re-create the SAVEPOINT whenever the previous nested transaction ends
        # so the session is always sitting on a fresh savepoint.
        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            nested = connection.begin_nested()

    yield session

    session.close()
    outer_transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# Convenience row fixtures (DB suite)
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db_session: Session) -> User:
    """A persisted User row, rolled back after the test."""
    u = User(sub="fixture-sub", email="fixture@example.com")
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def depot(db_session: Session, user: User) -> Depot:
    """A persisted Depot row owned by `user`, rolled back after the test."""
    d = Depot(user_id=user.id, name="Default")
    db_session.add(d)
    db_session.flush()
    return d


@pytest.fixture
def dividend_entry(db_session: Session, depot: Depot) -> DividendEntry:
    """A persisted DividendEntry row inside `depot`, rolled back after the test."""
    e = DividendEntry(depot_id=depot.id, year=2024, ticker="TEST", name="Test Corp")
    db_session.add(e)
    db_session.flush()
    return e


# ---------------------------------------------------------------------------
# DB-backed repository + service fixtures (DB suite)
# ---------------------------------------------------------------------------


@pytest.fixture
def db_repo(db_session: Session) -> YieldRepository:
    """A YieldRepository wired to the test session."""
    return YieldRepository(sub=TEST_SUB, email=TEST_EMAIL, session=db_session)


@pytest.fixture
def db_service(db_repo: YieldRepository) -> YieldService:
    """A YieldService backed by the DB repository."""
    return YieldService(db_repo)


# ---------------------------------------------------------------------------
# HTTP clients backed by the test DB session (depot + integration HTTP suite)
# ---------------------------------------------------------------------------


def _make_db_client(auth_ctx: dict, session: Session) -> TestClient:
    """TestClient that uses real DB session but fake auth context."""
    app.dependency_overrides[get_auth_context] = lambda: auth_ctx
    from app.db.session import get_db

    app.dependency_overrides[get_db] = lambda: session
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture
def free_db_client(db_session: Session) -> TestClient:
    client = _make_db_client(
        {"email": TEST_EMAIL, "sub": TEST_SUB, "is_premium": False}, db_session
    )
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def premium_db_client(db_session: Session) -> TestClient:
    client = _make_db_client(
        {"email": "premium@example.com", "sub": "premium-sub", "is_premium": True},
        db_session,
    )
    yield client
    app.dependency_overrides.clear()
