"""
Unit tests for the NewsFeed model.
"""
import unittest

from src.models.new_feed import NewsFeed


class TestNewsFeed(unittest.TestCase):
    """Test cases for the NewsFeed class."""

    def setUp(self):
        """Set up test fixtures."""
        self.news_feed = NewsFeed(
            id=1,
            raw_id="test123",
            url="https://example.com/article/test123",
            thumbnail="https://example.com/thumb.jpg",
            title="Test Article Title"
        )

    def test_news_feed_initialization(self):
        """Test that NewsFeed initializes correctly."""
        self.assertEqual(self.news_feed.id, 1)
        self.assertEqual(self.news_feed.raw_id, "test123")
        self.assertEqual(self.news_feed.url,
                         "https://example.com/article/test123")
        self.assertEqual(self.news_feed.thumbnail,
                         "https://example.com/thumb.jpg")
        self.assertEqual(self.news_feed.title, "Test Article Title")

    def test_news_feed_str_representation(self):
        """Test the string representation of NewsFeed."""
        expected = (
            "NewsFeed(id=1, raw_id=test123, "
            "url=https://example.com/article/test123, "
            "thumbnail=https://example.com/thumb.jpg, "
            "title=Test Article Title)"
        )
        self.assertEqual(str(self.news_feed), expected)

    def test_news_feed_dict_conversion(self):
        """Test that NewsFeed can be converted to dict."""
        news_dict = self.news_feed.__dict__
        self.assertIsInstance(news_dict, dict)
        self.assertEqual(news_dict['id'], 1)
        self.assertEqual(news_dict['raw_id'], "test123")


if __name__ == '__main__':
    unittest.main()
