from fastapi import APIRouter, BackgroundTasks

from src.parser.cnn_parser import cnn_parser
from src.repositories.news_repository import NewsRepository
from src.database.service import DBSession

router = APIRouter(prefix="/news")


@router.get("/")
async def start_news_parser(background_tasks: BackgroundTasks, session: DBSession):
    background_tasks.add_task(
        NewsRepository.add_all_news_from_parser, parser=cnn_parser, session=session
    )
    return {"message": "Ok"}
