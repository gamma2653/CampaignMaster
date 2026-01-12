from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..util import get_basic_logger
from .models import Base
from .settings import GUISettings

# from . import planning
logger = get_basic_logger(__name__)


settings = GUISettings()
engine = create_engine(settings.db_settings.db_scheme, connect_args=settings.db_settings.db_connect_args)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


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
    session = SessionLocal()
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


def create_db_and_tables():
    Base.metadata.create_all(engine)


def create_example_data():
    """Create example data in the database for testing purposes."""
    pass
    # with SessionLocal() as session:
    # Create a proto user
    # proto_user = ProtoUser(username="example_user")
    # session.add(proto_user)
    # session.flush()

    # Create some example IDs
