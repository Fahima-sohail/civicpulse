# CivicPulse runbook

This runbook covers the Docker Compose stack and the Kubernetes manifests in `k8s/`.

## Start and inspect the development stack

From the repository root:

```powershell
docker compose up --build --detach --wait
docker compose ps
```

The first start can take longer because Ollama downloads the configured model. Wait for all services to report healthy before testing the website at <http://localhost:5173>.

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

## Stop, reset, and recover

```powershell
docker compose down
docker compose up --build --detach --wait
```

The first command retains named volumes. Only use this destructive reset when you intentionally want to delete local data and models:

```powershell
docker compose down --volumes
```

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
