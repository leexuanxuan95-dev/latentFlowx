# demo/audit_pipeline_demo.py
from core.engine import LatentFlowEngine
from core.infer.cost import CostCounter
from core.plugins.rule_plugin import ActivityRule
from core.infer.continuous import ContinuousBuffer

from core.guard.state_guard import StateGuard, GuardViolation
from core.guard.rules import max_steps, deny_block_types, max_event_count
from core.audit.logger import AuditLogger

def demo():
    logger = AuditLogger(path="logs/audit.jsonl", also_stdout=False)

    guard = StateGuard(rules=[
        max_steps(10),
        deny_block_types({"forbidden"}),
        max_event_count(limit=3, event_type="event"),
    ])

    engine = LatentFlowEngine(
        plugins=[ActivityRule()],
        guard=guard,
        audit_logger=logger,
    )

    state = engine.init()
    cost = CostCounter()
    buf = ContinuousBuffer(delimiter="\n", block_type="event")

    buf.append("a\nb\nc\nd\n")
    blocks = buf.emit_blocks()

    for b in blocks:
        try:
            state, delta, guard_trace = engine.consume(state, b, cost)
            engine.reason(state)
        except GuardViolation:
            # already audited in incremental_update
            break

    print("Done. Audit log written to logs/audit.jsonl")
    print("Final cost:", cost.summary())
    print("Final state:", state.summary())

if __name__ == "__main__":
    demo()
