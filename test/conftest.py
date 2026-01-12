"""Pytest configuration and fixtures for CampaignMaster tests."""

from typing import Generator

import pytest
from sqlalchemy import Engine

from campaign_master.content import database
from campaign_master.content.models import Base


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine]:
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
