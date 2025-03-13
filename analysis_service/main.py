import asyncio
import json

from aio_pika import Message, connect_robust
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractIncomingMessage,
)
from database.models.order_model import Order
from logger import configure_logging
from schemas import OrderSchema
from worker_config import rabbit_config

# Настройка логгера
logger = configure_logging(__name__)


async def process_message(
    message: AbstractIncomingMessage, channel: AbstractChannel
) -> None:
    """
    Обрабатывает сообщение из очереди RabbitMQ, десериализует его, добавляет заказ в базу данных,
    подтверждает успешную обработку сообщения и отправляет информацию в очередь уведомлений.

    Если во время обработки возникла ошибка, сообщение отклоняется и помещается обратно в очередь
    для повторной обработки.

    :param message: Сообщение из очереди RabbitMQ.
    :param channel: Канал для отправки сообщений.
    """
    try:
        order = OrderSchema.model_validate(json.loads(message.body.decode()))
        logger.info(f"Обработка заказа: {order}")

        # Добавление заказа в базу данных
        order_id = await Order.add_order(order=order)
        if order_id:
            logger.info(f"Заказ {order_id} успешно добавлен в базу данных")

            await asyncio.sleep(2)
            await channel.default_exchange.publish(
                Message(body=f"{order_id}_{order.user_id}_{len(order.items)}".encode()),
                routing_key=rabbit_config.NOTIFICATION_RABBITMQ_QUEUE,
            )
            logger.info(f"Заказ {order_id} отправлен в очередь уведомлений")
            await message.ack()
    except Exception as e:
        logger.error(f"Ошибка при обработке заказа: {e}")


async def main() -> None:
    """
    Основная функция для запуска воркер-сервиса. Устанавливает соединение с RabbitMQ,
    подписывается на очередь и начинает обработку сообщений.

    В случае ошибки в процессе выполнения логируется ошибка и сервис корректно завершает работу.
    """
    connection: AbstractConnection | None = None

    try:
        logger.info("Запуск воркер-сервиса")
        queue_key = rabbit_config.ORDERS_RABBITMQ_QUEUE

        connection = await connect_robust(rabbit_config.url)
        channel = await connection.channel(publisher_confirms=False)

        queue = await channel.declare_queue(queue_key, durable=True)

        await queue.consume(lambda message: process_message(message, channel))

        await asyncio.Future()

    except Exception as e:
        logger.error(f"Ошибка при запуске воркер-сервиса: {e}")
    finally:
        logger.info("Остановка воркер-сервиса")
        if connection:
            await connection.close()


if __name__ == "__main__":
    """
    Запускает основной процесс воркер-сервиса. В случае остановки сервиса вручную
    или из-за ошибки выводится соответствующий лог.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Сервис был остановлен вручную!")
