import asyncio

from src.configs.rabbit_config import rabbit_config
from src.logger.logger_config import configure_logging
from src.rabbit.consumer import WorkerService
from src.rabbit.message_processor import MessageProcessor
from src.rabbit.rabbit_connection import RabbitConnection

logger = configure_logging(__name__)

if __name__ == "__main__":
    """
    Запускает основной процесс воркер-сервиса. В случае остановки сервиса вручную
    или из-за ошибки выводится соответствующий лог.
    """
    try:
        connection = RabbitConnection(rabbit_config.url)
        processor = MessageProcessor(connection.get_channel())
        worker = WorkerService(connection, processor, rabbit_config.PARSER_QUEUE)

        asyncio.run(worker.run())

    except KeyboardInterrupt:
        logger.info("Сервис был остановлен вручную!")
