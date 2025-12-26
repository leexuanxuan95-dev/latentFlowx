"""
Agentless demo:
- Use a BFS planner to reach a goal
- Execute actions via ToolExecutor
- Feed tool_result blocks back into LatentFlow state
- No LLM, no tokens
"""
from core.audit.logger import AuditLogger
from core.engine import LatentFlowEngine
from core.executor.registry import ToolRegistry
from core.executor.executor import ToolExecutor
from core.infer.cost import CostCounter
from core.infer.block import Block
from core.verify.verifier import Verifier
from core.planner.search_planner import SearchPlanner
from core.planner.action import Action
from core.state.view import effective_type_count


def demo():
    logger = AuditLogger(path="logs/audit.jsonl", also_stdout=False)
    engine = LatentFlowEngine(verifier=Verifier(), audit_logger=logger)
    cost = CostCounter()

    # Tools (local functions)
    registry = ToolRegistry()
    registry.register("login", lambda: {"ok": True})
    registry.register("create_order", lambda item=None: {"order_id": "X-1", "item": item})
    registry.register("cancel_order", lambda order_id=None: {"canceled": True, "order_id": order_id})

    executor = ToolExecutor(registry, audit_logger=logger)

    # Initial state + seed goal block
    state = engine.init()
    state, _, _ = engine.consume(state, Block({"goal": "cancel_order"}, block_type="goal"), cost)

    goal = {"goal": "cancel_order"}

    # Planner domain functions
    def state_key(s):
        # minimal key from compressed_core + short_history len
        return repr(s.summary()["compressed_core"]) + f":{len(s.short_history)}"

    def goal_test(s, g):
        # satisfied if we have at least one tool_result of cancel_order
        # Here we just check count of tool_result blocks (event type tool_result) in state
        return effective_type_count(s, "tool_result") >= 1

    def action_generator(s, g):
        # Domain: always try login -> create_order -> cancel_order
        # In real use, you'd generate based on state.
        return [
            Action("login"),
            Action("create_order", {"item": "demo_item"}),
            Action("cancel_order", {"order_id": "X-1"}),
        ]

    def transition_fn(s, act):
        # Simulate next state without mutating original: snapshot then apply an "action" marker block
        ns = s.snapshot()
        ns.update(Block({"simulate": act.name}, block_type="sim"))
        return ns

    planner = SearchPlanner(
        state_key_fn=state_key,
        action_generator=action_generator,
        transition_fn=transition_fn,
        goal_test=goal_test,
        max_depth=3,
    )

    plan = planner.plan(state, goal)
    print("Plan:", plan)

    # Execute plan in real engine
    for act in plan or []:
        result_block = executor.execute(act)
        state, _, _ = engine.consume(state, result_block, cost)

    out, tr = engine.reason(state)
    print("Decision:", out, tr)
    print("Final state:", state.summary())
    print("Cost:", cost.summary())
    print("Audit -> logs/audit.jsonl")

if __name__ == "__main__":
    demo()