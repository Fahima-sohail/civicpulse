# CivicPulse backend

Municipal complaint intake, deterministic/LLM triage, PostgreSQL persistence, and Redis-backed caching/rate limiting.

## Run

```powershell
docker compose up --build
```

Open http://localhost:8000/health. The Compose startup applies the Alembic migration and idempotently seeds 30 complaints.

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
- `postgres_data` persists database rows. `redis_data` persists Redis AOF, retaining limiter state/cache across restarts.
