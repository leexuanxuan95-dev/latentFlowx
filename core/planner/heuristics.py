# =========================================================
# ===== file: core/planner/heuristics.py
# =========================================================
from __future__ import annotations

from typing import List, Tuple

from core.planner.action import Action


def _plan_cost(plan: List[Action]) -> float:
    """
    Default cost:
      - shorter is cheaper
      - some actions have intrinsic cost
    """
    base = len(plan) * 1.0
    extra = 0.0
    for a in plan:
        if a.name in ("check_balance",):
            extra += 0.5
        if a.name in ("submit_transfer", "submit_withdraw"):
            extra += 0.2
    return base + extra


def rank_plans(plans: List[List[Action]]) -> List[List[Action]]:
    """
    Rank candidate plans by heuristic cost (ascending).
    """
    scored: List[Tuple[float, List[Action]]] = []
    for p in plans:
        scored.append((_plan_cost(p), p))
    scored.sort(key=lambda x: x[0])
    return [p for _, p in scored]
