"""Unit tests for SRLExtractor."""

import os
import sys
import unittest

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
sys.path.insert(0, src_path)

from nlp.extraction.SRLExtractor import SRLExtractor


class TestSRLExtractor(unittest.TestCase):
    """Test cases for SRLExtractor class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.extractor = SRLExtractor()
    
    def test_simple_is_sentence(self):
        """Test extraction from simple IS sentence."""
        sentence = "The cat is small."
        result = self.extractor.extract_primitives(sentence)
        
        self.assertIn('cat', result['subjects'])
        self.assertIn('IS', result['verbs'])
        self.assertIn('small', result['objects'])
    
    def test_simple_has_sentence(self):
        """Test extraction from simple HAS sentence."""
        sentence = "John has a car."
        result = self.extractor.extract_primitives(sentence)
        
        self.assertIn('John', result['subjects'])
        self.assertIn('HAS', result['verbs'])
        self.assertIn('car', result['objects'])
    
    def test_action_verb_sentence(self):
        """Test extraction from action verb sentence."""
        sentence = "Mary runs fast."
        result = self.extractor.extract_primitives(sentence)
        
        self.assertIn('Mary', result['subjects'])
        self.assertIn('run', result['verbs'])  # lemmatized
    
    def test_batch_extraction(self):
        """Test batch sentence extraction."""
        sentences = [
            "The dog is happy.",
            "Alice has a book.",
            "Bob runs quickly."
        ]
        results = self.extractor.extract_batch(sentences)
        
        self.assertEqual(len(results), 3)
        self.assertIn('dog', results[0]['subjects'])
        self.assertIn('Alice', results[1]['subjects'])
        self.assertIn('Bob', results[2]['subjects'])
    
    def test_empty_sentence(self):
        """Test extraction from empty sentence."""
        sentence = ""
        result = self.extractor.extract_primitives(sentence)
        
        self.assertEqual(len(result['subjects']), 0)
        self.assertEqual(len(result['verbs']), 0)
        self.assertEqual(len(result['objects']), 0)


if __name__ == '__main__':
    unittest.main()
