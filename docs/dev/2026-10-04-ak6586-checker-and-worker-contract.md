---
summary: "AK6586 frozen coverage, static extraction and experimental six-worker contract; real candidate evidence pending."
read_when:
  - "Using or changing AK6586 coverage accounting or the six-worker preparation."
type: "reference"
task_id: 6586
---

# Independent coverage and six-worker preparation

## Implemented and checked

The operator ordered coverage accounting, assignment and fast checks, then
explicitly approved static extraction and the experimental worker/aggregation
candidate. Implementation is local; real clean-source candidate evidence is pending.

- [Coverage checker](../../tests/ci_coverage.py): strict JSON data accounting.
- [Frozen inventory](../../tests/ci_coverage_inventory.json):282 root executions,
  two nested upgrades,391 exact raw subtests,11 separate shell obligations.
- [Closed assignment](../../tests/ci_schedule.json) and
  [routing helper](../../tests/ci_schedule.py):33 slots across six workers.
- [Checker tests](../../tests/test_ci_coverage.py) and
  [routing tests](../../tests/test_ci_schedule.py):23 new fast contracts, selected
  by a separate owner guardrail cohort. Static/candidate cohorts add47 contracts;
  existing product cohorts stay unchanged.

The checker rejects missing/excess/duplicate/unknown methods and raw subtests,
invalid collection/execution/ordinal/status data, empty selector arguments,
fixture failures/skips, dirty or mismatched source, broken nested ownership,
and missing/duplicate/failed/unclean/command-mismatched shell receipts. Intentional
cross-cohort coverage remains separate; the nested upgrade suite remains inside
its ownership parent rather than an additional top-level execution.

The expected inventory comes from retained historical reports and explicit
source-inspected safety-net deltas, not the candidate's discovered results.
Three label-fix methods use their exact stable captures. The approved observer
truth table now uses direct assertions; its previous ten raw subcases and the
retained08f4de1 red profile remain recorded in the source bridge. No general raw
ID normalization or relabelling of that profile as green is permitted.
Literal raw suffix concatenation and provenance-reference aliases are lossless
compression, not parameter normalization or exclusion.

## Closed assignment and estimates

| Worker | Closed units in order | Estimated total including allowances |
|---|---|---:|
| 1 | sample-shell, R5, SYS, planning |857.4s|
| 2 | UPG, profile-community, fixtures, seam |863s|
| 3 | adversarial, profile-compact, Wrapper, R4, static-contracts |858s|
| 4 | PREP, profile-vouch, Safety, Gf, R2, candidate-contracts |871s|
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

Both preparation CLIs produce JSON only and launch no processes. The routing
helper's callback API accepts an explicitly injected fake spy and stops at first
failure. A separate [experimental backend](../../tests/ci_worker.py) executes one
closed slot per explicit call; [aggregation](../../tests/ci_aggregate.py) reads
correlated captures without rerunning units. See the
[local candidate update](2026-10-04-ak6586-local-candidate-contract-update.md).

## Proof limits and remaining obligations

The checker checks supplied records; it cannot authenticate their host provenance
or prove that supplied shell receipt assertions are truthful. Successful synthetic
accounting therefore keeps performance, product equivalence, host authenticity and
assertion-execution proof flags false. The assignment keeps `ready_for_hosted=false`.

The [static entrypoint](../../tests/ci_guardrails_static.sh) is present and its
actual focused shell command passes locally. Mechanical reconstruction preserves
all951 original lines/bytes and four original cohort calls; the public wrapper
adds only two fast contract calls. No skip flag or duplicate product Python run
is introduced. Real clean-source slot/candidate receipts, full isolation and
serial/unit equivalence, cold hosted results and required native wide proof remain.
Local heavy-job admission has no confirmed repair; no retry or bypass is implied.

Fast checks cover schema/multiset mutations, routing/order/failure stops, low-budget
counterexamples, exact selector collection without running product fixtures, and
unchanged source budgets. Use the pinned Copier runtime for collection dependencies:

```bash
PYTHONDONTWRITEBYTECODE=1 uvx --from copier==9.11.1 python -B -m unittest \
  tests.test_ci_guardrails tests.test_ci_worker tests.test_ci_aggregate \
  tests.test_ci_candidate_workflow tests.test_ci_coverage tests.test_ci_schedule \
  tests.test_ci_generation_units tests.test_ci_reorder tests.test_ci_profile \
  tests.test_hosted_ci tests.test_l0_check_timeouts \
  tests.test_company_ontology_ref_inheritance.WrapperTests.test_source_fixture_copies_and_budgets
```

Revert the local candidate commit to remove this slice. Default main's complete
serial command remains unchanged; only the explicit performance-branch candidate
path is prepared. No production output, source admission, hosted success or task
completion is claimed.
