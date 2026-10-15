"""Pytest configuration and shared fixtures.

Tests run against an in-memory SQLite database so they have no external
dependencies. The application's ``get_db`` dependency is overridden so the
FastAPI app under test uses the same in-memory database.
"""
from __future__ import annotations

import os
import sys
from collections.abc import Generator
from typing import Iterator

# Ensure the backend directory is importable as ``app``.
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Force a SQLite test database before importing the app/config.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_at_least_16_chars_long")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("APP_ENV", "test")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import event, create_engine  # noqa: E402
from sqlalchemy.engine import Engine  # noqa: E402
from sqlalchemy.orm import sessionmaker, Session  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db.base import Base  # noqa: E402
import app.models  # noqa: E402,F401  (register models)
from app.db.dependencies import get_db  # noqa: E402


def _make_test_engine() -> Engine:
    """Create a single-connection in-memory SQLite engine.

    ``StaticPool`` + ``check_same_thread=False`` keeps the same in-memory
    database across multiple connections/threads used by TestClient.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    # Enable foreign-key enforcement so CASCADE behaviour is exercised.
    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_conn, _):  # pragma: no cover - test infra
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_session() -> Iterator[Session]:
    """Yield a fresh database session for each test, then drop all data."""
    engine = _make_test_engine()
    TestSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Iterator[TestClient]:
    """FastAPI test client wired to the per-test database session."""
    from app.main import app

    def _override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            # The session is closed by the db_session fixture.
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_token(client: TestClient) -> str:
    """Register a user and return a JWT access token."""
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "Sup3rSecret!",
            "password_confirm": "Sup3rSecret!",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Sup3rSecret!"},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture()
def auth_headers(auth_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture()
def second_user_token(client: TestClient) -> str:
    """Register a second user and return a token (for isolation tests)."""
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Second User",
            "email": "second@example.com",
            "password": "Sup3rSecret!",
            "password_confirm": "Sup3rSecret!",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "second@example.com", "password": "Sup3rSecret!"},
    )
    return response.json()["access_token"]


@pytest.fixture()
def second_user_headers(second_user_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {second_user_token}"}
