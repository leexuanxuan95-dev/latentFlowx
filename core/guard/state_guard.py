# core/guard/state_guard.py
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

@dataclass
class GuardViolation(Exception):
    code: str
    message: str
    meta: Optional[Dict[str, Any]] = None

    def __str__(self):
        return f"[{self.code}] {self.message} meta={self.meta or {}}"


GuardRule = Callable[[Any], None]
class StateGuard:
    def __init__(self, rules: Optional[List[GuardRule]] = None):
        self.rules = rules or []

    def add_rule(self, rule: GuardRule):
        self.rules.append(rule)

    def check(self, state) -> Dict[str, Any]:
        trace = {"checked": [], "passed": [], "failed": None}
        for rule in self.rules:
            name = getattr(rule, "__name__", rule.__class__.__name__)
            trace["checked"].append(name)
            try:
                rule(state)
                trace["passed"].append(name)
            except GuardViolation as e:
                trace["failed"] = {"rule": name, "code": e.code, "message": e.message, "meta": e.meta or {}}
                raise
        return trace

