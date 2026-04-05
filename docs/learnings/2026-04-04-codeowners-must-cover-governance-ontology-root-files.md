# CODEOWNERS Templates Must Cover All Governed Surfaces

**Date:** 2026-04-04
**Trigger:** Deep adversarial review found CODEOWNERS templates omitted `governance/**`, `ontology/**`, `AGENTS.md`, `README.md`, and `next_session_prompt.md`

## Pattern
When authoring CODEOWNERS templates for generated repos, the ownership coverage must match the actual governance surface. Every directory and root file that affects repo policy, ontology, or control-plane behavior needs an explicit ownership line.

Missing surfaces mean critical changes can be approved by anyone with write access.

## Checklist for L2 CODEOWNERS templates
- `governance/**` — work-items, task-scopes
- `ontology/**` — ROCS ontology sources
- `policy/**` — stack lanes, profile policy
- `scripts/**` — all deterministic tooling
- `AGENTS.md` — repo-level agent instructions
- `README.md` — repo identity
- `next_session_prompt.md` — session handoff

## Heuristic
After adding a new governed directory or root file to a template, add a corresponding CODEOWNERS line in the same commit. If the file is governance-sensitive, ownership must be explicit.
