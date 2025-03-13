from aio_pika.abc import AbstractIncomingMessage, AbstractChannel
from src.logger.logger_config import configure_logging

logger = configure_logging(__name__)


class MessageProcessor:
    """
    Класс для обработки сообщений из RabbitMQ и выполнения логики, связанной с заказами.
    """

    def __init__(self, channel: AbstractChannel):
        self._channel = channel

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        # try:
        body = message.body.decode()
        logger.info(f"Обработка заказа: {body}")

        #
        #     # Добавление заказа в базу данных
        #     order_id = await Order.add_order(order=order)
        #     if order_id:
        #         logger.info(f"Заказ {order_id} успешно добавлен в базу данных")
        #
        #         await asyncio.sleep(2)
        #         await self._channel.default_exchange.publish(
        #             Message(body=f"{order_id}_{order.user_id}_{len(order.items)}".encode()),
        #             routing_key=rabbit_config.NOTIFICATION_RABBITMQ_QUEUE,
        #         )
        #         logger.info(f"Заказ {order_id} отправлен в очередь уведомлений")
        #         await message.ack()
        # except Exception as e:
        #     logger.error(f"Ошибка при обработке заказа: {e}")
        #    await message.nack(requeue=True)  # Отклоняем сообщение и помещаем в очередь для повторной обработки.
