import os
import sqlite3
import sys

import networkx as nx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from nlp.visualization.GraphBuilder import GraphBuilder

def main():
    """Run the visualization from the existing knowledge database."""
    db_path = "data\\databases\\sreekant_frankenstein_graph.s3db"
    html_path = "data\\visualizations\\sreekant_frankenstein_knowledge_graph.html"

    primitive_labels = {
        10: "has",
        11: "of",
        20: "is_a",
        21: "in",
        30: "relates",
        31: "by",
        40: "contains",
        41: "of_collection",
        50: "is",
        60: "produces",
        61: "from",
        70: "causes",
    }
    
    print("Building graph from queries...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, name, value FROM vertices")
        vertices = cur.fetchall()
        vertex_name_by_id = {vid: name for vid, name, _ in vertices}

        graph = nx.DiGraph()
        for vid, name, value in vertices:
            graph.add_node(vid, label=name, value=value or 0)

        cur.execute("SELECT id, type, start, end, anchor FROM arcs")
        for _, arc_type, start, end, anchor in cur.fetchall():
            if not (graph.has_node(start) and graph.has_node(end)):
                continue

            base_label = primitive_labels.get(arc_type, f"type_{arc_type}")
            anchor_name = vertex_name_by_id.get(anchor) if anchor is not None else None

            if arc_type in (30, 31) and anchor_name:
                label = f"{base_label}.{anchor_name}"
            elif arc_type in (60, 61) and anchor_name:
                label = f"{base_label}.{anchor_name}"
            else:
                label = base_label

            graph.add_edge(start, end, label=label)
    finally:
        cur.close()
        conn.close()

    GraphBuilder.save_as_html(graph=graph, filename=html_path)
    
    print("=" * 60)
    print("Visualization completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
