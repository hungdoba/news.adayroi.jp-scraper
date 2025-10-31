"""
Web scraping module for fetching news articles.

This module provides functions to scrape news feeds and fetch individual articles.
"""
import os
import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional

from models.new_feed import NewsFeed
from utils.html import format_raw_html
from exceptions import ScrapingError

logger = logging.getLogger(__name__)


def scrape_news_feed(url: str, selector: Optional[str] = None) -> list[NewsFeed]:
    """
    Scrape news articles from a feed URL.

    Args:
        url: The feed URL to scrape
        selector: CSS selector for news items. If None, returns empty list.

    Returns:
        List of NewsFeed objects containing article metadata

    Raises:
        ScrapingError: If the request fails or parsing errors occur

    Example:
        >>> articles = scrape_news_feed("https://example.com", ".news-item")
        >>> print(len(articles))
        15
    """
    if not selector:
        logger.warning("No selector provided, returning empty list")
        return []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        logger.info(f"Scraping news feed from {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ScrapingError(
            f"Failed to fetch news feed from {url}: {e}") from e

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.select(selector)
        logger.info(
            f"Found {len(news_items)} news items with selector '{selector}'")
    except Exception as e:
        raise ScrapingError(f"Failed to parse HTML from {url}: {e}") from e

    articles = []
    index = 0

    for news in news_items:
        for link in news.select('a'):
            index += 1
            href = link.get('href')

            # Type narrowing: ensure href is a string
            if not href or not isinstance(href, str):
                continue

            article_id = href.split('/')[-1]

            img = link.select_one('img')
            if img:
                src = img.get('src')
                # Type narrowing: ensure src is a string
                if src and isinstance(src, str):
                    thumbnail = src.split('?')[0]

                    articles.append(NewsFeed(
                        id=index,
                        raw_id=article_id,
                        url=href,
                        thumbnail=thumbnail,
                        title="",
                    ))

    logger.info(f"Successfully extracted {len(articles)} articles from feed")
    return articles


def fetch_and_save_article(url: str, article_id: str, output_dir: str) -> Optional[str]:
    """
    Fetch an article's content and save it to an HTML file.

    Args:
        url: URL of the article to fetch
        article_id: Unique identifier for the article
        output_dir: Directory where the HTML file will be saved

    Returns:
        The article title if successful, None if failed or article_id is "000"

    Raises:
        ScrapingError: If the request fails or parsing errors occur

    Example:
        >>> title = fetch_and_save_article(
        ...     "https://example.com/article/123",
        ...     "123",
        ...     "data/raw_html"
        ... )
        >>> print(title)
        "Breaking News Title"
    """
    if article_id == "000":
        logger.debug("Skipping article with ID '000'")
        return None

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        logger.info(f"Fetching article {article_id} from {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ScrapingError(
            f"Failed to fetch article {article_id} from {url}: {e}"
        ) from e

    try:
        # Create output directory
        output_dir = os.path.join(os.getcwd(), output_dir)
        os.makedirs(output_dir, exist_ok=True)

        # Process and save content
        file_path = os.path.join(output_dir, f"{article_id}.html")
        title_content, format_content = format_raw_html(response.text)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(format_content)

        logger.info(f"Successfully saved article {article_id} to {file_path}")
        return title_content

    except Exception as e:
        raise ScrapingError(
            f"Failed to process and save article {article_id}: {e}"
        ) from e
