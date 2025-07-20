"""
Unit tests for utility functions.
"""
import unittest
import tempfile
import os
import json
from unittest.mock import patch, mock_open

from src.utils.log import get_all_ids, log_id


class TestLogUtils(unittest.TestCase):
    """Test cases for logging utilities."""

    def test_log_id_creates_file_if_not_exists(self):
        """Test that log_id creates file if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test_log.txt")

            # File shouldn't exist initially
            self.assertFalse(os.path.exists(log_file))

            # Log an ID
            log_id(log_file, "test_id_123")

            # File should now exist
            self.assertTrue(os.path.exists(log_file))

            # Read content
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # Should contain the logged ID
            self.assertIn("test_id_123", content)

    def test_get_all_ids_empty_file(self):
        """Test getting IDs from empty or non-existent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "empty_log.txt")

            # Non-existent file should return empty list
            ids = get_all_ids(log_file)
            self.assertEqual(ids, [])

            # Create empty file
            open(log_file, 'w').close()

            # Empty file should return empty list
            ids = get_all_ids(log_file)
            self.assertEqual(ids, [])

    def test_get_all_ids_with_content(self):
        """Test getting IDs from file with content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "content_log.txt")

            # Create file with test IDs using the correct JSON format
            test_ids = ["id1", "id2", "id3"]
            with open(log_file, 'w', encoding='utf-8') as f:
                for test_id in test_ids:
                    entry = {"timestamp": "2025-07-20T10:00:00", "id": test_id}
                    f.write(json.dumps(entry) + '\n')

            # Get all IDs
            ids = get_all_ids(log_file)

            # Should contain all test IDs in the same order
            self.assertEqual(ids, test_ids)
            self.assertEqual(len(ids), len(test_ids))


if __name__ == '__main__':
    unittest.main()
