import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from nlp.visualization.GraphBuilder import GraphBuilder

def main():
    """Run the visualization from the existing knowledge database."""
    db_path = "data\\databases\\sreekant_frankenstein_graph.s3db"
    html_path = "data\\visualizations\\sreekant_frankenstein_knowledge_graph_query_filtered.html"

    # Filter arcs connected to key entities using case-insensitive matching.
    arc_query = """
        WITH target_vertices AS (
            SELECT id
            FROM vertices
            WHERE lower(name) IN (
                'elizabeth',
                'elizabeth lavenza',
                'victor',
                'victor frankenstein',
                'frankenstein',
                'creature',
                'mother',
                'father'
            )
        ),
        primitive_arcs AS (
            SELECT id
            FROM arcs
            WHERE type IN (10, 11, 20, 21, 30, 31, 40, 41, 50, 60, 61, 70)
        )
        SELECT a.id
        FROM arcs a
        JOIN primitive_arcs p ON p.id = a.id
        WHERE a.start IN (SELECT id FROM target_vertices)
           OR a.end IN (SELECT id FROM target_vertices)
    """

    print("Building graph from queries...")
    graph = GraphBuilder.build_from_sqlite(db_path, arc_query=arc_query)
    GraphBuilder.save_as_html(graph=graph, filename=html_path)
    
    print("=" * 60)
    print("Visualization completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
