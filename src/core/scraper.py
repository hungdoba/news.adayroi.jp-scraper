import os
import requests
from bs4 import BeautifulSoup

from models.new_feed import NewsFeed
from utils.html import format_raw_html


def scrape_news_feed(url, selector=None):
    if not selector:
        return []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    news_items = soup.select(selector)

    articles = []
    index = 0
    for news in news_items:
        for link in news.select('a'):
            index += 1
            href = link.get('href')
            if not href:
                continue

            article_id = href.split('/')[-1]

            img = link.select_one('img')
            if img and img.get('src'):
                thumbnail = img.get('src').split('?')[0]

                articles.append(NewsFeed(
                    id=index,
                    raw_id=article_id,
                    url=href,
                    thumbnail=thumbnail,
                    title="",
                ))

    return articles


def fetch_and_save_article(url, article_id, output_dir):
    if article_id == "000":
        return None

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Make the request
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Create output directory
    output_dir = os.path.join(os.getcwd(), output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Process and save content
    file_path = os.path.join(output_dir, f"{article_id}.html")
    title_content, format_content = format_raw_html(response.text)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(format_content)

    return title_content
