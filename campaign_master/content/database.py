from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..util import get_basic_logger
from .models import Base
from .settings import GUISettings

# from . import planning
logger = get_basic_logger(__name__)


settings = GUISettings()
engine = create_engine(
    settings.db_settings.db_scheme, connect_args=settings.db_settings.db_connect_args
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


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
