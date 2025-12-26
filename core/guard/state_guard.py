# core/guard/state_guard.py
from dataclasses import dataclass
from typing import Callable, List, Optional, Any, Dict

@dataclass
class GuardViolation(Exception):
    code: str
    message: str
    meta: Optional[Dict[str, Any]] = None

    def __str__(self):
        return f"[{self.code}] {self.message} meta={self.meta or {}}"

GuardRule = Callable[[Any], None]  # rule(state) -> None or raise GuardViolation

class StateGuard:
    """
    Rule-based state guard.
    - check() returns an audit trace
    - raises GuardViolation on failure
    """

    def __init__(self, rules: Optional[List[GuardRule]] = None):
        self.rules: List[GuardRule] = rules or []

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
                trace["failed"] = {
                    "rule": name,
                    "code": e.code,
                    "message": e.message,
                    "meta": e.meta or {}
                }
                raise

        return trace
