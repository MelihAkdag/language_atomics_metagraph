
import networkx as nx
import matplotlib.pyplot as plt
import sys

from cor.knowledge.Knowledge import Knowledge

# 1. Create a graph object
G = nx.DiGraph()  # For an undirected graph


# 2. Load the knowledge base
kb = Knowledge('graph')

# 3. Add nodes
nodemap = dict()
for vid in kb.graph.get_vertices():
    name = kb.graph.get_vertex(vid)['name']
    nodemap[vid] = name
    G.add_node( vid, label=nodemap[vid] )


# 4. Add edges (connections between nodes)
edgemap = dict()
for eid in kb.graph.get_arcs():
    arc     = kb.graph.get_arc(eid)
    start   = arc['start']
    end     = arc['end']
    name    = arc['name']
    edgemap[(start,end)] = name
    G.add_edge(start, end, label=name)

# 5. Draw the network
# You can specify a layout algorithm, e.g., 'spring_layout' for a force-directed layout
pos = nx.spring_layout(G, seed=11)

nx.draw_networkx_nodes(G, pos, node_size=20, node_color="lightblue")
nx.draw_networkx_edges(
    G,
    pos,
    arrowstyle="->", edge_color="gray"
)

nx.draw_networkx_labels(G, pos, labels=nodemap, font_size=10, font_color="black", horizontalalignment='left')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edgemap, font_color='red')
    
# 6. Display the plot
plt.title("Knowledge Graph Visualization")
plt.show()

