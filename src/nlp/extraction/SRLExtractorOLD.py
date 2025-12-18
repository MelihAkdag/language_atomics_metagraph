"""Semantic Role Labeling extraction for knowledge graph construction."""

from typing import Dict, List, Optional, Set, Tuple
import spacy


class SRLExtractor:
    """Extracts semantic roles from sentences using spaCy."""

    # Verb categories for primitive extraction
    DENOTATION_VERBS = {
        "am", "are", "is", "was", "were", "be", "being", "been"
    }

    ATTRIBUTION_VERBS = {
        "have", "has", "had", "own", "owns", "owned",
        "possess", "possesses", "possessed",
        "contain", "contains", "contained",
        "include", "includes", "included",
        "comprise", "comprises", "comprised",
        "hold", "holds", "held"
    }

    SUBJECT_DEPS: Set[str] = {"nsubj", "nsubjpass", "csubj"}
    OBJECT_DEPS: Set[str] = {"obj", "dobj", "attr", "oprd"} 
    COMPLEMENT_DEPS: Set[str] = {"xcomp", "ccomp", "pcomp"}  # embedded verbs

    # deps that often make noun phrases explode into full clauses
    CLAUSE_DEPS = {"relcl", "acl", "advcl"}     # relative/attributive clauses etc.
    APPOS_DEPS  = {"appos"}                     # appositive "Bob, the engineer"
    NAME_DEPS   = {"compound", "flat", "name"}  # tight name span parts

    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize SRL extractor with spaCy model."""
        self.nlp = spacy.load(model_name)

    def extract_primitives(self, sentence: str) -> Dict[str, List[str]]:
        """
        Args:
            sentence: Input sentence to analyze
            
        Returns:
            Dictionary containing subjects, verbs, objects, anchors, and indirect_objects
        """
        doc = self.nlp(sentence)

        subjects: List[str] = []
        verbs: List[str] = []
        objects: List[str] = []
        anchors: List[str] = []
        indirect_objects: List[str] = []

        # Helper
        def add_unique(lst: List[str], val: Optional[str]) -> None:
            if val and val not in lst:
                lst.append(val)

        # Process sentence-by-sentence
        for sent in doc.sents:
            root = sent.root

            # 1) Handle copular clauses: "X is Y"
            # spaCy often makes Y the ROOT (NOUN/ADJ/PROPN) and "is" a 'cop' child
            if self._is_copular_root(root):
                subj_text = self._first_child_with_dep(root, {"nsubj", "nsubjpass", "csubj"})
                obj_text = self._first_child_with_dep(root, {"obj", "dobj", "attr", "oprd"})
                subjects.append(subj_text)
                objects.append(obj_text)
                verbs.append("IS")

            # 2) Predicate-centered extraction: root verb + embedded verbs
            predicate_verbs = self._collect_predicate_verbs(root)

            # Subjects for inheritance (if embedded verb has no explicit subject)
            inherited_subj_toks = self._get_subjects(root)
            inherited_subjs = self._expand_conj_phrases(inherited_subj_toks)

            for v in predicate_verbs:
                # only consider VERB/AUX predicates
                if v.pos_ not in {"VERB", "AUX"}:
                    continue

                verb_surrogate = self._get_verb_surrogate(v.lemma_)
                verbs.append(verb_surrogate)

                # subjects for this verb (or inherit)
                subj_toks = self._get_subjects(v)
                subj_phrases = self._expand_conj_phrases(subj_toks) or inherited_subjs

                for s in subj_phrases:
                    subjects.append(s)

                # HAS special handling
                if verb_surrogate == "HAS":
                    anchor, obj = self._extract_has_components(v)
                    anchors.append(anchor)
                    objects.append(obj)

                # direct objects / attrs
                obj_toks = self._get_objects(v)
                obj_phrases = self._expand_conj_phrases(obj_toks)

                for o in obj_phrases:
                    objects.append(o)


        return {
            "subjects": subjects,
            "verbs": verbs,
            "objects": objects,
            "anchors": anchors,
            "indirect_objects": indirect_objects,
        }

    
    def _extract_has_components(self, verb_token) -> Tuple[Optional[str], Optional[str]]:
        """Extract anchor and object from HAS relationships."""
        anchor = None
        obj = None

        for child in verb_token.children:
            # direct object is usually the anchor (attribute name)
            if child.dep_ in {"dobj", "obj"}:
                anchor = child.text

                # compound nouns (e.g., "home address")
                compounds = [c.text for c in child.children if c.dep_ == "compound"]
                if compounds:
                    anchor = " ".join(compounds + [child.text])

                # adjective modifiers as value ("blue eyes" -> value blue)
                for grandchild in child.children:
                    if grandchild.dep_ == "amod":
                        obj = grandchild.text
                    elif grandchild.dep_ == "prep":
                        # e.g., "address at 23 Dalcant"
                        for prep_child in grandchild.children:
                            if prep_child.dep_ == "pobj":
                                compounds2 = [
                                    c.text for c in prep_child.children
                                    if c.dep_ in {"compound", "nummod", "quantmod"}
                                ]
                                obj = " ".join(compounds2 + [prep_child.text]) if compounds2 else prep_child.text
                                break

                # fallback to phrase-ish object
                if not obj:
                    obj = self._expand_phrase(child)

            # attribute clauses (e.g., "has been a teacher")
            elif child.dep_ == "attr":
                anchor = "attribute"
                obj = self._expand_phrase(child)

        return anchor, obj

    def _get_verb_surrogate(self, lemma: str) -> str:
        """Map verb lemma to primitive surrogate."""
        lemma = (lemma or "").lower()
        if lemma == "be" or lemma in self.DENOTATION_VERBS:
            return "IS"
        elif lemma in {v.lower() for v in self.ATTRIBUTION_VERBS}:
            return "HAS"
        else:
            return lemma

    def extract_batch(self, sentences: List[str]) -> List[Dict[str, List[str]]]:
        """Extract primitives from multiple sentences."""
        return [self.extract_primitives(sent) for sent in sentences]

    def _is_copular_root(self, root) -> bool:
        # Typical: root is NOUN/ADJ/PROPN and has a 'cop' child ("is/are/was")
        if root.pos_ not in {"NOUN", "ADJ", "PROPN"}:
            return False
        return any(c.dep_ == "cop" for c in root.children)

    def _first_child_with_dep(self, head, deps: Set[str]):
        for c in head.children:
            if c.dep_ in deps:
                return c
        return None

    def _get_subjects(self, verb) -> List:
        return [c for c in verb.children if c.dep_ in self.SUBJECT_DEPS]

    def _get_objects(self, verb) -> List:
        return [c for c in verb.children if c.dep_ in self.OBJECT_DEPS]

    def _collect_predicate_verbs(self, root) -> List:
        """
        Collect root verb plus embedded complement verbs (xcomp/ccomp/pcomp),
        including prep->pcomp patterns like "looking at buying".
        """
        verbs: List = []

        def visit(v) -> None:
            if v.pos_ not in {"VERB", "AUX"}:
                return
            if v not in verbs:
                verbs.append(v)

            # direct complements (xcomp/ccomp/pcomp)
            for ch in v.children:
                if ch.dep_ in self.COMPLEMENT_DEPS and ch.pos_ == "VERB":
                    visit(ch)

            # prep -> pcomp (common in English)
            for prep in [c for c in v.children if c.dep_ == "prep"]:
                for ch in prep.children:
                    if ch.dep_ in self.COMPLEMENT_DEPS and ch.pos_ == "VERB":
                        visit(ch)

        visit(root)
        return verbs

    def _expand_conj_phrases(self, toks: List) -> List[str]:
        """
        Expand each token AND its conjuncts into readable phrases.
        """
        out: List[str] = []
        for t in toks:
            members = [t] + list(getattr(t, "conjuncts", []))
            for m in members:
                phrase = self._expand_phrase(m)
                if phrase and phrase not in out:
                    out.append(phrase)
        return out

    def _expand_phrase(self, token) -> str:
        """
        Prefer named entities; for PROPN use a tight name span;
        otherwise use subtree span but trim at relative/appositive clauses.
        """
        doc = token.doc

        # Prefer entity span (PERSON/ORG/GPE/MONEY...) if token is inside one
        for ent in doc.ents:
            if ent.start <= token.i < ent.end:
                return ent.text

        # Proper nouns: avoid appositive explosion ("Her colleague, Bob, ...")
        if token.pos_ == "PROPN":
            span = self._tight_propn_span(token)
            return span.text

        # Default: subtree span
        start = token.left_edge.i
        end = token.right_edge.i + 1
        span = doc[start:end]

        # Trim clause-y attachments ("that belong to ...")
        span = self._trim_span_at_clauses(span)

        return span.text


    def _tight_propn_span(self, token):
        """Return a minimal span for proper names: compounds/flat/name only."""
        doc = token.doc
        left = token.i
        right = token.i

        # include name/compound tokens on the left
        i = token.i - 1
        while i >= 0 and doc[i].head == token and doc[i].dep_ in self.NAME_DEPS:
            left = i
            i -= 1

        # include name/compound tokens on the right
        i = token.i + 1
        while i < len(doc) and doc[i].head == token and doc[i].dep_ in self.NAME_DEPS:
            right = i
            i += 1

        return doc[left:right+1]

    def _trim_span_at_clauses(self, span):
        """
        Trim span to exclude relative/appositive clauses.
        Keeps core NP but drops 'that belong to ...', ', Bob,', etc.
        """
        if len(span) == 0:
            return span

        # If any token inside is a clause/appos marker, cut span before it (best-effort).
        cut = None
        for i, tok in enumerate(span):
            if tok.dep_ in self.CLAUSE_DEPS or tok.dep_ in self.APPOS_DEPS:
                cut = i
                break

        if cut is not None and cut > 0:
            span = span[:cut]

        # trim edge punctuation
        while len(span) and span[0].is_punct:
            span = span[1:]
        while len(span) and span[-1].is_punct:
            span = span[:-1]

        return span





# BACKUP CODE BELOW

class SRLExtractor_OLD:
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
            if "nsubj" in token.dep_:
                subjects.append(token.text)
                print(f"Found subject: {token.text}")
            
            # Extract verbs and handle HAS relationships specially
            if "VERB" in token.pos_:
                verb_surrogate = self._get_verb_surrogate(token.lemma_)
                verbs.append(verb_surrogate)
                print(f"Found verb: {token.text} (surrogate: {verb_surrogate})")
                
                # For HAS verbs, extract anchors and objects
                if verb_surrogate == "HAS":
                    anchor, obj = self._extract_has_components(token)
                    if anchor:
                        anchors.append(anchor)
                    if obj:
                        objects.append(obj)
            
            # Extract objects 
            if "obj" in token.dep_:
                objects.append(token.text)
                print(f"Found object: {token.text}")
            
            # Extract indirect objects (dative as "to her", "for him", etc.)
            if "dative" in token.dep_:
                indirect_objects.append(token.text)
                print(f"Found indirect object: {token.text}")
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
