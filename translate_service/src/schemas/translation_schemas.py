from pydantic import BaseModel


class TranslatedNewsSchema(BaseModel):
    """
    Схема для представления переведенной новости.

    Args:
        news_id (int): Уникальный идентификатор новости.
        title (str): Заголовок новости.
        content (str): Текст переведенной новости.

    Returns:
        TranslatedNewsSchema: Объект, представляющий переведенную новость.
    """

    news_id: int
    title: str
    content: str
