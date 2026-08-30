---
summary: "AK 5209 record for making generated L1 validation compatible with agent-owned company policy."
read_when:
  - "Reviewing why existing L1 gates validate structure rather than canonical wording in company-owned paths."
type: "diary"
---

# AK 5209 — L1 agent-owned gate compatibility

## Trigger

Softwareco's fresh post-retirement refresh stopped at `check-template-ci.sh` because the generated gate required the birth-template phrase `AK CLI: ak <ak args...>` inside root `AGENTS.md`. AK 5187 deliberately classifies that file, plus README, CONTRIBUTING, `.gitignore`, company CI, and `docs/org/**`, as agent-owned and byte-preserved. Patching company policy to satisfy a stale generated assertion would have defeated the ownership membrane. Failure evidence remains AK evidence 7956; healthco was not started.

## Resolution

Generated L1 validation now treats fixed company-policy files as structural surfaces only: regular, readable, nonempty files. It no longer imposes birth wording, profile-derived document names, lane ignore lines, CI job labels, or README formatting on agent-owned paths.

A shipped stdlib lifecycle checker retains strong template-owned state validation:

- ownership schema/kind and active map digest;
- adopting attestation/evidence/hash binding;
- exact seven-field `applied_pending_receipt` shape and refresh marker;
- established marker and no lingering adoption attestation.

Canonical birth quality did not disappear: removed wording/profile assertions moved to L0 source/fixture/generation gates. Rich and compact organization-doc renders are now asserted directly at L0.

## Regression evidence

`tests/fixtures/l1-company-policy/` deliberately replaces AGENTS, README, CONTRIBUTING, `.gitignore`, company CI, and the entire `docs/org` shape with locally authored content lacking canonical birth markers. The ownership test proves those bytes survive refresh and the generated L1 gate passes. Brownfield tests separately prove adoption-attestation byte preservation and adopting lifecycle validation.

Focused validation before commit:

- `python3 -m unittest tests/test_l1_template_ownership.py` — 5 passed.
- `bash ./scripts/check-l0-guardrails.sh` — passed.
- `bash ./scripts/check-l0-generation.sh` — passed, including 10 behavior tests.
- Independent review `dispatch-1788077552711` — GO, no blockers.

## Rollback

Revert the scoped AK 5209 commit. Do not restore downstream canonical-content assertions without first changing the L1 ownership contract.
