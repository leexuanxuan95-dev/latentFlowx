
# =========================================================
# ===== file: core/lang/pipeline.py
# =========================================================
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from core.infer.block import Block
from core.lang.schema import IntentFrame
from core.lang.extractors import SlotExtractor
from core.lang.constraints import ConstraintCompiler
from core.lang.normalizer import normalize_whitespace


class IntentClassifier:
    """
    Deterministic intent classifier (industrial baseline).
    """

    def classify(self, text: str) -> Tuple[str, float, Dict[str, Any]]:
        t = normalize_whitespace(text)
        trace = {"signals": []}

        if re.search(r"(转账|转给|打款|transfer)", t, re.I):
            trace["signals"].append("money_transfer_keyword")
            return "transfer", 0.85, trace

        if re.search(r"(提现|withdraw)", t, re.I):
            trace["signals"].append("withdraw_keyword")
            return "withdraw", 0.85, trace

        if re.search(r"(取消|撤销|cancel)", t, re.I):
            trace["signals"].append("cancel_keyword")
            return "cancel_order", 0.80, trace

        if re.search(r"(购买|下单|buy|purchase)", t, re.I):
            trace["signals"].append("purchase_keyword")
            return "create_order", 0.78, trace

        if re.search(r"(总结|摘要|解释|说明|为什么|如何|是什么|what|why|how)", t, re.I):
            trace["signals"].append("qa_keyword")
            return "qa", 0.60, trace

        return "unknown", 0.40, trace


class LanguagePipeline:
    """
    text -> IntentFrame -> Block(intent)
    """

    def __init__(self, classifier=None, extractor=None, compiler=None):
        self.classifier = classifier or IntentClassifier()
        self.extractor = extractor or SlotExtractor()
        self.compiler = compiler or ConstraintCompiler()

    def to_intent_blocks(self, text: str) -> List[Block]:
        raw = text
        t = normalize_whitespace(text)

        intent, conf, it_trace = self.classifier.classify(t)
        slots, sl_trace = self.extractor.extract(t)
        constraints, c_trace = self.compiler.compile(t, slots)

        frame = IntentFrame(
            intent=intent,
            slots=slots,
            constraints=constraints,
            confidence=conf,
            trace={"intent": it_trace, "slots": sl_trace, "constraints": c_trace},
            raw=raw,
        )

        return [Block(frame.to_dict(), block_type="intent")]