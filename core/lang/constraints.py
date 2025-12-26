
# =========================================================
# ===== file: core/lang/constraints.py
# =========================================================
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from core.lang.schema import Constraint, ConstraintOp
from core.lang.normalizer import parse_amount, normalize_whitespace


class ConstraintCompiler:
    """
    NL -> constraints.
    Keep it deterministic. Later you can add learned constraint extractor.
    """

    def compile(self, text: str, slots: Dict[str, Any]) -> Tuple[List[Constraint], Dict[str, Any]]:
        t = normalize_whitespace(text)
        cons: List[Constraint] = []
        trace: Dict[str, Any] = {"rules": []}

        # "不超过1000" / "最多1000" / "<= 1000"
        m = re.search(r"(不超过|最多|<=|≤)\s*([0-9]+(?:\.[0-9]+)?\s*(?:k|K|w|W|万|千)?)", t)
        if m:
            v = parse_amount(m.group(2))
            if v is not None:
                cons.append(Constraint(key="amount", op=ConstraintOp.LE, value=v, meta={"src": m.group(0)}))
                trace["rules"].append({"constraint": "amount<=X", "src": m.group(0)})

        # "小于1000"
        m = re.search(r"(小于|<)\s*([0-9]+(?:\.[0-9]+)?\s*(?:k|K|w|W|万|千)?)", t)
        if m:
            v = parse_amount(m.group(2))
            if v is not None:
                cons.append(Constraint(key="amount", op=ConstraintOp.LT, value=v, meta={"src": m.group(0)}))
                trace["rules"].append({"constraint": "amount<X", "src": m.group(0)})

        # "不要审批" / "无需审批"
        if re.search(r"(不要|无需)\s*审批", t):
            cons.append(Constraint(key="requires_approval", op=ConstraintOp.FORBIDDEN, value=True, meta={"src": "no_approval"}))
            trace["rules"].append({"constraint": "forbid_approval", "src": "不要/无需审批"})

        # "必须审批"
        if re.search(r"(必须)\s*审批", t):
            cons.append(Constraint(key="requires_approval", op=ConstraintOp.REQUIRED, value=True, meta={"src": "must_approval"}))
            trace["rules"].append({"constraint": "require_approval", "src": "必须审批"})

        # "禁止转给X"
        m = re.search(r"(禁止|不要)\s*(转给|给|to)\s*([A-Za-z0-9_\-\u4e00-\u9fa5]{1,32})", t, re.I)
        if m:
            cons.append(Constraint(key="to", op=ConstraintOp.NEQ, value=m.group(3), meta={"src": m.group(0)}))
            trace["rules"].append({"constraint": "to!=X", "src": m.group(0)})

        # slots-driven safety defaults
        # If intent looks like money movement and amount exists, we can attach a "non_negative" constraint.
        if "amount" in slots:
            cons.append(Constraint(key="amount", op=ConstraintOp.GE, value=0, meta={"src": "default_non_negative"}))
            trace["rules"].append({"constraint": "amount>=0", "src": "default"})

        return cons, trace