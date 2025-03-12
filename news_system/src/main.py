from fastapi import FastAPI

from src.api.base_router import base_router

app = FastAPI(
    title="News Service",
    description="Сервис парсинга новостей с сайта CNN",
    version="1.0.0",
)

app.include_router(base_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app")
