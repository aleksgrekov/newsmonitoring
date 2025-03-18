from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class NewsSchema(BaseModel):
    """
    Схема для представления новости.

    Attributes:
        title (str): Заголовок новости.
        content (Optional[str]): Текст новости.
        pub_date (Optional[datetime]): Дата публикации новости.
        url (str): URL новости. Должен соответствовать формату HTTP/HTTPS.
    """

    title: str = Field(
        ...,
        title="Заголовок новости",
        description="Основной заголовок новостной статьи.",
        example="Новые технологии в IT",
        min_length=1,
        max_length=255,
    )
    content: Optional[str] = Field(
        default=None,
        title="Текст новости",
        description="Основной текст новостной статьи.",
        example="Компания X представила новую технологию...",
    )
    pub_date: Optional[datetime] = Field(
        default=None,
        title="Дата публикации",
        description="Дата и время публикации новости.",
        example="2023-10-01T12:00:00",
    )
    url: str = Field(
        ...,
        title="URL новости",
        description="Ссылка на новость. Должна начинаться с http:// или https://.",
        example="https://example.com/news/new-technology",
        pattern=r"https?://\S+",
    )


class NewsResponseSchema(BaseModel):
    """
    Схема для ответа API, содержащего список новостей.

    Attributes:
        header (Optional[str]): Заголовок ответа.
        news (List[NewsSchema]): Список новостей.
    """

    header: Optional[str] = Field(
        default=None,
        title="Заголовок ответа",
        description="Дополнительный заголовок для ответа API.",
        example="Последние новости",
    )
    news: List[NewsSchema] = Field(
        ...,
        title="Список новостей",
        description="Список новостных статей.",
    )
