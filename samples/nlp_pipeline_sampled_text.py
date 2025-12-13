"""Test the NLP knowledge extraction pipeline with Frankenstein text."""

import os
import sys

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

from nlp.pipeline.KnowledgePipeline import KnowledgePipeline


def main():
    """Run the complete NLP pipeline on sample text."""
    # Initialize pipeline
    pipeline = KnowledgePipeline()
    
    # Setup paths - use data directory structure
    project_root = os.path.join(os.path.dirname(__file__), '..')
    data_dir = os.path.join(project_root, 'data')

    # Load text from data/raw
    text_path = os.path.join(data_dir, 'raw', 'sampled_text.txt')
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Process text and build knowledge graph
    template_path = os.path.join(project_root, 'tests', 'cor', 'knowledge', 'graph.s3db')
    db_path = os.path.join(data_dir, 'databases', 'db_sampled_text')
    
    print("=" * 60)
    print("NLP Knowledge Extraction Pipeline")
    print("=" * 60)
    
    kb = pipeline.process_text(text, db_path, template=template_path)
    
    # Visualize - save to data/visualizations
    html_path = os.path.join(data_dir, 'visualizations', 'sampled_text_knowledge_graph.html')
    pipeline.visualize(db_name=db_path, output_file=html_path, physics=True)
    
    print("=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
