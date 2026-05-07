---
summary: "Session note: 2026 03 30 Review Full Adversarial Stack Followup."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 03 30 review full adversarial stack followup."
type: "reference"
---

# 2026-03-30 — Full adversarial stack follow-up

## What I Did
- Ran `./scripts/check-l0-guardrails.sh`, `./scripts/check-l0-generation.sh`, and `./scripts/check-l0-fixtures.sh` from repo root.
- Adversarially tested the shared Copier answers parser with multiline and escaped scalar values.
- Reproduced silent multiline fallback corruption in `preview-l1-diff.sh` and generated `new-repo-from-copier.sh` when PyYAML was unavailable.
- Reproduced live `governance/task-scopes/` deletion in generated `check-template-ci.sh` and false foreign-snapshot failures in symlinked repos.
- Implemented the nexus fixes: parser status preservation, explicit parse-error surfacing, canonical repo-path comparison for task-scope checks, and task-scope probe restore semantics in template CI.
- Re-ran `./scripts/check-l0-generation.sh` and `./scripts/check-l0-fixtures.sh` after propagating the fixes through template + fixture surfaces.

## What Surprised Me
- The repo had already crystallized the intended guardrail (“fail closed”) before the caller plumbing actually preserved parser failures.
- A single shell-status bug in the shared answers helper was enough to make both preview and descendant rendering silently lie while the suite stayed green.
- The most dangerous data-loss bug lived in validation code, not generation code: generated `check-template-ci.sh` deleted the whole task-scope directory after its own probe.

## Patterns
- Success-path checks cover canonical values well but need explicit degraded-runtime cases (`python` present but no PyYAML) to catch shell-fallback regressions.
- Shared helper extraction reduced duplication but also turned status-handling bugs into stack-wide failures across preview, rendering, and generated descendants.
- Repo-identity checks that compare raw path strings are brittle; canonicalization has to happen before any ownership assertion.

## Crystallization Candidates
- → docs/learnings/: updated the shared-parser learning with the completed fix set and the corrected fail-closed contract.
- → tips/meta/: add an adversarial checklist item for degraded dependency paths (for example: Python available, YAML module unavailable).
- → scripts/: keep extending regression coverage at the control-plane boundaries, especially for canonical-path and scratch-vs-live-state behavior.
