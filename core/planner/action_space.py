# =========================================================
# ===== file: core/planner/action_space.py
# =========================================================
from __future__ import annotations
from typing import Any, Dict, List

from core.planner.action import Action


class ActionSpace:
    """
    Map intent -> candidate actions.
    No LLM. Deterministic.
    """

    def candidates(self, intent_frame: Dict[str, Any], state=None) -> List[List[Action]]:
        """
        Returns a list of candidate plans (each plan is a list[Action]).
        Keep candidates small (Top-K).
        """
        intent = intent_frame.get("intent", "unknown")
        slots = intent_frame.get("slots", {}) or {}

        if intent == "transfer":
            # two candidate plans: with/without pre-check
            to = slots.get("to")
            amt = slots.get("amount")
            cur = slots.get("currency", "CNY")

            plan1 = [
                Action("check_user", {"user": to}),
                Action("check_balance", {"currency": cur, "amount": amt}),
                Action("create_transfer", {"to": to, "amount": amt, "currency": cur}),
                Action("submit_transfer", {}),
            ]
            plan2 = [
                Action("create_transfer", {"to": to, "amount": amt, "currency": cur}),
                Action("submit_transfer", {}),
            ]
            return [plan1, plan2]

        if intent == "withdraw":
            amt = slots.get("amount")
            cur = slots.get("currency", "CNY")
            return [[
                Action("check_balance", {"currency": cur, "amount": amt}),
                Action("create_withdraw", {"amount": amt, "currency": cur}),
                Action("submit_withdraw", {}),
            ]]

        if intent == "cancel_order":
            oid = slots.get("order_id")
            return [[
                Action("load_order", {"order_id": oid}),
                Action("cancel_order", {"order_id": oid}),
            ]]

        if intent == "create_order":
            item = slots.get("item")
            return [[
                Action("create_order", {"item": item}),
                Action("submit_order", {}),
            ]]

        # qa/doc tasks: do not execute tools by default (safe)
        if intent == "qa":
            return [[Action("answer", {"query": intent_frame.get("raw", "")})]]

        return []