# AI usage disclosure

Per the course's AI assistance policy: honest, specific attribution carries no
penalty. This document names the tools used, which parts of CivicPulse they
wrote or shaped, and what we changed afterwards and why.

<!--
Fill in every [bracketed] placeholder honestly before committing — this file
is only useful if it's accurate. Delete any row that doesn't apply to your
team, and add rows for anything not listed here (e.g. a specific ChatGPT
session, GitHub Copilot autocomplete, a different assistant). "Wrote" means
the AI produced the first version; "shaped" means it was a design discussion,
debugging session or review that changed something you wrote yourself.
-->

## Tools used

- **[Tool name and version, e.g. Claude Sonnet 4.6 via claude.ai]** — used by
  [team member] for [what kind of work, e.g. "debugging Docker networking",
  "reviewing branch/merge state", "drafting documentation"].
- **[Tool name]** — used by [team member] for [...].

## What AI wrote or shaped, by area

| Area | What AI did | What we changed afterwards |
|---|---|---|
| Backend (`app/routes`, `app/services`, `app/repositories`) | [e.g. "Wrote the initial state-machine transition table"; or "none — written by hand"] | [e.g. "Rewrote the 409 error message to match the exact contract wording"] |
| AI layer (`app/providers/triage/*`) | [e.g. "Suggested the retry/jitter pattern for LLMTriage; we wrote the prompt-injection delimiting ourselves"] | [...] |
| Frontend (`frontend/src`) | [...] | [...] |
| Docker / Compose | [...] | [...] |
| Kubernetes manifests | [...] | [...] |
| CI/CD workflows (`.github/workflows`) | [e.g. "Drafted ci.yml and cd.yml from the assignment's job table; we fixed the Trivy action version and the smoke-test URLs"] | [...] |
| Documentation (README, ADRs, RUNBOOK, ENGINEERING-NOTES, this file) | [e.g. "Drafted TRIAGE.md from our own provider code; drafted this file's structure"] | [e.g. "Filled in the actual tools, cache hit rate, and index justifications ourselves"] |
| Debugging / troubleshooting | [e.g. "Diagnosed a Docker Hub pull timeout, an unmerged branch, missing evidence files"] | n/a — advice, not committed code |

## What we did not use AI for

[e.g. "Neither of us used AI to write the eight ENGINEERING-NOTES.md answers
without independently understanding the trade-off first" — state whatever is
true for your team.]

## Why this is acceptable

Per the assignment: presenting AI-generated work as your own original work is
plagiarism; specific, honest disclosure is not. Everything above was reviewed,
tested, and can be defended by either partner individually at viva — that is
the actual bar, not who typed a given line first.
