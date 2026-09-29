import pytest

from app.providers.triage.base import TriageError
from app.providers.triage.ollama import OllamaTriage


class FakeResponse:
    def __init__(self, response: bytes):
        self.response = response

    def read(self):
        return self.response

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


@pytest.mark.parametrize(
    "model_response",
    [
        b'{"response":"{\\"category\\":\\"water\\"}"}',
        b'{"response":"{\\"category\\":\\"spaceships\\",\\"priority\\":\\"high\\",\\"summary\\":\\"Bad category\\",\\"confidence\\":0.8}"}',
        b'{"response":"{\\"category\\":\\"water\\",\\"priority\\":\\"high\\",\\"summary\\":\\"A\\",\\"confidence\\":1.2}"}',
    ],
)
def test_ollama_rejects_schema_invalid_json(monkeypatch, model_response):
    monkeypatch.setattr(
        "app.providers.triage.ollama.urlopen",
        lambda *_args, **_kwargs: FakeResponse(model_response),
    )

    with pytest.raises(TriageError, match="ValidationError"):
        OllamaTriage("http://ollama:11434", "llama3.2:1b").triage("Water pipe burst", "Block A")
