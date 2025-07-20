import re
from bs4 import BeautifulSoup, Tag


def remove_multiple_attributes(html: str, attribute_names: list[str]) -> str:
    modified_html = html
    for attribute_name in attribute_names:
        modified_html = remove_attribute(modified_html, attribute_name)
    return modified_html


def remove_attribute(html: str, attribute_name: str) -> str:
    pattern = rf'\s+{attribute_name}\s*=\s*"[^"]*?"|\s+{attribute_name}\s*=\s*\'[^\']*?\''
    return re.sub(pattern, '', html, flags=re.IGNORECASE)


def remove_html_comments(html: str) -> str:
    return re.sub(r'<!--[\s\S]*?-->', '', html)


def extract_article_info(article: Tag) -> tuple[str, str]:
    if not article:
        return "", ""

    title_element = article.select_one('h1')
    title_content = title_element.text.strip() if title_element else ""
    content_element = article.select_one('div.article_body')

    if content_element and content_element.text.strip():
        soup = BeautifulSoup("<article></article>", 'html.parser')
        new_article = soup.article

        if title_element:
            new_article.append(title_element)
        new_article.append(content_element)

        return title_content, str(new_article)

    return title_content, str(article) if article else ""


def change_a_tags_with_img(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    modified_html = str(soup)

    for a_tag in soup.find_all('a'):
        if a_tag.find('img'):
            a_html = str(a_tag)
            new_html = re.sub(r'<a\s+[^>]*?>', '<div>', a_html)
            new_html = new_html.replace('</a>', '</div>')
            modified_html = modified_html.replace(a_html, new_html, 1)

    return modified_html


def format_raw_html(html_content: str) -> tuple[str, str]:
    soup = BeautifulSoup(html_content, 'html.parser')
    article = soup.find('article')

    # Extract article info
    title_content, formatted_html = extract_article_info(article)

    # Remove specified attributes
    attributes_to_remove = [
        "class", "data-cl-params", "data-ual-view-type",
        "data-ual", "srcset", "type", "alt"
    ]
    formatted_html = remove_multiple_attributes(
        formatted_html, attributes_to_remove)

    # Remove HTML comments and replace a tags with div tags
    formatted_html = remove_html_comments(formatted_html)
    formatted_html = change_a_tags_with_img(formatted_html)

    return title_content, formatted_html
