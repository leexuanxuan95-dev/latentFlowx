# core/guard/rules.py
from core.guard.state_guard import GuardViolation
from core.state.view import effective_type_count

def max_steps(limit: int):
    def rule(state):
        if state.counter > limit:
            raise GuardViolation(
                code="MAX_STEPS",
                message=f"state steps exceeded limit: {state.counter} > {limit}",
                meta={"steps": state.counter, "limit": limit}
            )
    rule.__name__ = f"max_steps({limit})"
    return rule

def max_core_keys(limit: int):
    def rule(state):
        n = len(state.compressed_core)
        if n > limit:
            raise GuardViolation(
                code="CORE_KEYS_OVERFLOW",
                message=f"compressed_core keys overflow: {n} > {limit}",
                meta={"keys": n, "limit": limit}
            )
    rule.__name__ = f"max_core_keys({limit})"
    return rule

def deny_block_types(deny: set):
    def rule(state):
        for b in state.short_history:
            if b.block_type in deny:
                raise GuardViolation(
                    code="DENY_BLOCK_TYPE",
                    message=f"denied block_type detected: {b.block_type}",
                    meta={"block_type": b.block_type, "deny": list(deny)}
                )
    rule.__name__ = f"deny_block_types({','.join(sorted(list(deny)))})"
    return rule

def max_event_count(limit: int, event_type: str = "event"):
    def rule(state):
        count = effective_type_count(state, event_type)
        if count > limit:
            raise GuardViolation(
                code="MAX_EVENT_COUNT",
                message=f"{event_type} count overflow: {count} > {limit}",
                meta={"event_type": event_type, "count": count, "limit": limit}
            )
    rule.__name__ = f"max_event_count({event_type},{limit})"
    return rule
