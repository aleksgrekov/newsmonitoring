import json

from aio_pika.abc import AbstractChannel, AbstractIncomingMessage
from src.logger.logger_config import configure_logging
from src.rabbit.interfaces import IMessageProcessor
from src.repositories.news_analyzer_repository import NewsAnalyzerRepository

logger = configure_logging(__name__)


class MessageProcessor(IMessageProcessor):
    """
    Процессор для обработки сообщений из очереди RabbitMQ.

    Attributes:
        _channel (AbstractChannel): Канал RabbitMQ.
    """

    def __init__(self, channel: AbstractChannel):
        self._channel = channel

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        """
        Обрабатывает входящее сообщение.

        Args:
            message (AbstractIncomingMessage): Входящее сообщение из очереди.
        """
        try:
            body = message.body.decode()
            data = json.loads(body)
            logger.info("Получено сообщение: %s", data["message"])

            await NewsAnalyzerRepository.analyze_and_save_news()
            await message.ack()
            logger.info("Анализ новостей завершен! - Analysis Service")

        except Exception as exc:
            logger.error("Ошибка при обработке сообщения: %s", exc)
