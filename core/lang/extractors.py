# =========================================================
# ===== file: core/lang/extractors.py
# =========================================================
from __future__ import annotations

import re
from typing import Any, Dict, Tuple


def _parse_amount(text: str):
    """
    Parse amount:
      - "100" -> 100
      - "1k" -> 1000
      - "2w" -> 20000 (万)
      - "3万" -> 30000
      - "900 元" -> 900
    """
    t = text.strip().lower()

    # 3万
    m = re.search(r"(\d+(?:\.\d+)?)\s*万", t)
    if m:
        return float(m.group(1)) * 10000

    # 2w / 1k
    m = re.search(r"(\d+(?:\.\d+)?)\s*(w|k)\b", t)
    if m:
        num = float(m.group(1))
        unit = m.group(2)
        return num * (10000 if unit == "w" else 1000)

    # 900元 / 900 元
    m = re.search(r"(\d+(?:\.\d+)?)\s*(元|rmb|cny|usd|usdt)?", t)
    if m:
        return float(m.group(1))

    return None


def _extract_currency(text: str):
    t = text.lower()
    if "usdt" in t:
        return "USDT"
    if "usd" in t:
        return "USD"
    if "cny" in t or "rmb" in t or "元" in t:
        return "CNY"
    return None


def _extract_target(text: str):
    """
    Extract recipient:
      - 给Bob转账
      - 转给 Alice
      - to Tom
    """
    # Chinese patterns
    m = re.search(r"(给|转给)\s*([A-Za-z0-9_\-一-龥]+)", text)
    if m:
        return m.group(2)

    # English pattern
    m = re.search(r"\bto\s+([A-Za-z0-9_\-]+)", text, re.I)
    if m:
        return m.group(1)

    return None


def _extract_order_id(text: str):
    m = re.search(r"(订单|order)\s*#?\s*([A-Za-z0-9_-]+)", text, re.I)
    return m.group(2) if m else None


def _extract_item(text: str):
    # "购买 iPhone 15" / "buy xxx"
    m = re.search(r"(购买|buy|purchase)\s+(.+)", text, re.I)
    if m:
        return m.group(2).strip()
    return None


class SlotExtractor:
    """
    Cheap deterministic slot extraction.
    Returns (slots, trace)
    """

    def extract(self, text: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        slots: Dict[str, Any] = {}
        trace: Dict[str, Any] = {"matched": []}

        to = _extract_target(text)
        if to:
            slots["to"] = to
            trace["matched"].append("slot:to")

        oid = _extract_order_id(text)
        if oid:
            slots["order_id"] = oid
            trace["matched"].append("slot:order_id")

        item = _extract_item(text)
        if item:
            slots["item"] = item
            trace["matched"].append("slot:item")

        # amount
        m = re.search(r"(\d+(?:\.\d+)?\s*(万|w|k)?\s*(元|rmb|cny|usd|usdt)?)", text, re.I)
        if m:
            amt = _parse_amount(m.group(1))
            if amt is not None:
                slots["amount"] = amt
                trace["matched"].append("slot:amount")

        cur = _extract_currency(text)
        if cur:
            slots["currency"] = cur
            trace["matched"].append("slot:currency")

        return slots, trace