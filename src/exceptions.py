"""
Custom exceptions for the news scraper application.
"""


class NewsScraperError(Exception):
    """Base exception for news scraper application."""
    pass


class ConfigurationError(NewsScraperError):
    """Raised when there's a configuration error."""
    pass


class ScrapingError(NewsScraperError):
    """Raised when there's an error during web scraping."""
    pass


class ProcessingError(NewsScraperError):
    """Raised when there's an error during data processing."""
    pass


class AIProcessingError(NewsScraperError):
    """Raised when there's an error during AI processing (Gemini API)."""
    pass


class DeploymentError(NewsScraperError):
    """Raised when there's an error during deployment."""
    pass


class FileOperationError(NewsScraperError):
    """Raised when there's an error during file operations."""
    pass
