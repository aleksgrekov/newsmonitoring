import asyncio
from typing import Dict, List

import aiohttp
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from src.configs.parser_config import parser_settings
from src.logger.logger_config import configure_logging

logger = configure_logging(__name__)


class ArticleParser:
    def __init__(self):
        self.__headers = self.__create_headers

    @property
    def __create_headers(self):
        return {
            "Accept": parser_settings.YOUR_ACCEPT_HEADER,
            "User-Agent": parser_settings.YOUR_USER_AGENT_HEADER,
        }

    async def parse_article_page(self, url: str) -> Dict[str, str]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, headers=self.__headers, timeout=45
                ) as response:
                    response.raise_for_status()
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, "lxml")

                    content_container = soup.find("div", class_="article__content")
                    paragraphs = (
                        content_container.find_all("p") if content_container else []
                    )
                    full_text = " ".join(p.text.strip() for p in paragraphs)

                    date_tag = soup.find("div", class_="timestamp vossi-timestamp")
                    raw_date = date_tag.text.strip() if date_tag else ""
                    raw_date = (
                        raw_date.replace("Updated", "").replace("Published", "").strip()
                    )

                    pub_date = None
                    if raw_date:
                        try:
                            pub_date = date_parser.parse(
                                raw_date, ignoretz=True
                            ).isoformat()
                        except ValueError as e:
                            logger.error(f"Ошибка при парсинге даты: {e}")

                    return {"full_text": full_text, "pub_date": pub_date}
        except Exception as e:
            logger.error(f"Ошибка при парсинге страницы новости {url}: {e}")
            return {"full_text": "", "pub_date": None}

    async def parse_page(self, html_content: bytes) -> List[Dict[str, str]]:
        try:
            soup = BeautifulSoup(html_content, "lxml")
            containers = soup.select("div.card.container__item")

            tasks = [
                self.__parse_cnn_container(container)
                for container in containers
                if container
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            print(len(results))
            return [result for result in results if isinstance(result, dict)]
        except Exception as e:
            logger.error(f"Ошибка при парсинге страницы: {e}")
            return []

    # async def parse_page(self, html_content: bytes) -> List[Dict[str, str]]:
    #     try:
    #         soup = BeautifulSoup(html_content, "lxml")
    #         containers = soup.select("div.card.container__item")
    #         with ThreadPoolExecutor() as executor:
    #             # Параллельная обработка всех контейнеров
    #             futures = [
    #                 executor.submit(await self.__parse_cnn_container, container)
    #                 for container in containers
    #                 if container
    #             ]
    #             results = []
    #             for future in as_completed(futures):
    #                 result = future.result()
    #                 if result:
    #                     results.append(result)
    #             return results
    # return [
    #     self.__parse_cnn_container(container)
    #     for container in containers
    #     if container
    # ]
    # except Exception as e:
    #     logger.error(f"Ошибка при парсинге страницы: {e}")
    #     return []

    async def __parse_cnn_container(self, container) -> Dict[str, str]:
        try:
            headline_tag = container.find("span", class_="container__headline-text")
            title = headline_tag.text.strip() if headline_tag else "No title"

            link_tag = container.find("a", href=True)
            link = link_tag["href"] if link_tag else "#"
            if not link.startswith("http"):
                link = f"https://www.cnn.com{link}"

            article_data = await self.parse_article_page(link)
            return {"title": title, "url": link, **article_data}
        except Exception as e:
            logger.error(f"Ошибка при парсинге контейнера: {e}")
            return {}
