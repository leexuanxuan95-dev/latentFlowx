# core/infer/cost.py

class CostCounter:
    """
       Simple cost meter:
       - operations: count of state updates / baseline recomputations
       - bytes_in: bytes of incoming payloads
       """

    def __init__(self):
        self.operations = 0
        self.bytes_in = 0

    def add_ops(self, n=1):
        self.operations += n

    def add_bytes(self, payload):
        if payload is None:
            return
        if isinstance(payload, str):
            self.bytes_in += len(payload.encode("utf-8"))
        else:
            self.bytes_in += len(repr(payload).encode("utf-8"))

    def summary(self):
        return {"operations": self.operations, "bytes_in": self.bytes_in}
