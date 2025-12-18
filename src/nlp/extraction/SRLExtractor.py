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

    REL_PRONOUNS = {"that", "which", "who", "whom", "whose"}

    CORE_PREPS = {"to", "for", "with", "onto", "into"}  # prepositions that often mark objects

    SUBJECT_DEPS: Set[str] = {"nsubj", "nsubjpass", "csubj"}
    OBJECT_DEPS: Set[str] = {"obj", "dobj", "attr", "oprd"} 
    COMPLEMENT_DEPS: Set[str] = {"xcomp", "ccomp", "pcomp"}  # embedded verbs

    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize SRL extractor with spaCy model."""
        self.nlp = spacy.load(model_name)
    
    def _split_into_clauses(self, sent):
        """
        Split into:
          - main clause tokens (sentence minus any relcl subtrees)
          - each relative clause as a contiguous span (relcl verb subtree)
        Returns a list where the first item is a LIST of tokens (main clause),
        and the rest are spaCy spans (relative clauses).
        """
        # 1) Collect relative clauses (spans) and all their token indices
        relcl_spans = []
        relcl_token_ids = set()

        for t in sent:
            if t.dep_ == "relcl" and t.pos_ in {"VERB", "AUX"}:
                toks = list(t.subtree)
                start = toks[0].i
                end = toks[-1].i + 1
                span = sent.doc[start:end]
                relcl_spans.append(span)
                relcl_token_ids.update(tok.i for tok in toks)

        # 2) Main clause = sentence tokens excluding relcl tokens
        main_clause_tokens = [tok for tok in sent if tok.i not in relcl_token_ids]

        # Sort relcls left-to-right
        relcl_spans.sort(key=lambda sp: sp.start)

        # main clause first, then relcls
        return [main_clause_tokens] + relcl_spans
    

    def _resolve_relative_pronoun(self, tokens, arg):
        """
        Generic resolver for relative pronouns inside a relative clause.

        If `arg` is a relative pronoun (that/which/who/whom/whose) AND the given
        token sequence contains a relcl verb, resolve it to the antecedent noun
        (relcl_verb.head.text). Otherwise return `arg` unchanged.

        Args:
            tokens: iterable of spaCy Tokens (list[Token] or Span)
            arg: str | None

        Returns:
            str | None
        """
        if not arg:
            return arg

        if arg.lower() not in self.REL_PRONOUNS:
            return arg

        relcl_verb = None
        for t in tokens:
            if t.dep_ == "relcl" and t.pos_ in {"VERB", "AUX"}:
                relcl_verb = t
                break

        if not relcl_verb:
            return arg  # not a relative clause context

        return relcl_verb.head.text

    def _get_relcl_antecedent(self, tokens):
        """If tokens belong to a relcl clause, return the antecedent noun text; else None."""
        for t in tokens:
            if t.dep_ == "relcl" and t.pos_ in {"VERB", "AUX"}:
                return t.head.text
        return None

    def _get_verb(self, sent):
        """
        Return the full verbal predicate, including auxiliaries.
        e.g. 'has created', 'was built', 'is working'
        """
        main = None

        # find the main verb
        for token in sent:
            if token.pos_ == "VERB" and token.dep_ != "aux":
                main = token
                break

        if not main:
            return None

        # collect auxiliaries attached to the main verb
        verbs = []
        for tok in sent:
            if tok == main or (tok.dep_ in {"aux", "auxpass"} and tok.head == main):
                verbs.append(tok)

        # sort by token position
        verbs.sort(key=lambda t: t.i)

        return " ".join(t.text for t in verbs)


    def _get_subjects(self, sent):
        subs = []

        for token in sent:
            if token.dep_ in self.SUBJECT_DEPS:
                subs.append(token)
                subs.extend(list(token.conjuncts))  # gets "Bob" in "Alice and Bob"

                # dedupe + keep order
                seen = set()
                out = []
                for t in subs:
                    if t.i in seen:
                        continue
                    seen.add(t.i)
                    out.append(t.text)

                return out

        return []


    def _get_objects(self, sent):
        antecedent = self._get_relcl_antecedent(sent)  # None if not a relcl clause
        main_verb_token = None

        # find main verb
        for t in sent:
            if t.pos_ == "VERB" and t.dep_ != "aux":
                main_verb_token = t
                break

        objs = []

        for token in sent:
            # Direct objects
            if token.dep_ in self.OBJECT_DEPS:
                objs.append(token)

                # handle conjunctions
                objs.extend(list(token.conjuncts))

                # nmod/compound nouns
                for child in token.children:
                    if child.dep_ in {"nmod", "compound"} and child.pos_ in {"NOUN", "PROPN"}:
                        objs.append(child)

            ## Prepositional objects attached to the main verb with core preps
            #if token.dep_ == "pobj" and token.head.dep_ == "prep" and token.head.head == main_verb_token:
            #    if token.head.text.lower() in self.CORE_PREPS:
            #        objs.append(token)

        # dedupe, keep order + filter relative pronouns
        seen = set()
        out = []
        for t in objs:
            if t.i in seen:
                continue
            seen.add(t.i)

            if t.text.lower() in self.REL_PRONOUNS:
                if antecedent:
                    out.append(antecedent)
                continue

            out.append(t.text)

        return out

    def _get_attributes(self, sent, heads=None):
        """
        Return adjective attributes grouped by the noun they modify.

        Args:
            sent: iterable of tokens (clause)
            heads: optional list of head noun texts to restrict to (e.g., your objects)

        Returns:
            Dict[str, List[str]] mapping noun -> adjectives
            e.g. {"equipment": ["advanced"], "instruments": ["specialized"]}
        """
        heads_set = set(heads) if heads is not None else None
        attrs = {}

        for token in sent:
            # Noun-modifying adjectives
            if token.pos_ == "ADJ" and token.dep_ == "amod":
                head = token.head.text
                if heads_set is not None and head not in heads_set:
                    continue

                attrs.setdefault(head, []).append(token.text)

                # grab coordinated adjectives: "new and brilliant researcher"
                for conj in token.conjuncts:
                    if conj.pos_ == "ADJ":
                        attrs[head].append(conj.text)

        # dedupe while preserving order
        for head, adjs in attrs.items():
            seen = set()
            deduped = []
            for a in adjs:
                if a in seen:
                    continue
                seen.add(a)
                deduped.append(a)
            attrs[head] = deduped

        return attrs

    def _get_quantifiers(self, sent, heads):
        """
        Extract numeric modifiers (e.g. 'three') attached to given head nouns.

        Args:
            sent: iterable of tokens (clause)
            heads: list of noun texts (e.g. objects you already extracted)

        Returns:
            Dict[str, List[str]] mapping head noun -> list of quantities
            e.g. {"microscopes": ["three"]}
        """
        quantifiers = {}

        for token in sent:
            if token.dep_ == "nummod" and token.head.text in heads:
                quantifiers.setdefault(token.head.text, []).append(token.text)

        return quantifiers

    def _get_prep_pobj_pairs(self, sent, objects=None):
        objects = set(objects or [])
        pairs = []
    
        for token in sent:
            if token.dep_ == "prep":
                pobj = None
                for child in token.children:
                    if child.dep_ in {"pobj", "dative"}:
                        pobj = child.text
                        break
                if pobj and pobj not in objects:
                    pairs.append((token.text, pobj))
    
        return pairs


    def extract_primitives(self, sentence: str) -> Dict[str, List[str]]:
        """
        Args:
            sentence: Input sentence to analyze
            
        Returns:
            Dictionary containing subjects, verbs, objects, anchors, and indirect_objects
        """
        doc = self.nlp(sentence)
                
        for sent in doc.sents:
            clauses = self._split_into_clauses(sent)

            for clause in clauses:
                # normalize clause to token iterable
                tokens = clause if isinstance(clause, list) else list(clause)

                print("-----")
                print("\nCLAUSE:", " ".join(t.text for t in tokens))
                print("-----")

                verb = self._get_verb(tokens)
                obj = self._get_objects(tokens)
                attrs = self._get_attributes(tokens, heads=obj)
                quants = self._get_quantifiers(tokens, obj)
                prep_pobj_pairs = self._get_prep_pobj_pairs(tokens)

                # resolve rel-pronouns for objects/pobj
                obj = [self._resolve_relative_pronoun(tokens, o) for o in obj]
                
                # get *all* subjects (coordinated) and resolve
                subjects = self._get_subjects(tokens)
                subjects = [self._resolve_relative_pronoun(tokens, s) for s in subjects]


                print("  SUBJECT:", subjects)
                print("  VERB:", verb)
                print("  OBJECT:", obj)
                print("  QUANTIFIERS:", quants)
                print("  ATTRIBUTES:", attrs)
                print("  PREP-POBJ PAIRS:", prep_pobj_pairs)
                print("-----")
        exit()
        

        


    def extract_has_components(self, verb_token) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract components for HAS-type sentences.
        
        Args:
            verb_token: The verb token representing the HAS action
        Returns:
            Tuple of (anchor, object) if found, else (None, None)
        """
        pass


    def _get_verb_surrogate(self, lemma: str) -> str:
        """Map verb lemma to primitive surrogate.
        Args:
            lemma: Verb lemma
        Returns:
            Primitive surrogate string
        """
        lemma = (lemma or "").lower()
        if lemma == "be" or lemma in self.DENOTATION_VERBS:
            return "IS"
        elif lemma in {v.lower() for v in self.ATTRIBUTION_VERBS}:
            return "HAS"
        else:
            return lemma