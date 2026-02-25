# 2026-02-24 — Legacy template path drift in L1 helper scripts

## What I Did
- Continued deep review and found stale `copier/template-repo` references in generated L1 helper scripts.
- Fixed `copier-template/scripts/install-hooks.sh` to target current templates (`copier/tpl-agent-repo`, `tpl-org-repo`, `tpl-project-repo`, `tpl-individual-repo`) instead of removed legacy path.
- Fixed `copier-template/scripts/ci/smoke.sh` nested-copier lint target from dead path to active configs (`copier.yml` and `copier/*/copier.yml`).
- Strengthened `copier-template/scripts/check-template-ci.sh` to assert:
  - no legacy path references,
  - install-hooks coverage for all current template script lanes,
  - smoke lane checks active config locations.
- Strengthened `scripts/check-l0-guardrails.sh` with equivalent L0 assertions so this class of drift cannot silently reappear.
- Added runtime coverage in `scripts/check-l0-generation.sh` to execute generated L1 `scripts/install-hooks.sh` and `scripts/ci/smoke.sh` before idempotency commit.
- Synced fixtures and re-ran full L0 checks.

## What Surprised Me
- `check-l0-generation` still passed because it never executes `scripts/install-hooks.sh`, so broken utility scripts could ship unnoticed.
- A dead path inside an `if grep ...` check can silently disable safety logic due non-match behavior.

## Patterns
- Topology migrations (`template-repo` -> `tpl-*`) require executable migration checks, not only directory absence checks.
- Utility scripts are high-risk drift zones because they are less frequently exercised than main generation paths.

## Crystallization Candidates
- -> `docs/learnings/2026-02-24-legacy-path-drift-needs-negative-and-positive-assertions.md`
- -> `tips/meta/` candidate: after structural renames, enforce both negative assertions (legacy path absent) and positive assertions (new paths actively referenced).
