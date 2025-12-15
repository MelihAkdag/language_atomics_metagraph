"""Unit tests for TextCleaner."""

import os
import sys
import unittest

from nlp.preprocessing.TextCleaner import TextCleaner


class TestTextCleaner(unittest.TestCase):
    """Test cases for TextCleaner class."""
    
    def test_remove_line_breaks(self):
        """Test line break removal."""
        text = "Hello\nWorld\nTest"
        expected = "Hello World Test"
        result = TextCleaner.remove_line_breaks(text)
        self.assertEqual(result, expected)
    
    def test_remove_multiple_spaces(self):
        """Test multiple space removal."""
        text = "Hello    World   Test"
        expected = "Hello World Test"
        result = TextCleaner.remove_multiple_spaces(text)
        self.assertEqual(result, expected)
    
    def test_clean(self):
        """Test complete cleaning process."""
        text = "Hello\nWorld    \n  Test   Example"
        expected = "Hello World Test Example"
        result = TextCleaner.clean(text)
        self.assertEqual(result, expected)
    
    def test_empty_string(self):
        """Test cleaning empty string."""
        text = ""
        expected = ""
        result = TextCleaner.clean(text)
        self.assertEqual(result, expected)
    
    def test_single_line_break(self):
        """Test single line break replacement."""
        text = "Before\nAfter"
        expected = "Before After"
        result = TextCleaner.clean(text)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
