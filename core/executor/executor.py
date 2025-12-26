# =========================================================
# ===== file: core/executor/executor.py
# =========================================================
from core.infer.block import Block
from core.audit.logger import fingerprint


class ToolExecutor:
    """
    Executes tools and returns result blocks to feed back into state.
    """

    def __init__(self, registry, audit_logger=None):
        self.registry = registry
        self.audit_logger = audit_logger

    def execute(self, action):
        fn = self.registry.get(action.name)
        result = fn(**(action.params or {}))

        block = Block(
            content={"tool": action.name, "result": result},
            block_type="tool_result",
        )

        if self.audit_logger:
            self.audit_logger.emit("tool_exec", {
                "action": repr(action),
                "result_fp": fingerprint(repr(result)),
            })

        return block