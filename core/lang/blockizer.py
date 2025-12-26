# =========================================================
# ===== file: core/lang/blockizer.py
# =========================================================
from typing import List
from core.infer.block import Block


class NewlineBlockizer:
    def __init__(self, block_type="event"):
        self.block_type = block_type

    def blockize(self, text: str) -> List[Block]:
        lines = [x.strip() for x in text.split("\n")]
        return [Block(x, block_type=self.block_type) for x in lines if x]