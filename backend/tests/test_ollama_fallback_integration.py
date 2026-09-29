from app.providers.triage.ollama import OllamaTriage


class MalformedResponse:
    def read(self):
        return b'{"response":"not-json"}'

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def test_ollama_invalid_response_uses_rules_fallback_for_complaint_intake(app, client, complaint_payload, monkeypatch):
    app.state.triage.provider = OllamaTriage("http://ollama:11434", "llama3.2:1b")
    monkeypatch.setattr(
        "app.providers.triage.ollama.urlopen",
        lambda *_args, **_kwargs: MalformedResponse(),
    )

    response = client.post("/api/complaints", json=complaint_payload)

    assert response.status_code == 201
    assert response.json()["triaged_by"] == "rules:fallback"
    outcome = client.get("/api/meta/providers").json()["outcomes"][0]
    assert outcome == {"provider": "rules:fallback", "latency_ms": outcome["latency_ms"], "fallback": True}
