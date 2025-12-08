"""Semantic Role Labeling extraction for knowledge graph construction."""

from typing import Dict, List
import spacy


class SRLExtractor:
    """Extracts semantic roles from sentences using spaCy."""
    
    # Verb categories for primitive extraction
    DENOTATION_VERBS = {
        "am", "are", "is", "was", "were", "be", "being", "been",
        "have been", "has been", "had been"
    }
    
    ATTRIBUTION_VERBS = {
        "have", "has", "had", "own", "owns", "owned",
        "possess", "possesses", "possessed",
        "contain", "contains", "contained",
        "include", "includes", "included",
        "comprise", "comprises", "comprised",
        "hold", "holds", "held"
    }
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize SRL extractor with spaCy model.
        
        Args:
            model_name: Name of the spaCy model to load
        """
        self.nlp = spacy.load(model_name)
    
    def extract_primitives(self, sentence: str) -> Dict[str, List[str]]:
        """Extract semantic primitives from a sentence.
        
        Args:
            sentence: Input sentence to analyze
            
        Returns:
            Dictionary containing subjects, verbs, objects, and indirect_objects
        """
        doc = self.nlp(sentence)
        subjects = []
        verbs = []
        objects = []
        indirect_objects = []
        
        for token in doc:
            if "subj" in token.dep_:
                subjects.append(token.text)
            
            if "VERB" in token.pos_:
                verb_surrogate = self._get_verb_surrogate(token.lemma_)
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
    
    def _get_verb_surrogate(self, lemma: str) -> str:
        """Map verb lemma to primitive surrogate.
        
        Args:
            lemma: Verb lemma
            
        Returns:
            Primitive verb surrogate (IS, HAS, or original lemma)
        """
        if lemma in self.DENOTATION_VERBS:
            return "IS"
        elif lemma in self.ATTRIBUTION_VERBS:
            return "HAS"
        else:
            return lemma
    
    def extract_batch(self, sentences: List[str]) -> List[Dict[str, List[str]]]:
        """Extract primitives from multiple sentences.
        
        Args:
            sentences: List of sentences to process
            
        Returns:
            List of extraction results
        """
        return [self.extract_primitives(sent) for sent in sentences]
