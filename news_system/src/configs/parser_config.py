from base_config import Settings


class ParserSettings(Settings):

    NEWS_URL: str
    YOUR_ACCEPT_HEADER: str
    YOUR_USER_AGENT_HEADER: str


# Создание глобального экземпляра настроек базы данных
parser_settings: ParserSettings = ParserSettings()  # type: ignore
