# =========================================================
# ===== file: core/meta/causal.py
# =========================================================
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CausalRecord:
    """
    轻量因果记忆：
    (context, plan) -> outcome
    """
    key: str
    context: Dict[str, Any]
    plan: Tuple[str, ...]
    outcome: Dict[str, Any]


@dataclass
class CausalMemory:
    """
    非“科学因果”，而是工程可用因果：
    - 在某类上下文中，某计划常成功/失败
    - 用于 Planner 选更稳的计划
    """
    records: List[CausalRecord] = field(default_factory=list)
    max_records: int = 2000

    def _mk_key(self, intent: str, slots: Dict[str, Any], constraints: List[Dict[str, Any]]):
        # 极简 key：intent + 关键槽位
        core = {"intent": intent, "to": slots.get("to"), "amount": slots.get("amount"), "order_id": slots.get("order_id")}
        return str(core)

    def add(self, *, intent: str, slots: Dict[str, Any], constraints: List[Dict[str, Any]], plan_actions: Tuple[str, ...], ok: bool, failure_type: Optional[str] = None):
        key = self._mk_key(intent, slots, constraints)
        outcome = {"ok": ok, "failure_type": failure_type}
        rec = CausalRecord(key=key, context={"intent": intent, "slots": slots, "constraints": constraints}, plan=plan_actions, outcome=outcome)
        self.records.append(rec)
        if len(self.records) > self.max_records:
            self.records = self.records[-self.max_records :]

    def plan_score(self, *, intent: str, slots: Dict[str, Any], constraints: List[Dict[str, Any]], plan_actions: Tuple[str, ...]) -> float:
        """
        返回该计划在相似上下文中的经验分数：越高越好
        """
        key = self._mk_key(intent, slots, constraints)
        ok = 0
        bad = 0
        for r in self.records[-500:]:
            if r.key == key and r.plan == plan_actions:
                if r.outcome.get("ok"):
                    ok += 1
                else:
                    bad += 1
        total = ok + bad
        if total == 0:
            return 0.5
        return ok / total