# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine, select, insert, update, delete
from sqlalchemy.orm import sessionmaker
from ..util import get_basic_logger
from .settings import GUISettings
from .db import Base, ObjectID, ProtoUser, PydanticToSQLModel
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


def generate_id(prefix: str, proto_user_id: int = 0) -> "planning.ID":
    """Generate a new unique ID with the given prefix for the specified user."""
    with SessionLocal() as session:
        # query first for released IDs, reuse if available
        # released_id = (
        #     session.query(cls)
        #     .filter_by(prefix=prefix, released=True, proto_user_id=proto_user_id)
        #     .order_by(cls.numeric)
        #     .first()
        # )
        # if released_id:
        #     released_id.released = False
        #     session.flush()
        #     return released_id
        # Otherwise, create a new ID
        prior_obj_id = (
            session.execute(
                select(ObjectID)
                .where(
                    ObjectID.prefix == prefix,
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
        return new_obj_id.to_pydantic()


def retrieve_ids(prefix: str | None = None, proto_user_id: int = 0) -> list["ObjectID"]:
    """Retrieve all IDs for the specified user, optionally filtered by prefix."""
    with SessionLocal() as session:
        query = select(ObjectID).where(ObjectID.proto_user_id == proto_user_id)
        if prefix:
            query = query.where(ObjectID.prefix == prefix)
        result = session.execute(query).scalars().all()
        return list(result)


def _create_object(obj: planning.Object) -> planning.Object:
    """Create a new object in the database."""
    with SessionLocal() as session:
        session.add(obj)
        session.commit()
        return obj

def create_object(type: type[planning.Object]) -> planning.Object:
    """Create a new object of the specified type."""
    sql_model = PydanticToSQLModel[type]
    obj = sql_model.from_pydantic(type.model_validate({}))
    print(f"Created obj: {obj}")
    return _create_object(obj)
