# Evidence index

This folder contains screenshots captured while validating CivicPulse locally and in GitHub Actions. Each item is named for the behaviour it demonstrates.

## Docker Compose

| Evidence | What it demonstrates |
| --- | --- |
| `docker/all services healthy.png` | Frontend, backend, PostgreSQL, Redis, and Ollama are running and healthy. |
| `docker/network seperation 1.png` and `docker/network seperation 2.png` | The `edge` and `internal` Docker networks have the intended service membership. |
| `docker/database isolation proof.png` | The frontend cannot resolve or reach PostgreSQL directly. |
| `docker/backend dependencies.png` | The backend can resolve its internal PostgreSQL and Redis dependencies. |

## Kubernetes and scaling

| Evidence | What it demonstrates |
| --- | --- |
| `evidence k8s/kubernetes workloads running.png` | The workloads, Services, Ingress, HPA, and VPA are present. |
| `evidence k8s/k8s top nodes.png` | metrics-server is returning cluster resource metrics. |
| `evidence k8s/live HPA scaling.png` | The HPA scaled the backend from 2 to 4 replicas under load. |
| `evidence k8s/hpa-describe-successful-rescale.png` | The HPA recorded successful rescale events. |
| `evidence k8s/vpa recommendation.png` | The VPA recommender returned CPU and memory recommendations. |
| `evidence k8s/full k6 result.png` | The k6 test completed 37,723 successful requests with no failed checks. |

## CI

`evidence-ci-cd/ci-cd all tests passed .png` shows the pull-request CI suite passing: backend checks, frontend checks, container scanning, Compose smoke testing, and Kubernetes-manifest validation.

## Still to capture

Add browser screenshots for complaint submission, triage result, dashboard filtering/statistics, and a completed status update. Add the main-branch CD run and release evidence after those workflows have been run.
