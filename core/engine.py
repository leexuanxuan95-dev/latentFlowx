# core/engine.py
from core.state.latent_state import LatentState
from core.input.incremental import incremental_update

class LatentFlowEngine:
    def __init__(self, plugins=None, guard=None, audit_logger=None):
        self.plugins = plugins or []
        self.guard = guard
        self.audit_logger = audit_logger

    def init(self):
        return LatentState()

    def consume(self, state, block, cost):
        return incremental_update(state, block, cost, guard=self.guard, audit_logger=self.audit_logger)

    def reason(self, state):
        matched = None
        decision = "no rule matched"

        for plugin in self.plugins:
            result = plugin.apply(state)
            if result:
                matched = plugin.__class__.__name__
                decision = result
                break

        output = {"decision": decision}
        trace = {"plugin": matched}

        if self.audit_logger:
            self.audit_logger.emit("reason", {
                "decision": output,
                "trace": trace,
                "state": state.summary(),
            })

        return output, trace
