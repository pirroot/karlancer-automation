from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    telegram_api_id: int | None = None
    telegram_api_hash: SecretStr | None = None
    telegram_session: str = "karlancer_session"
    database_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    @field_validator("telegram_api_id", mode="before")
    @classmethod
    def empty_api_id_to_none(cls, value):
        return None if value == "" else value

    @field_validator("telegram_api_hash", mode="before")
    @classmethod
    def empty_api_hash_to_none(cls, value):
        return None if value == "" else value


@lru_cache
def get_settings() -> Settings:
    return Settings()
