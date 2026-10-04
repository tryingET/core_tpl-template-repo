---
summary: "AK6586 independent coverage checker, closed six-worker assignment and fast routing verification; not hosted adoption."
read_when:
  - "Using or changing AK6586 coverage accounting or the six-worker preparation."
type: "reference"
task_id: 6586
---

# Independent coverage and six-worker preparation

## Implemented and checked

The operator ordered: coverage checker, worker assignment, then fast synthetic
checks. Those steps were implemented in that order without a hosted launch.

- [Coverage checker](../../tests/ci_coverage.py): strict JSON data accounting.
- [Frozen inventory](../../tests/ci_coverage_inventory.json):235 root executions,
  two nested upgrades,401 exact raw subtests,11 separate shell obligations.
- [Closed assignment](../../tests/ci_schedule.json) and
  [routing helper](../../tests/ci_schedule.py):31 units across six workers.
- [Checker tests](../../tests/test_ci_coverage.py) and
  [routing tests](../../tests/test_ci_schedule.py):23 new fast contracts, selected
  by a separate owner guardrail cohort. Existing product cohorts stay unchanged.

The checker rejects missing/excess/duplicate/unknown methods and raw subtests,
invalid collection/execution/ordinal/status data, empty selector arguments,
fixture failures/skips, dirty or mismatched source, broken nested ownership,
and missing/duplicate/failed/unclean/command-mismatched shell receipts. Intentional
cross-cohort coverage remains separate; the nested upgrade suite remains inside
its ownership parent rather than an additional top-level execution.

The expected inventory comes from retained historical reports and explicit
source-inspected safety-net deltas, not the candidate's discovered results.
Three label-fix methods use their exact stable captures. One changed observer
truth table uses its ten passing raw subcases from the retained08f4de1 serial
profile; that full profile failed another method, so it is not relabelled green.
Literal raw suffix concatenation and provenance-reference aliases are lossless
compression, not parameter normalization or exclusion.

## Proposed assignment and estimates

| Worker | Closed units in order | Estimated total including allowances |
|---|---|---:|
| 1 | sample-shell, R5, SYS, planning |857.4s|
| 2 | UPG, profile-community, fixtures, seam |863s|
| 3 | adversarial, profile-compact, Wrapper, R4 |848s|
| 4 | PREP, profile-vouch, Safety, Gf, R2 |861s|
| 5 | REV, profile-release, FULL, R7, Mf |841s|
| 6 | R1, R3, APPLY, R6, R8, guardrails-static, doc-references, session-checkpoint, supply-chain |843s|

Aliases resolve to existing explicit selectors in the assignment. Gf preserves
module collection for dynamic reverse tests and imported observer tests; Mf uses
31 literal methods. Slow generation methods are separate units; the whole
24-minute generation Python cohort is never scheduled as one unit.

Each estimate includes proposed120s cold setup and30s aggregation allowances.
The validator fixes those allowances and refuses a planning budget above900s.
Overloaded workers cannot be made feasible by changing allowances to1ms.
These are estimates, **not a measured <=15-minute workflow**. Gf's selected-method
sums are33.934s /33.710s in retained conditions; its50s estimate includes an
allowance for imports, full-cohort unattributed overhead and new observer work.

## Read-only interfaces

Run preparation from the candidate repository root:

```bash
python3 -B tests/ci_schedule.py --worker 4
python3 -B tests/ci_coverage.py --input /path/to/retained-request.json
```

The coverage request contains exactly `expected_source_commit`, `profiles` and
`receipts`. The source SHA must be full and exact; each report/receipt must claim
that same source and an empty dirty-state list. Report packets retain the existing
unittest profile schema. Receipt envelopes bind a closed unit and exact canonical
command to a complete successful managed capture with clean process-group teardown.

Both CLIs produce JSON only and launch no processes. The routing helper's callback
API accepts an explicitly injected fake spy, stops at its first failure, and stops
before an unimplemented route. There is no default real execution backend.

## Proof limits and remaining obligations

The checker checks supplied records; it cannot authenticate their host provenance
or prove that supplied shell receipt assertions are truthful. Successful synthetic
accounting therefore keeps performance, product equivalence, host authenticity and
assertion-execution proof flags false. The assignment keeps `ready_for_hosted=false`.

The planned guardrails-static entrypoint is still absent. It must preserve all
original shell assertions and negative cases, without a broad skip flag or duplicate
Python execution, before a complete real candidate can run. Actual unit isolation,
serial/unit equivalence, cold hosted results and required native wide proof remain.
Local heavy-job admission has no confirmed repair; no retry or bypass is implied.

Fast checks cover schema/multiset mutations, routing/order/failure stops, low-budget
counterexamples, exact selector collection without running product fixtures, and
unchanged source budgets. Use the pinned Copier runtime for collection dependencies:

```bash
PYTHONDONTWRITEBYTECODE=1 uvx --from copier==9.11.1 python -B -m unittest \
  tests.test_ci_coverage tests.test_ci_schedule tests.test_ci_generation_units \
  tests.test_ci_reorder tests.test_ci_profile tests.test_hosted_ci tests.test_l0_check_timeouts
```

Reverting the scoped safety-net commit removes this preparation. No production
output, main/PR10 workflow, source admission or task completion was changed.
