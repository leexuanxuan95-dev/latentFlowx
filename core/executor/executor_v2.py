# =========================================================
# ===== file: core/executor/executor_v2.py
# =========================================================
from core.infer.block import Block
from core.audit.logger import fingerprint


class ToolExecutorV2:
    """
    Deterministic executor (no agent).
    Executes a plan step-by-step.
    """

    def __init__(self, registry, audit_logger=None):
        self.registry = registry
        self.audit_logger = audit_logger

    def execute_plan(self, plan):
        blocks = []

        for action in plan:
            tool = self.registry.get(action.name)
            result = tool(**(action.params or {}))

            block = Block(
                content={
                    "action": action.name,
                    "params": action.params,
                    "result": result,
                },
                block_type="tool_result",
            )

            if self.audit_logger:
                self.audit_logger.emit("tool_exec", {
                    "action": repr(action),
                    "result_fp": fingerprint(result),
                })

            blocks.append(block)

        return blocks
