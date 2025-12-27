# =========================================================
# ===== file: core/lang/schema.py
# =========================================================
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ConstraintOp(str, Enum):
    # slot required / forbidden
    REQUIRED = "required"
    FORBIDDEN = "forbidden"

    # numeric relations
    LE = "le"
    LT = "lt"
    GE = "ge"
    GT = "gt"

    # equality
    EQ = "eq"
    NEQ = "neq"


@dataclass
class IntentFrame:
    """
    Canonical intent representation (industrial baseline):
    - intent: str
    - slots: dict
    - constraints: list[dict]
    - confidence: float
    - trace: parse trace
    - raw: original text
    """
    intent: str
    slots: Dict[str, Any] = field(default_factory=dict)
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    trace: Dict[str, Any] = field(default_factory=dict)
    raw: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "slots": self.slots,
            "constraints": self.constraints,
            "confidence": self.confidence,
            "trace": self.trace,
            "raw": self.raw,
        }