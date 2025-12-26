# core/engine.py
f
# =========================================================
# ===== file: core/engine.py
# =========================================================
from core.state.latent_state import LatentState
from core.input.incremental import incremental_update


class LatentFlowEngine:
    """
    v0.2 Engine:
    - consume(): incremental update + guard + invariants + audit + rollback on failure
    - reason(): plugin-based decision + audit
    """

    def __init__(self, plugins=None, guard=None, verifier=None, audit_logger=None):
        self.plugins = plugins or []
        self.guard = guard
        self.verifier = verifier
        self.audit_logger = audit_logger

    def init(self):
        return LatentState()

    def consume(self, state, block, cost):
        return incremental_update(
            state,
            block,
            cost,
            guard=self.guard,
            verifier=self.verifier,
            audit_logger=self.audit_logger,
        )

    def reason(self, state):
        matched = None
        decision = "no rule matched"

        for plugin in self.plugins:
            r = plugin.apply(state)
            if r is not None:
                matched = plugin.__class__.__name__
                decision = r
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