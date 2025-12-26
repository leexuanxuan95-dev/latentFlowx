# core/state/latent_state.py
import copy

class LatentState:
    def __init__(self, max_history=3):
        self.short_history = []
        self.compressed_core = {}
        self.counter = 0
        self.max_history = max_history

    def update(self, block):
        self.counter += 1
        self.short_history.append(block)
        if len(self.short_history) >= self.max_history:
            self._compress()

    def _compress(self):
        """
        Compress short_history into compressed_core with bounded memory:
        - count
        - last
        - recent (fixed window)
        - first_seen
        """
        for block in self.short_history:
            t = block.block_type
            entry = self.compressed_core.get(
                t,
                {"count": 0, "first_seen": block.content, "last": None, "recent": []}
            )
            entry["count"] += 1
            entry["last"] = block.content
            entry["recent"].append(block.content)
            entry["recent"] = entry["recent"][-3:]  # fixed window
            self.compressed_core[t] = entry

        self.short_history = []

    def snapshot(self):
        return copy.deepcopy(self)

    def rollback(self, snapshot):
        self.short_history = snapshot.short_history
        self.compressed_core = snapshot.compressed_core
        self.counter = snapshot.counter

    def summary(self):
        return {
            "steps": self.counter,
            "compressed_core": self.compressed_core,
            "short_history_len": len(self.short_history)
        }
