# core/infer/cost.py

class CostCounter:
    def __init__(self):
        self.operations = 0
        self.bytes_in = 0

    def add(self, n=1):
        self.operations += n

    def add_bytes(self, s: str):
        self.bytes_in += len(s.encode("utf-8"))

    def summary(self):
        return {"operations": self.operations, "bytes_in": self.bytes_in}
