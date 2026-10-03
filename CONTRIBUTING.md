---
summary: "Contributing."
read_when:
  - "Read when you need contributing."
type: "reference"
---

# Contributing

This repository is the **L0 source template** for AI Society (`L0 -> L1 -> L2`).

## Workflow

1. Create a feature branch.
2. Keep changes scoped and contract-safe.
3. Run full checks:
   ```bash
   bash ./scripts/check-l0.sh
   ```
   Finite wall-clock defaults: `1800` seconds for guardrails, the light checks,
   adversarial and fixtures; `3600` seconds for generation. Optional base override:
   ```bash
   L0_CHECK_TIMEOUT_SECONDS=120 bash ./scripts/check-l0.sh
   ```
   An explicit base override retains the historical generation multiplier of two.
   Per-lane overrides take precedence: `L0_CHECK_TIMEOUT_GENERATION_SECONDS`,
   `L0_CHECK_TIMEOUT_ADVERSARIAL_SECONDS`, `L0_CHECK_TIMEOUT_FIXTURES_SECONDS`.
   The runner still invokes `timeout`/`gtimeout`, fails on timeout, and aborts
   subsequent checks. No coverage is excluded to fit the budget.

   Calibration evidence: `diary/ak6351-verification-final/generation.json`
   records a successful `1653.568129274s` generation run; `adversarial.json`
   records a successful `367.709930772s` adversarial run; `guardrails.json`
   records the actual full guardrail leaf passing in `778.654000745s` (96 + 4
   tests and shell guardrails). An initial `1200s` owner attempt timed out in
   guardrails, so the earlier `661.065s` focused subset was not sufficient
   calibration. The new defaults allow approximately 2.18x generation and
   2.31x the measured full guardrail leaf, plus 50% above that failed cap,
   with larger margin for adversarial/fixtures. These are single-host
   verification budgets, not timing guarantees. Production birth/execution
   remains bounded at its unchanged `3600s` with its existing sandbox and
   process-group teardown; verification budgets are a separate concern.
   Hosted CI checks out full history (retirement and pinned-reader ancestry proofs),
   installs Bubblewrap and probes the real sandbox before checks. Ubuntu's AppArmor
   user-namespace admission is scoped to `/usr/bin/bwrap`, not disabled globally.
   Golden agent births bind a strict synthetic task-visibility executable through
   `AK_CMD` per invocation; no private AK runtime or workspace database is required
   by the test harness. Production creation gates remain unchanged.
   Documentation references use the byte-identical pinned owner bundle in
   `tools/agent-scripts/`; its source commit and file hashes are checked in guardrails.
   Hosted CI also provisions the public ROCS core at immutable commit
   `ac75e95e30d66b3543abca27cb79d69a9dc01e93` with its frozen lock, so the existing
   real-core integration probe executes instead of taking its no-core branch.
   Ownership tests bind their synthetic AK only for full CI; template CI keeps
   its own snapshot-capable fixture and is not overridden by ambient `AK_CMD`.
   Optional timing observation retains the full serial schedule and all assertions:
   ```bash
   profile_dir="$(mktemp -d)" # external TMPDIR; directory must stay private
   L0_PROFILE_DIR="$profile_dir" L0_PROFILE_CONDITION=serial bash ./scripts/check-l0.sh
   ```
   Unittest JSON preserves resolved IDs, subtests, outcomes, existing multiplicity,
   method timings and unassigned overhead; generation TSV records monotonic phase
   boundaries. Reports refuse source-tree, linked, public or retained output paths.
   Use a fresh profile directory per condition. This is measurement, not a passing
   substitute for checks or a performance guarantee.
4. Prefer deterministic wrappers over ad-hoc scripting:
   ```bash
   ./scripts/rocs.sh --doctor
   ./scripts/rocs.sh --which
   ./scripts/ak.sh --doctor
   ./scripts/ak.sh --which
   ```
   Use `./scripts/ak.sh` when template work touches repo-local AK tasks or the task-scope snapshot contract.
5. Capture session notes in `./diary/` (repo-local KES rule), then crystallize durable patterns into `docs/learnings/` and `tips/meta/`.
6. Update docs when behavior changes.
7. Open a PR with validation output.

## Required guardrails

- Do not introduce nested Copier runs inside template `_tasks`.
- Preserve recursion bounds (`L0 -> L1 -> L2`, no reverse/cycle).
- Keep `.copier-answers.yml` committed in generated repos.
- Keep baseline folder skeleton aligned where intended (`docs/`, `examples/`, `external/`, `ontology/`, `policy/`, `src/`, `tests/`) and document any intentional divergence.
- Keep fixtures in sync when template outputs change:
  ```bash
  bash ./scripts/sync-l0-fixtures.sh
  bash ./scripts/check-l0-fixtures.sh
  ```
- If you touch operator-facing helper scripts (`new-l1-from-copier.sh`, `preview-l1-diff.sh`, `migrate-l1-structure.sh`, `preflight-repo-census.sh`, lane bootstrap flows), run the adversarial suite directly too:
  ```bash
  bash ./scripts/check-l0-adversarial.sh
  ```

## Profile toggles note

This L0 now exposes optional profile toggles:
- `enable_community_pack` (issue templates / PR template / CoC / support docs)
- `enable_release_pack` (release-please / release-check / publish + release docs/scripts)
- `enable_vouch_gate` (vouch trust-gate workflows + `.github/VOUCHED.td`)

Defaults stay `false`; enable per repository governance/risk profile.
Policy references:
- `docs/profile-governance-policy.md`
- `docs/vouch-td-primer.md`
- `docs/feature-matrix-l0-l1-l2-vs-pi-template.md`
