# =========================================================
# ===== file: core/verify/post_checks.py
# =========================================================
from typing import Any, Dict, List, Optional


class PostCheckError(Exception):
    pass


class PostChecks:
    """
    执行后校验：比 invariants 更语义
    """

    def check(self, *, intent_frame: Dict[str, Any], executed_actions: List[str], tool_results: List[Dict[str, Any]]):
        intent = intent_frame.get("intent")

        if intent in ("transfer", "withdraw"):
            # 必须出现 submit_*
            if not any(a.startswith("submit_") for a in executed_actions):
                raise PostCheckError(f"POSTCHECK_MISSING_SUBMIT: intent={intent} actions={executed_actions}")

        if intent == "cancel_order":
            if not any(a == "cancel_order" for a in executed_actions):
                raise PostCheckError("POSTCHECK_MISSING_CANCEL_ORDER")

        return True
