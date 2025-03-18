from fastapi import FastAPI

from report_service.src.logger.logger_config import configure_logging
from report_service.src.api.base_router import base_router

logger = configure_logging(__name__)


app = FastAPI(
    title="Report Service",
    description="Сервис генерации отчетов о новостях с сайта CNN",
    version="1.0.0",
)

app.include_router(base_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
