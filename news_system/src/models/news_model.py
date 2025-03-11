from datetime import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base_model import Base


class News(Base):
    __tablename__ = "news"

    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    pub_date: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=datetime.now
    )
    source: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(255), unique=True)

    def __repr__(self):
        return (
            f"<News("
            f"id={self.id!r}, "
            f"title={self.title!r}, "
            f"pub_date={self.pub_date!r}, "
            f"source={self.source!r}, "
            f"url={self.url!r}"
            f")>"
        )
