---
summary: "Session note: 2026 03 30 Feat Ak Task Scope Agent Org Rollout."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 03 30 feat ak task scope agent org rollout."
type: "reference"
---

# 2026-03-30 — extend AK-native task-scope rollout to agent/org templates and fix task-id guidance

## What I Did
- Re-ran `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` and confirmed the runtime head still resolves to `FCOS-M36-04` for `core/tpl-template-repo`.
- Claimed `AK-621` and finished the remaining repo-local follow-up from the task-scope snapshot enforcement slice.
- Added generated `scripts/check-task-scope-snapshots.sh` helpers plus `scripts/ci/full.sh` enforcement for `tpl-agent-repo` and `tpl-org-repo`.
- Added lightweight governance/task-scope guidance for the agent/org templates so explicit AK task scope has a documented home at `governance/task-scopes/`.
- Standardized task-scope placeholder wording from the ambiguous `<AK-ID>` / `AK-<id>` forms to `TASK-ID`-based guidance across L0/L1/L2 docs and prompts.
- Extended the generated L1 template CI + L0 regression surface so agent/org repos are now covered end-to-end:
  - positive generated agent/org snapshot validation against a temp AK DB
  - rejection of foreign task snapshots in generated agent repos
  - rejection of drifted snapshot content in generated org repos
- Re-synced deterministic fixtures after the template/doc/check changes landed.

## What Surprised Me
- The generated agent/org templates already carried `scripts/ak.sh` and conditional work-item checks, so the missing part was mostly task-scope documentation + enforcement rather than AK wrapper plumbing.
- Adding the new agent/org runtime tests was cheap once the shared task-scope checker contract already existed for project/monorepo repos.

## Patterns
- Once repo-side AK artifacts are treated as frozen exports, the right rollout shape is: document the path, add a verifier, wire it into the full lane, then encode positive/negative regression cases.
- Placeholder language is part of the executable contract; if docs imply a value shape the CLI rejects, the wording itself becomes production debt.

## Validation
- `bash ./scripts/sync-l0-fixtures.sh`
- `bash ./scripts/check-l0-generation.sh`
- `bash ./scripts/check-l0.sh`

## Crystallization Candidates
- → docs/learnings/: task-id placeholder wording should be treated as part of the executable AK contract surface when repo guidance shells out to a strict CLI
- → tips/meta/: rollout pattern for repo-consumption exports = docs + checker + CI + adversarial regression cases
