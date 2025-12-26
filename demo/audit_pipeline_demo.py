from core.engine import LatentFlowEngine
from core.infer.cost import CostCounter
from core.infer.continuous import ContinuousBuffer
from core.audit.logger import AuditLogger
from core.verify.verifier import Verifier
from core.guard.state_guard import StateGuard
from core.guard.rules import max_steps, max_event_count

def demo():
    logger = AuditLogger(path="logs/audit.jsonl", also_stdout=False)
    engine = LatentFlowEngine(
        plugins=[],
        guard=StateGuard([max_steps(100), max_event_count(1000, "event")]),
        verifier=Verifier(),
        audit_logger=logger
    )

    state = engine.init()
    cost = CostCounter()
    buf = ContinuousBuffer(delimiter="\n", block_type="event")

    buf.append("login\nclick_buy\ncancel_order\n")
    for b in buf.emit_blocks():
        state, _, _ = engine.consume(state, b, cost)

    engine.reason(state)
    print("Done. logs/audit.jsonl generated.")
    print("Cost:", cost.summary())
    print("State:", state.summary())

if __name__ == "__main__":
    demo()