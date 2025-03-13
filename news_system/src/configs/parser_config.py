from src.configs.base_config import Settings


class ParserSettings(Settings):

    NEWS_URL: str
    ACCEPT: str
    ACCEPT_LANGUAGE: str
    CONNECTION: str


# Создание глобального экземпляра настроек базы данных
parser_settings: ParserSettings = ParserSettings()  # type: ignore
