class Reasoner:
    def __init__(self, plugins):
        self.plugins = plugins

    def reason(self, state):
        trace = {
            "checked": [],
            "matched": None,
            "state": state.summary()
        }

        for plugin in self.plugins:
            name = plugin.__class__.__name__
            trace["checked"].append(name)
            result = plugin.apply(state)
            if result is not None:
                trace["matched"] = name
                return {"decision": result}, trace

        return {"decision": "no rule matched"}, trace
