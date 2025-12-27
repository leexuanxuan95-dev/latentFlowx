# =========================================================
# ===== file: core/dialog/response_builder.py
# =========================================================
from typing import Any, Dict, List, Optional


class ResponseBuilder:
    """
    把结构化结果渲染成“像 GPT 的解释”，但不靠 LLM。
    """

    def render(self, result: Dict[str, Any]) -> str:
        status = result.get("status")

        if status == "OK":
            intent = result.get("intent")
            slots = result.get("slots", {})
            steps = result.get("executed_steps", [])
            return self._ok(intent, slots, steps)

        if status == "NEED_CLARIFICATION":
            qs = result.get("questions", [])
            reason = result.get("reason")
            s = "我需要补充一些信息才能继续。\n"
            if reason:
                s += f"原因：{reason}\n"
            for i, q in enumerate(qs, 1):
                s += f"{i}. {q}\n"
            return s.strip()

        if status == "DENY":
            return f"我不能执行该请求：{result.get('reason') or '触发安全/策略约束'}"

        return f"执行失败：{result.get('reason') or '未知错误'}"

    def _ok(self, intent: str, slots: Dict[str, Any], steps: List[str]) -> str:
        head = f"已完成：{intent}\n"
        if slots:
            head += f"参数：{slots}\n"
        if steps:
            head += f"执行步骤：{steps}\n"
        head += "（可审计/可回滚）"
        return head
