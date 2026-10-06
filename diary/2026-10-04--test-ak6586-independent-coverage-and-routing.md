---
summary: "AK6586 ordered checker, six-worker assignment and fast synthetic proof; retained serial budget failure diagnosed and narrowly repaired."
read_when:
  - "Continuing AK6586 after the explicit 1-checker, 2-assignment, 3-synthetic-tests request."
type: "session"
task_id: 6586
---

# 2026-10-04 — Implement the safety net before the scheduler

## Ordered execution

The operator explicitly ordered: implement the independent coverage checker,
prepare the six-worker assignment, then run fast synthetic routing checks.
AK6586 was reclaimed by the same session after workspace DB preflight.

1. Implemented the pure read-only checker and its separately frozen inventory.
   Methods/subtests are compared by exact multiset/cohort/parent; shell obligations
   require distinct bound successful capture receipts. Expected values are not
   inferred from candidate collection. Synthetic input acceptance is not host
   authenticity or product execution proof; all such proof flags remain false.
2. Prepared31 closed units across six workers, splitting the long generation
   Python cohort by existing selectors. Nested upgrades stay within their parent.
   Unknown/duplicate/missing/misrouted units and source selector/runtime drift
   are rejected. Public/main scheduling is unchanged. Guardrails-static is still
   explicitly unimplemented, so no hosted-readiness claim is made.
3. Ran fast synthetic and collection-only checks, followed by existing fast
   regressions. No heavy/full/native/hosted run was launched.

## Current serial failure now observable

Run37207664622 at08f4de1 completed red with artifacts. The [serial capture](ak6586-verification-reset/run37207664622/command.json)
shows child exit1, complete output, no IO errors and clean process-group teardown.
The [losslessly encoded original log](ak6586-verification-reset/run37207664622/command.log.b64)
records six owner checks passing and guardrails failing: its script had953 lines
against the unchanged951 cap. The [selected events](ak6586-verification-reset/run37207664622/selected-events.json)
retain that failure plus the changed observer's ten passing raw subcases, with
an original-profile digest. This does not explain the older lost-runner attempt.
The log is base64 encoded because its original Git-diff whitespace fails the
repository whitespace check; bytes are preserved rather than stripped. Its
[encoding metadata](ak6586-verification-reset/run37207664622/command-log-encoding.json)
records the original filename, SHA-256 and round-trip check.

The narrow repair removes three non-executable lines and adds the separate fast
planning-cohort invocation, yielding951 lines. The limit remains951; original
product selectors are unchanged. Its isolated real static-budget test passes.
No full current-head hosted green or native-wide proof is inferred.

## Findings repaired, not concealed

- First synthetic collection run found a second source-inspected import-time Git
  HEAD probe. The fake is now restricted to the two actual read-only forms,
  returns metadata only, blocks other processes/fixtures and restores module/path
  state. It is not a substitute for running ownership lifecycles.
- Child timing proposal confused119 method membership with seconds and used a
  1,200-second planning budget. Parent checked raw timings: Gf selected methods
  sum33.934s /33.710s, proposes50s with overhead, and enforces <=900s budget.
- Independent inspection `dispatch-1791128621488` reproduced acceptance of empty
  profile selectors and lowered cold/aggregation allowances. Both are fixed;
  regressions include the overloaded971s worker disguised by1ms allowances.
  Focused independent recheck:2 passed in0.042s under pinned Copier9.11.1.
- The combined authored-test provenance digest uses declared order, each basename
  plus NUL followed by exact file bytes. Recipe and per-file digests are recorded
  in the inventory; it is an authorized delta relative to f3a7516, not an assertion
  that the added test files existed in that base commit.

## Verification and limits

- Initial23 new contracts plus isolated budget assertion:24 passed in0.389s.
- After inspection fixes:24 passed in0.355s.
- Existing fast suites:96 passed in14.642s before the final two-new-module fixes.
  Final combined rerun:120 passed in14.733s, including the isolated budget assertion;
  inspected terminal result is OK. No full owner/integration suite was run.
- All-worker dry-run accounts235 root methods, two nested methods,401 exact raw
  subtests and11 shell units. The extra23 root methods are new safety-net checks.
- Proposed worker totals including fixed120s setup /30s aggregation allowances:
  857.4,863,848,861,841,843 seconds. These are estimates, not measured timing.
- Required next work: real guardrails-static entrypoint, isolated unit execution
  and equivalence, complete candidate hosted proof, and native-wide proof when
  heavy-job admission is owner-confirmed repaired. No waiver or bypass.
- No push, new hosted run, merge, task completion, production/golden/policy/ontology
  change or source-owner adoption occurred. The unrelated full live-AK docs strict
  failure for the stale AK6133 handoff remains recorded under evidence13649.

See the [checker and worker contract](../docs/dev/2026-10-04-ak6586-checker-and-worker-contract.md)
for interfaces, estimates, limitations and rollback.
