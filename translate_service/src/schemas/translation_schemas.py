from pydantic import BaseModel


class TranslatedNewsSchema(BaseModel):
    """
    Схема для представления переведенной новости.
    """

    news_id: int
    title: str
    content: str
