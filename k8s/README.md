# Kubernetes deployment

The manifests use Kustomize with a shared `base` and `dev`/`prod` overlays. They deploy the backend and frontend at two replicas, PostgreSQL as a StatefulSet with durable storage, and Redis as a Deployment with a PVC. All four application services are internal `ClusterIP` services; the Ingress is the only HTTP entry point.

## Prerequisites

- Docker Desktop running
- `kubectl`
- A local kind or k3d cluster
- An nginx Ingress controller
- metrics-server for HPA metrics
- Vertical Pod Autoscaler CRDs and recommender for the VPA object
- k6 for the scale test

## Build and load local images for a kind cluster

```powershell
docker build -t civicpulse-backend:dev ./backend
docker build -t civicpulse-frontend:dev ./frontend
kind create cluster --name civicpulse
kind load docker-image civicpulse-backend:dev --name civicpulse
kind load docker-image civicpulse-frontend:dev --name civicpulse
```

Install an nginx Ingress controller, metrics-server, and VPA using their official installation instructions before applying the manifests. The VPA manifest is deliberately recommender-only (`updateMode: Off`); it needs its CRD to exist.

## Deploy the development overlay

```powershell
kubectl apply -k k8s/overlays/dev
kubectl -n civicpulse wait --for=condition=complete job/backend-migrate-seed --timeout=180s
kubectl -n civicpulse rollout status statefulset/postgres
kubectl -n civicpulse rollout status deployment/redis
kubectl -n civicpulse rollout status deployment/backend
kubectl -n civicpulse rollout status deployment/frontend
```

The committed Secret contains the literal placeholder `CHANGE_ME`; it is safe only for a disposable local cluster. Replace it through your deployment-secret process before any non-local deployment. The default provider is `rules`, so no hosted LLM key is needed to verify the stack.

Map the hostname to the local ingress address, then open `http://civicpulse.local`. For a simple local check without ingress, run `kubectl -n civicpulse port-forward service/frontend 8080:80` and open `http://localhost:8080`.

## Validate and load test

```powershell
kubectl kustomize k8s/overlays/dev
kubectl -n civicpulse get pods,svc,ingress,hpa,pdb,pvc
kubectl -n civicpulse get hpa backend -w
k6 run -e BASE_URL=http://civicpulse.local load/k6-script.js
```

Save the `get hpa -w` output and plot replicas against offered load for the assignment evidence. Do not claim a scale-out until metrics-server is installed and the output has been captured.

## Roll back and remove

```powershell
kubectl -n civicpulse rollout undo deployment/backend
kubectl -n civicpulse rollout undo deployment/frontend
kubectl delete -k k8s/overlays/dev
```

PVC deletion is intentionally separate from deleting the workloads. Delete claims only if you intend to remove local PostgreSQL and Redis data.
