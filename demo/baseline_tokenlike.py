# demo/baseline_tokenlike.py
from core.state.latent_state import LatentState
from core.state.state_delta import StateDelta

class TokenLikeBaselineEngine:
    """
    Token-like baseline:
    - 每次输入都重算全部历史（模拟 token attention / replay prompt）
    - 不是tokenizer，只是模拟“历史回放计算”
    """

    def init(self):
        return LatentState()

    def consume(self, state, block, cost):
        # baseline：保存历史（这里用 short_history 暂存相当于“上下文”）
        state.short_history.append(block)
        state.counter += 1

        # “重算历史”：每次都遍历所有历史来做一次计算
        # 这就是 token / prompt replay 的结构代价
        before = state.snapshot()
        for b in state.short_history:
            cost.add(1)  # 每回放一个历史块，就算一次操作

        # baseline 不做压缩（模拟上下文越来越长）
        return state, StateDelta(before, state)
