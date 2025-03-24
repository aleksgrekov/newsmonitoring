import asyncio
import signal

from src.logger.logger_config import configure_logging
from src.rabbit.rabbit_factory import factory

logger = configure_logging(__name__)


def run_service() -> None:
    """
    Запускает основной процесс воркер-сервиса.
    В случае остановки сервиса вручную
    или из-за ошибки выводится соответствующий лог.

    Raises:
        Exception: Логирует ошибку в случае сбоя.
    """

    try:
        worker = factory.create_worker()
        logger.info("Запуск сервиса обработки сообщений...")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, worker.shutdown)

        loop.run_until_complete(worker.run())

    except KeyboardInterrupt:
        logger.info("Сервис был остановлен вручную.")

    except Exception as critical_exc:
        logger.exception(
            "Критическая ошибка в работе сервиса: %s",
            critical_exc,
            exc_info=True,
        )


if __name__ == "__main__":
    run_service()
