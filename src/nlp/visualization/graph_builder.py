"""Graph visualization utilities for knowledge graphs."""

import os
import networkx as nx
from pyvis.network import Network
from typing import Dict, Any, Optional

from cor.knowledge.Knowledge import Knowledge


class GraphBuilder:
    """Builds and visualizes knowledge graphs."""
    
    @staticmethod
    def build_from_database(db_name: str) -> nx.DiGraph:
        """Build NetworkX graph from knowledge database.
        
        Args:
            db_name: Name/path of the knowledge database
            
        Returns:
            NetworkX directed graph
        """
        G = nx.DiGraph()
        kb = Knowledge(db_name)
        
        # Add nodes
        nodemap = {}
        for vid in kb.graph.get_vertices():
            name = kb.graph.get_vertex(vid)['name']
            nodemap[vid] = name
            G.add_node(vid, label=nodemap[vid])
        
        # Add edges
        edgemap = {}
        for eid in kb.graph.get_arcs():
            arc = kb.graph.get_arc(eid)
            start = arc['start']
            end = arc['end']
            name = arc['name']
            edgemap[(start, end)] = name
            G.add_edge(start, end, label=name)
        
        return G
    

    @staticmethod
    def build_from_query(db_name: str, 
                        vertex_query: Optional[str] = None,
                        arc_query: Optional[str] = None) -> nx.DiGraph:
        """Build NetworkX graph from custom SQL queries.
        
        Args:
            db_name: Name/path of the knowledge database
            vertex_query: SQL query for vertices (must return 'id' column)
            arc_query: SQL query for arcs (must return 'id' column)
            
        Returns:
            NetworkX directed graph
            
        Example:
            # Get only subjects (value=1) and their connections
            graph = GraphBuilder.build_from_query(
                "my_kb.s3db",
                vertex_query="SELECT id FROM vertices WHERE value = 1"
            )
        """
        G = nx.DiGraph()
        kb = Knowledge(db_name)
        cursor = kb.graph.db.conn.cursor()
        
        # Get vertices from query
        if vertex_query:
            cursor.execute(vertex_query)
            vertex_ids = [row[0] for row in cursor.fetchall()]
        else:
            vertex_ids = kb.graph.get_vertices()
        
        # Add nodes
        nodemap = {}
        for vid in vertex_ids:
            vertex = kb.graph.get_vertex(vid)
            if vertex:
                name = vertex['name']
                value = vertex.get_value()
                nodemap[vid] = name
                G.add_node(vid, label=name, value=value)
        
        # Get arcs from query
        if arc_query:
            cursor.execute(arc_query)
            arc_ids = [row[0] for row in cursor.fetchall()]
        else:
            arc_ids = kb.graph.get_arcs()
        
        # Add edges
        for eid in arc_ids:
            arc = kb.graph.get_arc(eid)
            start = arc['start']
            end = arc['end']
            name = arc['name']
            
            # Only add edge if both vertices exist in our graph
            if start in nodemap and end in nodemap:
                G.add_edge(start, end, label=name)
        
        return G


    @staticmethod
    def save_as_html(graph: nx.DiGraph, filename: str, 
                     height: str = "1200px", 
                     width: str = "100%",
                     physics: bool = True) -> str:
        """Save graph as interactive HTML file with selection highlighting.
        
        Args:
            graph: NetworkX graph to visualize
            filename: Output HTML filename
            height: Height of the visualization
            width: Width of the visualization
            physics: Whether to enable physics simulation
            
        Returns:
            Absolute path to the saved HTML file
        """
        pyvis_nt = Network(
            height=height,
            width=width,
            bgcolor="#222222",
            font_color="white",
            notebook=True,
            directed=True,
            cdn_resources='in_line',
            neighborhood_highlight=True
        )
        
        # Configure physics for better layout
        pyvis_nt.set_options("""
        var options = {
          "physics": {
            "enabled": """ + ("true" if physics else "false") + """,
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
        """)

        
        pyvis_nt.from_nx(graph)
        
        # Generate HTML with selection highlighting
        html = pyvis_nt.generate_html()
        
        # Write with UTF-8 encoding
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        abs_path = os.path.abspath(filename)
        print(f"Graph saved to {filename}")
        print(f"Open it in your browser: file:///{abs_path}")
        
        return abs_path
