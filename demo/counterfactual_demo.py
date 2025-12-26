# =========================================================
# ===== file: demo/counterfactual_demo.py
# =========================================================
from copy import deepcopy

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


def run_one(text, policy):
    logger = AuditLogger(path=None, also_stdout=False)
    engine = LatentFlowEngine(guard=StateGuard([max_steps(2000)]), verifier=Verifier(), audit_logger=logger)
    state = engine.init()
    cost = CostCounter()

    lp = LanguagePipeline()
    planner = ConstrainedPlanner(verifier=ConstraintsVerifier(policy=policy))

    reg = ToolRegistry()
    reg.register("check_user", lambda user=None: {"exists": True})
    reg.register("check_balance", lambda currency=None, amount=None: {"ok": True})
    reg.register("create_transfer", lambda to=None, amount=None, currency=None: {"transfer_id": "T-1"})
    reg.register("submit_transfer", lambda: {"submitted": True})

    executor = ToolExecutorV2(registry=reg, audit_logger=logger)
    rt = MetaRuntime(engine=engine, planner=planner, executor=executor, audit_logger=logger)

    intent_block = lp.to_intent_blocks(text)[0]
    state, result = rt.run(state=state, cost=cost, intent_block=intent_block)
    return result.status, result.error, result.executed, policy


def main():
    text = "给Alice转账 900 元，不要审批"

    p1 = Policy(max_transfer_amount=1000.0, require_approval_over=500.0)  # 会冲突
    p2 = Policy(max_transfer_amount=1000.0, require_approval_over=2000.0) # 不会冲突

    for p in (p1, p2):
        status, err, executed, pol = run_one(text, p)
        print("\nPolicy(require_approval_over):", pol.require_approval_over)
        print("STATUS:", status)
        print("ERROR:", err)
        print("EXEC:", executed)


if __name__ == "__main__":
    main()
