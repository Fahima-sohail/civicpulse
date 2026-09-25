# Engineering notes

These notes record the evidence currently present in the repository. They deliberately do not claim completed CI/CD or Kubernetes work that has not yet been implemented.

## 1. Container image choices

PostgreSQL and Redis use Alpine images in both Compose files (`docker-compose.yml:2` and `docker-compose.yml:19`). The frontend is served by nginx and proxies the API to the backend (`frontend/nginx.conf:7-16`). Development builds the application images locally; production references `${BACKEND_IMAGE}:${IMAGE_TAG}` and `${FRONTEND_IMAGE}:${IMAGE_TAG}` (`compose.prod.yaml:75-76`, `compose.prod.yaml:111-112`).

Ollama uses a dedicated image and a persistent `ollama_models` volume (`docker-compose.yml:33-55`). Its larger resource allocation in production acknowledges the model-serving workload.

## 2. Pipeline timing and cost

Not yet measured. CI workflows have not been added, so there is no truthful pipeline-duration or hosted-runner cost evidence to report. Once CI exists, record the run URL, duration, and whether dependency/image caching changed it.

## 3. Frontend runtime configuration

The frontend uses relative `/api/` calls, while nginx resolves the Docker service name `backend` at runtime (`frontend/nginx.conf:7-13`). This prevents an environment-specific API URL from being compiled into Vite's static files and lets one frontend image run in development and production.

## 4. Triage correctness and resilience

The provider factory selects deterministic rules, simulated behaviour, Groq, or Ollama (`backend/app/providers/triage/factory.py:7-13`). Before accepting a provider response, `TriageService` validates it, records latency, and caches an accepted result for 24 hours (`backend/app/services/triage.py:23-43`). On provider or validation failure it records the error class and returns rule-based fallback output (`backend/app/services/triage.py:45-54`).

The result is a controlled degradation path rather than an intake outage. Formal provider-quality measurements and cache-hit-rate reporting are still to be collected.

## 5. Scaling decision

Not yet implemented. There is no Kubernetes HPA, load test, or evidence-driven replica threshold in this repository. The next Kubernetes task should define requests/limits, add a backend HPA, run a reproducible load test, and record the observed scaling behaviour.

## 6. Vertical scaling decision

Not yet implemented. No VPA is configured. Any future VPA recommendation should use actual CPU/memory history and avoid automatically changing a latency-sensitive production workload without review.

## 7. Network and hosted-LLM reasoning

`frontend` belongs only to `edge`; PostgreSQL and Redis belong only to `internal`; only `backend` belongs to both (`docker-compose.yml:57-81` and `docker-compose.yml:89-110`). Docker marks `internal` as an internal network, so it does not provide an external route. The backend retains its ordinary `edge` interface and can use that route for an optional Groq request. The exact isolation demonstration is:

```powershell
docker compose exec frontend ping -c 1 postgres
```

It must fail. The backend internet test is documented in [the runbook](RUNBOOK.md).

## 8. Operational learning

No real production incident has yet been recorded, so this project does not invent one as evidence. When a genuine local or deployment troubleshooting event occurs, add its date, symptom, command/output (with secrets removed), root cause, fix, and prevention measure here.
