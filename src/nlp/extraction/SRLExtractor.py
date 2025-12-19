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
        "take", "takes", "took",
        "receive", "receives", "received",
        "earn", "earns", "earned",
        "get", "gets", "got",
        "carry", "carries", "carried",
        "hold", "holds", "held"
    }

    ATTRIBUTION_VERBS_INVERSE = {
        "belong", "belongs", "belonged",
        "relate", "relates", "related",
        "associate", "associates", "associated"
        }
    
    INVERSE_PREPS = {"in", "at", "from", "of", "on", "under", "above", "below", "near"} # these will be used to create HAS_INVERSE anchors

    REL_PRONOUNS = {"that", "which", "who", "whom", "whose"}

    CORE_PREPS = {"to", "for", "with", "onto", "into"}  # prepositions that often mark objects

    SUBJECT_DEPS: Set[str] = {"nsubj", "nsubjpass", "csubj"}
    OBJECT_DEPS: Set[str] = {"obj", "dobj", "attr", "oprd"} 

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
        (relcl_verb.head). Otherwise return `arg` unchanged.

        Args:
            tokens: iterable of spaCy Tokens (list[Token] or Span)
            arg: str | None

        Returns:
            str | None
        """
        if not arg:
            return arg

        if arg.text.lower() not in self.REL_PRONOUNS:
            return arg

        relcl_verb = None
        for t in tokens:
            if t.dep_ == "relcl" and t.pos_ in {"VERB", "AUX"}:
                relcl_verb = t
                break

        if not relcl_verb:
            return arg  # not a relative clause context

        return relcl_verb.head

    def _get_relcl_antecedent(self, tokens):
        """If tokens belong to a relcl clause, return the antecedent noun; else None."""
        for t in tokens:
            if t.dep_ == "relcl" and t.pos_ in {"VERB", "AUX"}:
                return t.head
        return None

    def _get_verb(self, sent):
        """
        Return the main verb's lemma (root form), ignoring auxiliaries.
        """
        for token in sent:
            if token.pos_ == "VERB" or (token.dep_ == "ROOT" and token.dep_ != "aux"):
                return token.lemma_
        return None


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
                    out.append(t)

                return out

        return []


    def _get_appositives(self, sent):
        """
        Extract appositive relationships (e.g., "Her colleague, Bob").

        Returns:
            Dict mapping head noun -> list of appositive tokens
            e.g., {colleague_token: [Bob_token]}
        """
        appositives = {}

        for token in sent:
            if token.dep_ == "appos":
                head = token.head
                appositives.setdefault(head, []).append(token)

                # Handle coordinated appositives: "my friends, Alice and Bob"
                for conj in token.conjuncts:
                    appositives[head].append(conj)

        return appositives


    def _get_objects(self, sent):
        antecedent = self._get_relcl_antecedent(sent)  # None if not a relcl clause
        main_verb_token = None

        # find main verb
        for t in sent:
            if t.pos_ == "VERB" or (t.dep_ == "ROOT" and t.dep_ != "aux"):
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

            # Prepositional objects attached to the main verb with core preps
            if token.dep_ == "pobj" and token.head.dep_ == "prep" and token.head.head == main_verb_token:
                if token.head.text.lower() in self.CORE_PREPS:
                    objs.append(token)
            
            # Adjectival complements (copular constructions)
            if token.dep_ == "acomp" and token.head == main_verb_token:
                objs.append(token)

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

            out.append(t)

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
                head = token.head
                if heads_set is not None and head not in heads_set:
                    continue

                attrs.setdefault(head, []).append(token)

                # grab coordinated adjectives: "new and brilliant researcher"
                for conj in token.conjuncts:
                    if conj.pos_ == "ADJ":
                        attrs[head].append(conj)

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
            if token.dep_ == "nummod" and token.head in heads:
                quantifiers.setdefault(token.head, []).append(token)

        return quantifiers

    def _get_possessives(self, sent):
        """
        Extract possessive relationships (e.g., "her colleague" -> she HAS colleague).

        Returns:
            Dict mapping possessed noun -> possessor token
            e.g., {colleague_token: her_token}
        """
        possessives = {}

        for token in sent:
            # Check for possessive determiners (her, his, their, my, your, our, its)
            if token.dep_ == "poss" and token.pos_ in {"PRON", "DET"}:
                head = token.head
                possessives[head] = token

        return possessives


    def _get_prep_pobj_pairs(self, sent, objects=None):
        objects = set(objects or [])
        pairs = []
    
        for token in sent:
            if token.dep_ == "prep":
                pobj = None
                for child in token.children:
                    if child.dep_ in {"pobj", "dative"}:
                        pobj = child
                        break
                if pobj and pobj not in objects:
                    pairs.append((token, pobj))
    
        return pairs


    def _prepare_anchors(self, objects, quantifiers=None, attributes=None, prep_pobj_pairs=None):
        """
        Prepare anchors for HAS primitive.

        Args:
            verb: spaCy Token or string representing the main verb
            objects: list of spaCy Tokens (direct objects or acomp)
            quantifiers: dict mapping object text -> list of quantities
            attributes: dict mapping object text -> list of attributes
            prep_pobj_pairs: list of (prep, pobj_text) tuples

        Returns:
            Tuple of (anchors, inverse_relations)
            - anchors: List of anchor dicts for attributes/quantifiers
            - inverse_relations: List of (prep, pobj) tuples that should become HAS_INVERSE
        """
        anchors = []
        quantifiers = quantifiers or {}
        attributes = attributes or {}
        prep_pobj_pairs = prep_pobj_pairs or []
        inverse_relations = []

        # 1) Define attributes and quantifiers as anchor for objects
        for head, quants in quantifiers.items():
            if head in objects:
                for quant in quants:
                    anchors.append({head.text: quant.text})

        for head, adjs in attributes.items():
            if head in objects:
                for adj in adjs:
                    anchors.append({head.text: adj.text})
        
        # 2) Anchors from prepositional object pairs
        for obj in objects:
            for prep, pobj in prep_pobj_pairs:
                if pobj not in [o.text if not isinstance(o, str) else o for o in objects]:
                    # Check if this preposition indicates an inverse relationship
                    if prep.text.lower() in self.INVERSE_PREPS:
                        inverse_relations.append((prep.text.lower(), pobj.text.lower(), obj.text.lower()))
                    else:
                        # Keep as anchor for non-inverse preps
                        anchors.append({obj.text: f"{prep.text} {pobj.text}"})

        return anchors, inverse_relations


    def extract_primitives(self, sentence: str):
        """
        Args:
            sentence: Input sentence to analyze
            
        Returns:
            Dictionary containing subjects, verbs, objects, anchors, and indirect_objects
        """
        doc = self.nlp(sentence)
        results = []
                
        for sent in doc.sents:
            clauses = self._split_into_clauses(sent)

            for clause in clauses:
                # normalize clause to token iterable
                tokens = clause if isinstance(clause, list) else list(clause)

                verb = self._get_verb(tokens)
                # Use verb surrogate for IS and HAS primtives
                verb = self._get_verb_surrogate(verb)
                objects = self._get_objects(tokens)
                attrs = self._get_attributes(tokens, heads=objects)
                quants = self._get_quantifiers(tokens, objects)
                prep_pobj_pairs = self._get_prep_pobj_pairs(tokens)

                # resolve rel-pronouns for objects/pobj
                objects = [self._resolve_relative_pronoun(tokens, o) for o in objects]
                
                # get *all* subjects (coordinated) and resolve
                subjects = self._get_subjects(tokens)
                subjects = [self._resolve_relative_pronoun(tokens, s) for s in subjects]

                appositives = self._get_appositives(tokens) # To catch subjects such as "My friend, Sreekant ..."

                # Enrich subjects with their appositives
                enriched_subjects = []
                for subj in subjects:
                    enriched_subjects.append(subj)
                    if subj in appositives:
                        enriched_subjects.extend(appositives[subj])

                subjects = enriched_subjects

                anchors, inverse_relations = self._prepare_anchors(
                    objects=objects,
                    quantifiers=quants,
                    attributes=attrs,
                    prep_pobj_pairs=prep_pobj_pairs
                )

                possessives = self._get_possessives(tokens) # To catch possessive relationships such as "her colleague ..."

                # Extract possessive relationships and add to results
                possessive_relations = []
                for possessed_noun, possessor in possessives.items():
                    possessor_text = self._resolve_possessive_to_subject(possessor.text.lower())

                    # Get the full noun phrase including appositives
                    possessed_items = [possessed_noun]
                    if possessed_noun in appositives:
                        possessed_items.extend(appositives[possessed_noun])

                    # Add each possessive relationship
                    for item in possessed_items:
                        possessive_relations.append({
                            "subject": possessor_text,
                            "object": item.text.lower()
                        })

                subjects = [s.text.lower() for s in subjects]
                objects = [o.text.lower() for o in objects]
                
                result = {
                    "subjects": subjects,
                    "verbs": verb,
                    "objects": objects,
                    "anchors": anchors,
                    "inverse_relations": inverse_relations,
                    "possessive_relations": possessive_relations
                }
                results.append(result)
                
                #print("-----")
                #print("\nCLAUSE:", " ".join(t.text for t in tokens))
                #print("-----")
                #print("  SUBJECT:", subjects)
                #print("  VERB:", verb)
                #print("  OBJECT:", objects)
                #print("  QUANTIFIERS:", quants)
                #print("  ATTRIBUTES:", attrs)
                #print("  PREP-POBJ PAIRS:", prep_pobj_pairs)
                #print("  ANCHORS (for HAS):", anchors if verb == "HAS" else "N/A")
                #print("  INVERSE RELATIONS (for HAS_INVERSE):", inverse_relations if verb == "HAS_INVERSE" else "N/A")
                #print("  POSSESSIVE RELATIONS:", possessive_relations)
                #print("-----")
            #exit()
        return results


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
        elif lemma in {v.lower() for v in self.ATTRIBUTION_VERBS_INVERSE}:
            return "HAS_INVERSE"
        else:
            return lemma
    
    def _resolve_possessive_to_subject(self, possessive: str) -> str:
        """Convert possessive pronouns to subject form."""
        mapping = {
            "my": "i",
            "your": "you",
            "his": "he",
            "her": "she",
            "its": "it",
            "our": "we",
            "their": "they"
        }
        return mapping.get(possessive, possessive)


            