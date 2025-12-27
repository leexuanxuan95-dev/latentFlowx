# =========================================================
# ===== file: core/lang/constraints.py
# =========================================================
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from core.lang.schema import ConstraintOp


class ConstraintCompiler:
    """
    Compile natural language constraints -> structured constraints.
    Deterministic baseline.

    Output format:
      {"key": "...", "op": "...", "value": ...}
    """

    def compile(self, text: str, slots: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        cons: List[Dict[str, Any]] = []
        trace: Dict[str, Any] = {"matched": []}

        t = text.strip()

        # "不要审批" / "no approval"
        if re.search(r"(不要审批|不需要审批|no\s+approval|without\s+approval)", t, re.I):
            cons.append({"key": "requires_approval", "op": ConstraintOp.FORBIDDEN.value, "value": True})
            trace["matched"].append("constraint:forbid_approval")

        # "不要超过 1000" / "不超过1000" / "<= 1000"
        m = re.search(r"(不要超过|不超过|<=)\s*(\d+(?:\.\d+)?)", t)
        if m:
            cons.append({"key": "amount", "op": ConstraintOp.LE.value, "value": float(m.group(2))})
            trace["matched"].append("constraint:amount_le")

        # "至少 100" / ">= 100"
        m = re.search(r"(至少|>=)\s*(\d+(?:\.\d+)?)", t)
        if m:
            cons.append({"key": "amount", "op": ConstraintOp.GE.value, "value": float(m.group(2))})
            trace["matched"].append("constraint:amount_ge")

        # required slots by intent keywords in text (optional)
        # Example: "必须有订单号"
        if re.search(r"(必须|需要)\s*(订单号|order\s*id)", t, re.I):
            cons.append({"key": "order_id", "op": ConstraintOp.REQUIRED.value, "value": True})
            trace["matched"].append("constraint:order_id_required")

        return cons, trace