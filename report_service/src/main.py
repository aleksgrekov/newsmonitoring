from fastapi import FastAPI
from src.api.base_router import base_router
from src.logger.logger_config import configure_logging

logger = configure_logging(__name__)


app = FastAPI(
    title="Report Service",
    description="Сервис генерации отчетов о новостях с сайта CNN",
    version="1.0.0",
)

app.include_router(base_router)
