from contextlib import asynccontextmanager

from fastapi import FastAPI

from news_system.src.api.base_router import base_router
from news_system.src.handlers.base_handler import exception_handler
from news_system.src.logger.logger_config import configure_logging
from news_system.src.rabbit.rabbit_connection import connection

logger = configure_logging(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Управляет жизненным циклом приложения:
    - Устанавливает соединение с брокером сообщений при запуске.
    - Закрывает соединение при завершении работы сервиса.
    """
    logger.info("Подключение к RabbitMQ...")
    await connection.connect()
    yield
    logger.info("Завершение работы с RabbitMQ...")
    await connection.disconnect()


app = FastAPI(
    title="News Service",
    description="Сервис парсинга новостей с сайта CNN",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(base_router)
app.add_exception_handler(Exception, exception_handler)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
