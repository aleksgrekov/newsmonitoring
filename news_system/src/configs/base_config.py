from abc import ABC
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings, ABC):
    """
    Базовый класс для настроек, загружаемых из переменных окружения или файла `.env`.

    Attributes:
        PATH_TO_ENV (str): Путь к файлу `.env`.
    """

    PATH_TO_ENV: str = str(
        Path(__file__).resolve().parent.parent.parent.parent / ".env"
    )

    model_config = SettingsConfigDict(
        env_file=PATH_TO_ENV,
        extra="ignore",
    )
