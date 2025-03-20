from datetime import datetime
from typing import Optional

from src.models.base_model import Base
from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class News(Base):
    __tablename__ = "news"
    __table_args__ = (UniqueConstraint("pub_date", "url", name="pub_date_url_const"),)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[Optional[str]] = mapped_column(Text)
    pub_date: Mapped[Optional[datetime]]
    url: Mapped[str] = mapped_column(String(255))

    analysis = relationship(
        "NewsAnalysis",
        back_populates="news_analyse",
        cascade="all, delete",
        passive_deletes=True,
    )
    translations = relationship(
        "Translation",
        back_populates="news_translation",
    )

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
