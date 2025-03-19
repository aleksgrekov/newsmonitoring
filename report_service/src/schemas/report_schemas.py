from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class GenerateReportRequest(BaseModel):
    """
    Схема запроса для генерации отчета.

    Args:
        filename (Optional[str]): Имя файла для сохранения отчета.
        output_dir (Optional[str]): Директория для сохранения отчета.
    """

    filename: Optional[str] = Field(
        None, description="Имя файла для отчета, не более 10 символов."
    )
    output_dir: Optional[str] = Field(
        None, description="Директория, куда будет сохранен отчет."
    )


class SendReportByEmailRequest(BaseModel):
    """
    Схема запроса для отправки отчета на email.

    Args:
        email (EmailStr): Адрес электронной почты для отправки отчета.
    """

    email: EmailStr = Field(
        ..., description="Адрес электронной почты для отправки отчета."
    )


class ReportRequestBodySchema(GenerateReportRequest, SendReportByEmailRequest):
    """
    Объединенная схема запроса для генерации отчета и отправки его на email.

    Этот класс комбинирует запросы на генерацию отчета и его отправку по email.
    """

    pass
