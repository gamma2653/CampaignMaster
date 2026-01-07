from pydantic import Field as PydanticField
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    """
    Settings for the database connection.
    """

    db_scheme: str = "sqlite:///campaignmaster.db"
    db_connect_args: dict = {"check_same_thread": False}  # For SQLite

    model_config = SettingsConfigDict(env_prefix="DB_")


class GUISettings(BaseSettings):
    """
    Settings for the GUI application.
    """

    model_config = SettingsConfigDict(env_prefix="CM_")
    db_settings: DBSettings = DBSettings()
