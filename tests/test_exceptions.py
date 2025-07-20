"""
Unit tests for the exceptions module.
"""
import unittest

from src.exceptions import (
    NewsScraperError,
    ConfigurationError,
    ScrapingError,
    ProcessingError,
    AIProcessingError,
    DeploymentError,
    FileOperationError
)


class TestExceptions(unittest.TestCase):
    """Test cases for custom exceptions."""

    def test_news_scraper_error_inheritance(self):
        """Test that all custom exceptions inherit from NewsScraperError."""
        exceptions = [
            ConfigurationError,
            ScrapingError,
            ProcessingError,
            AIProcessingError,
            DeploymentError,
            FileOperationError
        ]

        for exception_class in exceptions:
            self.assertTrue(issubclass(exception_class, NewsScraperError))
            self.assertTrue(issubclass(exception_class, Exception))

    def test_exception_can_be_raised_and_caught(self):
        """Test that exceptions can be properly raised and caught."""
        with self.assertRaises(ConfigurationError):
            raise ConfigurationError("Test configuration error")

        with self.assertRaises(ScrapingError):
            raise ScrapingError("Test scraping error")

        with self.assertRaises(NewsScraperError):
            # Should catch any of our custom exceptions
            raise ProcessingError("Test processing error")

    def test_exception_messages(self):
        """Test that exceptions can carry custom messages."""
        message = "Custom error message"

        try:
            raise ConfigurationError(message)
        except ConfigurationError as e:
            self.assertEqual(str(e), message)


if __name__ == '__main__':
    unittest.main()
