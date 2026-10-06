---
summary: "AK6586 local static/experimental candidate contract; real clean-source and hosted evidence remain pending."
read_when:
  - "Packaging or checking the AK6586 local candidate and its proof limits."
type: "reference"
task_id: 6586
---

# Local candidate contract update

## Implemented scope

The [static entrypoint](../../tests/ci_guardrails_static.sh),
[worker](../../tests/ci_worker.py), [aggregator](../../tests/ci_aggregate.py) and
[experimental workflow](../../.github/workflows/l0-check.yml) are implemented
locally. This is packaging under parent delegation, not hosted adoption or task
completion. The parent retains the task claim; no qualified native owner route
is available. Default main still runs the complete serial owner command.

The source-map/seam contracts reconstruct all951 original lines and exact bytes
from `1b92011ad09a25eb2510468be5c9d0244dbf84b1`, SHA256
`8869dcb682ed6d6d5d6741820141b945a63f76bb5bf2cbad07f90115fca52bce`.
The public wrapper preserves all four original cohort calls and adds two fast
contract calls. Static extraction removes no original assertion or negative case;
it does not run the product Python cohorts again. To resolve the packaging EOF
whitespace failure without trimming preserved bytes, the static owner appended
exactly `# end of preserved guardrail source range` plus newline after helpers'
255 and context's42 mapped lines. The source-map ranges/hashes are unchanged;
the closed validator permits only those two exact non-executable end comments
and rejects missing, duplicate, altered or executable substitutes.

## Execution and transport contract

- Six independent workers cover33 closed slots. Each slot has a separate capture
  and immutable artifact upload before the next slot; aggregation follows workers.
  Failed slots stop later calls, without erasing already retained evidence.
- Existing per-unit capture deadlines remain1800/3600 seconds. The candidate job's
  60-minute deadline is not a new15-minute passing cap. Maximum cold/setup/aggregate
  estimate871s is planning only, not measured whole-workflow performance proof.
- Every unit and aggregate must match the exact same run, attempt, full source SHA,
  plan SHA256 and inventory SHA256; source must be clean before and after execution.
  Missing, duplicate, failed or mismatched slots cannot become green.
- File-only artifact transport requires a private `container.marker` containing
  exactly `l0.profile-container/1` plus newline, even for empty shell profile sets.
  It is indexed and hash-verified, not an optional directory placeholder. Download
  rejects links, nonregular/multilink files and foreign ownership before restoring
  private modes, without rewriting bytes. The reviewed marker/capture code stays
  intact.
- Immutable source-map and ROCS Git pins and artifact-action SHA pins are retained;
  Copier remains9.11.1 and uv0.12.22. No runtime/pin change accompanies packaging.
- Prewarming covers **only the outer pinned Copier**. Outer units use offline flags,
  but the unchanged production birth sanitizer drops those flags and supplies a
  fresh private cache. Nested births may still use the network. Neither this
  workflow nor the whole product lifecycle is claimed offline.

## Frozen accounting and bounded evidence

The [inventory](../../tests/ci_coverage_inventory.json) declares282 root executions,
two nested upgrades,391 exact raw subtests and11 shell obligations. Authorized-delta
provenance is refreshed from every declared current test source: planning's two
files and static/worker/aggregate/workflow's four files use declared-order UTF-8
basename + NUL + exact bytes; each file also has its own SHA256. The changed hosted
observer retains its standalone current-file hash. Labels, authoring-base roles,
expected IDs, aliases and shape are preserved, not rebuilt from candidate discovery.

Local packaging checks cover167 pinned fast tests including the isolated static
source-budget assertion, actual focused static shell execution, targeted docs
metadata/references, syntax/source/diff checks and component file budgets. Synthetic
transport/accounting checks are not real candidate execution, host authentication,
full product equivalence or cold timing evidence. Parent-reported prior evidence:
167 fast checks passed in21.151s; independent marker inspection's four tests passed
in1.005s. Packaging records its own results in the
[raw diary](../../diary/2026-10-04--test-ak6586-local-candidate-packaging.md).

Run37207664622 remains red (the historical953-vs-951 line-budget failure). Earlier
run37198379861's lost-runner cause remains unknown; no inference repairs that red.
The unrelated broad live-AK docs strict failure (stale6133 binding, evidence13649)
is retained, not fixed or waived by targeted docs success. Required native wide
proof remains blocked and unwaived; no heavy retry, full151/36 product suites,
native birth, hosted launch, publication, promotion or AK write is performed here.

Next: the parent checks a real nonheavy clean-source static slot and fast-contract
slot before deciding publication. Complete candidate receipts, same-source
serial/unit equivalence, cold whole-workflow wall time and runner minutes, and
lawfully admitted native wide evidence remain separate obligations.
