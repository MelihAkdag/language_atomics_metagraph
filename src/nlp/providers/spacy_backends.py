from __future__ import annotations

from typing import Any, Dict, List

from nlp.extraction.SRLExtractor import SRLExtractor
from nlp.preprocessing.CoreferenceResolver import CoreferenceResolver


class SpacySRLProvider:
    def __init__(self, extractor: SRLExtractor):
        self.extractor = extractor

    def extract_primitives(self, sentence: str) -> List[Dict[str, Any]]:
        return self.extractor.extract_primitives(sentence)


class HeuristicCorefProvider(CoreferenceResolver):
    def __init__(self, nlp):
        self._impl = CoreferenceResolver(nlp)

    def resolve_text(self, text: str, strategy: str = "filter", verbose: bool = False) -> str:
        return self._impl.resolve_text(text, strategy=strategy, verbose=verbose)