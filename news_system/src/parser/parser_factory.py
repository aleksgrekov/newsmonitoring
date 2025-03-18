from sqlalchemy.ext.asyncio import AsyncSession

from news_system.src.parser.article_parser import ArticleParser
from news_system.src.parser.cnn_parser import CNNParser
from news_system.src.parser.http_requester import HttpRequester
from news_system.src.parser.interfaces import INewsParser
from news_system.src.repositories.last_modified_repository import LastModifiedRepository


class ParserFactory:
    """
    Фабрика для создания парсеров новостей.

    Методы:
        - create_cnn_parser: Создает парсер для CNN.
    """

    @staticmethod
    def create_cnn_parser(session: AsyncSession) -> INewsParser:
        """
        Создает парсер для CNN.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.

        Returns:
            INewsParser: Объект парсера CNN.
        """
        http_requester = HttpRequester()
        article_parser = ArticleParser()
        last_modified_repository = LastModifiedRepository()
        return CNNParser(
            session, http_requester, article_parser, last_modified_repository
        )
