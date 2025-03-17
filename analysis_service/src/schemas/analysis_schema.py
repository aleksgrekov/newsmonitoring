from pydantic import BaseModel


class NewsAnalysisCreate(BaseModel):
    sentiment: float
    keywords: str
    news_id: int
