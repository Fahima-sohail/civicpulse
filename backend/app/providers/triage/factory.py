from app.config import Settings
from app.providers.triage.llm import LLMTriage
from app.providers.triage.ollama import OllamaTriage
from app.providers.triage.rules import RuleBasedTriage
from app.providers.triage.simulated import SimulatedTriage

def make_triage_provider(settings: Settings):
    match settings.triage_provider.lower():
        case "rules": return RuleBasedTriage()
        case "simulated": return SimulatedTriage(settings.simulated_failure_mode)
        case "llm" | "groq": return LLMTriage(settings.groq_api_key, settings.groq_model)
        case "ollama": return OllamaTriage(settings.ollama_base_url, settings.ollama_model)
        case unknown: raise ValueError(f"Unknown TRIAGE_PROVIDER: {unknown}")
