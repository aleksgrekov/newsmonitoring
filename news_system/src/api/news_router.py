from fastapi import APIRouter, BackgroundTasks, status

from news_system.src.db.service import DBSession
from news_system.src.repositories.news_repository import NewsRepository
from news_system.src.schemas.base_schemas import SuccessResponse

router = APIRouter(
    prefix="/news",
    tags=["News"],
)


@router.get(
    "/",
    summary="Запуск парсера новостей",
    description="""
    Запускает фоновую задачу для парсинга новостей и сохранения их в базу данных.
    """,
    response_description="Сообщение о успешном запуске задачи",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Задача успешно запущена",
            "content": {"application/json": {"example": {"message": "OK"}}},
        }
    },
)
async def start_news_parser(
    background_tasks: BackgroundTasks,
    session: DBSession,
) -> SuccessResponse:
    """
    Запускает фоновую задачу для парсинга новостей.

    Args:
        background_tasks (BackgroundTasks): Фоновые задачи FastAPI.
        session (DBSession): Сессия базы данных.

    Returns:
        SuccessResponse: Сообщение о успешном запуске задачи.
    """
    background_tasks.add_task(NewsRepository.add_all_news_from_parser, session=session)
    return SuccessResponse(message="OK")
