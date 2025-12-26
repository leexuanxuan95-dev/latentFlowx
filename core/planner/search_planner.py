# =========================================================
# ===== file: core/planner/search_planner.py
# =========================================================
from collections import deque
from typing import Callable, List, Optional, Set, Tuple
from core.planner.action import Action


class SearchPlanner:
    """
    Minimal BFS planner (agentless).
    - state is abstracted as a hashable key via state_key_fn
    - transitions are provided by action_generator (domain-specific)
    - goal_test checks whether the state satisfies the goal
    """

    def __init__(
        self,
        state_key_fn: Callable,
        action_generator: Callable,
        transition_fn: Callable,
        goal_test: Callable,
        max_depth: int = 6,
    ):
        self.state_key_fn = state_key_fn
        self.action_generator = action_generator
        self.transition_fn = transition_fn
        self.goal_test = goal_test
        self.max_depth = max_depth

    def plan(self, init_state, goal) -> Optional[List[Action]]:
        q = deque()
        seen: Set[str] = set()

        key0 = self.state_key_fn(init_state)
        q.append((init_state, [], 0))
        seen.add(key0)

        while q:
            state, path, depth = q.popleft()
            if self.goal_test(state, goal):
                return path
            if depth >= self.max_depth:
                continue

            for act in self.action_generator(state, goal):
                nxt = self.transition_fn(state, act)
                k = self.state_key_fn(nxt)
                if k in seen:
                    continue
                seen.add(k)
                q.append((nxt, path + [act], depth + 1))

        return None

