# =========================================================
# ===== file: demo/industrial_intent_planner_demo.py
# =========================================================
"""
Industrial demo:
- Non-token NL -> Intent/Slots/Constraints (LanguagePipeline)
- ConstraintsVerifier + Policy -> accept/deny
- ConstrainedPlanner -> agentless plan
- ToolExecutor executes tools -> tool_result blocks fed to LatentFlow
- LatentFlow provides incremental + audit + rollback + invariants
"""
from core.audit.logger import AuditLogger
from core.engine import LatentFlowEngine
from core.infer.cost import CostCounter
from core.infer.block import Block
from core.verify.verifier import Verifier  # invariants verifier
from core.guard.state_guard import StateGuard
from core.guard.rules import max_steps

from core.lang.pipeline import LanguagePipeline
from core.verify.policy import Policy
from core.verify.constraints_verifier import ConstraintsVerifier

from core.planner.constrained_planner import ConstrainedPlanner
from core.executor.registry import ToolRegistry
from core.executor.executor import ToolExecutor


def demo():
    # --- audit / safety ---
    logger = AuditLogger(path="logs/audit.jsonl", also_stdout=False)
    engine = LatentFlowEngine(
        plugins=[],
        guard=StateGuard([max_steps(1000)]),
        verifier=Verifier(),  # invariants
        audit_logger=logger
    )
    state = engine.init()
    cost = CostCounter()

    # --- language pipeline ---
    lp = LanguagePipeline()

    # --- constraints / policy ---
    policy = Policy(
        max_transfer_amount=1000.0,
        require_approval_over=500.0,
        blocked_targets={"EvilGuy"},
    )
    cver = ConstraintsVerifier(policy=policy)

    # --- planner ---
    planner = ConstrainedPlanner(verifier=cver)

    # --- tools (domain) ---
    reg = ToolRegistry()

    # cheap deterministic tool stubs
    reg.register("check_user", lambda user=None: {"exists": user is not None and user != "Unknown"})
    reg.register("check_balance", lambda currency=None, amount=None: {"ok": True, "currency": currency, "amount": amount})
    reg.register("create_transfer", lambda to=None, amount=None, currency=None: {"transfer_id": "T-1", "to": to, "amount": amount, "currency": currency})
    reg.register("submit_transfer", lambda: {"submitted": True})

    reg.register("create_withdraw", lambda amount=None, currency=None: {"withdraw_id": "W-1", "amount": amount, "currency": currency})
    reg.register("submit_withdraw", lambda: {"submitted": True})

    reg.register("load_order", lambda order_id=None: {"order_id": order_id, "status": "CREATED"})
    reg.register("cancel_order", lambda order_id=None: {"order_id": order_id, "canceled": True})

    reg.register("create_order", lambda item=None: {"order_id": "O-1", "item": item})
    reg.register("submit_order", lambda: {"submitted": True})

    # QA tool is intentionally "safe": no external calls
    reg.register("answer", lambda query=None: {"answer": f"(safe) I got your query: {query}"})

    executor = ToolExecutor(reg, audit_logger=logger)

    # --- test inputs ---
    inputs = [
        "给Bob转账 500 元，今天之前完成，不要超过 1000",
        "给EvilGuy转账 100 元",             # blocked target
        "给Alice转账 900 元，不要审批",        # violates policy approval threshold (900 > 500) but user forbids approval
        "我想取消订单 order #A1024",
        "帮我购买 iPhone 15",
        "为什么我转账失败了？请总结原因",       # QA intent
    ]

    for text in inputs:
        # 1) NL -> intent block
        intent_blocks = lp.to_intent_blocks(text)
        intent_block = intent_blocks[0]
        frame = intent_block.content

        print("\n========================================")
        print("TEXT:", text)
        print("FRAME:", frame)

        # 2) Feed intent into LatentFlow state (auditable)
        state, _, _ = engine.consume(state, intent_block, cost)

        # 3) Plan (agentless) using constraints
        plan, plan_trace = planner.plan(frame, state=state)
        print("PLAN_TRACE:", plan_trace)

        if not plan:
            print("DECISION: DENY / NEED_CLARIFICATION")
            # optional: ask LLM adapter for clarification questions (not core)
            continue

        print("PLAN:", plan)

        # 4) Execute plan tools -> tool_result blocks -> LatentFlow
        for act in plan:
            result_block = executor.execute(act)
            state, _, _ = engine.consume(state, result_block, cost)

        # 5) Produce a simple deterministic output (no transformer)
        out = {
            "ok": True,
            "intent": frame.get("intent"),
            "slots": frame.get("slots"),
            "executed_steps": [a.name for a in plan],
        }
        logger.emit("final_output", {"output": out, "state": state.summary(), "cost": cost.summary()})
        print("OUTPUT:", out)

    print("\n========================================")
    print("FINAL STATE:", state.summary())
    print("COST:", cost.summary())
    print("Audit -> logs/audit.jsonl")


if __name__ == "__main__":
    demo()