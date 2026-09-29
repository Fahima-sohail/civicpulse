# Ollama reliability behaviour

`OllamaTriage` is the local-model provider selected with `TRIAGE_PROVIDER=ollama`. It sends only complaint text and location to the internal Ollama service; `reporter_contact` is never included in the model prompt.

## Failure policy

Each inference call has a hard 10-second timeout. CivicPulse retries exactly once, with a small random jitter, only for:

- HTTP `429` responses;
- HTTP `5xx` responses;
- socket timeouts, including timeouts wrapped by `URLError`.

It does not retry HTTP `4xx` validation/client errors or connection-refused errors. A response that is not valid JSON, does not include all required fields, uses a category outside the allowed enum, or has invalid confidence is rejected by Pydantic.

Every terminal provider failure uses `RuleBasedTriage`, so the complaint is still saved with `triaged_by: "rules:fallback"`. The backend writes one structured warning containing the complaint id, active provider, and error class; it does not log the reporter's contact details.

## Demonstration checks

Use a new complaint sentence when changing providers, because triage results are cached by SHA-256 hash of complaint text for 24 hours.

```powershell
docker compose exec backend env | Select-String TRIAGE_PROVIDER
docker compose exec ollama ollama list
Invoke-RestMethod http://localhost:8000/api/meta/providers
docker compose logs --tail 100 backend
```

For a normal local-model result, the complaint and provider metadata show `llm:ollama`. For an intentional failure demonstration, stop the Ollama service or use malformed provider output in a test; the complaint remains accepted and reports `rules:fallback`.
