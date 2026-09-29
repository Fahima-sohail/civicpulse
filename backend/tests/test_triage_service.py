from uuid import uuid4

from app.providers.triage.base import TriageResult
from app.schemas import Category, Priority
from app.services.metrics import Metrics
from app.services.triage import TriageService
from tests.conftest import fake_redis


class CountingProvider:
    name = "llm:counting"

    def __init__(self):
        self.calls = 0

    def triage(self, text: str, location: str) -> TriageResult:
        self.calls += 1
        return TriageResult(
            category=Category.water,
            priority=Priority.normal,
            summary="Water service report.",
            confidence=0.9,
        )


class FailingProvider:
    name = "llm:failing"

    def triage(self, text: str, location: str) -> TriageResult:
        raise RuntimeError("provider unavailable")


def test_triage_service_caches_identical_text_and_skips_second_inference():
    provider = CountingProvider()
    service = TriageService(provider, fake_redis(), Metrics())

    first = service.triage(uuid4(), "Water pipe leaking outside the school gate.", "Block A")
    second = service.triage(uuid4(), "Water pipe leaking outside the school gate.", "Block B")

    assert provider.calls == 1
    assert first[1] == "llm:counting"
    assert second[1] == "llm:counting"
    assert second[2] == 0
    assert len(service.outcomes) == 2


def test_triage_service_records_and_caches_rules_fallback_after_provider_failure():
    service = TriageService(FailingProvider(), fake_redis(), Metrics())

    first = service.triage(uuid4(), "A burst water pipe is flooding the road.", "Block A")
    second = service.triage(uuid4(), "A burst water pipe is flooding the road.", "Block A")

    assert first[1] == "rules:fallback"
    assert second[1] == "rules:fallback"
    assert service.outcomes[0].fallback is True
    assert service.outcomes[0].latency_ms == 0
