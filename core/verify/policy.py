# =========================================================
# ===== file: core/verify/policy.py
# =========================================================
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class Policy:
    """
    Enterprise policy knobs (cheap, deterministic).
    """
    max_transfer_amount: float = 1000.0
    max_withdraw_amount: float = 1000.0
    blocked_targets: Set[str] = field(default_factory=set)
    require_approval_over: float = 500.0

    # permissions example
    allowed_intents: Set[str] = field(default_factory=lambda: {"transfer", "withdraw", "cancel_order", "create_order", "qa"})


