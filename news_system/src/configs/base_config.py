from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PATH_TO_ENV: str = str(
        Path(__file__).resolve().parent.parent.parent.parent / ".env"
    )

    model_config = SettingsConfigDict(
        env_file=PATH_TO_ENV,  # Путь к файлу .env
        extra="ignore",  # Игнорировать лишние переменные окружения
    )
