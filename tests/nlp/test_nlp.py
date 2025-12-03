# %%
"""
##########################################################
# SOME TOOLS WE CAN USE FROM NLTK LIBRARY
##########################################################

* Classification: Assigning a label or category to a piece of text. TODO: Can we use it for converting "not" into "False"?

* Tokenization: Breaking text into smaller units (tokens), usually words or sentences.

* Stemming: Reducing words to their root form by chopping off suffixes (not always a real word). Example: "running", "runs", "runner" → "run". Probably we can use lemmatization instead of stemming.

* Lemmatization: Reducing words to their base or dictionary form (unlike stemming, it produces real words). Example: "running" → "run", "better" → "good". TODO: Do we want to keep tenses?

* Tagging (Part-of-speech (POS) tagging): Assigning grammatical tags to words (noun, verb, adjective, adverb). Example: "I love NLP" → [("I", PRON), ("love", VERB), ("NLP", NOUN)]. TODO: Make a list of tags.

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


* Parsing: Analyzing the grammatical structure of a sentence (syntax tree). Example: "The cat sat on the mat" → A tree showing subject, verb, object, etc.

* Chunking: Grouping words into meaningful phrases (like noun phrases or verb phrases). Example: "The big dog" → [NP The big dog].

* Named entity recognition (NER): Identifying and classifying named entities in text (like people, organizations, locations). Example: "Barack Obama was born in Hawaii" → [("Barack Obama", PERSON), ("Hawaii", LOCATION)].

* Dependency parsing: Finding relationships between words (subject, object, modifiers). Example: "The cat chased the mouse" → cat (subject) → chased (verb) → mouse (object).

* Semantic Reasoning: Understanding meaning and relationships beyond syntax.

"""

# %%
import nltk
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
# Remove line breaks and join sentences
def remove_line_breaks(text):
    """ Remove line breaks from the text """
    return text.replace('\n', ' ')

# Remove multiple spaces
def remove_multiple_spaces(text):
    """ Remove multiple spaces from the text """
    return ' '.join(text.split())

# Lowercase the text
def lowercase_text(text):
    """ Lowercase the text """
    return text.lower()

# Split into sentences
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


# %%
##########################################################
# IMPLEMENTATION EXAMPLE
##########################################################

sample_text = """ This is the most favourable period for travelling in Russia. They fly
quickly over the snow in their sledges; the motion is pleasant, and, in
my opinion, far more agreeable than that of an English stagecoach. The
cold is not excessive, if you are wrapped in furs—a dress which I have
already adopted, for there is a great difference between walking the
deck and remaining seated motionless for hours, when no exercise
prevents the blood from actually freezing in your veins. I have no
ambition to lose my life on the post-road between St. Petersburgh and
Archangel."""

# Text cleaning
cleaned_text = remove_line_breaks(sample_text)
cleaned_text = remove_multiple_spaces(cleaned_text)
cleaned_text = lowercase_text(cleaned_text)

# Sentence splitting
sentences = split_into_sentences(cleaned_text)
for sentence in sentences:
    print("Sentence:", sentence)
print("\n")

# Lemmatization and POS tagging
lemmatizer = WordNetLemmatizer()
lemmatized_sentences = []
for sentence in sentences:
    tags, lemmatized_tokens, lemmatized_sentence = pos_tag_and_lemmatize(sentence)
    lemmatized_sentences.append(lemmatized_sentence)
    print("Original Sentence:", sentence)
    print("Tokens and POS Tags:", tags)
    print("Lemmatized sentence:", lemmatized_sentence)
    print("\n")

# Stop words
stop_words = set(stopwords.words('english'))


# %%
