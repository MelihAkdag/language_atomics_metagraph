"""
Example usage of the NLP module components.
This demonstrates how to use individual modules or the complete pipeline.
"""

import os
import sys


def example_text_cleaner():
    """Example: Using TextCleaner independently."""
    print("\n" + "="*60)
    print("Example 1: Text Cleaning")
    print("="*60)
    
    from nlp.preprocessing.TextCleaner import TextCleaner
    
    text = """This is a sample text.
    It has multiple    spaces   and
    line breaks that need
    to be cleaned."""
    
    print("Original text:")
    print(repr(text))
    
    cleaned = TextCleaner.clean(text)
    print("\nCleaned text:")
    print(repr(cleaned))


def example_srl_extractor():
    """Example: Using SRLExtractor independently."""
    print("\n" + "="*60)
    print("Example 2: Semantic Role Labeling")
    print("="*60)
    
    from nlp.extraction.SRLExtractor import SRLExtractor
    
    extractor = SRLExtractor()
    
    sentences = [
        "The cat is small.",
        "John has a car.",
        "Mary runs quickly."
    ]
    
    for sentence in sentences:
        result = extractor.extract_primitives(sentence)
        print(f"\nSentence: {sentence}")
        print(f"  Subjects: {result['subjects']}")
        print(f"  Verbs: {result['verbs']}")
        print(f"  Objects: {result['objects']}")


def example_full_pipeline():
    """Example: Using the complete KnowledgePipeline."""
    print("\n" + "="*60)
    print("Example 3: Complete Pipeline")
    print("="*60)
    
    from nlp.pipeline.KnowledgePipeline import KnowledgePipeline
    
    # Initialize pipeline
    pipeline = KnowledgePipeline()
    
    # Sample text
    text = """
    The cat is on the mat. The dog is brown. 
    John has a car. Mary has a book.
    The car is red. The book is interesting.
    """
    
    # Process - use data directory structure
    project_root = os.path.join(os.path.dirname(__file__), '..')
    data_dir = os.path.join(project_root, 'data')
    
    db_path = os.path.join(data_dir, 'databases', 'example_output_db')
    html_path = os.path.join(data_dir, 'visualizations', 'example_graph.html')
    
    print("\nProcessing text...")
    kb = pipeline.process_text(text, db_path)
    
    print("\nGenerating visualization...")
    pipeline.visualize(db_path, html_path) 

    print(f"\n✅ Graph saved to: {html_path}")
    print("Open it in your browser to see the knowledge graph!")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("NLP Module Usage Examples")
    print("="*60)
    
    example_text_cleaner()
    example_srl_extractor()
    example_full_pipeline()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
