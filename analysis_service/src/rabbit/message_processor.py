import json

from aio_pika.abc import AbstractChannel, AbstractIncomingMessage

from src.logger.logger_config import configure_logging
from src.rabbit.interfaces import IMessageProcessor
from analysis_service.src.repositories.news_repository import NewsRepository

logger = configure_logging(__name__)


class MessageProcessor(IMessageProcessor):
    """
    Класс для обработки сообщений из RabbitMQ и выполнения логики, связанной с заказами.
    """

    def __init__(self, channel: AbstractChannel):
        self._channel = channel

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        # try:
        body = message.body.decode()
        data = json.loads(body)
        logger.info(f"{data["message"]}")
        await NewsRepository.text_analysis()

        await message.ack()
        # except Exception as e:
        #     logger.error(f"Ошибка при обработке заказа: {e}")
        #    await message.nack(requeue=True)  # Отклоняем сообщение и помещаем в очередь для повторной обработки.
