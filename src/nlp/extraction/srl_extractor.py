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
            Dictionary containing subjects, verbs, objects, anchors, and indirect_objects
        """
        doc = self.nlp(sentence)
        subjects = []
        verbs = []
        objects = []
        anchors = []
        indirect_objects = []
        
        for token in doc:
            # Extract subjects
            if "subj" in token.dep_:
                subjects.append(token.text)
            
            # Extract verbs and handle HAS relationships specially
            if "VERB" in token.pos_:
                verb_surrogate = self._get_verb_surrogate(token.lemma_)
                verbs.append(verb_surrogate)
                
                # For HAS verbs, extract anchors and objects
                if verb_surrogate == "HAS":
                    anchor, obj = self._extract_has_components(token)
                    if anchor:
                        anchors.append(anchor)
                    if obj:
                        objects.append(obj)
            
            # Extract objects (for non-HAS verbs)
            if "obj" in token.dep_ and "HAS" not in verbs:
                objects.append(token.text)
            
            # Extract indirect objects (dative as "to her", "for him", etc.)
            if "dative" in token.dep_:
                indirect_objects.append(token.text)
        
        return {
            'subjects': subjects,
            'verbs': verbs,
            'objects': objects,
            'anchors': anchors,
            'indirect_objects': indirect_objects
        }
    
    def _extract_has_components(self, verb_token) -> tuple:
        """Extract anchor and object from HAS relationships.
        
        For patterns like:
        - "has a home" → anchor="home", object="home" (or more specific if available)
        - "has address at X" → anchor="address", object="X"
        - "has blue eyes" → anchor="eyes", object="blue"
        
        Args:
            verb_token: The HAS verb token from spaCy
            
        Returns:
            Tuple of (anchor, object)
        """
        anchor = None
        obj = None
        
        for child in verb_token.children:
            # Direct object is usually the anchor (attribute name)
            if child.dep_ == "dobj":
                anchor = child.text

                # Check for compound nouns (e.g., "home address")
                compounds = [c.text for c in child.children if c.dep_ == "compound"]
                if compounds:
                    anchor = " ".join(compounds + [child.text])
                
                # Look for adjective modifiers as the actual value
                for grandchild in child.children:
                    if grandchild.dep_ == "amod":  # Adjectival modifier
                        obj = grandchild.text
                    elif grandchild.dep_ == "prep":  # Prepositional phrase
                        # e.g., "address at 23 Dalcant"
                        for prep_child in grandchild.children:
                            if prep_child.dep_ == "pobj":
                                # Get full prepositional object with compounds/numbers
                                compounds = [c.text for c in prep_child.children 
                                           if c.dep_ in ["compound", "nummod"]]
                                if compounds:
                                    obj = " ".join(compounds + [prep_child.text])
                                else:
                                    obj = prep_child.text
                                break  # Take the first pobj found
                
                # If no specific object found, use a compound or the anchor itself
                if not obj:
                    # Check if there's a determiner + noun pattern
                    det_children = [c for c in child.children if c.dep_ == "det"]
                    if det_children:
                        obj = f"{det_children[0].text} {child.text}"
                    else:
                        obj = child.text
            
            # Handle attribute clauses (e.g., "has been a teacher")
            elif child.dep_ == "attr":
                anchor = "attribute"
                obj = child.text
        
        return anchor, obj
    
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
