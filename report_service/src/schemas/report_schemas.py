from pydantic import BaseModel, EmailStr, Field


class EmailSchema(BaseModel):
    """
    Схема запроса для отправки отчета на email.

    Args:
        email (EmailStr): Адрес электронной почты для отправки отчета.
    """

    email: EmailStr = Field(
        ..., description="Адрес электронной почты для отправки отчета."
    )
