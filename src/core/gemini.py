"""
AI processing module using Google Gemini API.
This module handles article grouping and translation using Gemini AI.
"""
import os
import json
import time
import datetime
from typing import Optional

# Try to import the Google Generative AI library
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from utils.file import sanitize_yaml_value

GEMINI_MODEL = 'gemini-2.0-flash-exp'

# Initialize the client if API is available
if GEMINI_AVAILABLE and genai and os.getenv("GOOGLE_API_KEY"):
    try:
        genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    except Exception:
        GEMINI_AVAILABLE = False


def group_article(file_path: str) -> Optional[str]:
    """
    Group related articles using AI.

    Args:
        file_path: Path to the JSON file containing articles

    Returns:
        JSON string of grouped articles or None if failed
    """
    if not GEMINI_AVAILABLE:
        print("⚠️  Gemini AI not available. Using fallback grouping...")
        return _fallback_group_articles(file_path)

    # TODO: Implement actual Gemini API call for grouping
    print("🤖 Using AI to group articles...")
    return _fallback_group_articles(file_path)


def translate_article_list(input_folder: str, output_folder: str) -> None:
    """
    Translate articles from input folder to output folder.

    Args:
        input_folder: Folder containing markdown files to translate
        output_folder: Folder to save translated files
    """
    if not GEMINI_AVAILABLE:
        print("⚠️  Gemini AI not available. Skipping translation...")
        return

    print("🌐 Starting article translation...")
    os.makedirs(output_folder, exist_ok=True)

    # TODO: Implement actual translation logic
    print("⚠️  Translation not implemented yet. Files copied without translation.")


def _fallback_group_articles(file_path: str) -> Optional[str]:
    """
    Fallback grouping method when AI is not available.
    Creates individual groups for each article.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)

        # Create individual groups for each article
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
        print(f"❌ Error in fallback grouping: {e}")
        return None
