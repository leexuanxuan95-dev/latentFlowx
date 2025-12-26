
# =========================================================
# ===== file: core/lang/extractors.py
# =========================================================
from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

from core.lang.normalizer import parse_amount, parse_currency, parse_deadline, normalize_whitespace


class SlotExtractor:
    """
    Industrial-style: keep it cheap + deterministic first.
    You can later add a char-model extractor without changing the pipeline interface.
    """

    def extract(self, text: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Returns (slots, trace)
        """
        t = normalize_whitespace(text)
        slots: Dict[str, Any] = {}
        trace: Dict[str, Any] = {"matches": []}

        # common slots
        amt = self._extract_amount(t)
        if amt is not None:
            slots["amount"] = amt
            trace["matches"].append({"slot": "amount", "value": amt})

        cur = parse_currency(t)
        if cur:
            slots["currency"] = cur
            trace["matches"].append({"slot": "currency", "value": cur})

        to_user = self._extract_target(t)
        if to_user:
            slots["to"] = to_user
            trace["matches"].append({"slot": "to", "value": to_user})

        oid = self._extract_order_id(t)
        if oid:
            slots["order_id"] = oid
            trace["matches"].append({"slot": "order_id", "value": oid})

        item = self._extract_item(t)
        if item:
            slots["item"] = item
            trace["matches"].append({"slot": "item", "value": item})

        deadline = parse_deadline(t)
        if deadline:
            slots["deadline"] = deadline
            trace["matches"].append({"slot": "deadline", "value": deadline})

        return slots, trace

    def _extract_amount(self, t: str) -> Optional[float]:
        # patterns: "转账500", "500元", "金额500", "amount 500"
        m = re.search(r"(金额|amount|转账|转给|支付|pay)\s*[:：]?\s*([0-9]+(?:\.[0-9]+)?\s*(?:k|K|w|W|万|千)?)", t, re.I)
        if m:
            return parse_amount(m.group(2))

        m = re.search(r"([0-9]+(?:\.[0-9]+)?\s*(?:k|K|w|W|万|千)?)\s*(元|rmb|cny|usd|eur|￥|\$|€)?", t, re.I)
        if m:
            amt = parse_amount(m.group(1))
            # Only accept if there's some payment hint nearby
            if re.search(r"(转账|转给|支付|pay|withdraw|提现)", t, re.I):
                return amt
        return None

    def _extract_target(self, t: str) -> Optional[str]:
        # "给Bob转账" / "to Bob"
        m = re.search(r"(给|to)\s*([A-Za-z0-9_\-\u4e00-\u9fa5]{1,32})\s*(转账|支付|打款|transfer|pay)?", t, re.I)
        if m:
            return m.group(2)
        return None

    def _extract_order_id(self, t: str) -> Optional[str]:
        m = re.search(r"(订单|order)\s*#?\s*([A-Za-z0-9_-]{2,64})", t, re.I)
        return m.group(2) if m else None

    def _extract_item(self, t: str) -> Optional[str]:
        # "购买 iPhone" / "buy iphone"
        m = re.search(r"(购买|buy|purchase)\s+(.+)$", t, re.I)
        if m:
            item = m.group(2).strip()
            # cut tail constraints keywords
            item = re.split(r"(不超过|最多|小于|大于|<=|>=|<|>|before|今天|明天)", item, maxsplit=1)[0].strip()
            return item or None
        return None