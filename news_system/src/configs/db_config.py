from typing import Optional
from news_system.src.configs.base_config import Settings


class DBSettings(Settings):
    """
    Класс для управления настройками подключения к базе данных Postgres.

    Настройки загружаются из переменных окружения или файла `.env`.

    Attributes:
        DB_HOST (str): Хост базы данных.
        DB_PORT (int): Порт базы данных.
        POSTGRES_USER (str): Имя пользователя базы данных.
        POSTGRES_PASSWORD (str): Пароль пользователя базы данных.
        POSTGRES_DB (str): Название базы данных.
    """

    DB_HOST: str
    DB_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    def db_url(self, driver: Optional[str] = None) -> str:
        """
        Формирует URL для подключения к базе данных Postgres.

        Args:
            driver (Optional[str]): Опциональный драйвер подключения (например, 'asyncpg').

        Returns:
            str: Строка с URL подключения к базе данных.
        """
        return "postgresql{driver}://{user}:{password}@{host}:{port}/{name}".format(
            driver=f"+{driver}" if driver else "",
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            name=self.POSTGRES_DB,
        )


db_settings: DBSettings = DBSettings()
