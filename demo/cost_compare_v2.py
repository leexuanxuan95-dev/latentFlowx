from core.state.latent_state import LatentState
from core.infer.block import Block
from core.infer.cost import CostCounter


def latentflow_run(n=50, max_history=3):
    state = LatentState(max_history=max_history)
    cost = CostCounter()
    for i in range(n):
        b = Block(f"user event {i}", block_type="event")
        cost.add_ops(1)
        cost.add_bytes(b.content)
        state.update(b)
    return cost, state


def full_replay_baseline(n=50):
    """
    Token-like full replay: step i recomputes over all history [0..i]
    ops = 1 + 2 + ... + n
    """
    cost = CostCounter()
    history = []
    for i in range(n):
        history.append(f"user event {i}")
        # recompute all
        for _ in history:
            cost.add_ops(1)
    # mimic state size growth
    state = LatentState(max_history=10**9)
    for h in history:
        state.update(Block(h, block_type="event"))
    return cost, state


def window_replay_baseline(n=50, k=5):
    """
    Sliding window baseline: recompute only last k history each step.
    """
    cost = CostCounter()
    history = []
    for i in range(n):
        history.append(f"user event {i}")
        window = history[-k:]
        for _ in window:
            cost.add_ops(1)
    state = LatentState(max_history=10**9)
    for h in history:
        state.update(Block(h, block_type="event"))
    return cost, state


def main():
    n = 50

    print("=== LatentFlow (incremental + compression) ===")
    c1, s1 = latentflow_run(n=n, max_history=3)
    print("Cost:", c1.summary())
    print("State:", s1.summary())
    print()

    print("=== Full replay baseline (token-like) ===")
    c2, s2 = full_replay_baseline(n=n)
    print("Cost:", c2.summary())
    print("State:", s2.summary())
    print()

    print("=== Sliding window baseline (k=5) ===")
    c3, s3 = window_replay_baseline(n=n, k=5)
    print("Cost:", c3.summary())
    print("State:", s3.summary())
    print()

    print("=== Compare ===")
    print("Ops ratio full_replay / latentflow:", round(c2.summary()["operations"] / c1.summary()["operations"], 2))
    print("Ops ratio window(k=5) / latentflow:", round(c3.summary()["operations"] / c1.summary()["operations"], 2))


if __name__ == "__main__":
    main()