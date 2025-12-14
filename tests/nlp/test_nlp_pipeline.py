"""Unit tests for NLP knowledge extraction pipeline."""

import os
import sys
import unittest
import tempfile
import shutil
import time
import gc

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
sys.path.insert(0, src_path)

from nlp.pipeline.KnowledgePipeline import KnowledgePipeline


class TestKnowledgePipeline(unittest.TestCase):
    """Test cases for KnowledgePipeline class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that are used by all tests."""
        # Load sampled text from data/raw
        text_path = "data\\raw\\sampled_text.txt"
        with open(text_path, 'r', encoding='utf-8') as f:
            cls.test_text = f.read()
        
        # Create temporary directory for test outputs
        cls.temp_dir = tempfile.mkdtemp()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        # Force garbage collection to close database connections
        gc.collect()
        
        # Give Windows time to release file locks
        time.sleep(0.5)
        
        # Remove temporary directory with retry logic
        max_retries = 3
        for i in range(max_retries):
            try:
                if os.path.exists(cls.temp_dir):
                    shutil.rmtree(cls.temp_dir)
                break
            except PermissionError:
                if i < max_retries - 1:
                    time.sleep(1)
                    gc.collect()
                else:
                    # If still failing, just warn instead of erroring
                    print(f"\nWarning: Could not delete temporary directory: {cls.temp_dir}")
    
    def setUp(self):
        """Set up before each test."""
        self.pipeline = KnowledgePipeline()
    
    def test_process_text(self):
        """Test processing text and building knowledge graph."""
        db_path = os.path.join(self.temp_dir, 'test_pipeline_db')
        
        # Process text
        kb = self.pipeline.process_text(self.test_text, db_path)
        
        # Verify database was created
        self.assertTrue(os.path.exists(db_path + '.s3db'))
        
        # Verify knowledge base is not None
        self.assertIsNotNone(kb)
        
        # Clean up reference to help release database
        del kb
        gc.collect()
    
    def test_visualize(self):
        """Test visualization generation."""
        db_path = os.path.join(self.temp_dir, 'test_viz_db')
        html_path = os.path.join(self.temp_dir, 'test_graph.html')
        
        # Process text first
        kb = self.pipeline.process_text(self.test_text, db_path)
        
        # Generate visualization
        self.pipeline.visualize(db_path, html_path)
        
        # Verify HTML file was created
        self.assertTrue(os.path.exists(html_path))
        
        # Verify HTML file is not empty
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertTrue(len(content) > 0)
        
        # Clean up reference to help release database
        del kb
        gc.collect()
    
    def test_complete_pipeline(self):
        """Test complete pipeline execution."""
        db_path = os.path.join(self.temp_dir, 'test_complete_db')
        html_path = os.path.join(self.temp_dir, 'test_complete_graph.html')
        
        # Process text
        kb = self.pipeline.process_text(self.test_text, db_path)
        
        # Generate visualization
        self.pipeline.visualize(db_path, html_path)
        
        # Verify both outputs exist
        self.assertTrue(os.path.exists(db_path + '.s3db'))
        self.assertTrue(os.path.exists(html_path))
        
        # Clean up reference to help release database
        del kb
        gc.collect()


if __name__ == "__main__":
    unittest.main()