from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class NewsSchema(BaseModel):
    title: str
    content: Optional[str]
    pub_date: Optional[datetime]
    url: str = Field(pattern=r"https?://\S+")


class NewsResponseSchema(BaseModel):
    header: Optional[str]
    news: List[NewsSchema]
