from fastapi import FastAPI

from src.api.base_router import base_router
from src.handlers.base_handler import exception_handler

app = FastAPI(
    title="News Service",
    description="Сервис парсинга новостей с сайта CNN",
    version="1.0.0",
)

app.include_router(base_router)
app.add_exception_handler(Exception, exception_handler)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app")
