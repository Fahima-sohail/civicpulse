import hashlib
from app.providers.triage.base import TriageError, TriageResult
from app.providers.triage.rules import RuleBasedTriage

class SimulatedTriage:
    """Offline deterministic fake. failure_mode: none, raise, malformed_json."""
    name = "simulated"
    def __init__(self, failure_mode: str = "none", seed: str = "civicpulse"):
        self.failure_mode, self.seed, self.rules = failure_mode, seed, RuleBasedTriage()

    def triage(self, text: str, location: str) -> TriageResult:
        if self.failure_mode == "raise": raise TriageError("injected provider error")
        if self.failure_mode == "malformed_json": return "not valid triage json"  # type: ignore[return-value]
        result = self.rules.triage(text, location)
        # Stable, harmless variation makes this look like a provider without network access.
        digest = hashlib.sha256((self.seed + text).encode()).digest()[0]
        return result.model_copy(update={"confidence": round(0.55 + digest / 1024, 3)})
