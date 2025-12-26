
# =========================================================
# ===== file: core/dialog/clarification.py
# =========================================================
from typing import Any, Dict, List, Tuple


class Clarifier:
    """
    不用 LLM 也能做的澄清：
    - 缺关键槽位
    - 策略冲突（审批/限额/黑名单）
    """

    REQUIRED_SLOTS = {
        "transfer": ["to", "amount"],
        "withdraw": ["amount"],
        "cancel_order": ["order_id"],
        "create_order": ["item"],
    }

    def questions_for_missing_slots(self, frame: Dict[str, Any]) -> List[str]:
        intent = frame.get("intent", "unknown")
        slots = frame.get("slots", {}) or {}
        req = self.REQUIRED_SLOTS.get(intent, [])
        qs = []
        for k in req:
            if slots.get(k) in (None, "", []):
                qs.append(self._ask_for(k, intent))
        return qs

    def questions_for_conflict(self, error: str) -> List[str]:
        if not error:
            return []
        qs = []
        if "BLOCKED_TARGET" in error:
            qs.append("该收款对象在黑名单中，你是否要更换收款人？")
        if "FORBID_APPROVAL" in error or "approval" in error.lower():
            qs.append("该操作按策略需要审批。你是否接受审批，或降低金额到免审批范围？")
        if "MAX_TRANSFER" in error or "exceeds policy" in error:
            qs.append("金额超过上限。你要降低金额还是拆分多笔？")
        return qs

    def _ask_for(self, slot: str, intent: str) -> str:
        mapping = {
            "to": "你要转给谁？请输入收款人标识。",
            "amount": "金额是多少？请输入数值（如 100/1k/2w）。",
            "order_id": "订单号是多少？例如 order #A1024。",
            "item": "你要购买什么商品？请给出名称。",
        }
        return mapping.get(slot, f"请提供 {slot} 的值。")
