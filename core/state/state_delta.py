# core/state/state_delta.py
class StateDelta:
    def __init__(self, before, after):
        self.delta_steps = after.counter - before.counter

    def summary(self):
        return {"delta_steps": self.delta_steps}
