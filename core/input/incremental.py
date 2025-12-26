# core/infer/incremental.py
from core.state.state_delta import StateDelta
from core.audit.logger import content_fingerprint

def incremental_update(state, block, cost, guard=None, audit_logger=None):
    before = state.snapshot()

    cost.add(1)
    cost.add_bytes(block.content)
    state.update(block)

    guard_trace = None
    rolled_back = False

    try:
        if guard:
            guard_trace = guard.check(state)
    except Exception as e:
        state.rollback(before)
        rolled_back = True

        if audit_logger:
            audit_logger.emit("consume_violation", {
                "block": {"type": block.block_type, "fp": content_fingerprint(block.content)},
                "error": str(e),
                "guard_trace": getattr(e, "meta", None),  # best-effort
                "state_after": state.summary(),
                "cost": cost.summary(),
            })
        raise

    delta = StateDelta(before, state)

    if audit_logger:
        audit_logger.emit("consume_ok", {
            "block": {"type": block.block_type, "fp": content_fingerprint(block.content)},
            "delta": delta.summary(),
            "guard_trace": guard_trace,
            "state_after": state.summary(),
            "cost": cost.summary(),
            "rolled_back": rolled_back,
        })

    return state, delta, guard_trace
