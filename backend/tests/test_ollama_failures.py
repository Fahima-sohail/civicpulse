import socket
from urllib.error import URLError

import pytest

from app.providers.triage.base import TriageError
from app.providers.triage.ollama import OllamaTriage


def test_ollama_retries_once_after_socket_timeout(monkeypatch):
    attempts = []

    def fake_urlopen(*_args, **_kwargs):
        attempts.append(1)
        raise socket.timeout("timed out")

    monkeypatch.setattr("app.providers.triage.ollama.urlopen", fake_urlopen)
    monkeypatch.setattr("app.providers.triage.ollama.time.sleep", lambda _: None)

    with pytest.raises(TriageError, match="TimeoutError"):
        OllamaTriage("http://ollama:11434", "llama3.2:1b").triage("Water pipe burst", "Block A")

    assert len(attempts) == OllamaTriage.MAX_ATTEMPTS


def test_ollama_retries_timeout_wrapped_by_url_error(monkeypatch):
    attempts = []

    def fake_urlopen(*_args, **_kwargs):
        attempts.append(1)
        raise URLError(socket.timeout("timed out"))

    monkeypatch.setattr("app.providers.triage.ollama.urlopen", fake_urlopen)
    monkeypatch.setattr("app.providers.triage.ollama.time.sleep", lambda _: None)

    with pytest.raises(TriageError, match="URLError"):
        OllamaTriage("http://ollama:11434", "llama3.2:1b").triage("Water pipe burst", "Block A")

    assert len(attempts) == OllamaTriage.MAX_ATTEMPTS


def test_ollama_does_not_retry_non_timeout_connection_error(monkeypatch):
    attempts = []

    def fake_urlopen(*_args, **_kwargs):
        attempts.append(1)
        raise URLError(ConnectionRefusedError("connection refused"))

    monkeypatch.setattr("app.providers.triage.ollama.urlopen", fake_urlopen)

    with pytest.raises(TriageError, match="URLError"):
        OllamaTriage("http://ollama:11434", "llama3.2:1b").triage("Water pipe burst", "Block A")

    assert len(attempts) == 1
