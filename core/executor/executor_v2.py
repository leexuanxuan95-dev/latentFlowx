# =========================================================
# ===== file: core/executor/executor_v2.py
# =========================================================
from typing import Any, Dict, Tuple

from core.infer.block import Block
from core.audit.logger import fingerprint


class ToolExecutorV2:
    """
    V2：返回 (block, ok, error_str)
    - 不强行 raise，让上层 Runtime 决策是否回滚/重试/澄清
    """

    def __init__(self, registry, audit_logger=None):
        self.registry = registry
        self.audit_logger = audit_logger

    def execute(self, action) -> Tuple[Block, bool, str | None]:
        try:
            fn = self.registry.get(action.name)
            result = fn(**(action.params or {}))
            ok = True
            err = None
        except Exception as e:
            result = {"error": str(e)}
            ok = False
            err = str(e)

        block = Block(content={"tool": action.name, "result": result, "ok": ok}, block_type="tool_result")

        if self.audit_logger:
            self.audit_logger.emit("tool_exec", {
                "action": repr(action),
                "ok": ok,
                "err": err,
                "result_fp": fingerprint(repr(result)),
            })

        return block, ok, err
