from pydantic_settings import BaseSettings, SettingsConfigDict

# See campaign_master/content/settings.py for DB settings
from ..content.settings import DBSettings


class Settings(BaseSettings):
    #### Web server settings
    web_host: str = "127.0.0.1"
    web_port: int = 8000
    debug_mode: bool = False
    db_settings: DBSettings = DBSettings()

    model_config = SettingsConfigDict(env_prefix="CM_")
