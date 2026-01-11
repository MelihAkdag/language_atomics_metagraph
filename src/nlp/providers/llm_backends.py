from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol

from nlp.providers.contracts import SRLProvider, CorefResolver


class LLMClient(Protocol):
    """
    Minimal client contract for future LLM integration.
    Implementations could wrap OpenAI/Azure/Ollama/etc.
    """
    def complete_json(self, *, system: str, user: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        ...


class LLMSRLProvider(SRLProvider):
    """
    Template SRL provider that will call an LLM and return the same schema
    as the spaCy SRL provider.
    """
    def __init__(self, client: LLMClient, model: str = "gpt-4o-mini"):
        self.client = client
        self.model = model

    def extract_primitives(self, sentence: str) -> List[Dict[str, Any]]:
        raise NotImplementedError(
            "LLMSRLProvider is a template. Implement by calling your LLM client and "
            "returning List[Dict[str, Any]] with keys: subjects, verbs, objects, anchors, "
            "inverse_relations, possessive_relations."
        )


class LLMCorefProvider(CorefResolver):
    """
    Template coreference resolver. Must return a transformed text string.
    """
    def __init__(self, client: LLMClient, model: str = "gpt-4o-mini"):
        self.client = client
        self.model = model

    def resolve_text(self, text: str, strategy: str = "filter", verbose: bool = False) -> str:
        raise NotImplementedError(
            "LLMCorefProvider is a template. Implement by calling your LLM client and "
            "returning resolved text. Keep strategy semantics consistent with CoreferenceResolver."
        )