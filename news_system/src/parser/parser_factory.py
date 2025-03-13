import asyncio

from src.parser.article_parser import ArticleParser
from src.parser.cnn_parser import CNNParser
from src.parser.http_requester import HttpRequester
from src.parser.interfaces import INewsParser


class ParserFactory:
    @staticmethod
    def create_cnn_parser() -> INewsParser:
        http_requester = HttpRequester()
        article_parser = ArticleParser()
        return CNNParser(http_requester, article_parser)


parser = ParserFactory.create_cnn_parser()
news = asyncio.run(parser.collect_news())
print(news)
print(len(news))
