---
summary: "Session note: 2026 03 30 Feat Ak Task Scope L0 Surface."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 03 30 feat ak task scope l0 surface."
type: "reference"
---

# 2026-03-30 — AK-native task-scope L0/L1 helper surface

## What I Did
- Claimed `AK-546` after the upstream `AK-545` dependency was reported complete.
- Bootstrapped a repo-local `./scripts/ak.sh` wrapper in `core/tpl-template-repo` so AK task operations in this repo now follow the workspace wrapper policy instead of calling raw `ak` directly.
- Updated the L0 repo docs (`README.md`, `AGENTS.md`, `CONTRIBUTING.md`) so this repo now teaches the deterministic AK wrapper and the AK-authored task-scope snapshot contract.
- Updated the generated L1 helper/docs surface in:
  - `copier-template/README.md.jinja`
  - `copier-template/AGENTS.md.jinja`
  - `copier-template/governance/README.md.jinja`
- Kept the new wording bounded and truthful:
  - AK authors explicit task scope
  - frozen `governance/task-scopes/AK-<id>.snapshot.json` files are repo-consumption exports
  - hand-authored `governance/task-scopes/AK-*.json` files are transitional scaffolding, not authority
- Re-synced the generated L1 fixture so the rendered docs stay in lockstep with the L0 template surface.

## Why This Slice Was Bounded
This session only handled the L0/L1 helper-contract surface for `FCOS-M36-04`:
- it did **not** yet propagate task-scope wording into each descendant L2 template surface (`AK-547`)
- it did **not** add new regression assertions beyond keeping the existing fixture render in sync (`AK-548`)

## Validation
- `bash ./scripts/sync-l0-fixtures.sh`
- `bash ./scripts/check-l0.sh`

## Files
- `scripts/ak.sh`
- `README.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `copier-template/README.md.jinja`
- `copier-template/AGENTS.md.jinja`
- `copier-template/governance/README.md.jinja`
- `fixtures/l1/template-repo/README.md`
- `fixtures/l1/template-repo/AGENTS.md`
- `fixtures/l1/template-repo/governance/README.md`

## Follow-up
- `AK-547` — propagate the AK-native task-scope wording/pattern into descendant template chains.
- `AK-548` — tighten regression checks around the new task-scope adoption surface.
