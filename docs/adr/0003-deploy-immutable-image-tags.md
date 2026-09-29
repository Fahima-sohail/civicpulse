# ADR 0003: Deploy versioned images, not local builds

- Status: Accepted
- Date: 2026-09-25

## Context

A production deployment must identify the exact backend and frontend code it is running. A `build:` instruction on the deployment host makes this harder to reproduce and can make a later rollback ambiguous.

## Decision

`compose.prod.yaml` accepts `${BACKEND_IMAGE}:${IMAGE_TAG}` and `${FRONTEND_IMAGE}:${IMAGE_TAG}` rather than building locally (`compose.prod.yaml:75-76` and `compose.prod.yaml:111-112`). The intended release process is to set `IMAGE_TAG` to the commit SHA produced by CI.

## Consequences

- Deployments and rollbacks can select a known image tag.
- Production requires a registry publishing step and environment variables for image names/tags.
- The current repository has not yet added the CI/CD workflow that publishes SHA tags; that remains a follow-up task.
