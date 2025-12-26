# =========================================================
# ===== file: core/meta/learning.py
# =========================================================
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple


@dataclass
class LearningStats:
    """
    自主学习（工程可控版本）：
    - 统计：意图成功率、动作成功率、失败类型
    - 输出：heuristics 权重（给 Planner 用）
    """
    intent_success: Dict[str, int] = field(default_factory=dict)
    intent_fail: Dict[str, int] = field(default_factory=dict)

    action_success: Dict[str, int] = field(default_factory=dict)
    action_fail: Dict[str, int] = field(default_factory=dict)

    failure_types: Dict[str, int] = field(default_factory=dict)

    def record(self, *, intent: str, plan_actions: Tuple[str, ...], ok: bool, failure_type: str | None = None):
        if ok:
            self.intent_success[intent] = self.intent_success.get(intent, 0) + 1
            for a in plan_actions:
                self.action_success[a] = self.action_success.get(a, 0) + 1
        else:
            self.intent_fail[intent] = self.intent_fail.get(intent, 0) + 1
            for a in plan_actions:
                self.action_fail[a] = self.action_fail.get(a, 0) + 1
            if failure_type:
                self.failure_types[failure_type] = self.failure_types.get(failure_type, 0) + 1

    def success_rate_intent(self, intent: str) -> float:
        s = self.intent_success.get(intent, 0)
        f = self.intent_fail.get(intent, 0)
        return s / (s + f) if (s + f) > 0 else 0.5

    def success_rate_action(self, action: str) -> float:
        s = self.action_success.get(action, 0)
        f = self.action_fail.get(action, 0)
        return s / (s + f) if (s + f) > 0 else 0.5

    def heuristics(self) -> Dict[str, Any]:
        """
        给 Planner 用的权重表：动作越可靠，成本越低
        """
        weights = {}
        for a in set(list(self.action_success.keys()) + list(self.action_fail.keys())):
            sr = self.success_rate_action(a)
            # sr 越大，weight 越小（更偏好）
            weights[a] = 1.5 - sr  # 约在 [0.5, 1.5]
        return {"action_weights": weights, "intent_success_rate": dict((k, self.success_rate_intent(k)) for k in set(weights.keys()))}
