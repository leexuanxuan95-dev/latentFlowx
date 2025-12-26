# demo/cost_compare_demo.py
from core.engine import LatentFlowEngine
from core.infer.cost import CostCounter
from core.plugins.rule_plugin import ActivityRule
from core.infer.continuous import ContinuousBuffer

from demo.baseline_tokenlike import TokenLikeBaselineEngine

def run_latentflow(messages):
    engine = LatentFlowEngine(plugins=[ActivityRule()])
    state = engine.init()
    cost = CostCounter()
    buf = ContinuousBuffer(delimiter="\n", block_type="event")

    for m in messages:
        buf.append(m + "\n")
        blocks = buf.emit_blocks()
        for b in blocks:
            state, _ = engine.consume(state, b, cost)

    return cost.summary(), state.summary()

def run_baseline(messages):
    engine = TokenLikeBaselineEngine()
    state = engine.init()
    cost = CostCounter()
    buf = ContinuousBuffer(delimiter="\n", block_type="event")

    for m in messages:
        buf.append(m + "\n")
        blocks = buf.emit_blocks()
        for b in blocks:
            state, _ = engine.consume(state, b, cost)

    return cost.summary(), state.summary()

def demo():
    # 模拟 N 条连续事件（你可以加大 N 看差距）
    N = 50
    messages = [f"user event {i}" for i in range(N)]

    lf_cost, lf_state = run_latentflow(messages)
    bl_cost, bl_state = run_baseline(messages)

    print("=== LatentFlow (incremental + compression) ===")
    print("Cost:", lf_cost)
    print("State:", lf_state)

    print("\n=== Token-like baseline (recompute history) ===")
    print("Cost:", bl_cost)
    print("State:", bl_state)

    # 关键对比指标
    print("\n=== Compare ===")
    print("Ops ratio (baseline / latentflow):", bl_cost["operations"] / max(1, lf_cost["operations"]))

if __name__ == "__main__":
    demo()
