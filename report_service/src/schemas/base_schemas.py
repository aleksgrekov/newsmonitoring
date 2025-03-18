from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """
    Схема для успешного ответа API.

    Используется для передачи подтверждения выполнения операции.

    Attributes:
        message (str): Сообщение, подтверждающее успешное выполнение операции.
    """

    message: str = Field(
        ...,
        title="Сообщение об успехе",
        description="Сообщение, подтверждающее успешное выполнение операции.",
    )
