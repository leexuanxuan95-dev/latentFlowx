# =========================================================
# ===== file: core/api/contracts.py
# =========================================================
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


class Status(str, Enum):
    OK = "OK"
    DENY = "DENY"
    NEED_CLARIFICATION = "NEED_CLARIFICATION"
    FAIL = "FAIL"


class Trace(TypedDict, total=False):
    plugin: Optional[str]
    plan_trace: Dict[str, Any]
    guard_trace: Dict[str, Any]
    verifier_trace: Dict[str, Any]
    affect: Dict[str, Any]
    causal: Dict[str, Any]


@dataclass
class DecisionResult:
    """
    A 分支输出给 B 分支的唯一标准结构。
    B 只能渲染，不允许绕过 A 的 guard/verifier。
    """
    status: Status
    intent: str = "unknown"
    slots: Dict[str, Any] = field(default_factory=dict)
    constraints: List[Dict[str, Any]] = field(default_factory=list)

    # OK 时
    plan: List[str] = field(default_factory=list)
    executed_steps: List[str] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)

    # NEED_CLARIFICATION 时
    questions: List[str] = field(default_factory=list)

    # DENY/FAIL 时
    reason: Optional[str] = None

    # debug/observability
    trace: Dict[str, Any] = field(default_factory=dict)
    audit_ref: Optional[str] = None  # 以后可接 ELK/Datadog trace id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "intent": self.intent,
            "slots": self.slots,
            "constraints": self.constraints,
            "plan": self.plan,
            "executed_steps": self.executed_steps,
            "tool_results": self.tool_results,
            "questions": self.questions,
            "reason": self.reason,
            "trace": self.trace,
            "audit_ref": self.audit_ref,
        }
