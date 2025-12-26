from core.verify.invariants import Invariants, InvariantViolation


class Verifier:
    """
    Runs invariants (and later post-checks) after update / compression.
    """

    def verify(self, state):
        try:
            Invariants.check(state)
        except InvariantViolation as e:
            raise
        return True