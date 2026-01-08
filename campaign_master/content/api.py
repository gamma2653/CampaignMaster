# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from functools import wraps
from typing import Callable, ParamSpec, Sequence, TypeVar, cast

from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session

from ..util import get_basic_logger
from . import planning
from .database import SessionLocal
from .models import ObjectBase, ObjectID, PydanticToSQLModel

# from . import planning
logger = get_basic_logger(__name__)


# TODO: Find more elegant way to type this
T = TypeVar("T")
P = ParamSpec("P")


def perform_w_session(f: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator providing automatic session management with error handling.

    - Creates session if not provided
    - Handles exceptions with automatic rollback
    - Commits only if auto_commit=True (default for top-level functions)
    - Tracks session ownership to avoid double-close
    """

    @wraps(f)
    def wrapped(*args: P.args, **kwargs: P.kwargs):
        session = kwargs.get("session", None)
        auto_commit = kwargs.pop("auto_commit", True)
        owns_session = session is None

        if owns_session:
            session = SessionLocal()
            kwargs["session"] = session

        try:
            result = f(*args, **kwargs)

            # Only commit if we own the session AND auto_commit is True
            if owns_session and auto_commit:
                session.commit()
                logger.debug(f"({f.__name__}) Transaction committed")

            return result

        except Exception as e:
            # Only rollback if we own the session
            if owns_session:
                session.rollback()
                logger.error(f"({f.__name__}) Transaction rolled back: {e}")
            raise

        finally:
            # Only close if we own the session
            if owns_session:
                session.close()

    return wrapped


@perform_w_session
def _generate_id(
    prefix: str,
    session: Session | None = None,
    proto_user_id: int = 0,
    auto_commit: bool = False,
) -> "ObjectID":
    """
    Generate a new unique ID with the given prefix for the specified user.

    Note: This is an internal helper that does NOT commit by default.
    The caller is responsible for committing the transaction.
    """
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
    session.flush()  # Flush to make ID available in this transaction
    # REMOVED: session.commit() - Let caller handle commit
    return new_obj_id


@perform_w_session
def generate_id(
    prefix: str, session: Session | None = None, proto_user_id: int = 0
) -> "planning.ID":
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
    db_obj_id = _retrieve_id(
        prefix, numeric, session=session, proto_user_id=proto_user_id
    )
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
    db_ids = _retrieve_ids(prefix=prefix, proto_user_id=proto_user_id, session=session)
    return [db_id.to_pydantic() for db_id in db_ids]


@perform_w_session
def _create_object(
    obj: planning.Object,
    session: Session | None = None,
    proto_user_id: int = 0,
    auto_commit: bool = False,
) -> "ObjectBase":
    """
    Create a new object in the database.

    Note: This is an internal helper that does NOT commit by default.
    The caller is responsible for committing the transaction.
    """
    session = cast(Session, session)  # for mypy
    sql_model = cast(type[ObjectBase], PydanticToSQLModel[type(obj)])
    # logger.debug(f"Object data: {obj}")
    db_obj = sql_model.from_pydantic(obj, proto_user_id=proto_user_id, session=session)
    # logger.debug(f"Created object in DB: {db_obj}")
    session.add(db_obj)
    session.flush()  # Flush to make object available in this transaction
    # REMOVED: session.commit() - Let caller handle commit
    return db_obj


@perform_w_session
def create_object(
    type_: type[planning.Object],
    session: Session | None = None,
    proto_user_id: int = 0,
    auto_commit: bool = True,
) -> planning.Object:
    """
    Create a new object of the specified type.

    This is a top-level API function that commits the transaction by default.
    Pass auto_commit=False when using within a larger transaction context.
    """
    session = cast(Session, session)  # for mypy
    # Generate a new ID first (won't commit due to auto_commit=False)
    new_id = _generate_id(
        prefix=type_._default_prefix,
        proto_user_id=proto_user_id,
        session=session,
        auto_commit=False,
    )
    # Create the Pydantic object with the generated ID
    pydantic_obj = type_(obj_id=new_id.to_pydantic())
    # Convert to SQLAlchemy and save (won't commit due to auto_commit=False)
    db_obj = _create_object(
        pydantic_obj, proto_user_id=proto_user_id, session=session, auto_commit=False
    )
    # Commit happens in decorator (if auto_commit=True and owns session)
    return db_obj.to_pydantic(session=session)


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
        db_obj = session.execute(select(sql_model).where(sql_model.id == db_obj_id.id))
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


@perform_w_session
def retrieve_objects(
    obj_type: type[planning.Object],
    session: Session | None = None,
    proto_user_id: int = 0,
) -> list[planning.Object]:
    """Retrieve all objects of a specific type."""
    session = cast(Session, session)  # for mypy
    sql_model = cast(type[ObjectBase], PydanticToSQLModel[obj_type])
    prefix = obj_type._default_prefix

    # Get all IDs for this type
    db_ids = _retrieve_ids(prefix=prefix, proto_user_id=proto_user_id, session=session)

    results = []
    for db_id in db_ids:
        db_obj = (
            session.execute(select(sql_model).where(sql_model.id == db_id.id))
            .scalars()
            .first()
        )
        if db_obj:
            results.append(db_obj.to_pydantic(session=session))

    return results


@perform_w_session
def update_object(
    obj: planning.Object,
    session: Session | None = None,
    proto_user_id: int = 0,
    auto_commit: bool = True,
) -> planning.Object:
    """
    Update an existing object in the database.

    This is a top-level API function that commits the transaction by default.
    Pass auto_commit=False when using within a larger transaction context.
    """
    session = cast(Session, session)  # for mypy
    sql_model = cast(type[ObjectBase], PydanticToSQLModel[type(obj)])

    # Retrieve existing object
    db_obj_id = _retrieve_id(
        prefix=obj.obj_id.prefix,
        numeric=obj.obj_id.numeric,
        proto_user_id=proto_user_id,
        session=session,
    )

    if not db_obj_id:
        raise ValueError(f"Object with ID {obj.obj_id} not found")

    # Get existing DB object
    db_obj = (
        session.execute(select(sql_model).where(sql_model.id == db_obj_id.id))
        .scalars()
        .first()
    )

    if not db_obj:
        raise ValueError(f"Object with ID {obj.obj_id} not found")

    # Update fields
    db_obj.update_from_pydantic(obj, session=session)
    # REMOVED: session.commit() - Let decorator handle commit
    session.refresh(db_obj)

    return db_obj.to_pydantic(session=session)


@perform_w_session
def delete_object(
    obj_id: planning.ID,
    session: Session | None = None,
    proto_user_id: int = 0,
    auto_commit: bool = True,
) -> bool:
    """
    Delete an object by its ID.

    This is a top-level API function that commits the transaction by default.
    Pass auto_commit=False when using within a larger transaction context.
    """
    session = cast(Session, session)  # for mypy
    sql_model = PydanticToSQLModel[obj_id.__class__]

    db_obj_id = _retrieve_id(
        prefix=obj_id.prefix,
        numeric=obj_id.numeric,
        proto_user_id=proto_user_id,
        session=session,
    )

    if not db_obj_id:
        return False

    db_obj = (
        session.execute(select(sql_model).where(sql_model.id == db_obj_id.id))
        .scalars()
        .first()
    )

    if not db_obj:
        return False

    session.delete(db_obj)
    # REMOVED: session.commit() - Let decorator handle commit
    return True
