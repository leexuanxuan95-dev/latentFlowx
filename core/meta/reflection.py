# =========================================================
# ===== file: core/meta/reflection.py
# =========================================================
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ReflectionResult:
    ok: bool
    failure_type: Optional[str] = None
    message: str = ""
    meta: Dict[str, Any] = None


class Reflector:
    """
    反思 = 失败分类 + 可复用经验
    """

    def classify_failure(self, err: Exception, stage: str) -> ReflectionResult:
        msg = str(err)

        # 约束/策略类
        if "POLICY_" in msg or "CONSTRAINT_" in msg:
            return ReflectionResult(ok=False, failure_type="constraint_violation", message=msg, meta={"stage": stage})

        # Guard 类（状态安全）
        if "MAX_" in msg or "DENY_" in msg or "State overflow" in msg:
            return ReflectionResult(ok=False, failure_type="state_guard_violation", message=msg, meta={"stage": stage})

        # 工具执行类
        if "Tool not found" in msg or "tool" in msg.lower():
            return ReflectionResult(ok=False, failure_type="tool_error", message=msg, meta={"stage": stage})

        return ReflectionResult(ok=False, failure_type="unknown_failure", message=msg, meta={"stage": stage})