from typing import Optional

from src.models.base_model import Base
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Translation(Base):
    __tablename__ = "translations"
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[Optional[str]] = mapped_column(Text)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id", ondelete="CASCADE"))

    news_translation = relationship(
        "News",
        back_populates="translations",
    )
