# 2026-02-24 — Legacy-path drift needs both negative and positive assertions

## Context
After migration from `copier/template-repo` to `copier/tpl-*`, deep review found helper scripts still referencing the removed path.

## Evidence
- `copier-template/scripts/install-hooks.sh` attempted to chmod files under `copier/template-repo/...`, causing runtime failure.
- `copier-template/scripts/ci/smoke.sh` grepped `copier/template-repo/copier.yml`; because file no longer exists, the nested-copier guard effectively became inert.
- Existing guardrails asserted legacy directory absence but did not assert helper scripts were updated to new topology.

## Pattern
Topology migrations can pass structural checks while operational scripts stay stale.

Negative checks alone (`legacy path absent`) are insufficient. You also need positive checks (`new topology actively referenced`).

## Guardrail
- Updated helper scripts to use active template topology:
  - `copier/tpl-agent-repo`
  - `copier/tpl-org-repo`
  - `copier/tpl-project-repo`
  - `copier/tpl-individual-repo`
- Added L1 CI assertions in `copier-template/scripts/check-template-ci.sh` for:
  - no legacy references,
  - full install-hooks coverage of current template lanes,
  - smoke checks against active copier configs.
- Added corresponding L0 guardrail assertions in `scripts/check-l0-guardrails.sh`.
- Increased runtime detection by executing generated L1 `scripts/install-hooks.sh` and `scripts/ci/smoke.sh` inside `scripts/check-l0-generation.sh`.

## Propagation
- Propagated: `tips/meta/tip-0004-executable-wrapper-contract-guardrails.md`.
