from sqlalchemy.ext.asyncio import AsyncSession

from news_system.src.parser.article_parser import ArticleParser
from news_system.src.parser.cnn_parser import CNNParser
from news_system.src.parser.http_requester import HttpRequester
from news_system.src.parser.interfaces import INewsParser


class ParserFactory:
    """
    Фабрика для создания парсеров.
    """

    @staticmethod
    def create_cnn_parser(session: AsyncSession) -> INewsParser:
        """
        Создает парсер для CNN.

        :param session: Асинхронная сессия SQLAlchemy.
        :return: Объект парсера CNN.
        """
        http_requester = HttpRequester()
        article_parser = ArticleParser()
        return CNNParser(session, http_requester, article_parser)
