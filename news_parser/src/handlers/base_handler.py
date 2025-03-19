import traceback

from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.logger.logger_config import configure_logging
from src.schemas.base_schemas import ErrorResponseSchema

logger = configure_logging(__name__)


async def exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """
    Обработчик непредвиденных ошибок.

    Логирует подробности ошибки и возвращает ответ с кодом состояния 500 (Internal Server Error)
    и информацией об ошибке.

    Args:
        _request (Request): Объект запроса FastAPI.
        exc (Exception): Исключение, которое было выброшено.

    Returns:
        JSONResponse: Ответ с типом ошибки, сообщением и кодом состояния 500.
    """
    error_type: str = exc.__class__.__name__
    error_message: str = str(exc)
    error_details: str = traceback.format_exc()

    logger.exception(
        "Произошла ошибка! Тип ошибки: %s, Сообщение: %s, Детали: %s\n\n",
        error_type,
        error_message,
        error_details,
    )

    error_response = ErrorResponseSchema(
        type=error_type,
        message=error_message,
    ).model_dump()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response,
    )
