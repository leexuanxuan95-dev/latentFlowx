from core.engine import LatentFlowEngine
from core.infer.cost import CostCounter
from core.plugins.rule_plugin import ActivityRule
from core.infer.continuous import ContinuousBuffer

from core.guard.state_guard import StateGuard, GuardViolation
from core.guard.rules import max_steps, deny_block_types, max_event_count


def run_case(event_limit: int, title: str):
    print("\n" + "=" * 10, title, f"(event_limit={event_limit})", "=" * 10)

    guard = StateGuard(rules=[
        max_steps(10),
        deny_block_types({"forbidden"}),
        max_event_count(limit=event_limit, event_type="event"),
    ])

    engine = LatentFlowEngine(
        plugins=[ActivityRule()],
        guard=guard
    )

    state = engine.init()
    cost = CostCounter()
    buf = ContinuousBuffer(delimiter="\n", block_type="event")

    buf.append("a\nb\nc\nd\n")
    blocks = buf.emit_blocks()

    for b in blocks:
        try:
            state, delta, guard_trace = engine.consume(state, b, cost)
            output, trace = engine.reason(state)

            print("Block:", b)
            print("Delta:", delta.summary())
            print("GuardTrace:", guard_trace)
            print("Decision:", output, "Trace:", trace)
            print("State:", state.summary())
            print("-" * 60)

        except GuardViolation as e:
            print("\n=== GUARD TRIGGERED ===")
            print("Violation:", str(e))
            print("State after rollback:", state.summary())
            print("Cost so far:", cost.summary())
            break

    print("Final Cost:", cost.summary())


def demo():
    # 先展示：推理命中（high activity 会出现）
    run_case(event_limit=3, title="CASE 1: decision happens before guard")

    # 再展示：强约束（第3个直接拦截）
    run_case(event_limit=2, title="CASE 2: strict guard triggers rollback early")


if __name__ == "__main__":
    demo()
