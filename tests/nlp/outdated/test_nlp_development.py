# %%
"""
# SOME TOOLS WE CAN USE FROM NLTK LIBRARY

* Classification: Assigning a label or category to a piece of text. TODO: Can we use it for converting "not" into "False"?

* Tokenization: Breaking text into smaller units (tokens), usually words or sentences.

* Stemming: Reducing words to their root form by chopping off suffixes (not always a real word). 
  Example: "running", "runs", "runner" → "run". Probably we can use lemmatization instead of stemming.

* Lemmatization: Reducing words to their base or dictionary form (unlike stemming, it produces real words). 
  Example: "running" → "run", "better" → "good". TODO: Do we want to keep tenses?

* Tagging (Part-of-speech (POS) tagging): Assigning grammatical tags to words (noun, verb, adjective, adverb). 
  Example: "I love NLP" → [("I", PRON), ("love", VERB), ("NLP", NOUN)].

        CC    Coordinating conjunction       and, but, or
        CD    Cardinal number                one, two, 3
        DT    Determiner                     the, a, an
        EX    Existential there              there (is)
        FW    Foreign word                   bonjour
        IN    Preposition/subordinating conj in, of, like
        JJ    Adjective                      big, blue
        JJR   Adjective, comparative         bigger
        JJS   Adjective, superlative         biggest
        LS    List item marker               1), A.
        MD    Modal                          can, will
        NN    Noun, singular or mass         dog, car
        NNS   Noun, plural                   dogs, cars
        NNP   Proper noun, singular          John, London
        NNPS  Proper noun, plural            Americans
        PDT   Predeterminer                  all, both
        POS   Possessive ending              ’s
        PRP   Personal pronoun               I, you, he
        PRP$  Possessive pronoun             my, your
        RB    Adverb                         quickly, silently
        RBR   Adverb, comparative            faster
        RBS   Adverb, superlative            fastest
        RP    Particle                       up, off
        SYM   Symbol                         $, %, &
        TO    to                             to go
        UH    Interjection                   oh, wow
        VB    Verb, base form                eat, run
        VBD   Verb, past tense               ate, ran
        VBG   Verb, gerund/present participle eating, running
        VBN   Verb, past participle          eaten, run
        VBP   Verb, non-3rd person singular present eat, run
        VBZ   Verb, 3rd person singular present eats, runs
        WDT   Wh-determiner                  which, that
        WP    Wh-pronoun                     who, what
        WP$   Possessive wh-pronoun          whose
        WRB   Wh-adverb                      where, when


* Parsing: Analyzing the grammatical structure of a sentence (syntax tree). 
  Example: "The cat sat on the mat" → A tree showing subject, verb, object, etc.

* Chunking: Grouping words into meaningful phrases (like noun phrases or verb phrases). 
  Chunking is shallow parsing. Instead of building a full syntax tree (like parsing), chunking groups words into meaningful phrases based on their POS tags. 
  Example: "The big dog" → [NP The big dog].

* Named entity recognition (NER): Identifying and classifying named entities in text (like people, organizations, locations). 
  Example: "Barack Obama was born in Hawaii" → [("Barack Obama", PERSON), ("Hawaii", LOCATION)].
    
* Dependency parsing: Finding relationships between words (subject, object, modifiers). 
  Example: "The cat chased the mouse" → cat (subject) → chased (verb) → mouse (object).

* Semantic Reasoning: Understanding meaning and relationships beyond syntax.

"""

# %%
# IMPORTS

import nltk
import string
from nltk import pos_tag
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer

# Uncomment the following lines to download necessary NLTK resources
# nltk.download('punkt')
# nltk.download('punkt_tab')
# nltk.download('stopwords')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger_eng')

# %% 
# FUNCTIONS

def remove_line_breaks(text):
    """ Remove line breaks from the text """
    return text.replace('\n', ' ')

def remove_multiple_spaces(text):
    """ Remove multiple spaces from the text """
    return ' '.join(text.split())

def remove_quatation_marks(text):
    """ Remove quotation marks from the text """
    return text.replace('“', '').replace('”', '').replace('"', '')

def change_colons_and_semicolons_to_periods(text):
    """ Change colons and semicolons to periods """
    return text.replace(':', '.').replace(';', '.')

def lowercase_text(text):
    """ Lowercase the text """
    return text.lower()

def split_into_sentences(text):
    """ Split text into sentences """
    return sent_tokenize(text)

def get_wordnet_pos(treebank_tag):
    """ Convert Penn Treebank POS tag to WordNet POS tag """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN  # Default to noun

def pos_tag_and_lemmatize(text):
    """ Function to POS tag and lemmatize input text """
    tokens = word_tokenize(text)
    tags = pos_tag(tokens)
    lemmatized_tokens = [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in tags]  
    lemmatized_sentence = ' '.join(lemmatized_tokens)
    return tags, lemmatized_tokens, lemmatized_sentence

def clean_sentence(sentence, punctuation):
    """ Remove stop words and punctuation from a sentence, keeping only specified POS tags """
    tokens = word_tokenize(sentence)
    
    filtered_tokens = []
    for word in tokens:
        # Keep almost everything except punctuation and very common stopwords
        if word not in punctuation and word.lower() not in {'the', 'a', 'an', '?', '!', '.'}:
            filtered_tokens.append(word.lower())
    filtered_sentence = ' '.join(filtered_tokens)
    return filtered_tokens, filtered_sentence


# %%
# EXAMPLE TEXT

sample_text = """ “Come, dearest Victor; you alone can console Elizabeth. She weeps
continually, and accuses herself unjustly as the cause of his death;
her words pierce my heart. We are all unhappy; but will not that be an
additional motive for you, my son, to return and be our comforter?
Your dear mother! Alas, Victor! I now say, Thank God she did not live
to witness the cruel, miserable death of her youngest darling!"""

# %%
# TEXT CLEANING AND PROCESSING

cleaned_text = remove_line_breaks(sample_text)
cleaned_text = remove_multiple_spaces(cleaned_text)
cleaned_text = remove_quatation_marks(cleaned_text)
cleaned_text = change_colons_and_semicolons_to_periods(cleaned_text)
cleaned_text = lowercase_text(cleaned_text)

print("Cleaned Text:\n", cleaned_text)

# %%
# SPLIT INTO SENTENCES

sentences = split_into_sentences(cleaned_text)
for sentence in sentences:
    print("Sentence:", sentence)
print("\n")

# %%
# LEMMATIZATION AND POS TAGGING

lemmatizer = WordNetLemmatizer()
lemmatized_sentences = []
for sentence in sentences:
    tags, lemmatized_tokens, lemmatized_sentence = pos_tag_and_lemmatize(sentence)
    lemmatized_sentences.append(lemmatized_sentence)
    print("Original Sentence:", sentence)
    print("Tokens and POS Tags:", tags)
    print("Lemmatized sentence:", lemmatized_sentence)
    print("\n")

# %%
# REMOVE SOME STOP WORDS AND PUNCTUATION
punctuation = set(string.punctuation)

filtered_sentences = []
for lemmatized_sentence in lemmatized_sentences:
    filtered_tokens, filtered_sentence = clean_sentence(lemmatized_sentence, punctuation)
    filtered_sentences.append(filtered_sentence)
    print("Lemmatized Sentence:", lemmatized_sentence)
    print("Filtered Sentence  :", filtered_sentence)
    print("\n")


# %%
# CHUNKING 

# TODO: We need to work on the grammer template to make it better suited for our needs

# Define chunk grammar
grammar = r"""
  NP: {<DT|PDT>?<RB.*>*<JJ.*>*<NN.*>}   # Noun Phrase: optional determiner, adjectives, noun. Allow RB/RBR/RBS before JJ, and NN.*, not only NN
  VP: {<VB.*><RB.*>*<NP|PP|ADJP>*}      # Verb Phrase: Groups verbs and optional adverbs or noun phrases. Less greedy and allow complements after verb
  PP: {<IN><NP>}                        # Prepositional Phrase: preposition followed by noun phrase
  ADJP: {<RB.*>*<JJ.*>+}                # Adjective Phrase: one or more adjectives
  ADVP: {<RB.*>+}                       # Adverb Phrase: one or more adverbs
"""

tree_sentences = []
chunk_parser = nltk.RegexpParser(grammar)
for filtered_sentence in filtered_sentences:
    tokens = word_tokenize(filtered_sentence)
    tags = pos_tag(tokens)
    sentence_tree = chunk_parser.parse(tags)
    tree_sentences.append(sentence_tree)
    print("Filtered Sentence:", filtered_sentence)
    print(sentence_tree)      # Shows chunk structure
    print("\n")

# Visualize the sentence trees
# for sentence_tree in tree_sentences:
#    sentence_tree.draw()


# %%
"""
# TEMPLATES
Denotation:   (DT|EX|<NN.*>|PRP|PRP$+(NN/NNS)|<NN.*>+POS+<NN.*>) -> is|be|was|were|... -> (DT|EX|<NN.*>|PRP|PRP$+(NN/NNS)|<NN.*>+POS+<NN.*>)
Collection/Attribution/Classification:  (DT|EX|<NN.*>|PRP|PRP$+(NN/NNS)|<NN.*>+POS+<NN.*>) -> has|had|to own|contain|... -> (<RB.*>|<JJ.*>)
Operation:    (DT|EX|<NN.*>|PRP|PRP$+(NN/NNS)|<NN.*>+POS+<NN.*>) -> (<VB.*> except (is|be|was|were|...) and (has|had|to own|contain|...)) and (to|for + <VB.*>)  -> (DT|EX|<NN.*>|PRP|PRP$+(NN/NNS)|<NN.*>+POS+<NN.*>)

# EXAMPLE
Sentence: this be most favourable period for travel in russia
Denotation:   this (DT|EX|<NN.*>|PRP|PRP$+(NN/NNS)|<NN.*>+POS+<NN.*>) -> is|be|was|were|... -> period (DT|EX|<NN.*>|PRP|PRP$+(NN/NNS)|<NN.*>+POS+<NN.*>)
Attribution:  period (DT|EX|<NN.*>|PRP|PRP$+(NN/NNS)|<NN.*>+POS+<NN.*>) -> has|had|to own|contain|... -> most favourable (<RB.*>|<JJ.*>)
Operation:    this (DT|EX|<NN.*>|PRP|PRP$+(NN/NNS)|<NN.*>+POS+<NN.*>) -> (<VB.*> except (is|be|was|were|...) and (has|had|to own|contain|...)) and (to|for + <VB.*>)  -> travel (DT|EX|<NN.*>|PRP|PRP$+(NN/NNS)|<NN.*>+POS+<NN.*>)
Operation:    travel (DT|EX|<NN.*>|PRP|PRP$+(NN/NNS)|<NN.*>+POS+<NN.*>) -> (<VB.*> except (is|be|was|were|...) and (has|had|to own|contain|...)) and (to|for + <VB.*>) -> russia (DT|EX|<NN.*>|PRP|PRP$+(NN/NNS)|<NN.*>+POS+<NN.*>)

# OUTPUT SHOULD BE SIMILAR TO THIS:
this(INSTANCE){
    IS(DENOTATION) period(INSTANCE);
    TO(OPERATION) travel(INSTANCE);
}

this.period{
    HAS(ATTRIBUTION) most-favourable(PROPERTY);
}

this.travel{
    TO(OPERATION) russia(INSTANCE);
}

"""
# %%
# NEW GRAMMER TEMPLATE FOR CHUNKING

grammar = r"""
  NP:   {<DT|PDT>?<RB.*>*<JJ.*>*<NN.*>+|<EX>|<PRP>|<PRP\$><NN.*>+|<NN.*><POS><NN.*>+}
  NP:   {<NNP|NNPS>+}
  NP:   {<DT>}
  ADJP: {<RB.*>*<JJ.*>+}
  ADVP: {<RB.*>+}
  PP:   {<IN><NP>}
  INF:  {<TO><VB.*>(<NP|PP|ADJP|ADVP>*)}
  NP:   {<NP><INF>}
  NP:   {<NP><PP>+}
  NP:   {<NP><CC><NP>}
  VP:   {<MD>?<VB.*><RB.*>*<NP|PP|ADJP|ADVP|INF>*}  # Added modal support
  VP:   {<VP><CC><VP>}
  SENT: {<NP><VP>}
  SENT: {<EX><VP>}  # Existential: "There is..."
  SENT: {<VP>}      # Imperative: "Come here!"
"""

chunk_parser = nltk.RegexpParser(grammar)
wnl = WordNetLemmatizer()

# quick sanity check
s = "i now say thank god she do not live to witness cruel miserable death of her young darling"
tags = pos_tag(word_tokenize(s))
tree = chunk_parser.parse(tags)
print(s)
print(tree)
# tree.draw()

# %%

# %%
