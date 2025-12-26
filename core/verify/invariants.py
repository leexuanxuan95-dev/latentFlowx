class InvariantViolation(Exception):
    pass
class Invariants:
    """
    Engineering-correctness invariants.
    """

    @staticmethod
    def check(state):
        # INV-1: counter equals seen_events
        if state.counter != state.seen_events:
            raise InvariantViolation(f"INV_COUNTER_SEEN_MISMATCH counter={state.counter} seen={state.seen_events}")

        # INV-2: counts are conserved
        core_total = 0
        for v in state.compressed_core.values():
            if isinstance(v, dict):
                core_total += int(v.get("count", 0))
        if core_total + len(state.short_history) != state.counter:
            raise InvariantViolation(
                f"INV_EVENT_COUNT_MISMATCH core_total={core_total} short={len(state.short_history)} counter={state.counter}"
            )

        # INV-3: dedup store bounded
        if len(state._dedup_lru) > state.dedup_capacity:
            raise InvariantViolation("INV_DEDUP_OVER_CAPACITY")

        return True