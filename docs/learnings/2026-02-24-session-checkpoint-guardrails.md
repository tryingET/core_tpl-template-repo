# 2026-02-24 — Session checkpoint guardrails are control-plane quality gates

## Context
A deep review found that `next_session_prompt.md` had relative validation commands (e.g. `cd softwareco/...`) that fail from normal repo working directories while still appearing correct.

## Evidence
- Repro from repo root failed: `cd softwareco/tpl-owned-repo` (path not found).
- Session checkpoint carried high-confidence validation claims without a built-in rollback clause.

## Pattern
Session continuity docs act like executable runbooks; if command snippets are not root-safe and rollback-ready, trust degrades and replays fail.

## Guardrail
- Added `scripts/check-session-checkpoint.sh` to enforce:
  - root-safe validation commands,
  - explicit `just fcos-check` evidence,
  - explicit rollback command for mirror drift,
  - explicit KES crystallization flow.
- Wired the check into `scripts/check-l0.sh` and PR checklist.

## Propagation
- TIP candidate: **yes** — generalize this lint pattern for all session checkpoint templates and equivalent runbook mirrors.
