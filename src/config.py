"""
Configuration management for the news scraper application.
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Config:
    """Application configuration class."""

    # API Configuration
    feed_url: str = ""
    news_feed_selector: str = ""
    google_api_key: str = ""

    # Directory Paths
    data_dir: str = ""
    yahoo_dir: str = ""
    obsidian_dir: str = ""
    nextjs_dir: str = ""

    # File Paths
    obsidian_path: str = ""
    ignore_file_path: str = ""
    processed_ids_file: str = ""
    npm_command: str = ""

    # URLs
    nextjs_url: str = ""

    # Pipeline Directories
    dir_step_1: str = ""
    dir_step_2: str = ""
    dir_step_3: str = ""
    dir_step_4: str = ""
    dir_step_5: str = ""
    dir_step_6: str = ""
    dir_step_8: str = ""

    def __post_init__(self):
        """Initialize configuration from environment variables."""
        self.feed_url = os.getenv("FEED_URL", "")
        self.news_feed_selector = os.getenv(
            "NEWS_FEED_SELECTOR", ".newsFeed_list")
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")

        self.data_dir = os.getenv("DATA_DIR", "data")
        self.yahoo_dir = os.getenv("YAHOO_DIR", "yahoo")
        self.obsidian_dir = os.getenv("OBSIDIAN_DIR", "obsidian")
        self.nextjs_dir = os.getenv("NEXTJS_DIR", "")

        self.obsidian_path = os.getenv("OBSIDIAN_PATH", "")
        self.ignore_file_path = os.getenv("IGNORE_FILE_PATH", "data/.ignore")
        self.processed_ids_file = os.getenv(
            "PROCESSED_IDS_FILE", "processed_ids.txt")
        self.npm_command = os.getenv("NPM_COMMAND", "npm")

        self.nextjs_url = os.getenv("NEXTJS_URL", "https://news.adayroi.jp")

        self.dir_step_1 = os.getenv("DIR_STEP_1", "data/1.raw_html")
        self.dir_step_2 = os.getenv("DIR_STEP_2", "data/2.groups")
        self.dir_step_3 = os.getenv("DIR_STEP_3", "data/3.merged")
        self.dir_step_4 = os.getenv("DIR_STEP_4", "data/4.markdown")
        self.dir_step_5 = os.getenv("DIR_STEP_5", "data/5.translated")
        self.dir_step_6 = os.getenv("DIR_STEP_6", "data/6.images/images")
        self.dir_step_8 = os.getenv("DIR_STEP_8", "data/6.images")

    def validate(self) -> None:
        """Validate required configuration values."""
        required_fields = [
            ("feed_url", self.feed_url),
            ("google_api_key", self.google_api_key),
        ]

        missing_fields = [field for field,
                          value in required_fields if not value]

        if missing_fields:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing_fields)}")

    def get_pipeline_dirs(self) -> list[str]:
        """Get all pipeline directory paths."""
        return [
            self.dir_step_1,
            self.dir_step_2,
            self.dir_step_3,
            self.dir_step_4,
            self.dir_step_5,
            self.dir_step_6,
            self.dir_step_8,
        ]


# Global configuration instance
config = Config()
