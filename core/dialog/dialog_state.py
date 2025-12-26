# =========================================================
# ===== file: core/dialog/dialog_state.py
# =========================================================
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DialogState:
    session_id: str
    goal: Optional[str] = None
    last_intent: Optional[str] = None
    pending_questions: List[str] = field(default_factory=list)
    memory: Dict[str, Any] = field(default_factory=dict)

    def set_pending(self, qs: List[str]):
        self.pending_questions = list(qs)

    def consume_user_answer(self, text: str):
        # very cheap: store raw answer; real system would parse and fill slots
        self.memory.setdefault("answers", []).append(text)
