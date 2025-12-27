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

from dataclasses import dataclass


@dataclass
class AffectState:
    """
    "情绪"（工程可控版本）= 决策调制器
    - 不直接决定行动
    - 只影响：探索/保守、风险阈值、搜索深度、澄清倾向
    """
    confidence: float = 0.7       # 最近成功率的平滑估计
    risk_tolerance: float = 0.5   # 0~1，越低越保守
    urgency: float = 0.3          # 0~1
    fatigue: float = 0.0          # 0~1，连续失败会升高

    def update_on_success(self):
        self.confidence = min(0.99, self.confidence * 0.95 + 0.05 * 1.0)
        self.fatigue = max(0.0, self.fatigue * 0.7)
        self.risk_tolerance = min(1.0, self.risk_tolerance * 0.97 + 0.03 * 0.8)

    def update_on_failure(self):
        self.confidence = max(0.01, self.confidence * 0.95 + 0.05 * 0.0)
        self.fatigue = min(1.0, self.fatigue * 0.8 + 0.2)
        self.risk_tolerance = max(0.0, self.risk_tolerance * 0.95 - 0.05 * 0.2)

    def knobs(self):
        """
        返回给 Planner 的调制参数
        """
        # 越疲劳/越低信心 → 越保守（更倾向澄清、减少执行）
        conservatism = min(1.0, (1.0 - self.confidence) * 0.6 + self.fatigue * 0.4)
        return {
            "confidence": self.confidence,
            "risk_tolerance": self.risk_tolerance,
            "urgency": self.urgency,
            "fatigue": self.fatigue,
            "conservatism": conservatism,
        }