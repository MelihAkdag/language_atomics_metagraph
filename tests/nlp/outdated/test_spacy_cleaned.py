
######################################################
# LIBRARY IMPORTS
######################################################
import sys
import os
import spacy
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt
from tqdm import tqdm

src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from cor.knowledge.Knowledge import Knowledge

# Initialize spaCy model
nlp = spacy.load("en_core_web_sm")


######################################################
# FUNCTION DEFINITIONS
######################################################

# Utility functions
def remove_line_breaks(text):
    """ Remove line breaks from the text """
    return text.replace('\n', ' ')


def remove_multiple_spaces(text):
    """ Remove multiple spaces from the text """
    return ' '.join(text.split())


# Define the function for simple Semantic Role Labeling (SRL) with primitives
def primitives_srl(sentence, nlp):
    """ Perform simple SRL using spaCy and return subjects, verbs, objects, indirect objects.
    
    Args:
        sentence (str): The input sentence to analyze.
        nlp (spacy.lang): The spaCy language model.

    Returns:
        dict: A dictionary containing lists of subjects, verbs, objects, and indirect objects.
    """

    DENOTATION_VERBS = ["am", "are", "is", "was", "were", "be", "being", "been", "have been", "has been", "had been"]

    ATTRIBUTION_VERBS = ["have", "has", "had",
                         "own", "owns", "owned",
                         "possess", "possesses", "possessed", 
                         "contain", "contains", "contained",
                         "include", "includes", "included", 
                         "comprise", "comprises", "comprised", 
                         "hold", "holds", "held"]
    
    doc = nlp(sentence)
    subjects = []
    verbs = []
    objects = []
    indirect_objects = []
    
    for token in doc:
        if "subj" in token.dep_:
            subjects.append(token.text)
        if "VERB" in token.pos_:
            if token.lemma_ in DENOTATION_VERBS:
                verb_surrogate = "IS"
            elif token.lemma_ in ATTRIBUTION_VERBS:
                verb_surrogate = "HAS"
            else:
                verb_surrogate = token.lemma_
            verbs.append(verb_surrogate)
        if "obj" in token.dep_:
            objects.append(token.text)
        if "dative" in token.dep_:
            indirect_objects.append(token.text)
            
    return {
        'subjects': subjects,
        'verbs': verbs,
        'objects': objects,
        'indirect_objects': indirect_objects
    }



def save_to_database(srl_results, name="knowledge", template=None):
    """ Save SRL results to knowledge database.
     
    Args:
        srl_results (list): List of SRL result dictionaries.
        name (str): Name of the knowledge database.
        template (str): Path to the database template.
    
    Returns:
        Knowledge: The populated Knowledge database (SQLite) object. 
    """
    kb = Knowledge(name, template)
    say = kb.speak()
    
    for result in tqdm(srl_results, desc="Saving to DB", unit="result"):
        subjects = result['subjects']
        verbs = result['verbs']
        objects = result['objects']
        indirect_objects = result['indirect_objects']
        
        for subject in subjects:
            for verb in verbs:
                for obj in objects:
                    if verb == "IS":
                        say.IS(subject, obj)
                    elif verb == "HAS":
                        say.HAS(subject, obj, f"{subject}.{obj}")
                for ind_obj in indirect_objects:
                    if verb == "IS":
                        say.IS(subject, ind_obj)
                    elif verb == "HAS":
                        say.HAS(subject, ind_obj, f"{subject}.{ind_obj}")
    return kb


# Visualize the graph from database
def build_and_plot_graph_primitives_html(name="graph", save_as_filename="knowledge_graph.html"):
    """ Build and plot the knowledge graph from the database using pyvis and save as HTML.
    
    Args:
        name (str): Name of the knowledge database.
        save_as_filename (str): Filename to save the HTML visualization.
    
    Returns:
        networkx.DiGraph: The constructed directed graph object.
    """

    # 1. Create a graph object
    G = nx.DiGraph()

    # 2. Load the knowledge base
    kb = Knowledge(name)
    
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
    
    # Enhanced configuration for better visualization
    pyvis_nt = Network(
        height="1000px", 
        width="100%", 
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
    
    pyvis_nt.from_nx(G)
    
    # Write with UTF-8 encoding to handle special characters
    html = pyvis_nt.generate_html()
    with open(save_as_filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Graph saved to {save_as_filename}")
    print(f"Open it in your browser: file:///{os.path.abspath(save_as_filename)}")
    return G



######################################################
# IMPLEMENTATION
######################################################

# Load the full Frankenstein text from file
print("Loading Frankenstein text...")
with open('tests/nlp/frankenstein.txt', 'r', encoding='utf-8') as f:
     frankenstein_text = f.read() 


cleaned_text = remove_line_breaks(frankenstein_text)
cleaned_text = remove_multiple_spaces(cleaned_text)

# Extract SRL results for each sentence of Frankenstein text using primitives SRL
print("Processing sentences...")
doc = nlp(cleaned_text)
sentences = list(doc.sents)

srl_results_primitives = []
for sent in tqdm(sentences, desc="Extracting SRL", unit="sentence"):
    result = primitives_srl(sent.text, nlp)
    srl_results_primitives.append(result)

# Save the graph to database
print("Saving to database...")
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "db_frankenstein")
kb = save_to_database(srl_results_primitives, name=db_path)

# Visualize the graph as html from database
print("Building visualization...")
html_path = os.path.join(script_dir, "frankenstein_knowledge_graph.html")
G = build_and_plot_graph_primitives_html(name=db_path, save_as_filename=html_path)