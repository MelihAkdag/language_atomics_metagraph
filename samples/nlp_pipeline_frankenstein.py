"""Test the NLP knowledge extraction pipeline with Frankenstein text."""

import os
import sys


from nlp.pipeline.KnowledgePipeline import KnowledgePipeline


def main():
    """Run the complete NLP pipeline on Frankenstein text."""
    # Initialize pipeline
    pipeline = KnowledgePipeline()
    
    text_path = "data\\raw\\frankenstein.txt"
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("=" * 60)
    print("NLP Knowledge Extraction Pipeline")
    print("=" * 60)
    
    db_path = "data\\databases\\db_frankenstein"
    html_path = "data\\visualizations\\frankenstein_knowledge_graph.html"

    kb = pipeline.process_text(text, db_path)
    
    # Select the arcs that connect important vertices
    pipeline.visualize(db_path, html_path)
    
    print("=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
