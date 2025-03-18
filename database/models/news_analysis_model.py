from models.base_model import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class NewsAnalysis(Base):
    __tablename__ = "news_analysis"
    sentiment: Mapped[float]
    keywords: Mapped[str] = mapped_column(String)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id", ondelete="CASCADE"))

    news_analyse = relationship(
        "News",
        back_populates="analysis",
    )
