# =========================================================
# ===== file: core/infer/block.py
# =========================================================
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Optional


def _stable_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


@dataclass
class Block:
    """
    A non-token unit. Could be:
    - raw text segment
    - event
    - structured dict
    """
    content: Any
    block_type: str = "event"
    ts: float = field(default_factory=lambda: time.time())
    block_id: Optional[str] = None  # idempotency key

    def __post_init__(self):
        if self.block_id is None:
            # Use content+type for stable id. For dict, use repr() (deterministic enough for v0.2)
            raw = f"{self.block_type}:{repr(self.content)}"
            self.block_id = _stable_hash(raw)

    def __repr__(self):
        return f"<Block type={self.block_type} id={self.block_id} content={self.content!r}>"
