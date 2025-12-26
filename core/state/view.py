# core/state/view.py

def effective_type_count(state, block_type: str) -> int:
    """
    Count = compressed_core count + short_history count (not yet compressed).
    This makes guard/plugin correct even before compression happens.
    """
    core_entry = state.compressed_core.get(block_type, {})
    core_count = core_entry.get("count", 0) if isinstance(core_entry, dict) else 0

    inc_count = 0
    for b in state.short_history:
        if b.block_type == block_type:
            inc_count += 1

    return core_count + inc_count


def effective_last(state, block_type: str):
    """
    Last seen content considering both core and short_history.
    """
    # Prefer short_history tail if present
    for b in reversed(state.short_history):
        if b.block_type == block_type:
            return b.content

    core_entry = state.compressed_core.get(block_type, {})
    if isinstance(core_entry, dict):
        return core_entry.get("last")
    return None
