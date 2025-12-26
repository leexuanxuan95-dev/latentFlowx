# =========================================================
# ===== file: demo/decision_loop_demo.py
# =========================================================
from core.audit.logger import AuditLogger
from core.engine import LatentFlowEngine
from core.guard.state_guard import StateGuard
from core.guard.rules import max_steps
from core.infer.cost import CostCounter
from core.verify.verifier import Verifier

from core.lang.pipeline import LanguagePipeline
from core.verify.policy import Policy
from core.verify.constraints_verifier import ConstraintsVerifier
from core.planner.constrained_planner import ConstrainedPlanner

from core.executor.registry import ToolRegistry
from core.executor.executor_v2 import ToolExecutorV2
from core.runtime.meta_runtime import MetaRuntime


def main():
    logger = AuditLogger(path="logs/audit.jsonl", also_stdout=False)

    engine = LatentFlowEngine(
        plugins=[],
        guard=StateGuard([max_steps(2000)]),
        verifier=Verifier(),
        audit_logger=logger
    )
    state = engine.init()
    cost = CostCounter()

    lp = LanguagePipeline()

    policy = Policy(
        max_transfer_amount=1000.0,
        require_approval_over=500.0,
        blocked_targets={"EvilGuy"},
    )
    planner = ConstrainedPlanner(verifier=ConstraintsVerifier(policy=policy))

    reg = ToolRegistry()
    # tools
    reg.register("check_user", lambda user=None: {"exists": user is not None and user != "Unknown"})
    reg.register("check_balance", lambda currency=None, amount=None: {"ok": True, "currency": currency, "amount": amount})
    reg.register("create_transfer", lambda to=None, amount=None, currency=None: {"transfer_id": "T-1", "to": to, "amount": amount, "currency": currency})
    reg.register("submit_transfer", lambda: {"submitted": True})

    reg.register("load_order", lambda order_id=None: {"order_id": order_id, "status": "CREATED"})
    reg.register("cancel_order", lambda order_id=None: {"order_id": order_id, "canceled": True})

    executor = ToolExecutorV2(registry=reg, audit_logger=logger)
    rt = MetaRuntime(engine=engine, planner=planner, executor=executor, audit_logger=logger)

    texts = [
        "给Bob转账 500 元，不要超过 1000",
        "给EvilGuy转账 100 元",          # blocked
        "给Alice转账 900 元，不要审批",    # conflict with approval policy
        "我想取消订单 order #A1024",
    ]

    for t in texts:
        intent_block = lp.to_intent_blocks(t)[0]
        state, result = rt.run(state=state, cost=cost, intent_block=intent_block)
        print("\nTEXT:", t)
        print("STATUS:", result.status)
        print("ERROR:", result.error)
        print("PLAN_TRACE:", result.trace.get("plan_trace"))
        print("EXEC:", result.executed)
        print("AFFECT:", rt.affect.knobs())
        print("STATE:", state.summary())
        print("COST:", cost.summary())

    print("\n=== LEARNING STATS ===")
    print("Action weights:", rt.learning.heuristics()["action_weights"])
    print("Failure types:", rt.learning.failure_types)

    print("\nAudit -> logs/audit.jsonl")


if __name__ == "__main__":
    main()
