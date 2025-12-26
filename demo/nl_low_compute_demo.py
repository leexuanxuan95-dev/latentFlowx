from core.engine import LatentFlowEngine
from core.infer.cost import CostCounter
from core.verify.verifier import Verifier
from core.lang.slu_rule import RuleSLU

def demo():
    engine = LatentFlowEngine(verifier=Verifier())
    slu = RuleSLU()
    state = engine.init()
    cost = CostCounter()

    texts = [
        "我想取消订单 order #A1024",
        "帮我购买 iPhone 15",
        "cancel order B-77",
        "随便说一句话"
    ]

    for t in texts:
        blocks = slu.parse(t)
        for b in blocks:
            state, delta, _ = engine.consume(state, b, cost)
            print("TEXT:", t)
            print("BLOCK:", b)
            print("DELTA:", delta.summary())
            print("STATE:", state.summary())
            print("-" * 60)

    print("Cost:", cost.summary())

if __name__ == "__main__":
    demo()