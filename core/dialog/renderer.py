# =========================================================
# ===== file: core/dialog/renderer.py
# =========================================================
from typing import Any, Dict


class Renderer:
    """
    多风格输出：简洁/详细/审计版
    """

    def concise(self, msg: str) -> str:
        return msg

    def detailed(self, msg: str, trace: Dict[str, Any] | None = None) -> str:
        if not trace:
            return msg
        return msg + "\n\nTRACE:\n" + str(trace)

    def audit_view(self, msg: str, state_summary: Dict[str, Any], cost_summary: Dict[str, Any]) -> str:
        return msg + f"\n\nSTATE={state_summary}\nCOST={cost_summary}"
