# =========================================================
# ===== file: core/lang/pipeline.py
# =========================================================
from typing import List

from core.infer.block import Block
from core.lang.schema import IntentFrame
from core.lang.normalizer import normalize_whitespace
from core.lang.extractors import SlotExtractor
from core.lang.constraints import ConstraintCompiler


class IntentClassifier:
    """
    Deterministic intent classifier (no ML, no token).
    """

    def classify(self, text: str):
        t = text.lower()

        if any(k in t for k in ["转账", "转给", "transfer"]):
            return "transfer", 0.85
        if any(k in t for k in ["提现", "withdraw"]):
            return "withdraw", 0.85
        if any(k in t for k in ["取消", "撤销", "cancel"]):
            return "cancel_order", 0.80
        if any(k in t for k in ["购买", "下单", "buy"]):
            return "create_order", 0.78
        if any(k in t for k in ["为什么", "怎么", "what", "why", "how"]):
            return "qa", 0.65

        return "unknown", 0.40


class LanguagePipeline:
    """
    Natural language → IntentFrame → Block(intent)
    """

    def __init__(
        self,
        classifier=None,
        extractor=None,
        compiler=None,
    ):
        self.classifier = classifier or IntentClassifier()
        self.extractor = extractor or SlotExtractor()
        self.compiler = compiler or ConstraintCompiler()

    def parse(self, text: str) -> List[Block]:
        raw = text
        t = normalize_whitespace(text)

        intent, confidence = self.classifier.classify(t)
        slots, slot_trace = self.extractor.extract(t)
        constraints, constraint_trace = self.compiler.compile(t, slots)

        frame = IntentFrame(
            intent=intent,
            slots=slots,
            constraints=constraints,
            confidence=confidence,
            trace={
                "slots": slot_trace,
                "constraints": constraint_trace,
            },
            raw=raw,
        )

        return [Block(frame.to_dict(), block_type="intent")]
