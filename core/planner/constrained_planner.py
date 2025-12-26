

# =========================================================
# ===== file: core/planner/constrained_planner.py
# =========================================================
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from core.planner.action_space import ActionSpace
from core.planner.heuristics import rank_plans
from core.verify.constraints_verifier import ConstraintsVerifier, ConstraintViolation


class ConstrainedPlanner:
    """
    Agentless planner:
      - verify constraints/policy BEFORE executing
      - generate candidate plans (deterministic)
      - pick best plan via heuristics
    """

    def __init__(self, verifier: Optional[ConstraintsVerifier] = None, action_space: Optional[ActionSpace] = None):
        self.verifier = verifier or ConstraintsVerifier()
        self.action_space = action_space or ActionSpace()

    def plan(self, intent_frame: Dict[str, Any], state=None):
        trace = {"candidates": 0, "selected": None, "constraint_trace": None, "error": None}

        try:
            ctrace = self.verifier.verify_intent_frame(intent_frame, state=state)
            trace["constraint_trace"] = ctrace
        except ConstraintViolation as e:
            trace["error"] = str(e)
            return None, trace

        candidates = self.action_space.candidates(intent_frame, state=state)
        trace["candidates"] = len(candidates)
        if not candidates:
            return None, trace

        ranked = rank_plans(candidates)
        plan = ranked[0]
        trace["selected"] = [repr(a) for a in plan]
        return plan, trace