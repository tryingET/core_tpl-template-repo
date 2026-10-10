---
summary: "AK6658: repair hosted L0 history, scratch isolation and documentation/AK fixture dependencies."
read_when:
  - "Reconstructing the PR11 hosted CI repair and its validation evidence."
type: "reference"
task_id: 6658
---

# 2026-10-04 — Hosted L0 CI dependencies

## What I Did

- Read the owner-supplied handoff fully; claimed AK6658 as this Pi session.
- Verified PR11 candidate `71dca023877efcf37ee902e57bc9a8a87806e473` and failed hosted
  run `37201539274`. Missing historical trees/retirement ancestry, docs-ref-check resolution,
  and the AK-5105 agent fixture existence lookup are observed failures.
- Changed only L0 CI/test infrastructure: full checkout history, external runner scratch, Node22,
  and a strict synthetic AK existence lookup. No template content, ontology pins or production
  ownership checks changed; no tests are skipped.
- The owner explicitly authorized public export of the docs-ref-check runtime from the private
  agent-scripts repo (AK evidence13587). Exported only seven committed runtime files, verified
  byte-identical to `d30dabe63500e8f0e2acc4c62f9458e22245fece`, with SHA-256 inventory.
  No CI credential or independent checker implementation is introduced.
- Added six guardrail tests for workflow provisioning, vendored hashes/import closure, synthetic
  AK refusal, the real creation-gate refusal, checker positive/negative controls, and resolution
  without a workspace checkout. Focused run: six tests passed.

## What Surprised Me

- Renderer failure was **not** caused by shallow history: with scratch inside the full-history
  L0 checkout, the existing rerender test fails with the exact hosted birth-root provenance
  message. With external scratch it passes (one test, 12.573s). Uninitialized destinations
  discover their parent's `.git`; the production refusal is correct.
- The completed-transition test already uses synthetic AK evidence. Its hosted stack failed on
  retirement ancestry, not a live-AK dependency. No skip or weakening was needed.
- `ak direction check` reports missing native direction nodes here. This is a pre-existing
  orientation gap, retained outside exact AK6658; no direction mutation was attempted.

## Verification / Publication

- Initial full native run at `e4ef582`: seven passed, none skipped, two existing Git re-init
  warnings (AK evidence13591). Independent inspection found no blockers at that candidate;
  its focused probes did not test global AK injection through the entire aggregate.
- Run `37203487549` refused before scheduling jobs: the initial job-level env referenced
  runner scratch. Moving env to step scope admitted run `37203603649` at `e1d7797`.
- That hosted attempt reached full-history tests but exceeded the 300s guardrail limit.
  Separately, the full local CI-environment run exposed global `AK_CMD` interference with
  generated CI's independent scratch-AK task-scope probes (five passed, two failed).
  Corrected to creation-subshell-only `L0_CREATION_AK_CMD` and bounded hosted limits of
  900s/1800s. These corrections preserve all tests and local installed-AK behavior.
- Full local CI-environment run at `f858356`: seven passed, none skipped, two existing warnings
  (AK evidence13606). Follow-up independent inspection reproduced the old injection failure
  and proved the nested scratch-AK simulator passes with the correction and no ambient AK calls.
- Hosted run `37204090540` at `f858356`: six passed, generation failed. Time limits suffice
  (guardrails398s, generation807s). Two company-ownership real-gate tests still relied on an
  ambient `ak` executable for the empty task-scope check. Explicitly injected their existing
  synthetic AK only into `ci/full.sh`, retaining actual entrypoint execution and nested-simulator
  independence. New full-gate positive/unsupported-scope refusal control and both previously
  failing tests passed locally (three tests,116.834s).
- The hosted optional real-core ROCS probe reports its pre-existing unavailable-workspace
  warning; no new skip is introduced. Local full runs still execute that optional probe.
- Final full native/hosted verification of the last correction remains pending at this capture
  point. Final run ids and exact heads belong in AK6658 evidence and an AK6648 coordinator update.
- CI repair is PR12. Owner retains merge authority; PR11 must include the CI repair
  before its hosted checks can pass. No admin merge bypass or main mutation is authorized.

## Patterns / Crystallization Candidates

- Hosted test harnesses must declare owner-tool dependencies and isolate temporary Git roots.
- CI doubles should accept only the precise fixture query and preserve negative gate tests.
- Durable regressions are encoded in `tests.test_hosted_ci`; reusable guidance is in
  `tools/agent-scripts/README.md`. No cross-owner knowledge promotion is claimed.

## Rebase onto main (2026-10-10)

- PR12 conflicted after PR10 (AK6351) and PR13 (AK6586) merged. Main's hosted push run
  `37414494666` at `f1e85e9` is green without this branch.
- Main already carries every repair from this session, in its own form, so the rebase
  dropped all of them (main's CI design kept unchanged):
  - full history: `fetch-depth: 0` in the `check`, `candidate` and `aggregate` jobs;
  - external scratch: `TMPDIR` set to runner temp at step scope and through `GITHUB_ENV`;
  - docs-ref-check: `tools/agent-scripts/` vendors the same seven files with identical
    SHA-256 hashes, pinned in `source-pin.json`, and `tests.test_hosted_ci` covers them;
  - no installed `ak`: synthetic `tests/fixtures/ak-creation-task.sh` is bound per birth
    in fixtures and generation, and company full-CI probes bind fixture AK;
  - time limits: main's defaults (1800s per leaf, 3600s generation) exceed the 900s/1800s
    hosted override proposed here; Node comes from the runner (needs >=18.2.0).
- Only this session record remains in PR12.
