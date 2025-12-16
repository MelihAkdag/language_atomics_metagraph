"""Semantic Role Labeling extraction for knowledge graph construction."""

from typing import Any, Dict, List
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
    
    def extract_primitives(self, sentence: str) -> Dict[str, Any]:
        """Extract semantic primitives as structured relations.
        
        Args:
            sentence: Input sentence to analyze
            
        Returns:
            Dictionary containing subjects, verbs, objects, anchors, and indirect_objects
        """
        doc = self.nlp(sentence)
        
        relations = []  # List of relation dictionaries
        
        for token in doc:
            if "VERB" in token.pos_:
                verb_surrogate = self._get_verb_surrogate(token.lemma_)
                
                # Extract subject for this verb
                subjects = [child.text for child in token.children if "subj" in child.dep_]
                
                if verb_surrogate == "HAS":
                    # Extract HAS relationship components together
                    anchor, obj = self._extract_has_components(token)
                    for subj in subjects:
                        relations.append({
                            'type': 'HAS',
                            'subject': subj,
                            'anchor': anchor,
                            'object': obj
                        })
                
                elif verb_surrogate == "IS":
                    # Extract IS relationship
                    objects = [child.text for child in token.children if "obj" in child.dep_ or "attr" in child.dep_]
                    for subj in subjects:
                        for obj in objects:
                            relations.append({
                                'type': 'IS',
                                'subject': subj,
                                'object': obj
                            })
                
                else:
                    # Other verbs
                    objects = [child.text for child in token.children if "obj" in child.dep_]
                    for subj in subjects:
                        for obj in objects:
                            relations.append({
                                'type': 'ACTION',
                                'subject': subj,
                                'verb': verb_surrogate,
                                'object': obj
                            })
                
                # Handle indirect objects (dative)
                indirect_objects = [child.text for child in token.children if "dative" in child.dep_]
                for subj in subjects:
                    for ind_obj in indirect_objects:
                        relations.append({
                            'type': 'TO',
                            'subject': subj,
                            'verb': verb_surrogate,
                            'indirect_object': ind_obj
                        })
        
        return {'relations': relations}
    
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
