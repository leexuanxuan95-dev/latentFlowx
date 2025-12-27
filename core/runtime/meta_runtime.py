# =========================================================
# ===== file: core/runtime/meta_runtime.py
# =========================================================
from core.lang.pipeline import LanguagePipeline
from core.planner.constrained_planner import ConstrainedPlanner
from core.executor.executor_v2 import ToolExecutorV2
from core.infer.cost import CostCounter


class MetaRuntime:
    """
    MetaRuntime = Language → Plan → Execute → Feed Back
    NO agent loop.
    NO transformer.
    Fully deterministic.
    """

    def __init__(self, engine, planner, executor, verifier=None):
        self.engine = engine
        self.planner = planner
        self.executor = executor
        self.lang = LanguagePipeline()
        self.cost = CostCounter()

    def step(self, state, text: str):
        # 1️⃣ NL → intent blocks
        blocks = self.lang.parse(text)

        for b in blocks:
            state, _, _ = self.engine.consume(state, b, self.cost)

        # 2️⃣ plan
        intent_frame = blocks[0].content
        plan, plan_trace = self.planner.plan(intent_frame, state)

        if not plan:
            return {
                "ok": False,
                "error": plan_trace,
                "state": state.summary(),
                "cost": self.cost.summary(),
            }

        # 3️⃣ execute
        result_blocks = self.executor.execute_plan(plan)
        for rb in result_blocks:
            state, _, _ = self.engine.consume(state, rb, self.cost)

        return {
            "ok": True,
            "plan": [repr(a) for a in plan],
            "state": state.summary(),
            "cost": self.cost.summary(),
        }
