from typing import Annotated

import fastapi
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.engine import Engine

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = fastapi.APIRouter()


class User(SQLModel, table=True):
    email: str = Field(primary_key=True)
    username: str | None = Field(default=None)
    full_name: str | None = Field(default=None)
    disabled: bool | None = Field(default=None)


def create_db_and_tables(engine: Engine):
    SQLModel.metadata.create_all(engine)


def _get_session(engine: Engine):
    with Session(engine) as session:
        yield session


def _get_SessionDep(dep_engine: Engine):
    return Annotated[Session, fastapi.Depends(lambda: _get_session(dep_engine))]


def fake_decode_token(token: str) -> User:
    # This doesn't provide any security at all
    # Check the next version
    return User(
        email=token + "@example.com",
        username=token,
        full_name="Fake User",
        disabled=False,
    )


async def get_current_user(
    token: Annotated[str, fastapi.Depends(oauth2_scheme)]
) -> User:
    # Placeholder implementation for user retrieval
    user = fake_decode_token(token)
    return user


@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, fastapi.Depends(get_current_user)]
):
    return current_user
