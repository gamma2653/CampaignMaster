import pathlib

from pydantic_settings import BaseSettings, SettingsConfigDict

# See campaign_master/content/settings.py for DB settings
from ..content.settings import DBSettings

# Default log directory (relative to project root)
DEFAULT_LOG_DIR = pathlib.Path("logs")


class Settings(BaseSettings):
    #### Web server settings
    web_host: str = "127.0.0.1"
    web_port: int = 8000
    debug_mode: bool = False
    db_settings: DBSettings = DBSettings()

    #### Logging settings (used when debug_mode=True)
    log_dir: pathlib.Path = DEFAULT_LOG_DIR
    log_filename: str = "fastapi_debug.log"

    #### File upload / storage settings
    upload_dir: pathlib.Path = pathlib.Path("uploads")
    s3_bucket: str | None = None
    s3_region: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_endpoint: str | None = None

    model_config = SettingsConfigDict(env_prefix="CM_")
