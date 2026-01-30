import pathlib
import uuid
from abc import ABC, abstractmethod

from fastapi import UploadFile

from ..util import get_basic_logger

logger = get_basic_logger(__name__)


class StorageBackend(ABC):
    @abstractmethod
    async def save(self, file: UploadFile, key: str) -> str:
        """Save a file and return its URL/path."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a file by its key/path."""


class LocalStorage(StorageBackend):
    def __init__(self, upload_dir: pathlib.Path):
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, file: UploadFile, key: str) -> str:
        file_path = self.upload_dir / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        contents = await file.read()
        file_path.write_bytes(contents)
        return f"/api/auth/uploads/{key}"

    async def delete(self, key: str) -> None:
        file_path = self.upload_dir / key
        if file_path.exists():
            file_path.unlink()


class S3Storage(StorageBackend):
    def __init__(
        self,
        bucket: str,
        region: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        endpoint: str | None = None,
    ):
        import boto3

        kwargs: dict = {}
        if region:
            kwargs["region_name"] = region
        if access_key and secret_key:
            kwargs["aws_access_key_id"] = access_key
            kwargs["aws_secret_access_key"] = secret_key
        if endpoint:
            kwargs["endpoint_url"] = endpoint

        self.s3 = boto3.client("s3", **kwargs)
        self.bucket = bucket
        self.endpoint = endpoint
        self.region = region

    async def save(self, file: UploadFile, key: str) -> str:
        contents = await file.read()
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=contents,
            ContentType=file.content_type or "application/octet-stream",
        )
        if self.endpoint:
            return f"{self.endpoint}/{self.bucket}/{key}"
        return f"https://{self.bucket}.s3.{self.region or 'us-east-1'}.amazonaws.com/{key}"

    async def delete(self, key: str) -> None:
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=key)
        except Exception as e:
            logger.warning("Failed to delete S3 object %s: %s", key, e)


def generate_file_key(user_id: int, filename: str) -> str:
    ext = pathlib.Path(filename).suffix.lower()
    return f"profile_pictures/{user_id}_{uuid.uuid4().hex}{ext}"


_storage: StorageBackend | None = None


def get_storage() -> StorageBackend:
    global _storage
    if _storage is not None:
        return _storage

    from .settings import Settings

    settings = Settings()
    if settings.s3_bucket:
        _storage = S3Storage(
            bucket=settings.s3_bucket,
            region=settings.s3_region,
            access_key=settings.s3_access_key,
            secret_key=settings.s3_secret_key,
            endpoint=settings.s3_endpoint,
        )
    else:
        _storage = LocalStorage(settings.upload_dir)
    return _storage
