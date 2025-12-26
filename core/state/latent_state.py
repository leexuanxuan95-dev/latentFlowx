# core/state/latent_state.py
import copy
from collections import deque
from typing import Any, Dict, Optional

class LatentState:
    """
    Bounded-memory state with:
    - short_history (recent blocks)
    - compressed_core (summarized)
    - dedup LRU (idempotency)
    """

    def __init__(self, max_history: int = 3, dedup_capacity: int = 512):
        self.short_history = []
        self.compressed_core: Dict[str, Dict[str, Any]] = {}
        self.counter = 0
        self.max_history = max_history

        # idempotency
        self.dedup_capacity = dedup_capacity
        self._dedup_lru = deque(maxlen=dedup_capacity)
        self._dedup_set = set()

        # for invariants
        self.seen_events = 0

        # compression stats
        self.compress_count = 0

    def snapshot(self):
        return copy.deepcopy(self)

    def rollback(self, snap):
        self.__dict__.update(copy.deepcopy(snap.__dict__))

    def seen(self, block_id: str) -> bool:
        return block_id in self._dedup_set

    def remember(self, block_id: str):
        if block_id in self._dedup_set:
            return
        if len(self._dedup_lru) >= self.dedup_capacity:
            # evict oldest
            old = self._dedup_lru[0]
            # deque will drop it after append; remove from set now or later
            # but since deque doesn't expose the popped element directly on append,
            # do manual eviction when full:
            old = self._dedup_lru.popleft()
            self._dedup_set.discard(old)
        self._dedup_lru.append(block_id)
        self._dedup_set.add(block_id)

    def update(self, block) -> Optional[Dict[str, Any]]:
        """
        Returns compress_trace if compression happened, else None.
        Idempotent: repeated block_id won't modify state.
        """
        self.seen_events += 1

        if self.seen(block.block_id):
            # idempotent no-op
            return {"dedup": True, "block_id": block.block_id}

        self.remember(block.block_id)
        self.counter += 1
        self.short_history.append(block)

        if len(self.short_history) >= self.max_history:
            return self._compress()

        return None

    def _compress(self) -> Dict[str, Any]:
        before_len = len(self.short_history)
        delta: Dict[str, Any] = {}

        for block in self.short_history:
            t = block.block_type
            entry = self.compressed_core.get(
                t,
                {"count": 0, "first_seen": block.content, "last": None, "recent": []},
            )
            entry["count"] += 1
            entry["last"] = block.content
            entry["recent"].append(block.content)
            entry["recent"] = entry["recent"][-3:]
            self.compressed_core[t] = entry
            delta[t] = delta.get(t, 0) + 1

        self.short_history = []
        self.compress_count += 1
        return {
            "type": "compress",
            "before_short": before_len,
            "delta_counts": delta,
            "after_short": len(self.short_history),
            "compress_count": self.compress_count,
        }

    def summary(self):
        return {
            "steps": self.counter,
            "seen_events": self.seen_events,
            "compressed_core": self.compressed_core,
            "short_history_len": len(self.short_history),
            "compress_count": self.compress_count,
            "dedup_size": len(self._dedup_set),
        }


