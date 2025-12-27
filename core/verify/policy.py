# =========================================================
# ===== file: core/verify/policy.py
# =========================================================
from dataclasses import dataclass, field
from typing import Set


@dataclass
class Policy:
    """
    Enterprise-level policy definition.
    Deterministic, auditable, cheap.
    """

    allowed_intents: Set[str] = field(default_factory=lambda: {
        "transfer",
        "withdraw",
        "cancel_order",
        "create_order",
        "qa",
        "unknown"
    })

    max_transfer_amount: float = 10000.0
    max_withdraw_amount: float = 5000.0
    require_approval_over: float = 2000.0

    blocked_targets: Set[str] = field(default_factory=set)
