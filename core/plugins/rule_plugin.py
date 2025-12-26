# core/plugins/rule_plugin.py
from core.plugins.base import ReasonPlugin
from core.state.view import effective_type_count

class ActivityRule(ReasonPlugin):
    def apply(self, state):
        count = effective_type_count(state, "event")
        if count > 2:
            return "high activity"
        return None
