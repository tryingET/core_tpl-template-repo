# 2026-03-01 — tpl-project-repo deep review and contract consolidation

## What I Did
- Ran a deep-review pass on `copier-template/copier/tpl-project-repo/` with explicit INVERSION/TELESCOPIC/NEXUS framing.
- Authored a single canonical project-template contract doc:
  - `copier-template/docs/dev/tpl-project-repo-file-contract.md`
- Updated L0/L1 docs to point to the canonical contract and removed stale governance-overlay references:
  - `README.md`
  - `copier-template/README.md.jinja`
  - `copier-template/AGENTS.md`
- Cleaned accidental generated artifacts from template source:
  - removed tracked `__pycache__/*.pyc` from project-template vendored ROCS source
  - tightened `.gitignore` rules in repo + template surfaces
- Aligned project work-items contract stack:
  - `governance/work-items.cue`
  - `governance/work-items.json.j2`
  - `governance/README.md`
- Strengthened drift guardrails:
  - `scripts/check-l0-guardrails.sh`
  - `copier-template/scripts/check-template-ci.sh`
  - added checks for canonical contract link + generated artifact contamination
- Regenerated fixtures and validated end-to-end:
  - `bash ./scripts/sync-l0-fixtures.sh`
  - `bash ./scripts/check-l0.sh` (all checks green)

## What Surprised Me
- `tpl-project-repo` had accumulated tracked `.pyc` files in the template source even though L2 excludes existed.
- Work-items docs/schema/seed were semantically out of sync while still appearing "complete".
- L1 narrative still referenced `docs/project/governance_overlay.md`, which did not exist.

## Patterns
- Distributed documentation authority causes stale-path drift.
- Exclude-at-render-time is not enough; source trees still need hard anti-artifact checks.
- Schema presence != validation quality unless seed model and schema constraints are aligned.

## Crystallization Candidates
- → docs/learnings/: "single-source template contracts prevent topology drift"
- → docs/learnings/: "add anti-artifact assertions for template source trees"
- → tips/meta/: "L0 template changes should require explicit contract-doc linkage checks"
