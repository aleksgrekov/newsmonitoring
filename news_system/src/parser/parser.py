from dateutil import parser
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_article_page(url: str) -> Dict[str, str]:
    """Парсинг страницы новости для извлечения полного текста и даты публикации."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        # Полный текст новости
        content_container = soup.find(
            "div", class_="article__content"
        )  # Класс для контейнера текста
        paragraphs = content_container.find_all("p") if content_container else []
        full_text = " ".join(p.text.strip() for p in paragraphs)

        # Дата публикации
        date_tag = soup.find(
            "div", class_="timestamp vossi-timestamp"
        )  # Класс для даты
        if date_tag:
            raw_date = date_tag.text.strip()
            # Убираем слова "Updated" и "Published", очищаем пробелы
            raw_date = raw_date.replace("Updated", "").replace("Published", "").strip()

            # Используем dateutil.parser для разбора даты
            try:
                pub_date = parser.parse(raw_date)
            except ValueError as e:
                print(f"Ошибка при парсинге даты: {e}")
                pub_date = None
        else:
            pub_date = None

        return {
            "full_text": full_text,
            "pub_date": pub_date,
        }
    except Exception as e:
        logger.error(f"Ошибка при парсинге страницы новости {url}: {e}")
        return {"full_text": "", "pub_date": None}


def parse_cnn_container(container) -> Dict[str, str]:
    """Парсинг одного контейнера новости."""
    try:
        # Заголовок
        headline_tag = container.find("span", class_="container__headline-text")
        title = headline_tag.text.strip() if headline_tag else "No title"

        # Ссылка
        link_tag = container.find("a", href=True)
        link = link_tag["href"] if link_tag and "href" in link_tag.attrs else "#"
        if not link.startswith("http"):
            link = f"https://www.cnn.com{link}"  # Добавляем базовый URL, если ссылка относительная

        # Парсим страницу новости для получения полного текста и даты
        article_data = parse_article_page(link)
        full_text = article_data.get("full_text", "")
        pub_date = article_data.get("pub_date", None)

        # Создаем объект новости
        return {
            "title": title,
            "url": link,
            "full_text": full_text,
            "pub_date": pub_date,
        }
    except Exception as e:
        logger.error(f"Ошибка при парсинге контейнера: {e}")
        return {}


def parse_cnn_page(url: str, headers: dict) -> List[Dict[str, str]]:
    """Парсинг страницы CNN."""
    try:
        response = requests.get(url, headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        # Поиск всех контейнеров новостей
        containers = soup.select("div.card.container__item")
        news_list = []

        for i, container in enumerate(containers):
            news = parse_cnn_container(container)
            if news:
                news_list.append(news)
            if i == 10:
                break
        for index, n in enumerate(news_list):
            print(
                "NEWS №{index}"
                "\n\t{title}"
                "\n\t{url}"
                "\n\t\t{full_text}"
                "\n\t{pub_date}".format(
                    index=index,
                    title=n.get("title"),
                    url=n.get("url"),
                    image_url=n.get("image_url"),
                    full_text=n.get("full_text"),
                    pub_date=n.get("pub_date"),
                )
            )

        return news_list
    except Exception as e:
        logger.error(f"Ошибка при запросе страницы {url}: {e}")
        return []


def collect_news(url: str, headers: dict) -> List[Dict[str, str]]:

    logger.info(f"Парсинг страницы: {url}")
    news_list = parse_cnn_page(url, headers)
    return news_list


collect_news(url, headers)
