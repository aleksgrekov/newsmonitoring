from typing import Optional

from fastapi import HTTPException, status

from src.logger.logger_config import configure_logging

logger = configure_logging(__name__)


class BaseCustomException(HTTPException):
    """
    Базовый класс для пользовательских исключений с логированием.
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_message: str = "Произошла ошибка"

    def __init__(self, message: Optional[str] = None):
        """
        Инициализация исключения с параметром сообщения.

        :param message: Сообщение, которое будет передано в исключение.
        Если не указано, используется сообщение по умолчанию.
        """
        detail = message or self.default_message
        super().__init__(status_code=self.status_code, detail=detail)
        logger.warning("%s: %s", self.__class__.__name__, detail)


class IntegrityViolationException(Exception):
    """
    Исключение, возникающее при нарушении целостности данных.
    """

    def __init__(self, message: str):
        """
        Инициализация исключения с сообщением ошибки.

        :param message: Сообщение о нарушении целостности.
        """
        super().__init__(message)
