from typing import Optional

from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """
    Схема для успешного ответа API.

    Используется для передачи подтверждения выполнения операции.

    Attributes:
        message (str): Сообщение, подтверждающее успешное выполнение операции.
    """

    message: Optional[str] = Field(
        default="ПРЕДУПРЕЖЖДЕНИЕ!!!\n'x-last-modified': "
        "не удалось установить значение хедера!",
        title="Сообщение об успехе",
        description="Сообщение, подтверждающее успешное выполнение операции.",
    )


class ErrorResponseSchema(BaseModel):
    """
    Схема для ответа API об ошибке.

    Используется для отправки информации о возникшей ошибке.

    Attributes:
        type (str): Тип ошибки, например,
        'ValidationError' или 'InternalServerError'.
        message (str): Сообщение, содержащее подробности об ошибке.
    """

    type: str = Field(
        ...,
        title="Тип ошибки",
        description="Тип ошибки, например, "
        "'ValidationError' или 'InternalServerError'.",
    )
    message: str = Field(
        ...,
        title="Сообщение об ошибке",
        description="Сообщение, содержащее подробности об ошибке.",
    )
