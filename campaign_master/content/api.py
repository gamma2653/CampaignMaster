# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import cast, Sequence
from sqlalchemy import create_engine, select, insert, update, delete
from sqlalchemy.orm import sessionmaker, Session
from ..util import get_basic_logger
from .settings import GUISettings
from .db import Base, ObjectID, ObjectBase, PydanticToSQLModel
from . import planning

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


# async def create_db_and_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

def _generate_id(
    prefix: str, proto_user_id: int = 0, session: Session | None = None
) -> "ObjectID":
    """Generate a new unique ID with the given prefix for the specified user."""
    def perform(session: Session) -> "ObjectID":
        prior_obj_id = (
            session.execute(
                select(ObjectID)
                .where(
                    ObjectID.prefix == prefix,
                    ObjectID.proto_user_id == proto_user_id,
                )
                .order_by(ObjectID.numeric.desc())
            )
            .scalars()
            .first()
        )
        logger.debug(f"Prior object ID for prefix '{prefix}': {prior_obj_id}")
        next_numeric = 1 if not prior_obj_id else prior_obj_id.numeric + 1
        new_obj_id = ObjectID(
            prefix=prefix,
            numeric=next_numeric,
            proto_user_id=proto_user_id,
        )
        session.add(new_obj_id)
        session.commit()
        return new_obj_id
    # New session, start and end here
    if session is None:
        with SessionLocal() as session_:
            return perform(session_)
    # Ongoing session
    return perform(session)

def generate_id(prefix: str, proto_user_id: int = 0, _session: Session | None = None) -> "planning.ID":
    """Generate a new unique ID with the given prefix for the specified user."""
    def perform(session: Session) -> "planning.ID":
        db_obj_id = _generate_id(prefix, proto_user_id, session)
        return db_obj_id.to_pydantic()
    # New session, start and end here
    if _session is None:
        with SessionLocal() as session:
            return perform(session)
    # Ongoing session
    return perform(_session)

def _retrieve_id(
    prefix: str, numeric: int, proto_user_id: int = 0, session: Session | None = None
) -> "ObjectID | None":
    """Retrieve a specific ID by prefix and numeric part for the specified user."""
    def perform(session: Session) -> "ObjectID | None":
        query = select(ObjectID).where(
            ObjectID.proto_user_id == proto_user_id,
            ObjectID.prefix == prefix,
            ObjectID.numeric == numeric,
        )
        result = session.execute(query).scalars().first()
        return result
    # New session, start and end here
    if session is None:
        with SessionLocal() as session_:
            return perform(session_)
    # Ongoing session
    return perform(session)
        

def retrieve_id(
    prefix: str, numeric: int, proto_user_id: int = 0, _session: Session | None = None
) -> "planning.ID | None":
    """Retrieve a specific ID by prefix and numeric part for the specified user."""
    def perform(session: Session) -> "planning.ID | None":
        db_obj_id = _retrieve_id(prefix, numeric, proto_user_id, session)
        if db_obj_id:
            return db_obj_id.to_pydantic()
        return None
    # New session, start and end here
    if _session is None:
        with SessionLocal() as session:
            return perform(session)
    # Ongoing session
    return perform(_session)


def _retrieve_ids(
    prefix: str | None = None, proto_user_id: int = 0, session: Session | None = None
) -> Sequence["ObjectID"]:
    """Retrieve all IDs for the specified user, optionally filtered by prefix."""
    def perform(session: Session) -> Sequence["ObjectID"]:
        query = select(ObjectID).where(ObjectID.proto_user_id == proto_user_id)
        if prefix:
            query = query.where(ObjectID.prefix == prefix)
        result = session.execute(query).scalars().all()
        return result
    if session is None:
        with SessionLocal() as session_:
            return perform(session_)
    return perform(session)


def retrieve_ids(
    prefix: str | None = None, proto_user_id: int = 0, _session: Session | None = None
) -> list["planning.ID"]:
    """Retrieve all IDs for the specified user, optionally filtered by prefix."""
    def perform(session: Session) -> list["planning.ID"]:
        db_ids = _retrieve_ids(prefix, proto_user_id, session)
        return [db_id.to_pydantic() for db_id in db_ids]
    # New session, start and end here
    if _session is None:
        with SessionLocal() as session:
            return perform(session)
    # Ongoing session
    return perform(_session)


def _create_object(obj: planning.Object, proto_user_id: int = 0, session: Session | None = None) -> "ObjectBase":
    """Create a new object in the database."""
    def perform(session: Session):
        sql_model = cast(type[ObjectBase], PydanticToSQLModel[type(obj)])
        logger.debug(f"Creating new object of type {type(obj).__name__}")
        db_obj = sql_model.from_pydantic(obj, proto_user_id=proto_user_id, _session=session)
        return db_obj
    if session is None:
        with SessionLocal() as session_:
            return perform(session_)
    return perform(session)


def create_object(type_: type[planning.Object], proto_user_id: int = 0, _session: Session | None = None) -> planning.Object:
    """Create a new object of the specified type."""
    def perform(session: Session) -> planning.Object:
        return _create_object(type_(), proto_user_id=proto_user_id, session=session)
    # New session, start and end here
    if _session is None:
        with SessionLocal() as session:
            return perform(session)
    # Ongoing session
    return perform(_session)

def _retrieve_object(
    obj_id: planning.ID, session: Session | None = None
) -> planning.Object | None:
    """Retrieve an object by its ID."""
    def perform(session: Session) -> planning.Object | None:
        sql_model = PydanticToSQLModel[obj_id.__class__]
        # first get the ObjectID
        logger.debug(f"Retrieving object with ID: {obj_id} of type {sql_model.__name__}")
        db_obj_id = _retrieve_id(
            prefix=obj_id.prefix,
            numeric=obj_id.numeric,
            proto_user_id=0,
            session=session,
        )
        logger.debug(f"Retrieved ObjectID from DB: {db_obj_id}")
        if db_obj_id:
            db_obj = session.execute(
                select(sql_model).where(sql_model.obj_id == db_obj_id)
            )
            result = db_obj.scalars().first()
            if result:
                return result.to_pydantic()
        logger.debug(f"No object found with ID {obj_id}")
        return None
    # New session, start and end here
    if session is None:
        with SessionLocal() as session_:
            return perform(session_)
    # Ongoing session
    return perform(session)

def retrieve_object(
    obj_id: planning.ID, _session: Session | None = None
) -> planning.Object | None:
    """Retrieve an object by its ID."""
    def perform(session: Session) -> planning.Object | None:
        return _retrieve_object(obj_id, session)
    # New session, start and end here
    if _session is None:
        with SessionLocal() as session:
            return perform(session)
    # Ongoing session
    return perform(_session)
