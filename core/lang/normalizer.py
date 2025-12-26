# =========================================================
# ===== file: core/lang/normalizer.py
# =========================================================
from __future__ import annotations

import re
from typing import Optional, Tuple


_CN_NUM = {
    "零": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
    "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10
}


def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def parse_amount(text: str) -> Optional[float]:
    """
    Parse amount from mixed text:
    - "500"
    - "500.5"
    - "1k" / "2K"
    - "3w" / "3万"
    - "两千" (very limited)
    """
    t = text.strip()

    m = re.search(r"(\d+(?:\.\d+)?)\s*(k|K|w|W|万|千)?", t)
    if m:
        num = float(m.group(1))
        unit = m.group(2)
        if unit in ("k", "K", "千"):
            return num * 1000.0
        if unit in ("w", "W", "万"):
            return num * 10000.0
        return num

    # very small CN number support: "两千"/"三万"
    m = re.search(r"([零一二两三四五六七八九十]+)\s*(千|万)", t)
    if m:
        cn = m.group(1)
        unit = m.group(2)
        base = _cn_to_int(cn)
        if base is None:
            return None
        if unit == "千":
            return float(base * 1000)
        if unit == "万":
            return float(base * 10000)

    return None


def _cn_to_int(cn: str) -> Optional[int]:
    # minimal: "十", "二十", "二十三", "两"
    if cn == "十":
        return 10
    if len(cn) == 1 and cn in _CN_NUM:
        return _CN_NUM[cn]
    # "二十" / "二十三"
    if "十" in cn:
        parts = cn.split("十")
        left = parts[0]
        right = parts[1] if len(parts) > 1 else ""
        l = _CN_NUM.get(left, 1) if left else 1
        r = _CN_NUM.get(right, 0) if right else 0
        return l * 10 + r
    return None


def parse_currency(text: str) -> Optional[str]:
    t = text
    if "usd" in t.lower() or "$" in t:
        return "USD"
    if "eur" in t.lower() or "€" in t:
        return "EUR"
    if "cny" in t.lower() or "rmb" in t.lower() or "元" in t or "人民币" in t or "￥" in t:
        return "CNY"
    return None


def parse_deadline(text: str) -> Optional[str]:
    """
    Very lightweight deadline extraction.
    Returns a normalized token, not a datetime:
      - "today" / "tomorrow" / "before_today"
    """
    t = text.lower()
    if "今天之前" in text or "今日之前" in text or "before today" in t:
        return "before_today"
    if "今天" in text or "today" in t:
        return "today"
    if "明天" in text or "tomorrow" in t:
        return "tomorrow"
    return None
