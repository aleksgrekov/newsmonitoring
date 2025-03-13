from fastapi import APIRouter, BackgroundTasks

from src.database.service import DBSession
from src.repositories.news_repository import NewsRepository

router = APIRouter(prefix="/news")


@router.get("/")
async def start_news_parser(background_tasks: BackgroundTasks, session: DBSession):
    background_tasks.add_task(NewsRepository.add_all_news_from_parser, session=session)
    return {"message": "Ok"}
