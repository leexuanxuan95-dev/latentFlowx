# =========================================================
# ===== file: core/lang/llm_adapter.py
# =========================================================
from __future__ import annotations
from typing import Any, Dict, List, Optional


class LLMAdapter:
    """
    Optional plugin. NOT CORE.
    Only allowed roles:
      - rewrite_output(result) -> nicer text
      - suggest_clarification(frame) -> questions
      - weak_label(text) -> training examples (offline)
    """

    def rewrite_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        return result

    def suggest_clarification(self, intent_frame_dict: Dict[str, Any]) -> List[str]:
        return []


class NoopLLMAdapter(LLMAdapter):
    pass
