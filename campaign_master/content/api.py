# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from functools import wraps
from typing import cast, Sequence, Callable, TypeVar, ParamSpec
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


# TODO: Find more elegant way to type this
T = TypeVar("T")
P = ParamSpec("P")
def perform_w_session(f: Callable[P, T]) -> Callable[P, T]:
    @wraps(f)
    def wrapped(*args: P.args, **kwargs: P.kwargs):
        session = kwargs.get('session', None)
        if session is None:
            with SessionLocal() as session_:
                logger.debug("(%s) Performing operation with new session (%s)", "perform_w_session", f.__name__)
                kwargs['session'] = session_
                return f(*args, **kwargs) # process, then close context
        return f(*args, **kwargs)
    return wrapped


@perform_w_session
def _generate_id(prefix: str, session: Session | None = None, proto_user_id: int = 0) -> "ObjectID":
    """Generate a new unique ID with the given prefix for the specified user."""
    session = cast(Session, session)  # for mypy
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

@perform_w_session
def generate_id(prefix: str, session: Session | None = None, proto_user_id: int = 0) -> "planning.ID":
    session = cast(Session, session)  # for mypy
    """Generate a new unique ID with the given prefix for the specified user."""
    db_obj_id = _generate_id(prefix, session=session, proto_user_id=proto_user_id)
    return db_obj_id.to_pydantic()

@perform_w_session
def _retrieve_id(
    prefix: str, numeric: int, session: Session | None = None, proto_user_id: int = 0
) -> "ObjectID | None":
    """Retrieve a specific ID by prefix and numeric part for the specified user."""
    session = cast(Session, session)  # for mypy
    query = select(ObjectID).where(
        ObjectID.proto_user_id == proto_user_id,
        ObjectID.prefix == prefix,
        ObjectID.numeric == numeric,
    )
    result = session.execute(query).scalars().first()
    return result
        
@perform_w_session
def retrieve_id(
    prefix: str, numeric: int, session: Session | None = None, proto_user_id: int = 0
) -> "planning.ID | None":
    """Retrieve a specific ID by prefix and numeric part for the specified user."""
    session = cast(Session, session)  # for mypy
    db_obj_id = _retrieve_id(prefix, numeric, session=session, proto_user_id=proto_user_id)
    if db_obj_id:
        return db_obj_id.to_pydantic()
    return None

@perform_w_session
def _retrieve_ids(
    session: Session | None = None, prefix: str | None = None, proto_user_id: int = 0
) -> Sequence["ObjectID"]:
    """Retrieve all IDs for the specified user, optionally filtered by prefix."""
    session = cast(Session, session)  # for mypy
    query = select(ObjectID).where(ObjectID.proto_user_id == proto_user_id)
    if prefix:
        query = query.where(ObjectID.prefix == prefix)
    result = session.execute(query).scalars().all()
    return result


@perform_w_session
def retrieve_ids(
    session: Session | None = None, prefix: str | None = None, proto_user_id: int = 0
) -> list["planning.ID"]:
    """Retrieve all IDs for the specified user, optionally filtered by prefix."""
    session = cast(Session, session)  # for mypy
    db_ids = _retrieve_ids(session, prefix, proto_user_id)
    return [db_id.to_pydantic() for db_id in db_ids]


@perform_w_session
def _create_object(obj: planning.Object, session: Session | None = None, proto_user_id: int = 0) -> "ObjectBase":
    session = cast(Session, session)  # for mypy
    """Create a new object in the database."""
    sql_model = cast(type[ObjectBase], PydanticToSQLModel[type(obj)])
    # logger.debug(f"Object data: {obj}")
    obj = sql_model.from_pydantic(obj, proto_user_id=proto_user_id, _session=session)
    # logger.debug(f"Created object in DB: {obj}")
    return obj


@perform_w_session
def create_object(type_: type[planning.Object], session: Session | None = None, proto_user_id: int = 0) -> planning.Object:
    """Create a new object of the specified type."""
    session = cast(Session, session)  # for mypy
    return _create_object(type_(), proto_user_id=proto_user_id, session=session).to_pydantic(session=session)

@perform_w_session
def _retrieve_object(
    obj_id: planning.ID, session: Session | None = None, proto_user_id: int = 0
) -> planning.Object | None:
    """Retrieve an object by its ID."""
    session = cast(Session, session)  # for mypy
    sql_model = PydanticToSQLModel[obj_id.__class__]
    # first get the ObjectID
    logger.debug(f"Retrieving object with ID: {obj_id} of type {sql_model.__name__}")
    db_obj_id = _retrieve_id(
        prefix=obj_id.prefix,
        numeric=obj_id.numeric,
        proto_user_id=proto_user_id,
        session=session,
    )
    logger.debug(f"Retrieved ObjectID from DB: {db_obj_id}")
    if db_obj_id:
        db_obj = session.execute(
            select(sql_model).where(sql_model.id == db_obj_id.id)
        )
        result = db_obj.scalars().first()
        if result:
            return result.to_pydantic(session=session)
    logger.debug(f"No object found with ID {obj_id}")
    return None

@perform_w_session
def retrieve_object(
    obj_id: planning.ID, session: Session | None = None, proto_user_id: int = 0
) -> planning.Object | None:
    """Retrieve an object by its ID."""
    session = cast(Session, session)  # for mypy    
    return _retrieve_object(obj_id, proto_user_id=proto_user_id, session=session)
