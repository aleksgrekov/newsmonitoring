from fastapi import APIRouter

from src.api.news_router import router as news_router

base_router = APIRouter(prefix="/api")

base_router.include_router(news_router)
