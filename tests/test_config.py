"""
Unit tests for the configuration module.
"""
import unittest
import os
from unittest.mock import patch

from src.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()

    def test_config_initialization(self):
        """Test that config initializes with default values."""
        self.assertEqual(self.config.data_dir, "data")
        self.assertEqual(self.config.news_feed_selector, ".newsFeed_list")
        self.assertEqual(self.config.processed_ids_file, "processed_ids.txt")

    @patch.dict(os.environ, {'DATA_DIR': 'test_data'})
    def test_config_from_env(self):
        """Test that config reads from environment variables."""
        config = Config()
        self.assertEqual(config.data_dir, "test_data")

    def test_validate_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        config = Config()
        config.feed_url = ""
        config.google_api_key = ""

        with self.assertRaises(ValueError):
            config.validate()

    def test_validate_with_required_fields(self):
        """Test validation passes when required fields are present."""
        config = Config()
        config.feed_url = "https://example.com"
        config.google_api_key = "test_key"

        # Should not raise an exception
        config.validate()

    def test_get_pipeline_dirs(self):
        """Test that pipeline directories are returned correctly."""
        dirs = self.config.get_pipeline_dirs()
        self.assertIsInstance(dirs, list)
        self.assertIn(self.config.dir_step_1, dirs)
        self.assertIn(self.config.dir_step_2, dirs)


if __name__ == '__main__':
    unittest.main()
