# =========================================================
# ===== file: core/session/state_store.py
# =========================================================
from core.state.latent_state import LatentState


class StateStore:
    """
    In-memory session state store (v0.2).
    Swap with Redis later.
    """

    def __init__(self):
        self._store = {}

    def get(self, session_id: str) -> LatentState:
        if session_id not in self._store:
            self._store[session_id] = LatentState()
        return self._store[session_id]

    def commit(self, session_id: str, state: LatentState):
        self._store[session_id] = state