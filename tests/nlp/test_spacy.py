#%% 
import sys
import os
import spacy
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt

# Initialize spaCy model
nlp = spacy.load("en_core_web_sm")

#%%
# Utility functions
def remove_line_breaks(text):
    """ Remove line breaks from the text """
    return text.replace('\n', ' ')

def remove_multiple_spaces(text):
    """ Remove multiple spaces from the text """
    return ' '.join(text.split())

# %%
# Define the function for simple Semantic Role Labeling (SRL)
def simple_srl(sentence, nlp):
    doc = nlp(sentence)
    subjects = []
    verbs = []
    objects = []
    indirect_objects = []
    
    for token in doc:
        if "subj" in token.dep_:
            subjects.append(token.text)
        if "VERB" in token.pos_:
            verbs.append(token.lemma_)
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

# %%
# Build and plot the knowledge graph with matplotlib
def build_and_plot_knowledge_graph_matplotlib(srl_results):
    G = nx.DiGraph()
    
    for result in srl_results:
        subjects = result['subjects']
        verbs = result['verbs']
        objects = result['objects']
        indirect_objects = result['indirect_objects']
        
        for subject in subjects:
            for verb in verbs:
                for obj in objects:
                    G.add_edge(subject, obj, label=verb)
                for ind_obj in indirect_objects:
                    G.add_edge(subject, ind_obj, label=verb)
    
    pos = nx.spring_layout(G, seed=42)
    
    # Draw nodes and edges
    nx.draw(G, pos, with_labels=True, node_color="skyblue", node_size=2000, font_size=12, font_color="black", font_weight="bold", arrows=True)
    
    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    # Show plot
    plt.show()

# %%
# Build and plot the knowledge graph with pyvis

def build_and_plot_knowledge_graph_html(srl_results, filename="knowledge_graph.html"):
    G = nx.DiGraph()
    
    for result in srl_results:
        subjects = result['subjects']
        verbs = result['verbs']
        objects = result['objects']
        indirect_objects = result['indirect_objects']
        
        for subject in subjects:
            for verb in verbs:
                for obj in objects:
                    G.add_edge(subject, obj, label=verb)
                for ind_obj in indirect_objects:
                    G.add_edge(subject, ind_obj, label=verb)
    
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
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Graph saved to {filename}")
    print(f"Open it in your browser: file:///{os.path.abspath(filename)}")
    return G

# %%
# Process each sentence and extract SRL results

sample_text = """ I passed a night of unmingled wretchedness. In the morning I went to
the court; my lips and throat were parched. I dared not ask the fatal
question, but I was known, and the officer guessed the cause of my
visit. The ballots had been thrown; they were all black, and Justine
was condemned.
"""

cleaned_text = remove_line_breaks(sample_text)
cleaned_text = remove_multiple_spaces(cleaned_text)

print("Cleaned Text:\n", cleaned_text)


# %%
# Extract SRL results for each sentence of sample text
srl_results = []
for sent in nlp(cleaned_text).sents:
    result = simple_srl(sent.text, nlp)
    print(result)
    print("-----")
    srl_results.append(result)

# Build and plot the knowledge graph with matplotlib
build_and_plot_knowledge_graph_matplotlib(srl_results)
G = build_and_plot_knowledge_graph_html(srl_results, filename="knowledge_graph.html")


# %%
# Process each sentence and extract SRL results

sample_text = """ 
So strange an accident has happened to us that I cannot forbear
recording it, although it is very probable that you will see me before
these papers can come into your possession.

Last Monday (July 31st) we were nearly surrounded by ice, which closed
in the ship on all sides, scarcely leaving her the sea-room in which
she floated. Our situation was somewhat dangerous, especially as we
were compassed round by a very thick fog. We accordingly lay to,
hoping that some change would take place in the atmosphere and weather.

About two o’clock the mist cleared away, and we beheld, stretched out
in every direction, vast and irregular plains of ice, which seemed to
have no end. Some of my comrades groaned, and my own mind began to
grow watchful with anxious thoughts, when a strange sight suddenly
attracted our attention and diverted our solicitude from our own
situation. We perceived a low carriage, fixed on a sledge and drawn by
dogs, pass on towards the north, at the distance of half a mile; a
being which had the shape of a man, but apparently of gigantic stature,
sat in the sledge and guided the dogs. We watched the rapid progress
of the traveller with our telescopes until he was lost among the
distant inequalities of the ice.

This appearance excited our unqualified wonder. We were, as we believed,
many hundred miles from any land; but this apparition seemed to denote that
it was not, in reality, so distant as we had supposed. Shut in, however, by
ice, it was impossible to follow his track, which we had observed with the
greatest attention.

About two hours after this occurrence we heard the ground sea, and before
night the ice broke and freed our ship. We, however, lay to until the
morning, fearing to encounter in the dark those large loose masses which
float about after the breaking up of the ice. I profited of this time to
rest for a few hours.

In the morning, however, as soon as it was light, I went upon deck and
found all the sailors busy on one side of the vessel, apparently
talking to someone in the sea. It was, in fact, a sledge, like that we
had seen before, which had drifted towards us in the night on a large
fragment of ice. Only one dog remained alive; but there was a human
being within it whom the sailors were persuading to enter the vessel.
He was not, as the other traveller seemed to be, a savage inhabitant of
some undiscovered island, but a European. When I appeared on deck the
master said, “Here is our captain, and he will not allow you to perish
on the open sea.”

On perceiving me, the stranger addressed me in English, although with a
foreign accent. “Before I come on board your vessel,” said he,
“will you have the kindness to inform me whither you are bound?”

You may conceive my astonishment on hearing such a question addressed
to me from a man on the brink of destruction and to whom I should have
supposed that my vessel would have been a resource which he would not
have exchanged for the most precious wealth the earth can afford. I
replied, however, that we were on a voyage of discovery towards the
northern pole.

Upon hearing this he appeared satisfied and consented to come on board.
Good God! Margaret, if you had seen the man who thus capitulated for
his safety, your surprise would have been boundless. His limbs were
nearly frozen, and his body dreadfully emaciated by fatigue and
suffering. I never saw a man in so wretched a condition. We attempted
to carry him into the cabin, but as soon as he had quitted the fresh
air he fainted. We accordingly brought him back to the deck and
restored him to animation by rubbing him with brandy and forcing him to
swallow a small quantity. As soon as he showed signs of life we
wrapped him up in blankets and placed him near the chimney of the
kitchen stove. By slow degrees he recovered and ate a little soup,
which restored him wonderfully.
"""

cleaned_text = remove_line_breaks(sample_text)
cleaned_text = remove_multiple_spaces(cleaned_text)

print("Cleaned Text:\n", cleaned_text)


# %%
# Define the function for Semantic Role Labeling (SRL) for primitives

DENOTATION_VERBS = ["am", "are", "is", "was", "were", "be", "being", "been", "have been", "has been", "had been"]
ATTRIBUTION_VERBS = ["have", "has", "had",
                     "own", "owns", "owned",
                     "possess", "possesses", "possessed", 
                     "contain", "contains", "contained",
                     "include", "includes", "included", 
                     "comprise", "comprises", "comprised", 
                     "hold", "holds", "held"]

def primitives_srl(sentence, nlp):
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

srl_results_primitives = []
for sent in nlp(cleaned_text).sents:
    result = primitives_srl(sent.text, nlp)
    print(result)
    print("-----")
    srl_results_primitives.append(result)


# %%
# Save the graph to database

# Add src folder to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from cor.knowledge.Knowledge import Knowledge


def save_to_database(srl_results, name="knowledge"):
    """ Save SRL results to knowledge database """
    kb = Knowledge(name=name)
    say = kb.speak()
    
    for result in srl_results:
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

kb = save_to_database(srl_results_primitives, "graph")

# %%
# Visualize the graph as html from database

def build_and_plot_graph_primitives_html(name="graph", save_as_filename="knowledge_graph.html"):
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

G = build_and_plot_graph_primitives_html(name="graph", save_as_filename="database_knowledge_graph.html")

# %%