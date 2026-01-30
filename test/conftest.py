"""Pytest configuration and fixtures for CampaignMaster tests."""

from typing import Iterator

import fastapi
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from campaign_master.content import database
from campaign_master.content.models import Base


@pytest.fixture(scope="session")
def test_engine() -> Iterator[Engine]:
    """
    Session-scoped fixture that creates a test database engine.

    Uses in-memory SQLite for fast test execution.
    The engine persists for the entire test session.
    """
    engine = database.configure_test_database(
        db_scheme="sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    yield engine
    database.reset_to_default_database()


@pytest.fixture(scope="function")
def db_session(test_engine: Engine):
    """
    Function-scoped fixture that provides a clean database for each test.

    Creates all tables before the test and drops them after.
    This ensures complete test isolation.
    """
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)
    yield
    Base.metadata.drop_all(test_engine)


@pytest.fixture(scope="function")
def test_app(db_session) -> fastapi.FastAPI:
    """
    Creates a fresh FastAPI app with API and auth routers for testing.
    """
    app = fastapi.FastAPI()

    from campaign_master.web.api import router as api_router
    from campaign_master.web.auth import router as auth_router

    app.include_router(api_router, prefix="/api")
    app.include_router(auth_router, prefix="/api/auth")

    return app


def _register_user(client: TestClient, username: str, email: str, password: str = "testpass123") -> str:
    """Register a user and return the auth token."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 200, f"Failed to register user: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def test_client(test_app: fastapi.FastAPI) -> Iterator[TestClient]:
    """
    TestClient for API tests, uses test database.

    Registers a default test user and includes auth headers
    on all requests via a wrapper.
    """
    with TestClient(test_app) as client:
        # Register a default test user
        token = _register_user(client, "testuser", "test@example.com")
        client.headers["Authorization"] = f"Bearer {token}"
        yield client
