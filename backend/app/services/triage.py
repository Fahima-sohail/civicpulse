import hashlib
import logging
import time
from uuid import UUID
from pydantic import ValidationError
from app.providers.redis_client import RedisClient
from app.providers.triage.base import TriageResult
from app.providers.triage.rules import RuleBasedTriage
from app.schemas import ProviderOutcome
from app.services.metrics import Metrics

logger = logging.getLogger(__name__)

class TriageService:
    def __init__(self, provider, redis_client: RedisClient, metrics: Metrics):
        self.provider, self.redis, self.metrics = provider, redis_client, metrics
        self.outcomes: list[ProviderOutcome] = []

    def _record(self, provider: str, latency_ms: int, fallback: bool) -> None:
        self.outcomes.insert(0, ProviderOutcome(provider=provider, latency_ms=latency_ms, fallback=fallback))
        del self.outcomes[20:]

    def triage(self, complaint_id: UUID, text: str, location: str) -> tuple[TriageResult, str, int]:
        key = "triage:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
        try:
            cached = self.redis.get_json(key)
            if cached:
                result = TriageResult.model_validate(cached["result"])
                provider, latency = cached["provider"], 0
                self._record(provider, latency, provider == "rules:fallback")
                return result, provider, latency
        except Exception:
            # Redis loss must not take complaint intake down.
            pass
        started = time.perf_counter()
        provider_name = getattr(self.provider, "name", "unknown")
        try:
            result = TriageResult.model_validate(self.provider.triage(text, location))
            latency = int((time.perf_counter() - started) * 1000)
            self.metrics.triage_latency.observe(latency / 1000)
            self._record(provider_name, latency, False)
            try: self.redis.set_json(key, {"result": result.model_dump(mode="json"), "provider": provider_name}, 86400)
            except Exception: pass
            return result, provider_name, latency
        except (Exception, ValidationError) as exc:
            latency = int((time.perf_counter() - started) * 1000)
            result = RuleBasedTriage().triage(text, location)
            logger.warning("triage_fallback", extra={"complaint_id": str(complaint_id), "provider": provider_name, "error_class": exc.__class__.__name__})
            self.metrics.triage_latency.observe(latency / 1000)
            self.metrics.fallbacks.inc()
            self._record("rules:fallback", latency, True)
            try: self.redis.set_json(key, {"result": result.model_dump(mode="json"), "provider": "rules:fallback"}, 86400)
            except Exception: pass
            return result, "rules:fallback", latency
