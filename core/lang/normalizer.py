# =========================================================
# ===== file: core/lang/normalizer.py
# =========================================================
from __future__ import annotations

import re


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace for deterministic parsing.
    - collapse multiple spaces
    - trim
    """
    if text is None:
        return ""
    t = str(text)
    t = re.sub(r"\s+", " ", t).strip()
    return t
