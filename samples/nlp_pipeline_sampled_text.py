"""Test the NLP knowledge extraction pipeline with Frankenstein text."""

import os
import sys


from nlp.pipeline.KnowledgePipeline import KnowledgePipeline


def main():
    """Run the complete NLP pipeline on sample text."""
    # Initialize pipeline
    pipeline = KnowledgePipeline(enable_coref=True, coref_strategy="replace")
    
    # Load text from data/raw
    text_path = "data\\raw\\sampled_text.txt"
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Process text and build knowledge graph
    db_path = "data\\databases\\db_sampled_text"
    
    print("=" * 60)
    print("NLP Knowledge Extraction Pipeline")
    print("=" * 60)
    
    kb = pipeline.process_text(text, db_path)
    
    # Visualize - save to data/visualizations
    html_path = "data\\visualizations\\sampled_text_knowledge_graph.html"
    pipeline.visualize(db_name=db_path, output_file=html_path, physics=True)
    
    print("=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
