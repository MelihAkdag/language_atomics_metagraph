from __future__ import annotations

from typing import Any, Dict, List, Protocol


class CorefResolver(Protocol):
    def resolve_text(self, text: str, strategy: str = "filter", verbose: bool = False) -> str:
        pass


class SRLProvider(Protocol):
    def extract_primitives(self, sentence: str) -> List[Dict[str, Any]]:
        pass