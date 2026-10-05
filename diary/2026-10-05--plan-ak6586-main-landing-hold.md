---
summary: "Operator-approved PR10-first main landing preparation; native-wide remains mandatory and no merge is authorized before it passes."
read_when:
  - "Preparing or considering merge of the AK6586 fast-CI landing PR."
type: "session"
task_id: 6586
---

# 2026-10-05 — Prepare main activation, retain the native merge hold

The operator requested main landing, then explicitly selected:

1. Land the green PR10 first, then the performance changes.
2. Keep native-wide verification required before merging; prepare the landing PR
   meanwhile. No waiver, bypass or task completion is implied.

## Boundaries and current state

- Current main is `a9d2125e3d004cee3cafe2f2e57459f732d58dc0`.
- PR10 is open at `f4713a901f288054c4b858df3bae1f6f355054d9`, hosted check green.
  The performance branch includes its feature ancestry; direct main comparison
  covers305 files. The performance-only stack against PR10 has no production
  template, fixture, contract, ontology, policy or AGENTS/CLAUDE changes.
- Prepare a **draft stacked PR** against PR10's feature branch. After its eventual
  qualified merge, retarget the performance PR to main and verify the resulting
  merge commit. Do not merge either PR while the required native obligation lacks
  its qualified execution/proof.
- PR11 and PR12 remain untouched. The canonical checkout is on PR12's branch and
  contains unrelated decision157 notes; all edits use the isolated held checkout.
- GitHub reports main unprotected and no repository/parent rulesets. Do not assume
  a skipped legacy `check` context enforces candidate/aggregate success. This is
  a manual merge hold, not a branch-protection-settings change or bypass.

## Activation patch and checks

The old fast predicate was experimental-only. The landing patch enables it for
main pushes, the exact experimental push and all same-repository pull requests.
Foreign-fork PRs retain the complete serial fallback; local public serial checks
remain unchanged. Workflow triggers, permissions, six-worker/33-slot assignment,
provisioning, immutable pins, allocated runner paths and capture/aggregation
contracts are unchanged. Landing-branch pushes alone do not trigger a new run;
opening the stacked PR provides the actual pull-request activation test.

Only the three routing expressions and their existing contract bodies change;
method IDs/counts and raw subtest expectations stay fixed. Independent inspection
`dispatch-1791167586672` found no patch-level blocker; four focused tests passed.
The child fast modules passed49 tests in6.838s. This is not native or hosted
activation proof. Refresh source provenance before publication.

Prior measured candidate `fb26d63` passed in13m26s (AK13830). That result is not
silently attributed to the new activation/merge SHA. PR CI must be inspected at
its exact SHA; native-wide remains blocked on the workstation owner-qualified
route and must pass before merging. No automatic merge or task close.
