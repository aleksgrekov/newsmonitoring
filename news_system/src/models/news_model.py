from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base_model import Base


class News(Base):
    __tablename__ = "news"

    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[Optional[str]] = mapped_column(Text)
    pub_date: Mapped[Optional[datetime]]
    url: Mapped[str] = mapped_column(String(255), unique=True)

    def __repr__(self):
        return (
            f"<News("
            f"id={self.id!r}, "
            f"title={self.title!r}, "
            f"content={self.content[:10]!r}..., "
            f"pub_date={self.pub_date!r}, "
            f"url={self.url!r}"
            f")>"
        )
