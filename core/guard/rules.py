# core/guard/rules.py
from core.guard.state_guard import GuardViolation
from core.state.view import effective_type_count

def max_steps(limit: int):
    def rule(state):
        if state.counter > limit:
            raise GuardViolation("MAX_STEPS", f"state steps exceeded: {state.counter} > {limit}", {"steps": state.counter, "limit": limit})
    rule.__name__ = f"max_steps({limit})"
    return rule

def deny_block_types(deny: set):
    def rule(state):
        for b in state.short_history:
            if b.block_type in deny:
                raise GuardViolation("DENY_BLOCK_TYPE", f"denied block_type: {b.block_type}", {"block_type": b.block_type, "deny": list(deny)})
    rule.__name__ = f"deny_block_types({','.join(sorted(list(deny)))})"
    return rule
def max_event_count(limit: int, event_type: str = "event"):
    def rule(state):
        count = effective_type_count(state, event_type)
        if count > limit:
            raise GuardViolation("MAX_EVENT_COUNT", f"{event_type} count overflow: {count} > {limit}", {"event_type": event_type, "count": count, "limit": limit})
    rule.__name__ = f"max_event_count({event_type},{limit})"
    return rule