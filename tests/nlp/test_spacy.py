#%% 
import spacy
import networkx as nx
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
srl_results = []
for sent in nlp(cleaned_text).sents:
    result = simple_srl(sent.text, nlp)
    print(result)
    print("-----")
    srl_results.append(result)

# Build and plot the knowledge graph with matplotlib
build_and_plot_knowledge_graph_matplotlib(srl_results)

# %%
