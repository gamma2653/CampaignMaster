from contextlib import contextmanager
from typing import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ..util import get_basic_logger
from .models import Base
from .settings import GUISettings

logger = get_basic_logger(__name__)

# ---------------------------------------------------------------------------
# Engine Registry: Allows tests to swap database configurations
# ---------------------------------------------------------------------------

_engine_registry: dict[str, Engine] = {}
_session_factory_registry: dict[str, sessionmaker[Session]] = {}
_active_key: str = "default"


def _create_engine_and_factory(
    db_scheme: str,
    connect_args: dict,
) -> tuple[Engine, sessionmaker[Session]]:
    """Create an engine and session factory pair."""
    eng = create_engine(db_scheme, connect_args=connect_args)
    factory = sessionmaker(bind=eng, autoflush=False, autocommit=False)
    return eng, factory


def _initialize_default_database() -> None:
    """Initialize the default production database from settings."""
    settings = GUISettings()
    eng, factory = _create_engine_and_factory(
        settings.db_settings.db_scheme,
        settings.db_settings.db_connect_args,
    )
    _engine_registry["default"] = eng
    _session_factory_registry["default"] = factory


# Initialize default database on module load (backward compatibility)
_initialize_default_database()


def get_engine() -> Engine:
    """Get the currently active engine."""
    return _engine_registry[_active_key]


def get_session_factory() -> sessionmaker[Session]:
    """Get the currently active session factory."""
    return _session_factory_registry[_active_key]


def configure_test_database(
    db_scheme: str = "sqlite:///:memory:",
    connect_args: dict | None = None,
) -> Engine:
    """
    Configure a test database and make it the active database.

    Args:
        db_scheme: SQLAlchemy connection string. Defaults to in-memory SQLite.
        connect_args: Connection arguments. Defaults to SQLite-appropriate args.

    Returns:
        The created Engine instance.
    """
    global _active_key

    if connect_args is None:
        connect_args = {"check_same_thread": False}

    # For in-memory SQLite, use StaticPool to share the same connection
    # across all sessions. Otherwise, each connection gets its own database.
    if db_scheme == "sqlite:///:memory:":
        eng = create_engine(
            db_scheme,
            connect_args=connect_args,
            poolclass=StaticPool,
        )
    else:
        eng = create_engine(db_scheme, connect_args=connect_args)

    factory = sessionmaker(bind=eng, autoflush=False, autocommit=False)
    _engine_registry["test"] = eng
    _session_factory_registry["test"] = factory
    _active_key = "test"

    logger.info(f"Test database configured: {db_scheme}")
    return eng


def reset_to_default_database() -> None:
    """Reset to the default production database configuration."""
    global _active_key
    _active_key = "default"
    logger.info("Reset to default database configuration")


# Backward-compatible aliases
engine = _engine_registry["default"]
SessionLocal = _session_factory_registry["default"]


@contextmanager
def transaction(proto_user_id: int = 0) -> Generator[Session, None, None]:
    """
    Context manager for multi-operation transactions.

    Usage:
        with transaction() as session:
            obj1 = create_object(Rule, session=session, auto_commit=False)
            obj2 = create_object(Character, session=session, auto_commit=False)
            # Both committed together at end

    Args:
        proto_user_id: User ID for scoping operations (0 = global)

    Yields:
        Session: Database session that will be committed on success or rolled back on error

    Raises:
        Exception: Re-raises any exception after rolling back the transaction
    """
    session = get_session_factory()()
    try:
        yield session
        session.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        session.rollback()
        logger.error(f"Transaction rolled back due to error: {e}")
        raise
    finally:
        session.close()


def create_db_and_tables(engine: Engine | None = None) -> None:
    """
    Create all database tables.

    Args:
        engine: Optional engine to use. If None, uses the active engine.
    """
    target_engine = engine if engine is not None else get_engine()
    Base.metadata.create_all(target_engine)


def create_example_data():
    """Create example data in the database for testing purposes."""
    pass
    # with SessionLocal() as session:
    # Create a proto user
    # proto_user = ProtoUser(username="example_user")
    # session.add(proto_user)
    # session.flush()

    # Create some example IDs
