from core.engine import LatentFlowEngine
from core.infer.cost import CostCounter
from core.infer.continuous import ContinuousBuffer
from core.plugins.rule_plugin import ActivityRule
from core.audit.logger import AuditLogger
from core.verify.verifier import Verifier

from core.guard.state_guard import StateGuard, GuardViolation
from core.guard.rules import max_steps, deny_block_types, max_event_count


def demo():
    logger = AuditLogger(path="logs/audit.jsonl", also_stdout=False)
    guard = StateGuard(rules=[max_steps(10), deny_block_types({"forbidden"}), max_event_count(limit=2, event_type="event")])
    engine = LatentFlowEngine(plugins=[ActivityRule(threshold=2)], guard=guard, verifier=Verifier(), audit_logger=logger)

    state = engine.init()
    cost = CostCounter()
    buf = ContinuousBuffer(delimiter="\n", block_type="event")

    buf.append("a\nb\nc\n")
    for b in buf.emit_blocks():
        try:
            state, delta, gt = engine.consume(state, b, cost)
            out, tr = engine.reason(state)
            print("Block:", b)
            print("Delta:", delta.summary())
            print("GuardTrace:", gt)
            print("Decision:", out, tr)
            print("State:", state.summary())
            print("-" * 60)
        except GuardViolation as e:
            print("\n=== GUARD TRIGGERED ===")
            print("Violation:", str(e))
            print("State after rollback:", state.summary())
            break

    print("Cost:", cost.summary())


if __name__ == "__main__":
    demo()