from fastapi import APIRouter

router = APIRouter(prefix="/news")


@router.get("/")
async def start_news_parser():
    return {"message": "Ok"}
