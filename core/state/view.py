# core/state/view.py

def effective_type_count(state, block_type: str) -> int:
    core_entry = state.compressed_core.get(block_type, {})
    core_count = core_entry.get("count", 0) if isinstance(core_entry, dict) else 0
    inc = 0
    for b in state.short_history:
        if b.block_type == block_type:
            inc += 1
    return core_count + inc


def effective_last(state, block_type: str):
    for b in reversed(state.short_history):
        if b.block_type == block_type:
            return b.content
    core_entry = state.compressed_core.get(block_type, {})
    if isinstance(core_entry, dict):
        return core_entry.get("last")
    return None