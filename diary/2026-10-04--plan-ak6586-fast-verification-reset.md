---
summary: "Operator-approved AK6586 reset: no new baseline runs or blocking watches; independent inventory prepared."
read_when:
  - "Continuing AK6586 after the operator challenged long serial verification waits."
type: "session"
task_id: 6586
---

# 2026-10-04 — Correct the verification plan, not the timeout

## Operator decision

The operator challenged the 1,800-second waits and approved correcting the plan.
The structured response selected:

1. Let the existing serial condition finish without a blocking wait; inspect its
   artifact at the next checkpoint.
2. Fast edit loop only; no new hosted run until diagnosis and the complete
   six-worker candidate are ready.

This supersedes repeatedly launching serial/reverse characterization after
mechanical edits. It does not lower owner timeouts, omit checks, authorize
scheduler adoption against unexplained red, or grant merge/task completion.

## Work performed

- Rewrote the [CI speed plan](../docs/dev/2026-10-03-ak6586-ci-speed-plan.md) to a fast/targeted/complete
  verification ladder with explicit stability and stopping criteria.
- Prepared the [draft coverage inventory](../tests/ci_coverage_inventory.draft.json) from historical successful
  reports plus explicit new observer methods and the 19 seam-contract identities.
  Expected multiset at the declared revision: 212 roots and two nested methods.
  It is not candidate discovery, an enforced checker or execution proof.
- Captured the existing 19-method fast seam cohort under pinned Copier9.11.1:
  19 passed in0.707s; report source is clean `08f4de1`, wall0.745s. This provides
  the new cohort's identities, not actual product or scheduler equivalence.
- Corrected a timing interpretation: monotonic boundaries give sample163.539s
  plus other shell420.225s =583.764s proxy. This excludes context/pre-profile/cold
  setup and is not actual private-unit timing. The entire generation Python
  cohort is1,424.7s, so six selectable units cannot simply become six workers.
- Independent plan critique: `dispatch-1791124459936`. Its caveats about unknown
  serial failure, independent inventory, raw subtests, shell execution and
  checkpoint limits are retained in the revised plan. Its sample-shell estimate
  was corrected against the actual named phase boundaries, not accepted blindly.

## Limits and next step

Targeted tracked-reference checks pass for the changed plan and this diary; draft
inventory shape/count/dynamic/nested checks pass. Full docs-list metadata strict
check passes without live AK closure inspection. Enabling `DOCS_LIST_AK_ARGV`
revealed one unrelated existing failure: the project handoff for completed AK6133
has no supersession marker. It was retained, not repaired outside this scope; do
not claim the full live-AK docs strict check is green.

Run37207664622 was still in its serial condition at the last status read. No new
hosted run, long wait, local heavy-job attempt or scheduler deployment occurred
in this reset. The previous serial failure is still unexplained (evidence13620).

At a future checkpoint, inspect this existing run and its serial artifact. Diagnose
before scheduling changes; rerun only a named failing unit if needed. Implement
complete independent runtime accounting and safe Python-unit separation only
when that diagnosis permits the next executable slice. No15-minute result proved.
