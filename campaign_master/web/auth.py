import pathlib
import uuid

import bcrypt
import fastapi
from fastapi import Depends, Header, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session as SASession

from ..content.database import get_session_factory
from ..content.models import AuthToken, AuthUser, ProtoUser
from ..util import get_basic_logger

logger = get_basic_logger(__name__)

router = fastapi.APIRouter()

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@localhost"
ADMIN_DEFAULT_PASSWORD = "admin"


def ensure_admin_user() -> None:
    """Ensure an AuthUser account exists for the default admin ProtoUser (id=0).

    Creates the admin account with default credentials if it doesn't already exist.
    The password should be changed after first login in production environments.
    """
    session = get_session_factory()()
    try:
        existing = session.execute(select(AuthUser).where(AuthUser.proto_user_id == 0)).scalar_one_or_none()

        if existing is not None:
            return

        admin = AuthUser(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            full_name="Administrator",
            hashed_password=_hash_password(ADMIN_DEFAULT_PASSWORD),
            proto_user_id=0,
        )
        session.add(admin)
        session.commit()
        logger.info("Created default admin AuthUser for proto_user_id=0")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str | None = None


class ProfileUpdateRequest(BaseModel):
    username: str | None = None
    email: str | None = None
    full_name: str | None = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class UserResponse(BaseModel):
    username: str
    email: str
    full_name: str | None = None
    proto_user_id: int
    profile_picture: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


async def get_authenticated_user(authorization: str | None = Header(default=None)) -> AuthUser:
    """FastAPI dependency that extracts and validates the Bearer token,
    returning the authenticated AuthUser (with proto_user_id)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise fastapi.HTTPException(status_code=401, detail="Not authenticated")

    token_str = authorization.removeprefix("Bearer ")

    session = get_session_factory()()
    try:
        token = session.execute(select(AuthToken).where(AuthToken.token == token_str)).scalar_one_or_none()

        if token is None:
            raise fastapi.HTTPException(status_code=401, detail="Invalid or expired token")

        user = token.user
        # Ensure proto_user_id is loaded before closing session
        _ = user.proto_user_id
        return user
    finally:
        session.close()


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    session = get_session_factory()()
    try:
        user = session.execute(select(AuthUser).where(AuthUser.username == request.username)).scalar_one_or_none()

        if user is None or not _verify_password(request.password, user.hashed_password):
            raise fastapi.HTTPException(status_code=401, detail="Invalid username or password")

        token = AuthToken(token=str(uuid.uuid4()), user_id=user.id)
        session.add(token)
        session.commit()

        return AuthResponse(
            access_token=token.token,
            token_type="bearer",
            user=_user_response(user),
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    session = get_session_factory()()
    try:
        existing = session.execute(
            select(AuthUser).where((AuthUser.username == request.username) | (AuthUser.email == request.email))
        ).scalar_one_or_none()

        if existing is not None:
            if existing.username == request.username:
                raise fastapi.HTTPException(status_code=409, detail="Username already taken")
            raise fastapi.HTTPException(status_code=409, detail="Email already registered")

        # Create a ProtoUser for this new account
        proto_user = ProtoUser()
        session.add(proto_user)
        session.flush()

        user = AuthUser(
            username=request.username,
            email=request.email,
            full_name=request.full_name,
            hashed_password=_hash_password(request.password),
            proto_user_id=proto_user.id,
        )
        session.add(user)
        session.flush()

        token = AuthToken(token=str(uuid.uuid4()), user_id=user.id)
        session.add(token)
        session.commit()

        return AuthResponse(
            access_token=token.token,
            token_type="bearer",
            user=_user_response(user),
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _user_response(user: AuthUser) -> UserResponse:
    return UserResponse(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        proto_user_id=user.proto_user_id,
        profile_picture=user.profile_picture,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(user: AuthUser = Depends(get_authenticated_user)):
    return _user_response(user)


@router.post("/logout")
async def logout(request: fastapi.Request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token_str = auth_header.removeprefix("Bearer ")
        session = get_session_factory()()
        try:
            token = session.execute(select(AuthToken).where(AuthToken.token == token_str)).scalar_one_or_none()
            if token:
                session.delete(token)
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    return {"message": "Logged out"}


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    user: AuthUser = Depends(get_authenticated_user),
):
    session = get_session_factory()()
    try:
        db_user = session.execute(
            select(AuthUser).where(AuthUser.id == user.id)
        ).scalar_one()

        if request.username is not None and request.username != db_user.username:
            existing = session.execute(
                select(AuthUser).where(AuthUser.username == request.username)
            ).scalar_one_or_none()
            if existing is not None:
                raise fastapi.HTTPException(status_code=409, detail="Username already taken")
            db_user.username = request.username

        if request.email is not None and request.email != db_user.email:
            existing = session.execute(
                select(AuthUser).where(AuthUser.email == request.email)
            ).scalar_one_or_none()
            if existing is not None:
                raise fastapi.HTTPException(status_code=409, detail="Email already registered")
            db_user.email = request.email

        if request.full_name is not None:
            db_user.full_name = request.full_name

        session.commit()
        session.refresh(db_user)
        return _user_response(db_user)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@router.put("/password")
async def change_password(
    request: PasswordChangeRequest,
    user: AuthUser = Depends(get_authenticated_user),
):
    session = get_session_factory()()
    try:
        db_user = session.execute(
            select(AuthUser).where(AuthUser.id == user.id)
        ).scalar_one()

        if not _verify_password(request.current_password, db_user.hashed_password):
            raise fastapi.HTTPException(status_code=400, detail="Current password is incorrect")

        db_user.hashed_password = _hash_password(request.new_password)
        session.commit()
        return {"message": "Password updated successfully"}
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@router.post("/profile/picture")
async def upload_profile_picture(
    file: UploadFile,
    user: AuthUser = Depends(get_authenticated_user),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise fastapi.HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: JPEG, PNG, GIF, WebP",
        )

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise fastapi.HTTPException(status_code=400, detail="File too large. Maximum size is 5MB")
    await file.seek(0)

    from .storage import generate_file_key, get_storage

    storage = get_storage()
    key = generate_file_key(user.id, file.filename or "image.png")

    session = get_session_factory()()
    try:
        db_user = session.execute(
            select(AuthUser).where(AuthUser.id == user.id)
        ).scalar_one()

        # Delete old picture if exists
        old_picture = db_user.profile_picture
        if old_picture:
            old_key = old_picture.split("/uploads/", 1)[-1] if "/uploads/" in old_picture else old_picture
            try:
                await storage.delete(old_key)
            except Exception as e:
                logger.warning("Failed to delete old profile picture: %s", e)

        url = await storage.save(file, key)
        db_user.profile_picture = url
        session.commit()
        return {"profile_picture_url": url}
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@router.get("/uploads/{file_path:path}")
async def get_upload(
    file_path: str,
    user: AuthUser = Depends(get_authenticated_user),
):
    """Serve uploaded files with header-based authentication."""
    # Prevent directory traversal
    from .settings import Settings

    settings = Settings()
    upload_dir = settings.upload_dir.resolve()
    requested = (upload_dir / file_path).resolve()

    if not str(requested).startswith(str(upload_dir)):
        raise fastapi.HTTPException(status_code=400, detail="Invalid file path")

    if not requested.is_file():
        raise fastapi.HTTPException(status_code=404, detail="File not found")

    return FileResponse(requested)
