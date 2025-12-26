# =========================================================
# ===== file: core/runtime/meta_runtime.py
# =========================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from core.meta.affect import AffectState
from core.meta.learning import LearningStats
from core.meta.causal import CausalMemory
from core.meta.reflection import Reflector
from core.verify.post_checks import PostChecks, PostCheckError


@dataclass
class DecisionResult:
    status: str  # OK | DENY | NEED_CLARIFICATION | FAIL
    intent_frame: Dict[str, Any]
    plan: Optional[List[Any]] = None
    executed: Optional[List[str]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    trace: Dict[str, Any] = None
    error: Optional[str] = None


class MetaRuntime:
    """
    A 分支大脑：
    - pipeline: text->intent_frame (你已有 LanguagePipeline)
    - planner: constrained planner (你已有)
    - engine: LatentFlowEngine (你已有)
    - executor: ToolExecutorV2
    - reflector/learning/affect/causal: 元能力
    """

    def __init__(self, *, engine, planner, executor, audit_logger=None):
        self.engine = engine
        self.planner = planner
        self.executor = executor
        self.audit_logger = audit_logger

        self.affect = AffectState()
        self.learning = LearningStats()
        self.causal = CausalMemory()
        self.reflector = Reflector()
        self.post_checks = PostChecks()

    def run(self, *, state, cost, intent_block) -> Tuple[Any, DecisionResult]:
        """
        输入是 intent_block（Block(type="intent")）
        输出：更新后的 state + DecisionResult
        """
        frame = intent_block.content
        trace = {"affect": self.affect.knobs(), "plan_trace": None, "exec": [], "postcheck": None}

        # 1) 先把意图进入 state（可审计）
        try:
            state, _, _ = self.engine.consume(state, intent_block, cost)
        except Exception as e:
            self.affect.update_on_failure()
            return state, DecisionResult(status="FAIL", intent_frame=frame, trace=trace, error=str(e))

        # 2) 规划（无代理）
        plan, plan_trace = self.planner.plan(frame, state=state)
        trace["plan_trace"] = plan_trace

        if not plan:
            # 这里可按 conservatism 决定拒绝/澄清
            status = "NEED_CLARIFICATION" if self.affect.knobs()["conservatism"] >= 0.4 else "DENY"
            self.affect.update_on_failure()
            return state, DecisionResult(status=status, intent_frame=frame, trace=trace, error=plan_trace.get("error"))

        # 3) 执行（工具闭环），工具结果作为 block 回灌 state
        executed = []
        tool_results = []
        plan_actions = tuple(a.name for a in plan)

        ok_all = True
        stage_err: Optional[Exception] = None

        for act in plan:
            block, ok, err = self.executor.execute(act)
            executed.append(act.name)
            tool_results.append(block.content)

            try:
                state, _, _ = self.engine.consume(state, block, cost)
            except Exception as e:
                ok_all = False
                stage_err = e
                break

            if not ok:
                ok_all = False
                stage_err = Exception(err or "tool_error")
                break

        # 4) post checks（语义正确性）
        if ok_all:
            try:
                self.post_checks.check(intent_frame=frame, executed_actions=executed, tool_results=tool_results)
                trace["postcheck"] = {"ok": True}
            except PostCheckError as e:
                ok_all = False
                stage_err = e
                trace["postcheck"] = {"ok": False, "error": str(e)}

        # 5) 反思+学习+因果+情绪调制
        if ok_all:
            self.affect.update_on_success()
            self.learning.record(intent=frame.get("intent", "unknown"), plan_actions=plan_actions, ok=True)
            self.causal.add(intent=frame.get("intent", "unknown"), slots=frame.get("slots", {}), constraints=frame.get("constraints", []), plan_actions=plan_actions, ok=True)
            return state, DecisionResult(
                status="OK",
                intent_frame=frame,
                plan=plan,
                executed=executed,
                tool_results=tool_results,
                trace=trace,
            )

        # failure
        self.affect.update_on_failure()
        rr = self.reflector.classify_failure(stage_err or Exception("unknown"), stage="execute_or_postcheck")
        self.learning.record(intent=frame.get("intent", "unknown"), plan_actions=plan_actions, ok=False, failure_type=rr.failure_type)
        self.causal.add(intent=frame.get("intent", "unknown"), slots=frame.get("slots", {}), constraints=frame.get("constraints", []), plan_actions=plan_actions, ok=False, failure_type=rr.failure_type)

        return state, DecisionResult(
            status="FAIL",
            intent_frame=frame,
            plan=plan,
            executed=executed,
            tool_results=tool_results,
            trace=trace,
            error=rr.message,
        )
