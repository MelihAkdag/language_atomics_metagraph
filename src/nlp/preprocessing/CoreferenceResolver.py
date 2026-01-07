"""Pronoun and reference resolution for knowledge graphs."""

from typing import List, Optional
from spacy.tokens import Doc
from tqdm import tqdm


class CoreferenceResolver:
    """Resolves pronouns to their likely antecedents using entity tracking."""
    
    # Pronouns to resolve
    PERSONAL_PRONOUNS = {
        'he', 'him', 'his', 'himself',
        'she', 'her', 'hers', 'herself',
        'they', 'them', 'their', 'theirs', 'themselves',
        'it', 'its', 'itself'
    }
    
    
    FIRST_SECOND_PERSON = {
        'i', 'me', 'my', 'mine', 'myself',
        'we', 'us', 'our', 'ours', 'ourselves',
        'you', 'your', 'yours', 'yourself', 'yourselves'
    }
    
    ALL_PRONOUNS = PERSONAL_PRONOUNS | FIRST_SECOND_PERSON
    
    def __init__(self, nlp):
        """Initialize resolver with spaCy model.
        
        Args:
            nlp: Loaded spaCy language model
        """
        self.nlp = nlp
        self.entity_memory = []  # Track recent entities
        self.memory_size = 50  # How many recent entities to remember
    
    def resolve_text(self, text: str, strategy: str = 'filter', verbose: bool = False) -> str:
        """Resolve pronouns in text.
        
        Args:
            text: Input text with pronouns
            strategy: 'filter' to remove pronouns, 'replace' to substitute
            verbose: Whether to show progress
            
        Returns:
            Text with pronouns handled according to strategy
        """
        doc = self.nlp(text)
        
        if strategy == 'filter':
            return self._filter_pronouns(doc, verbose)
        elif strategy == 'replace':
            return self._replace_pronouns(doc, verbose)
        else:
            return text
    
    def _filter_pronouns(self, doc: Doc, verbose: bool = False) -> str:
        """Remove sentences or clauses with unresolved pronouns.
        
        Args:
            doc: spaCy Doc object
            verbose: Whether to show progress
            
        Returns:
            Filtered text
        """
        filtered_sentences = []
        
        sentences = list(doc.sents)
        iterator = tqdm(sentences, desc="Filtering pronouns", unit="sent") if verbose else sentences
        
        for sent in iterator:
            has_pronoun = any(
                token.text.lower() in self.ALL_PRONOUNS 
                for token in sent
            )
            if not has_pronoun:
                filtered_sentences.append(sent.text)
        
        return ' '.join(filtered_sentences)
    
    def _replace_pronouns(self, doc: Doc, verbose: bool = False) -> str:
        """Replace pronouns with their likely antecedents (KG-safe)."""
        replacements = {}
        self.entity_memory = []

        sentences = list(doc.sents)
        iterator = tqdm(sentences, desc="Resolving pronouns", unit="sent") if verbose else sentences

        for sent in iterator:
            # Resolve pronouns using ONLY previous memory
            for token in sent:
                t = token.text.lower()

                # skip first/second person and anything non-personal
                if t in self.FIRST_SECOND_PERSON:
                    continue

                if t in self.PERSONAL_PRONOUNS:
                    antecedent = self._find_antecedent(token)
                    if antecedent:
                        replacements[token.i] = antecedent
            
            # Update memory with entities from this sentence
            for ent in sent.ents:
                if ent.label_ in {'PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT'}:
                    self._add_to_memory(ent.text, ent.label_)

            for chunk in sent.noun_chunks:
                if chunk.root.dep_ in {'nsubj', 'nsubjpass'}:
                    if chunk.text.lower() not in self.PERSONAL_PRONOUNS:
                        self._add_to_memory(chunk.text, 'NOUN')
            
        # reconstruct text
        new_tokens = []
        for token in doc:
            if token.i in replacements:
                new_tokens.append(replacements[token.i])
            else:
                new_tokens.append(token.text)

        return self._reconstruct_text(doc, new_tokens)

    
    def _add_to_memory(self, entity: str, label: str):
        """Add entity to memory buffer.
        
        Args:
            entity: Entity text
            label: Entity type/label
        """
        # Avoid duplicates and maintain recency
        entry = {'text': entity, 'label': label}
        self.entity_memory = [e for e in self.entity_memory if e['text'] != entity]
        self.entity_memory.append(entry)
        
        # Keep only recent entities
        if len(self.entity_memory) > self.memory_size:
            self.entity_memory.pop(0)
    
    def _find_antecedent(self, pronoun_token) -> Optional[str]:
        if not self.entity_memory:
            return None
    
        pronoun = pronoun_token.text.lower()
    
        # plural pronouns
        if pronoun in {'they', 'them', 'their', 'theirs', 'themselves'}:
            for entry in reversed(self.entity_memory):
                if entry['label'] in {'ORG', 'EVENT'}:
                    return entry['text']
            return None  # do NOT guess
    
        # singular personal pronouns
        if pronoun in {'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself'}:
            for entry in reversed(self.entity_memory):
                if entry['label'] in {'PERSON', 'NOUN'}:
                    return entry['text']
            return None
    
        # neuter pronouns
        if pronoun in {'it', 'its', 'itself'}:
            for entry in reversed(self.entity_memory):
                if entry['label'] in {'ORG', 'PRODUCT', 'EVENT', 'NOUN'}:
                    return entry['text']
    
        return None

    
    def _reconstruct_text(self, doc: Doc, tokens: List[str]) -> str:
        """Reconstruct text from tokens preserving spacing.
        
        Args:
            doc: Original spaCy Doc
            tokens: List of replacement tokens
            
        Returns:
            Reconstructed text
        """
        result = []
        for i, token in enumerate(tokens):
            result.append(token)
            # Add space if original had space after
            if i < len(doc) - 1 and doc[i].whitespace_:
                result.append(' ')
        
        return ''.join(result)
    
    def should_filter_entity(self, entity: str) -> bool:
        """Check if an entity is a pronoun that should be filtered.
        
        Args:
            entity: Entity text to check
            
        Returns:
            True if entity should be filtered out
        """
        return entity.lower() in self.ALL_PRONOUNS