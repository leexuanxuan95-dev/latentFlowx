
# =========================================================
# ===== file: core/verify/constraints_verifier.py
# =========================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.lang.schema import ConstraintOp
from core.verify.policy import Policy


@dataclass
class ConstraintViolation(Exception):
    code: str
    message: str
    meta: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        return f"[{self.code}] {self.message} meta={self.meta or {}}"


class ConstraintsVerifier:
    """
    Verify semantic constraints + policy.
    This is ABOVE low-level guard/invariants.
    """

    def __init__(self, policy: Optional[Policy] = None):
        self.policy = policy or Policy()

    def verify_intent_frame(self, frame: Dict[str, Any], state=None) -> Dict[str, Any]:
        trace = {"checked": [], "passed": [], "failed": None}

        intent = frame.get("intent", "unknown")
        if intent not in self.policy.allowed_intents:
            raise ConstraintViolation("POLICY_INTENT_DENY", f"intent not allowed: {intent}", {"intent": intent})
        trace["checked"].append("policy.allowed_intents")
        trace["passed"].append("policy.allowed_intents")

        slots = frame.get("slots", {}) or {}
        constraints = frame.get("constraints", []) or []

        # policy: blocked targets
        to = slots.get("to")
        if to and to in self.policy.blocked_targets:
            raise ConstraintViolation("POLICY_BLOCKED_TARGET", f"target blocked: {to}", {"to": to})
        trace["checked"].append("policy.blocked_targets")
        trace["passed"].append("policy.blocked_targets")

        # policy: max amount by intent
        amt = slots.get("amount")
        if intent == "transfer" and amt is not None and float(amt) > self.policy.max_transfer_amount:
            raise ConstraintViolation(
                "POLICY_MAX_TRANSFER",
                f"transfer amount exceeds policy max: {amt} > {self.policy.max_transfer_amount}",
                {"amount": amt, "max": self.policy.max_transfer_amount},
            )
        if intent == "withdraw" and amt is not None and float(amt) > self.policy.max_withdraw_amount:
            raise ConstraintViolation(
                "POLICY_MAX_WITHDRAW",
                f"withdraw amount exceeds policy max: {amt} > {self.policy.max_withdraw_amount}",
                {"amount": amt, "max": self.policy.max_withdraw_amount},
            )

        trace["checked"].append("policy.max_amount")
        trace["passed"].append("policy.max_amount")

        # explicit constraints
        for c in constraints:
            key = c.get("key")
            op = c.get("op")
            val = c.get("value")
            trace["checked"].append(f"constraint:{key}:{op}")

            cur = slots.get(key)

            if op == ConstraintOp.REQUIRED.value:
                if val is True and not cur:
                    raise ConstraintViolation("CONSTRAINT_REQUIRED", f"{key} required", {"key": key})

            elif op == ConstraintOp.FORBIDDEN.value:
                # e.g. forbidding approval while policy requires it
                if key == "requires_approval" and val is True:
                    if amt is not None and float(amt) > self.policy.require_approval_over:
                        raise ConstraintViolation(
                            "CONSTRAINT_FORBID_APPROVAL",
                            "approval required by policy but forbidden by user constraint",
                            {"amount": amt, "threshold": self.policy.require_approval_over},
                        )

            elif op == ConstraintOp.LE.value:
                if cur is not None and float(cur) > float(val):
                    raise ConstraintViolation("CONSTRAINT_LE", f"{key} exceeds constraint: {cur} > {val}", {"cur": cur, "val": val})

            elif op == ConstraintOp.LT.value:
                if cur is not None and float(cur) >= float(val):
                    raise ConstraintViolation("CONSTRAINT_LT", f"{key} violates constraint: {cur} >= {val}", {"cur": cur, "val": val})

            elif op == ConstraintOp.GE.value:
                if cur is not None and float(cur) < float(val):
                    raise ConstraintViolation("CONSTRAINT_GE", f"{key} violates constraint: {cur} < {val}", {"cur": cur, "val": val})

            elif op == ConstraintOp.GT.value:
                if cur is not None and float(cur) <= float(val):
                    raise ConstraintViolation("CONSTRAINT_GT", f"{key} violates constraint: {cur} <= {val}", {"cur": cur, "val": val})

            elif op == ConstraintOp.EQ.value:
                if cur != val:
                    raise ConstraintViolation("CONSTRAINT_EQ", f"{key} must equal {val}", {"cur": cur, "val": val})

            elif op == ConstraintOp.NEQ.value:
                if cur == val:
                    raise ConstraintViolation("CONSTRAINT_NEQ", f"{key} must not equal {val}", {"cur": cur, "val": val})

            trace["passed"].append(f"constraint:{key}:{op}")

        return trace

