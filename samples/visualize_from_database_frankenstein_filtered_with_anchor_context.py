import os
import sqlite3
import sys

import networkx as nx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from nlp.visualization.GraphBuilder import GraphBuilder


def main():
    """Run a filtered visualization and expand it with anchor-node context."""
    db_path = "data\\databases\\sreekant_frankenstein_graph.s3db"
    html_path = "data\\visualizations\\sreekant_frankenstein_knowledge_graph_query_filtered_with_anchor_context.html"

    target_names = {
        "elizabeth",
        "elizabeth lavenza",
        "victor",
        "victor frankenstein",
        "frankenstein",
        "creature",
        "mother",
        "father",
    }

    # Canonical + inverse primitive arc types from the schema.
    primitive_types = (10, 11, 20, 21, 30, 31, 40, 41, 50, 60, 61, 70)

    print("Building graph from filtered primitive arcs with anchor context...")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # 1) Resolve seed vertices from the target names.
        placeholders = ",".join("?" for _ in target_names)
        cur.execute(
            f"""
            SELECT id, name, value
            FROM vertices
            WHERE lower(name) IN ({placeholders})
            """,
            tuple(target_names),
        )
        seed_vertices = cur.fetchall()
        seed_vertex_ids = {row[0] for row in seed_vertices}

        if not seed_vertex_ids:
            print("No target vertices were found. Nothing to visualize.")
            return

        # 2) Collect seed primitive arcs connected to target vertices.
        type_placeholders = ",".join("?" for _ in primitive_types)
        seed_id_placeholders = ",".join("?" for _ in seed_vertex_ids)
        cur.execute(
            f"""
            SELECT id, name, type, start, end, anchor
            FROM arcs
            WHERE type IN ({type_placeholders})
              AND (start IN ({seed_id_placeholders}) OR end IN ({seed_id_placeholders}))
            """,
            tuple(primitive_types) + tuple(seed_vertex_ids) + tuple(seed_vertex_ids),
        )
        seed_arcs = cur.fetchall()

        if not seed_arcs:
            print("No primitive arcs matched the target-vertex filter. Nothing to visualize.")
            return

        seed_arc_ids = {row[0] for row in seed_arcs}
        anchor_ids = {row[5] for row in seed_arcs if row[5] is not None}

        # 3) Pull additional primitive arcs touching anchor vertices for context.
        anchor_context_arcs = []
        if anchor_ids:
            anchor_placeholders = ",".join("?" for _ in anchor_ids)
            cur.execute(
                f"""
                SELECT id, name, type, start, end, anchor
                FROM arcs
                WHERE type IN ({type_placeholders})
                  AND (start IN ({anchor_placeholders}) OR end IN ({anchor_placeholders}))
                """,
                tuple(primitive_types) + tuple(anchor_ids) + tuple(anchor_ids),
            )
            anchor_context_arcs = [row for row in cur.fetchall() if row[0] not in seed_arc_ids]

        all_arcs = seed_arcs + anchor_context_arcs

        # 4) Gather vertices from arc endpoints only (prevents isolated anchor-only nodes).
        vertex_ids = set()
        for _, _, _, start, end, anchor in all_arcs:
            vertex_ids.add(start)
            vertex_ids.add(end)

        vertex_placeholders = ",".join("?" for _ in vertex_ids)
        cur.execute(
            f"""
            SELECT id, name, value
            FROM vertices
            WHERE id IN ({vertex_placeholders})
            """,
            tuple(vertex_ids),
        )
        vertices = cur.fetchall()
        vertex_name_by_id = {vid: name for vid, name, _ in vertices}

        graph = nx.DiGraph()

        for vid, name, value in vertices:
            graph.add_node(vid, label=name, value=value or 0)

        # 5) Add real primitive edges from the database.
        for _, name, arc_type, start, end, anchor in all_arcs:
            if graph.has_node(start) and graph.has_node(end):
                anchor_name = vertex_name_by_id.get(anchor) if anchor is not None else None
                if arc_type in (30, 31) and anchor_name:
                    label = f"relates.{anchor_name}"
                elif arc_type in (60, 61) and anchor_name:
                    label = f"produces.{anchor_name}"
                else:
                    label = name
                graph.add_edge(start, end, label=label)

        GraphBuilder.save_as_html(graph=graph, filename=html_path)

        print("=" * 60)
        print("Visualization with anchor-node context completed successfully!")
        print(f"Seed primitive arcs: {len(seed_arcs)}")
        print(f"Anchor-context primitive arcs: {len(anchor_context_arcs)}")
        print(f"Total nodes: {graph.number_of_nodes()}, total edges: {graph.number_of_edges()}")
        print("=" * 60)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
