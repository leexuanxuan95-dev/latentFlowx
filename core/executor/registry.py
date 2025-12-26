# =========================================================
# ===== file: core/executor/registry.py
# =========================================================
from typing import Callable, Dict, Any


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, fn: Callable[..., Any]):
        self._tools[name] = fn

    def get(self, name: str):
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name]