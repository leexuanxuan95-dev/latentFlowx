# =========================================================
# ===== file: core/planner/constrained_planner.py
# =========================================================
from typing import Any, Dict, Optional

from core.verify.constraints_verifier import ConstraintsVerifier
from core.planner.action_space import ActionSpace
from core.planner.heuristics import rank_plans


class ConstrainedPlanner:
    """
    Agentless constrained planner:
    - verify intent + constraints first
    - generate deterministic candidate plans
    - select optimal plan by heuristic
    """

    def __init__(
        self,
        verifier: Optional[ConstraintsVerifier] = None,
        action_space: Optional[ActionSpace] = None,
    ):
        self.verifier = verifier or ConstraintsVerifier()
        self.action_space = action_space or ActionSpace()

    def plan(self, intent_frame: Dict[str, Any], state=None):
        trace = {
            "constraint_trace": None,
            "candidates": 0,
            "selected": None,
            "error": None,
        }

        # 1️⃣ constraint & policy verification
        try:
            trace["constraint_trace"] = self.verifier.verify_intent_frame(intent_frame, state)
        except Exception as e:
            trace["error"] = str(e)
            return None, trace

        # 2️⃣ generate candidate plans
        candidates = self.action_space.candidates(intent_frame, state)
        trace["candidates"] = len(candidates)

        if not candidates:
            trace["error"] = "NO_PLAN"
            return None, trace

        # 3️⃣ rank & choose best
        ranked = rank_plans(candidates)
        plan = ranked[0]
        trace["selected"] = [repr(a) for a in plan]

        return plan, trace
