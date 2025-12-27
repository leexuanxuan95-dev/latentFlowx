# =========================================================
# ===== file: core/planner/action_space.py
# =========================================================
from __future__ import annotations

from typing import Any, Dict, List

from core.planner.action import Action


class ActionSpace:
    """
    Domain action templates for each intent.
    Deterministic and auditable.
    """

    def candidates(self, frame: Dict[str, Any], state=None) -> List[List[Action]]:
        intent = frame.get("intent", "unknown")
        slots = frame.get("slots", {}) or {}

        plans: List[List[Action]] = []

        if intent == "transfer":
            to = slots.get("to")
            amt = slots.get("amount")
            cur = slots.get("currency", "CNY")
            # Candidate plan 1 (safe & standard)
            plans.append([
                Action("check_user", {"user": to}),
                Action("check_balance", {"currency": cur, "amount": amt}),
                Action("create_transfer", {"to": to, "amount": amt, "currency": cur}),
                Action("submit_transfer", {}),
            ])
            # Candidate plan 2 (skip check_balance - riskier / faster)
            plans.append([
                Action("check_user", {"user": to}),
                Action("create_transfer", {"to": to, "amount": amt, "currency": cur}),
                Action("submit_transfer", {}),
            ])
            return plans

        if intent == "withdraw":
            amt = slots.get("amount")
            cur = slots.get("currency", "CNY")
            plans.append([
                Action("check_balance", {"currency": cur, "amount": amt}),
                Action("submit_withdraw", {"amount": amt, "currency": cur}),
            ])
            return plans

        if intent == "cancel_order":
            oid = slots.get("order_id")
            plans.append([
                Action("load_order", {"order_id": oid}),
                Action("cancel_order", {"order_id": oid}),
            ])
            return plans

        if intent == "create_order":
            item = slots.get("item")
            plans.append([
                Action("create_order", {"item": item}),
            ])
            return plans

        if intent == "qa":
            # "qa" is not tool-exec by default, but you can add a local tool later
            plans.append([Action("answer", {"query": frame.get("raw")})])
            return plans

        # unknown: no plan
        return []