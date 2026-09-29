# ADR 0002: Use relative frontend API paths and nginx proxying

- Status: Accepted
- Date: 2026-09-25

## Context

Vite environment variables are compiled into static browser assets. Embedding an environment-specific backend URL would require a new frontend image for each deployment and could accidentally expose configuration in client-side code.

## Decision

The frontend calls relative `/api/...` URLs. nginx proxies `/api/` to `http://backend:8000` (`frontend/nginx.conf:7-13`). The browser speaks only to the frontend origin; Docker service discovery stays inside the edge network.

## Consequences

- The same frontend image works in development and production.
- No API hostname or secret is baked into JavaScript.
- The proxy is a runtime dependency, so its health is checked as part of the frontend container.
