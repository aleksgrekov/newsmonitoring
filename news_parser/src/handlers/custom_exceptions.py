from src.logger.logger_config import configure_logging

logger = configure_logging(__name__)


class IntegrityViolationException(Exception):
    """
    Исключение, возникающее при нарушении целостности данных.
    """

    def __init__(self, message: str):
        """
        Инициализация исключения с сообщением ошибки.

        Args:
            message (str): Сообщение о нарушении целостности.
        """
        super().__init__(message)
