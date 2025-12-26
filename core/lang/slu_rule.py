# =========================================================
# ===== file: core/lang/slu_rule.py
# =========================================================
import re
from typing import List
from core.infer.block import Block


class RuleSLU:
    """
    Non-token SLU: natural language -> structured intent blocks.
    CPU cheap, auditable.
    """

    def parse(self, text: str) -> List[Block]:
        t = text.strip()

        if re.search(r"(取消|撤销|cancel)", t, re.I):
            oid = self._extract_order_id(t)
            return [Block({"intent": "cancel_order", "slots": {"order_id": oid}, "raw": t}, block_type="intent")]

        if re.search(r"(购买|下单|buy|purchase)", t, re.I):
            item = self._extract_item(t)
            return [Block({"intent": "create_order", "slots": {"item": item}, "raw": t}, block_type="intent")]

        return [Block({"intent": "unknown", "slots": {}, "raw": t}, block_type="intent")]

    def _extract_order_id(self, t: str):
        m = re.search(r"(订单|order)\s*#?\s*([A-Za-z0-9_-]+)", t, re.I)
        return m.group(2) if m else None

    def _extract_item(self, t: str):
        m = re.search(r"(购买|buy|purchase)\s+(.+)", t, re.I)
        return m.group(2).strip() if m else None