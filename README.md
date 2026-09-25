# CivicPulse backend

Municipal complaint intake, deterministic/LLM triage, PostgreSQL persistence, and Redis-backed caching/rate limiting.

## Run

```powershell
docker compose up --build
```

Open http://localhost:5173 to use the CivicPulse website, or http://localhost:8000/health to check backend liveness. The Compose startup applies the Alembic migration and idempotently seeds 30 complaints.

## Frontend runtime configuration

The frontend only calls relative paths such as `/api/complaints`. Its nginx configuration proxies `/api/` to the Compose service name `backend`, so the browser never needs an environment-specific backend URL. This keeps one built image deployable across environments: baking an absolute API URL into Vite through `import.meta.env` would turn that URL into static JavaScript at build time and require a separate frontend image for every environment.

The Node 22 builder stage is approximately 678 MB (it includes build tooling and `node_modules`); the nginx runtime stage is approximately 73.8 MB and contains only nginx, the proxy configuration, and the compiled assets. The frontend's six Vitest component tests pass in the Docker test stage.

## API

| Method | Path | Purpose |
|---|---|---|
| POST | /api/complaints | Intake, triage and persist |
| GET | /api/complaints | Filtered/paginated list |
| GET | /api/complaints/{id} | One complaint |
| PATCH | /api/complaints/{id}/status | State transition |
| GET | /api/stats | Cached aggregate stats |
| GET | /api/meta/providers | Provider observability |
| GET | /health, /ready, /metrics | Operational endpoints |

## Operational choices

- Groq model guess: `llama-3.1-8b-instant`; set `GROQ_API_KEY` and `TRIAGE_PROVIDER=llm` to use it.
- Rate limit guess: 20 complaint submissions per IP per 60 seconds. Override `RATE_LIMIT_COUNT` and `RATE_LIMIT_WINDOW_SECONDS`.
- `pgdata` persists database rows. `redisdata` persists Redis AOF, retaining limiter state/cache across restarts. `ollama_models` retains the local Ollama model after its first download.
- Set `TRIAGE_PROVIDER=ollama` to use the local `llama3.2:1b` provider. Ollama is edge-only so it can download the model, while the backend remains the only service bridging `edge` and `internal`.
