from fastapi import APIRouter
from report_service.src.api.report_router import router as report_router

base_router = APIRouter(
    prefix="/api",
    tags=["API"],
)

base_router.include_router(report_router)
