"""
Data model for news feed articles.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class NewsFeed:
    """Represents a news feed article."""

    id: int
    raw_id: str
    url: str
    thumbnail: str
    title: str

    def __str__(self) -> str:
        """Return string representation of the news feed article."""
        return (
            f"NewsFeed(id={self.id}, raw_id={self.raw_id}, "
            f"url={self.url}, thumbnail={self.thumbnail}, title={self.title})"
        )
