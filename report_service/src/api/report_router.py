from fastapi import APIRouter, BackgroundTasks, status

from report_service.src.schemas.base_schemas import SuccessResponse
from report_service.src.repositories.report_repository import ReportRepository

router = APIRouter(
    prefix="/report",
    tags=["Report"],
)


@router.get(
    "/",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_report(background_tasks: BackgroundTasks) -> SuccessResponse:
    background_tasks.add_task(ReportRepository.generate_report)
    return SuccessResponse(message="Starting report generation...")
