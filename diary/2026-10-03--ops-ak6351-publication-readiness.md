---
summary: "AK6351 publication readiness after integrating published AK6328 main: fresh full owner check 7/7, operator-authorized handoff subject metadata repair, and retained acceptance limits."
read_when:
  - "Preparing the AK6351 source PR or inspecting its final merged-main proof."
type: reference
---

# AK6351 — publication readiness

## Bound code and proof

The isolated `feat/ak6351-pinned-l0-births` branch incorporated only published
`origin/main`: first AK6333 at `72828ad`, then landed AK6328 PR9 at `a9d2125`.
No unpublished AK6328 source or other session's checkout was taken/reset.
The map retains both published company-owned ontology policy and reserved
`copier-overlay/**`; the initial Copier-birth map/state digests match the combined
map. Active company ownership state was not changed or fabricated.

Fresh clean-source verification on `d09eb66` passed the complete native owner
contract: **7 passed, 0 failed, 0 skipped, exit 0, 3277.560175 seconds**.
Raw evidence is retained in `diary/ak6351-published-main-integration/`, particularly
`full-owner-final.json` and `full-owner-final.log`. The earlier 40d2d05/01d3031
proofs cover their own source versions; they are not substituted for this rerun.
Later `de90f209` changes were evidence-only. Production execution, descriptor
binding, snapshots, immutable pins, positive completion and timeout teardown
remain intact. The owner-approved verification budgets stay finite at base
1800 seconds / generation 3600 seconds. Warnings are not relabelled as absent.

## One-line metadata authorization

The merged upstream handoff
`docs/project/2026-10-02-ak6133-system4d-handoff.md` had one docs-strict finding:
missing subject-task binding. Read-only owner confirmation established that
`task_id: 6133` is supported by the filename/body, live AK6133 and evidence11679;
that confirmation did not grant document-authoring or execution authority.

The operator separately answered the current-session form:

> Authorize this exact one-line metadata-only correction, then rerun docs strict

Added only `task_id: 6133` to frontmatter. All body and policy bytes remain
unchanged. This identifies the primary subject, not a document-authoring task,
and does not authorize acting on live AK6135 or changing its ownership/holds.
Repo-wide docs strict now passes; the default tool reports its AK closure check
skipped unless an explicit AK argv is supplied, so no closure reconciliation is
claimed from that pass. AK is still the lifecycle authority.

## Accepted boundaries and next admission

Operator evidence12202 remains the authority for the four obsolete project-only
birth omissions, finite verification-budget recalibration and the original eight
metadata repairs. The old exact-equivalence report remains unchanged/false.
New births do not restore GitLab CI pointing at retired vendored tooling or the
retired work-items projections. No exact fleet/index equivalence is claimed.

This is native source verification and publication readiness, not hosted-green,
a waiver, an AK task completion, or a company-wave release. Source publication
follows the repo's branch/PR process. Every per-company deleting wave still needs
its own operator release; AK6352 and AK6353 have not been executed in this slice.
The canonical checkout and all company checkouts remain outside this branch's
mutations. No worktree or ownerless state was deleted.
