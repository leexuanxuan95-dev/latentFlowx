# core/plugins/base.py
class ReasonPlugin:
    def apply(self, state):
        raise NotImplementedError
