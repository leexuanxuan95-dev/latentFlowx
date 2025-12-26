from core.session.state_store import StateStore
from core.engine import LatentFlowEngine
from core.infer.cost import CostCounter
from core.infer.block import Block
from core.verify.verifier import Verifier

def demo():
    store = StateStore()
    engine = LatentFlowEngine(verifier=Verifier())
    cost = CostCounter()

    for sid in ["u1", "u2", "u1", "u2"]:
        state = store.get(sid)
        b = Block(f"{sid} event", block_type="event")
        state, _, _ = engine.consume(state, b, cost)
        store.commit(sid, state)

    print("u1:", store.get("u1").summary())
    print("u2:", store.get("u2").summary())
    print("Cost:", cost.summary())

if __name__ == "__main__":
    demo()