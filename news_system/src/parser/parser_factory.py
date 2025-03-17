from sqlalchemy.ext.asyncio import AsyncSession

from news_system.src.parser.article_parser import ArticleParser
from news_system.src.parser.cnn_parser import CNNParser
from news_system.src.parser.http_requester import HttpRequester
from news_system.src.parser.interfaces import INewsParser


class ParserFactory:
    @staticmethod
    def create_cnn_parser(session: AsyncSession) -> INewsParser:
        http_requester = HttpRequester(session)
        article_parser = ArticleParser()
        return CNNParser(http_requester, article_parser)
