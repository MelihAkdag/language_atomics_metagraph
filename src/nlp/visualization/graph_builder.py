"""Graph visualization utilities for knowledge graphs."""

import os
import networkx as nx
from pyvis.network import Network
from typing import Dict, Any

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
    def save_as_html(graph: nx.DiGraph, filename: str, 
                     height: str = "1000px", 
                     width: str = "100%") -> str:
        """Save graph as interactive HTML file.
        
        Args:
            graph: NetworkX graph to visualize
            filename: Output HTML filename
            height: Height of the visualization
            width: Width of the visualization
            
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
            cdn_resources='in_line'
        )
        
        # Configure physics for better layout
        pyvis_nt.set_options("""
        var options = {
          "physics": {
            "enabled": true,
            "stabilization": {
              "iterations": 200
            }
          }
        }
        """)
        
        pyvis_nt.from_nx(graph)
        
        # Write with UTF-8 encoding
        html = pyvis_nt.generate_html()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        abs_path = os.path.abspath(filename)
        print(f"Graph saved to {filename}")
        print(f"Open it in your browser: file:///{abs_path}")
        
        return abs_path
