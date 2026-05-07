---
summary: "Session note: 2026 02 24 Refactor Kes Repo Local Diary Contract."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 02 24 refactor kes repo local diary contract."
type: "reference"
---

# 2026-02-24 — Repo-local diary policy correction

## What I Did
- Switched diary policy to repo-local (`./diary/`) in L0 + L1 template docs.
- Migrated L2 archetype templates (`tpl-agent-repo`, `tpl-org-repo`, `tpl-project-repo`) from `docs/diary/` to `diary/`.
- Added guardrail assertions to enforce `diary/README.md` and reject legacy `docs/diary`.
- Updated TIP metadata/docs to reflect repo-local diary authority.

## What Surprised Me
- The prior policy had drifted across workspace notes and TIP artifacts, creating contradictory authority.

## Patterns
- Diary authority must live at the repo boundary to keep KES capture scoped and auditable.

## Crystallization Candidates
- → `tips/meta/` pattern: structural-template parity for KES primitives (`agent|org|project|individual`).
