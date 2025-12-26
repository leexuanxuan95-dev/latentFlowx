# =========================================================
# ===== file: core/planner/heuristics.py
# =========================================================
from __future__ import annotations
from typing import List

from core.planner.action import Action


def plan_cost(plan: List[Action]) -> int:
    # cheap heuristic: shorter plan cheaper
    return len(plan)


def rank_plans(plans: List[List[Action]]) -> List[List[Action]]:
    return sorted(plans, key=plan_cost)