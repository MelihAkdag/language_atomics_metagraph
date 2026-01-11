from __future__ import annotations

from typing import Optional

from nlp.providers.contracts import SRLProvider, CorefResolver
from nlp.providers.spacy_backends import SpacySRLProvider, HeuristicCorefProvider


def create_srl_provider(
    backend: str,
    *,
    extractor=None,
    llm_client=None,
) -> SRLProvider:
    backend = (backend or "spacy").lower()

    if backend == "spacy":
        if extractor is None:
            raise ValueError("extractor is required for srl_backend='spacy'")
        return SpacySRLProvider(extractor)

    if backend == "llm":
        if llm_client is None:
            raise ValueError("llm_client is required for srl_backend='llm'")
        from nlp.providers.llm_backends import LLMSRLProvider
        return LLMSRLProvider(llm_client)

    raise ValueError(f"Unknown srl_backend: {backend!r}")


def create_coref_resolver(
    backend: str,
    *,
    nlp=None,
    llm_client=None,
) -> Optional[CorefResolver]:
    backend = (backend or "heuristic").lower()

    if backend in ("none", "off", "disabled"):
        return None

    if backend in ("heuristic", "spacy"):
        if nlp is None:
            raise ValueError("nlp is required for coref_backend='heuristic'")
        return HeuristicCorefProvider(nlp)

    if backend == "llm":
        if llm_client is None:
            raise ValueError("llm_client is required for coref_backend='llm'")
        from nlp.providers.llm_backends import LLMCorefProvider
        return LLMCorefProvider(llm_client)

    raise ValueError(f"Unknown coref_backend: {backend!r}")