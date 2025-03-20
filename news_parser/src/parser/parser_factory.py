from sqlalchemy.ext.asyncio import AsyncSession
from src.parser.article_parser import ArticleParser
from src.parser.cnn_parser import CNNParser
from src.parser.http_requester import HttpRequester
from src.parser.interfaces import INewsParser
from src.repositories.last_modified_repository import LastModifiedRepository


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
