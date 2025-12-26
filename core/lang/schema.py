# =========================================================
# ===== file: core/lang/schema.py
# =========================================================
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ConstraintOp(str, Enum):
    LE = "le"          # <=
    LT = "lt"          # <
    GE = "ge"          # >=
    GT = "gt"          # >
    EQ = "eq"          # ==
    NEQ = "neq"        # !=
    IN = "in"          # in set
    NOT_IN = "not_in"  # not in set
    REQUIRED = "required"
    FORBIDDEN = "forbidden"


@dataclass
class Constraint:
    """
    Machine-checkable constraint. Example:
      Constraint(key="amount", op=ConstraintOp.LE, value=1000)
      Constraint(key="requires_approval", op=ConstraintOp.FORBIDDEN, value=True)
    """
    key: str
    op: ConstraintOp
    value: Any
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntentFrame:
    """
    Industrial-grade "semantic block" for intent/slots/constraints.
    This is what you feed into LatentFlow as a Block(content=dict, block_type="intent").
    """
    intent: str
    slots: Dict[str, Any] = field(default_factory=dict)
    constraints: List[Constraint] = field(default_factory=list)
    confidence: float = 0.7
    trace: Dict[str, Any] = field(default_factory=dict)
    raw: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "slots": self.slots,
            "constraints": [
                {"key": c.key, "op": c.op.value, "value": c.value, "meta": c.meta} for c in self.constraints
            ],
            "confidence": self.confidence,
            "trace": self.trace,
            "raw": self.raw,
        }
