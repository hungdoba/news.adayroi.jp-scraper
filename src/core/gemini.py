"""
AI processing module using Google Gemini API.
This module handles article grouping and translation using Gemini AI.
"""
from utils.file import sanitize_yaml_value
import logging
import os
import json
import time
import datetime
from typing import Optional
from google import genai


logger = logging.getLogger(__name__)

GEMINI_MODEL = 'gemini-2.5-flash'

PROMPT_GROUP_ARTICLES = r"""Optimize this JSON file by grouping related news articles based on their content, creating concise and descriptive summary titles for each group, and preserving ungrouped articles with their original titles. Ensure the titles are written in Japanese and reflect the core themes of the articles.

**Input format**:
```json
[
    {
        "id": 1,
        "raw_id": "0542e995e9ad3a5245c08127165b58dd3441e769",
        "title": "日ベトナム首脳会談　防衛協力強化で一致",
        "thumbnail": "https://newsatcl-pctr.c.yimg.jp/t/amd-img/20250430-00051007-asahibcv-000-1-thumb.jpg"
    },
    {
        "id": 2,
        "raw_id": "6ed68f1a3325700ee6500e304dbb4ff10d0de5d4",
        "title": "石破首相がベトナム・チン首相と首脳会談　トランプ政権の関税措置・対抗する中国の報復措置の世界経済への影響など議論",
        "thumbnail": "https://newsatcl-pctr.c.yimg.jp/t/amd-img/20250430-00065351-mbsnews-000-1-thumb.jpg"
    },
    {
        "id": 3,
        "raw_id": "3c622c782eac73e918f904e48a48c6379f151f17",
        "title": "今日の歴史（4月29日）",
        "thumbnail": "https://newsatcl-pctr.c.yimg.jp/t/amd-img/20250430-00010002-minkabu-000-1-view.jpg"
    }
]
```

**Output format**:
```json
[
    {
        "title": "Descriptive summary title for grouped news articles in Japanese",
        "id": [
            1,
            2
        ],
        "thumbnail": [empty]
    },
    {
        "title": "Original title for ungrouped article",
        "id": [3],
        "thumbnail": [empty]
    }
]
```

**Instructions**:
1. Analyze the titles of the input articles to identify common themes or topics.
2. Group articles that share a clear connection (e.g., same event, topic, or context) into a single entry.
3. Create a concise, meaningful summary title in Japanese for each group, capturing the essence of the grouped articles.
4. For articles that do not belong to any group, retain their original titles and list them individually with their IDs.
5. Ensure the output JSON is properly formatted and matches the specified structure.
6. The "thumbnail" field should be an empty array for all entries in the output JSON.

**Example Output** for the given input:
```json
[
    {
        "title": "日ベトナム首脳会談：防衛協力と世界経済の議論",
        "id": [
            1,
            2
        ],
        "thumbnail": []
    },
    {
        "title": "今日の歴史（4月29日）",
        "id": [3],
        "thumbnail": []
    }
]
```

Now, please generate the optimized JSON output based on the provided input, following the instructions and format above.

"""

PROMPT_TRANSLATE_ARTICLES = r"""Translate the following Japanese news article to Vietnamese with proper diacritical marks (tiếng Việt có dấu), preserving and extending the Markdown format as specified below. Output as JSON with the structure shown in the instructions.
    Instructions:
    1. Translation Accuracy:
        - Translate the Japanese text into natural, idiomatic Vietnamese with full diacritical marks.
        - Ensure no Japanese text remains untranslated.
        - Use proper Vietnamese orthography with all tone marks and diacritics.
    2. Output Structure:
        - Return a valid JSON with the following structure:
        ```json
        {{
            "title": "<Concise Title (max 50 characters) without special characters like \: or \" or \' etc.>",
            "slug": "<URL-friendly slug max 50 characters: lowercase ASCII only, use hyphens between words, no spaces or special characters>",
            "description": "<Brief Description of the article in Vietnamese without special characters like \: or \" or \' etc.>",
            "use": <Is this article related with Vietnamese people?, true or false>,
            "content": "<Article Content in Markdown format>"
        }}
        ```
    3. Content Extraction and Formatting:
        - Remove: 
        - Sections like "Related Articles" (関連記事), author information, and source information.
        - Social media sharing links, comments, and any non-content-related.
        - The creator information and any other irrelevant sections.
        - Preserve:
        - All image which has local path in the article, ex: ![](image/name.png).
        - All necessary links and images, ensuring the Markdown syntax for them is correct.
        - Headings, lists, and other structural elements.
        - Title and Description:
        - Create a concise title (maximum 50 characters) that accurately reflects the article's content.
        - Write a brief description summarizing the article's main points.
    4. Content Integrity:
        - Do not add, omit, or alter any information from the original article, except for removing unrelated sections as specified.
    5. Language:
        - The output must be entirely in Vietnamese with full diacritical marks (tiếng Việt có dấu).
    6. Output Constraints:
        - Return ONLY the JSON structure without any explanatory text.
        - Keep image links, hyperlinks, and other embedded content as they are in the content field.
    7. Additional Notes:
        - Ensure the translation is culturally appropriate and avoids literal translations that may sound unnatural in Vietnamese.
        - Maintain the tone and style of the original article.
        - Format the content to be SEO-friendly:
         Use appropriate heading hierarchy (H1, H2, H3)
         Include relevant keywords naturally in headings and content
         Ensure URL-friendly slugs with keywords when possible
         Break content into scannable chunks with subheadings

    Japanese Markdown Input:
    

"""


# Initialize the client if API is available
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def group_article(file_path: str) -> Optional[str]:
    """
    Group related articles using Gemini AI.

    Args:
        file_path: Path to the JSON file containing articles

    Returns:
        JSON string of grouped articles or None if failed
    """
    if not client:
        logger.warning("Gemini AI not available. Using fallback grouping...")
        return _fallback_group_articles(file_path)

    if not file_path:
        logger.error("File path is None, cannot process grouping.")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_content = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to read file: {e}")
        return None

    prompt = PROMPT_GROUP_ARTICLES + \
        json.dumps(json_content, ensure_ascii=False)
    max_retries = 3
    retry_delay = 5
    response = None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[prompt],
            )
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.error(
                    f"Error generating content (attempt {attempt+1}/{max_retries}): {e}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error(f"Failed after {max_retries} attempts: {e}")
                return None

    if not response or not hasattr(response, "text") or not response.text:
        logger.error("No response from API")
        return None

    response_text = response.text.strip()

    # Extract JSON from code blocks
    if "```json" in response_text:
        try:
            json_str = response_text.split("```json", 1)[
                1].split("```", 1)[0].strip()
        except IndexError:
            json_str = response_text
    elif "```" in response_text:
        try:
            json_str = response_text.split(
                "```", 1)[1].split("```", 1)[0].strip()
        except IndexError:
            json_str = response_text
    else:
        json_str = response_text

    try:
        return json.dumps(json.loads(json_str), ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON response")
        logger.error(f"Raw response: {response_text}")
        return None


def translate_article(file_path):
    """
    Translate a single article from Japanese to Vietnamese using Gemini AI.

    Args:
        file_path: Path to the input markdown file

    Returns:
        Dictionary with translated content or error message
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_content = file.read()
        lines = markdown_content.splitlines()
        thumbnail = None
        if lines and lines[0].startswith("![]("):
            thumbnail = lines[0]
            lines.pop(0)
        markdown_content = "\n".join(lines)

    prompt = PROMPT_TRANSLATE_ARTICLES + markdown_content
    max_retries = 3
    retry_delay = 5
    response = None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[prompt],
            )
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.error(
                    f"Error generating content (attempt {attempt+1}/{max_retries}): {e}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error(f"Failed after {max_retries} attempts: {e}")
                return {"error": str(e)}

    if not response or not hasattr(response, "text") or not response.text:
        logger.error("No response from API")
        return {"error": "No response from API"}
    response_text = response.text.strip()

    if "```json" in response_text and "```" in response_text.split("```json", 1)[1]:
        json_str = response_text.split("```json", 1)[
            1].split("```", 1)[0].strip()
    elif "```" in response_text and "```" in response_text.split("```", 1)[1]:
        json_str = response_text.split("```", 1)[1].split("```", 1)[0].strip()
    else:
        json_str = response_text

    try:
        result = json.loads(json_str)
        if thumbnail:
            thumbnail = thumbnail.replace("![](", "").replace(")", "")
            result["thumbnail"] = thumbnail
        return result
    except json.JSONDecodeError:
        logger.error("Failed to parse translation result")
        logger.error(f"Raw response: {response.text}")
        return response.text


def translate_article_list(input_folder, output_folder="data/5.translated"):
    """
    Translate all markdown articles in input_folder and save to output_folder.

    Args:
        input_folder: Folder containing markdown files to translate
        output_folder: Folder to save translated files
    """
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith('.md'):
            file_path = os.path.join(input_folder, filename)
            translated_content = translate_article(file_path)

            if isinstance(translated_content, dict):
                pass
            elif isinstance(translated_content, str):
                try:
                    translated_content = json.loads(translated_content)
                except json.JSONDecodeError:
                    logger.error(
                        f"Failed to parse translation result for {filename}")
                    continue

            title = sanitize_yaml_value(translated_content.get('title', ''))
            slug = translated_content.get('slug', '')
            thumbnail = translated_content.get('thumbnail', '')
            description = sanitize_yaml_value(
                translated_content.get('description', ''))
            use = translated_content.get('use', False)
            content = translated_content.get('content', '')

            if not title or not slug or not description or not content:
                logger.error(
                    f"Missing required fields in translation for {filename}")
                continue

            output_file_path = os.path.join(output_folder, f"{slug}.md")
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            yaml_header = f"""---
title: "{title}"
slug: "{slug}"
thumbnail: "{thumbnail}"
description: "{description}"
use: {str(use).lower()}
created_at: "{created_at}"
---

"""

            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(yaml_header + content)

            logger.info(f"Translated {filename} to {output_file_path}")
            time.sleep(4)


def _fallback_group_articles(file_path: str) -> Optional[str]:
    """
    Fallback grouping method when AI is not available.
    Creates individual groups for each article.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)

        groups = []
        for article in articles:
            group = {
                "id": [article["raw_id"]],
                "title": article["title"],
                "thumbnail": article["thumbnail"]
            }
            groups.append(group)

        return json.dumps(groups, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in fallback grouping: {e}")
        return None
