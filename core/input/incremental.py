# core/infer/incremental.py
from core.state.state_delta import StateDelta
from core.audit.logger import fingerprint
def incremental_update(state, block, cost, guard=None, verifier=None, audit_logger=None):
    before = state.snapshot()

    # cost: always count an attempted operation + input bytes
    cost.add_ops(1)
    cost.add_bytes(block.content)

    compress_trace = None
    try:
        # update (may dedup / may compress)
        compress_trace = state.update(block)

        # guard checks (post-update)
        guard_trace = guard.check(state) if guard else None

        # invariants verification
        if verifier:
            verifier.verify(state)
            # audit compression
        if audit_logger and isinstance(compress_trace, dict) and compress_trace.get("type") == "compress":
            audit_logger.emit("compress", {
                "trace": compress_trace,
                "state": state.summary(),
                "cost": cost.summary(),
            })

            # audit OK
        if audit_logger:
            audit_logger.emit("consume_ok", {
                "block": {"type": block.block_type, "id": block.block_id, "fp": fingerprint(block.content)},
                "guard_trace": guard_trace,
                "compress_trace": compress_trace,
                "delta": StateDelta(before, state).summary(),
                "state_after": state.summary(),
                "cost": cost.summary(),
            })
        return state, StateDelta(before, state), guard_trace

    except Exception as e:
        # rollback on any failure
        state.rollback(before)
        if audit_logger:
            audit_logger.emit("consume_violation", {
                "block": {"type": block.block_type, "id": block.block_id, "fp": fingerprint(block.content)},
                "error": str(e),
                "state_after_rollback": state.summary(),
                "cost": cost.summary(),
            })
        raise