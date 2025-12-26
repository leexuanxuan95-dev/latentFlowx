# core/plugins/rule_plugin.py

from core.plugins.base import ReasonPlugin
from core.state.view import effective_type_count


class ActivityRule(ReasonPlugin):
    def __init__(self, threshold: int = 2):
        self.threshold = threshold

    def apply(self, state):
        count = effective_type_count(state, "event")
        if count > self.threshold:
            return "high activity"
        return None
