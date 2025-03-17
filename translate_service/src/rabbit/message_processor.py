import json

from aio_pika.abc import AbstractChannel, AbstractIncomingMessage

from translate_service.src.logger.logger_config import configure_logging
from translate_service.src.rabbit.interfaces import IMessageProcessor

logger = configure_logging(__name__)


class MessageProcessor(IMessageProcessor):

    def __init__(self, channel: AbstractChannel):
        self._channel = channel

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        try:
            body = message.body.decode()
            data = json.loads(body)
            logger.info(f"{data["message"]}")

            await message.ack()
            logger.info(f"Анализ новостей окончен! - Translate Service")

        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
