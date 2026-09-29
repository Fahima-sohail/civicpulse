# CivicPulse runbook

This runbook covers the Docker Compose stack and the Kubernetes manifests in `k8s/`.

## Start and inspect the development stack

From the repository root:

```powershell
docker compose up --build --detach --wait
docker compose ps
```

The first start can take longer because Ollama downloads the configured model. Wait for all services to report healthy before testing the website at <http://localhost:5173>.

## Verify a complaint end to end

Run this from PowerShell after `/ready` succeeds. It verifies intake, persistence, and triage metadata without relying on the browser:

```powershell
$body = @{
  text = "Water pipe burst near the school gate and the road is flooding."
  location = "Street 12, Gulshan"
} | ConvertTo-Json

$complaint = Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/api/complaints `
  -ContentType "application/json" `
  -Body $body

Invoke-RestMethod "http://localhost:8000/api/complaints/$($complaint.id)"
Invoke-RestMethod http://localhost:8000/api/meta/providers
```

The first response must be `201` and include `id`, `category`, `priority`, `ai_summary`, `triaged_by`, and `triage_latency_ms`. The second request must return the same id. Provider metadata records the last 20 outcomes, including whether rules fallback was used.

## Read logs

```powershell
docker compose logs --follow backend
docker compose logs --follow frontend
docker compose logs --follow postgres
docker compose logs --follow redis
docker compose logs --follow ollama
```

Use `Ctrl+C` to stop following logs; it does not stop the containers.

## Verify health and network isolation

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/ready
docker compose exec frontend ping -c 1 postgres
docker compose exec backend python -c "import urllib.request; print(urllib.request.urlopen('https://api.groq.com', timeout=10).status)"
```

The frontend `ping` command must fail: it has no DNS route to `postgres` because only the backend bridges `edge` and `internal`. The backend command should print an HTTP status (often `404` or `405` is fine); that proves it can reach the public Groq host without exposing a key.

## Triage failure or slow triage

1. Inspect backend logs: `docker compose logs --tail 200 backend`.
2. Check the configured provider: `docker compose exec backend env | Select-String TRIAGE_PROVIDER`.
3. For Groq, ensure `GROQ_API_KEY` is present in local `.env`; never paste it into a log, issue, or commit.
4. For Ollama, check `docker compose logs --tail 200 ollama` and confirm the configured model is listed: `docker compose exec ollama ollama list`.
5. Complaint intake should still succeed through the deterministic `rules:fallback` path. Check `/api/meta/providers` and backend logs for the recorded fallback.
6. If a model provider remains unhealthy, set `TRIAGE_PROVIDER=rules`, then recreate the backend: `docker compose up --detach --force-recreate backend`.

The exact local-model retry, validation, and fallback policy is documented in [OLLAMA-RELIABILITY.md](OLLAMA-RELIABILITY.md).

## Switch triage providers safely

Provider selection happens when the backend starts. Update the untracked root `.env` file, then recreate only the backend:

```env
TRIAGE_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2:1b
```

```powershell
docker compose up --detach --force-recreate backend
docker compose exec backend env | Select-String TRIAGE_PROVIDER
Invoke-RestMethod http://localhost:8000/api/meta/providers
```

Use a new complaint sentence when demonstrating the change. Results are cached for 24 hours by the SHA-256 hash of complaint text, so repeated text can legitimately return a cached result generated before the provider switch. Do not use `FLUSHALL` during a normal demonstration because Redis also holds the distributed rate-limit counters.

## Stop, reset, and recover

```powershell
docker compose down
docker compose up --build --detach --wait
```

The first command retains named volumes. Only use this destructive reset when you intentionally want to delete local data and models:

```powershell
docker compose down --volumes
```

## Preserve or inspect local data

The normal `docker compose down` command retains the `pgdata`, `redisdata`, and `ollama_models` named volumes. To inspect persisted complaints without exposing PostgreSQL on a host port:

```powershell
docker compose exec postgres psql -U civicpulse -d civicpulse -c "SELECT id, category, priority, status, triaged_by, created_at FROM complaints ORDER BY created_at DESC LIMIT 10;"
```

Before any intentional `down --volumes`, export a database backup if the data matters:

```powershell
docker compose exec -T postgres pg_dump -U civicpulse -d civicpulse > civicpulse-backup.sql
```

Do not commit the backup: it can contain reporter contact details.

## Production Compose checks

Set credentials and image variables in a deployment environment, then validate and start:

```powershell
docker compose --env-file .env -f compose.prod.yaml config
docker compose --env-file .env -f compose.prod.yaml up --detach
```

Production uses pre-built images and does not bind-mount source code. PostgreSQL and Redis deliberately have no host ports. To roll back after images are published, set `IMAGE_TAG` to the previous known-good tag and repeat the production `up --detach` command.

## Kubernetes deploy and rollback

Prerequisites are a local kind/k3d cluster, an nginx Ingress controller, metrics-server, and VPA CRDs/recommender. Build/load local images, then apply the development overlay:

```powershell
docker build -t civicpulse-backend:dev ./backend
docker build -t civicpulse-frontend:dev ./frontend
kubectl apply -k k8s/overlays/dev
kubectl -n civicpulse wait --for=condition=complete job/backend-migrate-seed --timeout=180s
kubectl -n civicpulse rollout status deployment/backend
kubectl -n civicpulse rollout status deployment/frontend
```

Read Kubernetes logs with `kubectl -n civicpulse logs deployment/backend --tail=200` or `kubectl -n civicpulse logs statefulset/postgres --tail=200`. The default Kubernetes provider is `rules`; before enabling Groq, replace the placeholder Secret using a secure deployment mechanism.

To roll back a failing deployment, use:

```powershell
kubectl -n civicpulse rollout undo deployment/backend
kubectl -n civicpulse rollout undo deployment/frontend
```

Run `kubectl -n civicpulse get hpa backend -w` alongside `k6 run -e BASE_URL=http://civicpulse.local load/k6-script.js` to capture actual HPA evidence. The complete local-cluster instructions are in [k8s/README.md](../k8s/README.md).
