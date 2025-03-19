from src.configs.base_config import Settings


class ParserSettings(Settings):
    """
    Класс для управления настройками парсера новостей.

    Настройки загружаются из переменных окружения или файла `.env`.

    Attributes:
        NEWS_URL (str): URL для парсинга новостей.
        ACCEPT (str): Заголовок Accept для HTTP-запросов.
        ACCEPT_LANGUAGE (str): Заголовок Accept-Language для HTTP-запросов.
        CONNECTION (str): Заголовок Connection для HTTP-запросов.
    """

    NEWS_URL: str
    ACCEPT: str
    ACCEPT_LANGUAGE: str
    CONNECTION: str


parser_settings: ParserSettings = ParserSettings()
