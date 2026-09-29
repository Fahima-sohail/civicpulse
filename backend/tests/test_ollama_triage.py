from urllib.error import HTTPError

import pytest

from app.providers.triage.base import TriageError
from app.providers.triage.ollama import OllamaTriage
from app.schemas import Category, Priority


class ValidOllamaResponse:
    def read(self):
        return b'{"response":"{\\"category\\":\\"water\\",\\"priority\\":\\"high\\",\\"summary\\":\\"Burst pipe.\\",\\"confidence\\":0.9}"}'

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def test_ollama_retries_once_after_retryable_server_error(monkeypatch):
    attempts = []

    def fake_urlopen(*_args, **_kwargs):
        attempts.append(1)
        if len(attempts) == 1:
            raise HTTPError("http://ollama:11434/api/generate", 500, "server error", None, None)
        return ValidOllamaResponse()

    monkeypatch.setattr("app.providers.triage.ollama.urlopen", fake_urlopen)
    monkeypatch.setattr("app.providers.triage.ollama.time.sleep", lambda _: None)

    result = OllamaTriage("http://ollama:11434", "llama3.2:1b").triage("Water pipe burst", "Block A")

    assert len(attempts) == 2
    assert result.category is Category.water
    assert result.priority is Priority.high


def test_ollama_retries_once_after_rate_limit_and_uses_hard_timeout(monkeypatch):
    timeouts = []

    def fake_urlopen(*_args, **kwargs):
        timeouts.append(kwargs["timeout"])
        if len(timeouts) == 1:
            raise HTTPError("http://ollama:11434/api/generate", 429, "too many requests", None, None)
        return ValidOllamaResponse()

    monkeypatch.setattr("app.providers.triage.ollama.urlopen", fake_urlopen)
    monkeypatch.setattr("app.providers.triage.ollama.random.uniform", lambda *_: 0.12)
    monkeypatch.setattr("app.providers.triage.ollama.time.sleep", lambda _: None)

    result = OllamaTriage("http://ollama:11434", "llama3.2:1b").triage("Water pipe burst", "Block A")

    assert result.category is Category.water
    assert timeouts == [OllamaTriage.REQUEST_TIMEOUT_SECONDS] * 2


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [(429, True), (500, True), (503, True), (400, False), (404, False)],
)
def test_ollama_retry_status_policy(status_code, expected):
    assert OllamaTriage._is_retryable_http_status(status_code) is expected


def test_ollama_does_not_retry_non_retryable_client_error(monkeypatch):
    attempts = []

    def fake_urlopen(*_args, **_kwargs):
        attempts.append(1)
        raise HTTPError("http://ollama:11434/api/generate", 400, "bad request", None, None)

    monkeypatch.setattr("app.providers.triage.ollama.urlopen", fake_urlopen)

    with pytest.raises(TriageError, match="HTTP 400"):
        OllamaTriage("http://ollama:11434", "llama3.2:1b").triage("Water pipe burst", "Block A")

    assert len(attempts) == 1


def test_ollama_rejects_malformed_model_output(monkeypatch):
    class MalformedResponse(ValidOllamaResponse):
        def read(self):
            return b'{"response":"not-json"}'

    monkeypatch.setattr("app.providers.triage.ollama.urlopen", lambda *_args, **_kwargs: MalformedResponse())

    with pytest.raises(TriageError, match="JSONDecodeError"):
        OllamaTriage("http://ollama:11434", "llama3.2:1b").triage("Water pipe burst", "Block A")
