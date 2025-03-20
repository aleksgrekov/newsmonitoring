from fastapi import APIRouter, BackgroundTasks, status
from src.repositories.report_repository import ReportRepository
from src.schemas.base_schemas import SuccessResponse
from src.schemas.report_schemas import EmailSchema

router = APIRouter(
    prefix="/report",
    tags=["Report"],
)


@router.post(
    "/",
    summary="Запуск генерации отчета и отправки на электронную почту",
    description=(
        "Этот маршрут инициирует генерацию отчета в фоновом процессе. "
        "После вызова пользователю сразу возвращается сообщение о начале генерации отчета, "
        "в то время как сама генерация выполняется асинхронно в фоновом режиме. "
        "После того как отчет сгенерирован, он отправляется на почту пользователя, указанную в body."
    ),
    response_description="Сообщение о старте процесса генерации отчета.",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Процесс генерации отчета был успешно запущен.",
            "content": {
                "application/json": {
                    "example": {"message": "Starting report generation..."},
                },
            },
        },
    },
)
async def generate_report(
    background_tasks: BackgroundTasks, body: EmailSchema
) -> SuccessResponse:
    """
    Асинхронно инициирует процесс генерации отчета и отправки его на почту.

    - Генерирует отчет на основе данных в базе данных.
    - Отправляет сгенерированный отчет на указанный email.

    Args:
        background_tasks: Объект для управления фоновыми задачами.
        body: Email пользователя, для отправки отчета по электронной почте.

    Returns:
        SuccessResponse: Сообщение, подтверждающее, что процесс генерации отчета был успешно запущен.
    """
    background_tasks.add_task(
        ReportRepository.generate_report_and_send_to_email, email=body
    )
    return SuccessResponse(message="Starting report generation...")
