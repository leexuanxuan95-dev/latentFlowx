# core/infer/continuous.py

from typing import List, Optional
from core.infer.block import Block


class ContinuousBuffer:
    """
    Non-token continuous buffer.
    - delimiter mode: emits blocks split by delimiter
    - chunk_size mode: fixed-size chunks
    """

    def __init__(self, *, delimiter: Optional[str] = "\n", chunk_size: Optional[int] = None, block_type: str = "event"):
        if delimiter is None and chunk_size is None:
            raise ValueError("Either delimiter or chunk_size must be provided.")
        if delimiter is not None and chunk_size is not None:
            raise ValueError("Choose delimiter OR chunk_size, not both.")
        self.delimiter = delimiter
        self.chunk_size = chunk_size
        self.block_type = block_type
        self._buf: str = ""
        self._emitted_count: int = 0

    def append(self, data: str) -> None:
        if not isinstance(data, str):
            raise TypeError("ContinuousBuffer expects str input.")
        self._buf += data

    def emit_blocks(self) -> List[Block]:
        blocks: List[Block] = []

        if self.delimiter is not None:
            parts = self._buf.split(self.delimiter)
            complete, tail = parts[:-1], parts[-1]
            for p in complete:
                p = p.strip()
                if p:
                    blocks.append(Block(p, block_type=self.block_type))
            self._buf = tail
        else:
            while len(self._buf) >= self.chunk_size:
                chunk = self._buf[: self.chunk_size]
                self._buf = self._buf[self.chunk_size :]
                chunk = chunk.strip()
                if chunk:
                    blocks.append(Block(chunk, block_type=self.block_type))

        self._emitted_count += len(blocks)
        return blocks

    def flush(self) -> List[Block]:
        tail = self._buf.strip()
        self._buf = ""
        if tail:
            self._emitted_count += 1
            return [Block(tail, block_type=self.block_type)]
        return []

    @property
    def emitted_count(self) -> int:
        return self._emitted_count
