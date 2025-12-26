# =========================================================
# ===== file: core/planner/action.py
# =========================================================
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Action:
    name: str
    params: Optional[Dict[str, Any]] = None

    def __repr__(self):
        return f"Action(name={self.name}, params={self.params or {}})"

