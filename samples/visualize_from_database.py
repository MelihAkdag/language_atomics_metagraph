import os
import sys


from nlp.pipeline.KnowledgePipeline import KnowledgePipeline

def main():
    """Run the visualization from the existing knowledge database."""
    # Initialize pipeline
    pipeline = KnowledgePipeline()
    
    db_path = "data\\databases\\db_frankenstein"
    html_path = "data\\visualizations\\frankenstein_knowledge_graph.html"
    
    pipeline.visualize(db_path, html_path) 
    
    print("=" * 60)
    print("Visualization completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
