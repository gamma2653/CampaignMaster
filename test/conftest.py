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
def test_client(db_session) -> Iterator[TestClient]:
    """
    TestClient for API tests, uses test database.

    Depends on db_session to ensure clean database state.
    Creates a fresh FastAPI app with only the API router for testing.
    """
    # Create a fresh FastAPI app for each test
    test_app = fastapi.FastAPI()

    # Import and register API router
    from campaign_master.web.api import router as api_router

    test_app.include_router(api_router, prefix="/api")

    with TestClient(test_app) as client:
        yield client
