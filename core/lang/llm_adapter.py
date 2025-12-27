# =========================================================
# ===== file: core/lang/llm_adapter.py
# =========================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class LLMResponse:
    text: str
    meta: Dict[str, Any] | None = None


class LLMAdapter:
    """
    可选 LLM 适配器（不是核心！）
    允许做：
      - 润色/改写（render）
      - 生成澄清问题（clarify）
      - 生成解释文本（explain）
    不允许做：
      - 决策（plan/execute）
      - 改写 slot/constraint（除非作为建议返回给用户确认）
    """

    def is_enabled(self) -> bool:
        return False

    def render(self, structured: Dict[str, Any], style: str = "plain") -> LLMResponse:
        """
        输入结构化结果，输出更自然的文字。
        默认实现：不用 LLM，直接模板输出。
        """
        status = structured.get("status")
        if style == "plain":
            return LLMResponse(text=str(structured))
        return LLMResponse(text=str(structured))

    def generate_clarifying_questions(self, intent: str, missing: List[str], conflict_reason: Optional[str] = None) -> LLMResponse:
        """
        默认：不用 LLM，规则式生成问题
        """
        qs: List[str] = []
        for m in missing:
            qs.append(f"请补充 {m}。")
        if conflict_reason:
            qs.append(f"当前存在冲突：{conflict_reason}。你希望如何调整？")
        return LLMResponse(text="\n".join(qs), meta={"questions": qs})


class DummyLLMAdapter(LLMAdapter):
    """
    明确的无 LLM 实现：用于默认/本地 CPU
    """
    def is_enabled(self) -> bool:
        return False
