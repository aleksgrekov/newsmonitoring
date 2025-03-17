from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base


class NewsAnalysis(Base):
    __tablename__ = "news_analysis"
    sentiment: Mapped[float]
    keywords: Mapped[str] = mapped_column(String)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id", ondelete="CASCADE"))

    news = relationship(
        "News",
        back_populates="analysis",
    )
