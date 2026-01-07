import os
import sys


from nlp.pipeline.KnowledgePipeline import KnowledgePipeline

def main():
    """Run the visualization from the existing knowledge database."""
    # Initialize pipeline
    pipeline = KnowledgePipeline()
    
    db_path = "data\\databases\\db_frankenstein"
    html_path = "data\\visualizations\\frankenstein_knowledge_graph_query_filtered.html"

    # Example arc_query to filter specific arcs (Filter arcs connected to important vertices)
    arc_query = """
        SELECT id
        FROM arcs
        WHERE start IN (
            SELECT id FROM vertices 
            WHERE name IN ('elizabeth', 'victor', 'frankenstein', 'creature', 'mother', 'father')
        )
        OR end IN (
            SELECT id FROM vertices 
            WHERE name IN ('elizabeth', 'victor', 'frankenstein', 'creature', 'mother', 'father')
        )
    """

    pipeline.visualize(db_name=db_path, output_file=html_path, arc_query=arc_query) 
    
    print("=" * 60)
    print("Visualization completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
