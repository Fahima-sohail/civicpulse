# ADR 0004: Minimise data sent to external triage providers

- Status: Accepted
- Date: 2026-09-25

## Context

Complaint text and location can contain sensitive information. `reporter_contact` is stored in PostgreSQL (`backend/alembic/versions/0001_initial.py:35-45`) and must not be sent to a hosted model merely because it exists in the record.

## Decision

Use `rules` as the default provider. The local Ollama service supports offline triage. When Groq is explicitly enabled, the prompt contains the complaint text and location required for classification, but not `reporter_contact`. Access keys are supplied through environment variables, never committed.

## Consequences

- Operators must explicitly choose a hosted provider and provide a key.
- Groq use remains subject to its organisational approval, retention terms, and applicable privacy policy before real resident data is sent.
- Future work should add retention/deletion policy, access controls, and an auditable consent/data-classification process before a public deployment.
