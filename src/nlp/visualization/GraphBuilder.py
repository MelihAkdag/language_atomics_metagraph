import os
from typing import Any, Optional

import networkx as nx
from pyvis.network import Network

from cor.knowledge.Knowledge import Knowledge


def _get_field(obj: Any, field: str, default=None):
    """
    Robustly read a field from either:
    - dict-like objects
    - MultiTableActiveObject objects (Vertex/Arc) via __getitem__
    - objects exposing get_<field>() methods
    - objects exposing plain attributes
    """
    if obj is None:
        return default

    if isinstance(obj, dict):
        return obj.get(field, default)

    # MultiTableActiveObject supports obj[field]
    try:
        return obj[field]
    except Exception:
        pass

    getter = getattr(obj, f"get_{field}", None)
    if callable(getter):
        try:
            return getter()
        except Exception:
            return default

    return getattr(obj, field, default)


class GraphBuilder:
    """Builds and visualizes knowledge graphs."""

    @staticmethod
    def build_from_database(db_name: str) -> nx.DiGraph:
        """Build NetworkX graph from knowledge database."""
        graph_nx = nx.DiGraph()
        kb = Knowledge(db_name)

        # Nodes
        for vertex_id in kb.graph.get_vertices():
            vertex = kb.graph.get_vertex(vertex_id)
            name = _get_field(vertex, "name")
            value = _get_field(vertex, "value")
            graph_nx.add_node(vertex_id, label=name, value=value)

        # Edges
        for arc_id in kb.graph.get_arcs():
            arc = kb.graph.get_arc(arc_id)
            start = _get_field(arc, "start")
            end = _get_field(arc, "end")
            label = _get_field(arc, "name")
            graph_nx.add_edge(start, end, label=label)

        return graph_nx

    @staticmethod
    def build_from_query(
        db_name: str,
        vertex_query: Optional[str] = None,
        arc_query: Optional[str] = None,
    ) -> nx.DiGraph:
        """Build NetworkX graph from custom SQL queries."""
        graph_nx = nx.DiGraph()
        kb = Knowledge(db_name)

        conn = kb.graph.conn.connect()
        cursor = conn.cursor()
        try:
            # Vertices
            if vertex_query:
                cursor.execute(vertex_query)
                vertex_ids = [row[0] for row in cursor.fetchall()]
            else:
                vertex_ids = kb.graph.get_vertices()

            nodemap = {}
            for vertex_id in vertex_ids:
                vertex = kb.graph.get_vertex(vertex_id)
                if vertex is None:
                    continue
                name = _get_field(vertex, "name")
                value = _get_field(vertex, "value")
                nodemap[vertex_id] = name
                graph_nx.add_node(vertex_id, label=name, value=value)

            # Arcs
            if arc_query:
                cursor.execute(arc_query)
                arc_ids = [row[0] for row in cursor.fetchall()]
            else:
                arc_ids = kb.graph.get_arcs()

            for arc_id in arc_ids:
                arc = kb.graph.get_arc(arc_id)
                if arc is None:
                    continue
                start = _get_field(arc, "start")
                end = _get_field(arc, "end")
                label = _get_field(arc, "name")

                # Only add edge if both endpoints exist in our filtered node set
                if start in nodemap and end in nodemap:
                    graph_nx.add_edge(start, end, label=label)

            return graph_nx
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    @staticmethod
    def save_as_html(
        graph: nx.DiGraph,
        filename: str,
        height: str = "1200px",
        width: str = "100%",
        physics: bool = True,
    ) -> str:
        """Save graph as interactive HTML file."""
        pyvis_nt = Network(
            height=height,
            width=width,
            bgcolor="#222222",
            font_color="white",
            notebook=True,
            directed=True,
            cdn_resources="in_line",
            neighborhood_highlight=True,
        )

        pyvis_nt.set_options(
            """
        var options = {
          "physics": {
            "enabled": """
            + ("true" if physics else "false")
            + """,
            "barnesHut": {
              "gravitationalConstant": -50000,
              "centralGravity": 0.3,
              "springLength": 50,
              "springConstant": 0.04,
              "damping": 0.09,
              "avoidOverlap": 1
            }
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 200,
            "hideEdgesOnDrag": false,
            "navigationButtons": true,
            "keyboard": true
          }
        }
        """
        )

        pyvis_nt.from_nx(graph)

        html = pyvis_nt.generate_html()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        abs_path = os.path.abspath(filename)
        print(f"Graph saved to {filename}")
        print(f"Open it in your browser: file:///{abs_path}")

        return abs_path