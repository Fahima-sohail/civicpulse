# ADR 0001: Use a provider interface for triage

- Status: Accepted
- Date: 2026-09-25

## Context

CivicPulse needs a dependable default for development while also supporting a hosted LLM and an offline local model. Provider-specific networking, request formats, and failures must not leak into the complaint route.

## Decision

Keep provider selection in `backend/app/providers/triage/factory.py:7-13` and give every provider the same triage contract. The supported selections are deterministic rules, a simulated provider, Groq, and Ollama.

`TriageService` validates a provider response, caches it by a hash of complaint text for 24 hours, and falls back to deterministic rules when a provider fails (`backend/app/services/triage.py:23-54`). The API therefore remains available if Redis, Groq, or Ollama is unavailable.

## Consequences

- New providers can be added without changing API route behaviour.
- The selected provider and fallback outcomes are observable.
- Hosted providers may receive complaint text and location, so their use is governed by ADR 0004.
- A fallback can be less nuanced than a healthy model response, but predictable intake is preferable to rejecting a resident's report.
