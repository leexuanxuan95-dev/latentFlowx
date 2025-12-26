# core/audit/logger.py
import json
import os
import time
import hashlib
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Optional


def _safe(obj: Any) -> Any:
    """Make object JSON-serializable."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool, list, dict)):
        return obj
    if is_dataclass(obj):
        return asdict(obj)
    if hasattr(obj, "summary") and callable(obj.summary):
        return obj.summary()
    return str(obj)


def content_fingerprint(s: str) -> Dict[str, Any]:
    b = s.encode("utf-8")
    return {
        "len": len(b),
        "sha256_8": hashlib.sha256(b).hexdigest()[:8],
    }


class AuditLogger:
    """
    JSONL audit logger for production pipelines (ELK/Datadog).
    Writes one event per line.
    """

    def __init__(self, path: Optional[str] = "logs/audit.jsonl", also_stdout: bool = False):
        self.path = path
        self.also_stdout = also_stdout

        if self.path:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def emit(self, event_type: str, payload: Dict[str, Any]):
        record = {
            "ts": time.time(),
            "event": event_type,
            **{k: _safe(v) for k, v in payload.items()},
        }
        line = json.dumps(record, ensure_ascii=False)

        if self.path:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

        if self.also_stdout:
            print(line)
