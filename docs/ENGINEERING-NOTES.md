# Engineering notes

These notes record the evidence currently present in the repository. They deliberately do not claim completed CI/CD or Kubernetes work that has not yet been implemented.

## 1. Container image choices

My laptop and a CI runner can differ in host OS, installed Python, and installed frontend tools. Those differences are frozen by container definitions rather than assumed from the host: the backend runtime is `python:3.12-slim` (`backend/Dockerfile:7`), the frontend build stage is `node:22-alpine` (`frontend/Dockerfile:1`), and the frontend runtime is `nginx:1.27-alpine` (`frontend/Dockerfile:12`). Kubernetes then gives the backend a defined scheduling budget (`k8s/base/backend.yaml:104-110`) rather than relying on whichever CPU/memory happens to be free on a laptop.

PostgreSQL and Redis use Alpine images in both Compose files (`docker-compose.yml:2` and `docker-compose.yml:19`). Ollama uses a dedicated image and persistent `ollama_models` volume (`docker-compose.yml:33-55`); its larger production limit recognises model serving as a heavier workload.

## 2. Pipeline timing and cost

The project is currently below continuous integration: tests are runnable locally, but no server automatically runs them on every push or pull request. The next maturity rung is continuous integration, which will run linting, type checks, backend/frontend tests, and Compose smoke tests consistently before a merge. CI workflows have not been added yet, so there is no truthful pipeline-duration or hosted-runner cost evidence to report.

## 3. Frontend runtime configuration

The exact frontend guarantee is the relative `fetch(path, ...)` call in `frontend/src/api/client.ts:3-4`; nginx resolves `/api/` to the runtime Docker/Kubernetes service name at `frontend/nginx.conf:7-13`. This prevents an environment-specific API URL from being compiled into Vite's static files and lets one frontend image run in development and production. Without the proxy, each environment-specific absolute URL would require rebuilding the frontend image.

## 4. Triage correctness and resilience

With a live LLM, “correct” means the result passes the `TriageResult` schema, stays within the category/priority enum, and does not make complaint intake unavailable. The provider factory selects deterministic rules, simulated behaviour, Groq, or Ollama (`backend/app/providers/triage/factory.py:7-13`). Before accepting a provider response, `TriageService` validates it, records latency, and caches an accepted result for 24 hours (`backend/app/services/triage.py:23-43`). On provider or validation failure it records the error class and returns rule-based fallback output (`backend/app/services/triage.py:45-54`).

CI-facing tests are deterministic because the fixture injects `SimulatedTriage` (`backend/tests/conftest.py:18-27`), and the tests explicitly assert fallback for both an exception and malformed output (`backend/tests/test_api.py:31-41`). The injection test asserts that a malicious category outside the schema is not accepted (`backend/tests/test_api.py:87-90`). Formal provider-quality measurements and cache-hit-rate reporting are still to be collected.

## 5. Scaling decision

`k8s/base/hpa.yaml` defines an autoscaling/v2 backend HPA with `minReplicas: 2`, `maxReplicas: 10`, a 60% CPU target, immediate scale-up, and a 300-second scale-down window. The backend CPU request is `250m` in `k8s/base/backend.yaml`, which gives HPA the denominator it needs. `load/k6-script.js` supplies the repeatable offered load.

Actual HPA lag, watch output, and the replicas-versus-load chart are still pending a real run with metrics-server. Those measurements must be added rather than guessed.

## 6. Vertical scaling decision

`k8s/base/vpa.yaml` defines a backend VPA in recommender mode (`updateMode: Off`). It must stay in this mode because an Auto VPA changing CPU requests alters the denominator used by the CPU-based HPA: raising a request can lower measured utilisation and trigger an HPA scale-in, creating a feedback loop. A human should inspect the VPA target/lower/upper recommendations after a real load test before updating requests.

## 7. Network and hosted-LLM reasoning

`frontend` belongs only to `edge`; PostgreSQL and Redis belong only to `internal`; only `backend` belongs to both (`docker-compose.yml:57-81` and `docker-compose.yml:89-110`). Docker marks `internal` as an internal network, so it does not provide an external route. The backend retains its ordinary `edge` interface and can use that route for an optional Groq request. The exact isolation demonstration is:

```powershell
docker compose exec frontend ping -c 1 postgres
```

It must fail. The backend internet test is documented in [the runbook](RUNBOOK.md).

## 8. Operational learning

No real production incident has yet been recorded, so this project does not invent one as evidence. When a genuine local or deployment troubleshooting event occurs, add its date, symptom, command/output (with secrets removed), root cause, fix, and prevention measure here.
