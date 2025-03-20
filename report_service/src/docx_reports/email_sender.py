import asyncio

from src.logger.logger_config import configure_logging

logger = configure_logging(__name__)


class EmailSender:
    """Отправляет сгенерированный отчет на электронную почту пользователя."""

    @staticmethod
    async def send_report_by_email(email: str) -> None:
        """
        Имитация отправки отчета на почту.

        Args:
            email: Email адрес для отправки.
        Returns:
            Сообщение об успешной отправке.
        """
        logger.info("Имитация отправки отчета на email: %s...", email)
        await asyncio.sleep(5)
