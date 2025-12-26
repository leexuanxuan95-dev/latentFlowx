# core/audit/logger.py
import json
import os
import time
import hashlib
from typing import Any, Dict, Optional


def fingerprint(payload: Any) -> Dict[str, Any]:
    s = payload if isinstance(payload, str) else repr(payload)
    b = s.encode("utf-8")
    return {"len": len(b), "sha256_8": hashlib.sha256(b).hexdigest()[:8]}


def _safe(x: Any) -> Any:
    if x is None:
        return None
    if isinstance(x, (str, int, float, bool, list, dict)):
        return x
    if hasattr(x, "summary") and callable(x.summary):
        return x.summary()
    return str(x)

class AuditLogger:
    """
    JSONL logger for ELK/Datadog. One event per line.
    """

    def __init__(self, path: Optional[str] = "logs/audit.jsonl", also_stdout: bool = False):
        self.path = path
        self.also_stdout = also_stdout
        if self.path:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def emit(self, event: str, payload: Dict[str, Any]):
        record = {"ts": time.time(), "event": event}
        record.update({k: _safe(v) for k, v in payload.items()})
        line = json.dumps(record, ensure_ascii=False)
        if self.path:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        if self.also_stdout:
            print(line)