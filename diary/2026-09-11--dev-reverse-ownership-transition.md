---
summary: "Task5652: narrow receipted gitlink-to-ordinary-files transition and isolated lifecycle proofs."
read_when:
  - "Reviewing the reverse ownership topology transition or its validation limits."
type: "reference"
---

# 2026-09-11 — dev: reverse ownership transition

## Authority and scope

- Read task5652 JSON (claimed by parent session-01a05923-c39a-7caf-a44d-42586deb4720),
  target AGENTS, local engineering guidance, and compact engineering policy projection.
- This is independent L0 source-owner capability work. Decision157 is context only;
  no Softwareco, downstream consumer, live AK/DB/Decision, or registry mutation.
- No staging or commits in the source repository. Git commits, submodule operations,
  rollback, and authority records in tests are isolated TMPDIR fixtures only.

## What changed

- Extracted delta/path validation to `scripts/lib/l1_template_transition_delta.py`;
  the existing lifecycle engine imports it and remains below 500 lines.
- Added only this reverse ancestor exception: explicit parent `160000 -> 000000`,
  with strict descendants `000000 -> 100644|100755`. Present/absent OIDs and content
  digests still require the exact existing schema. Input order is immaterial.
- Existing forward collapse remains supported. Symlink/gitlink descendants,
  non-absent old descendants, other parent modes, and unrelated or descendant-to-
  descendant overlaps do not gain an exception. Noncanonical slash/dot path aliases
  are rejected rather than allowing normalization to obscure ancestor relationships.
- Added `tests/test_l1_template_reverse_transitions.py`; the existing named test
  module includes it via `load_tests`, so the current guardrails invocation exercises
  it without editing an out-of-scope gate script. Discovery does not double-load it.
- Generated checker and fixture/schema sources needed no changes. Agent-to-template
  adoption remains rejected; the reverse fixture changes an agent-owned exact path
  to an agent-owned subtree, not ownership authority.

## Observed validation

- Focused named suite: **17 tests pass**, including the 6 new reverse tests.
- Real local Git lifecycle: established forward v2 predecessor, deterministic reverse
  plan, exact staged reverse delta, pending commit, fixture receipt, state-only final
  commit, durable provenance, and execution of the generated history checker.
- Regular, executable, nested, and binary payloads verified; `.gitmodules` removal
  is explicitly planned. Apply's real atomic writes are checked to target only the
  two control files. No payload files are written by the lifecycle engine.
- Actual inverse rollback reverts final then pending commits and restores the entire
  predecessor Git tree and control bytes. A separate receipted forward inverse also
  passes through plan/apply/finalize and survives an ordinary later commit.
- Rejections cover ambiguous/unsafe overlaps, symlink payloads, malformed paths,
  modes/OIDs/digests, staged/untracked unplanned writes, forged staged bindings,
  missing/duplicate/weakened receipts, extra applied-commit writes, and non-state-only
  final commits. Rejected apply/finalize probes preserve both control files.
- Baseline sensitivity: replaying the complete reverse lifecycle test with HEAD's
  old validator fails at reverse planning with `ancestor-ambiguous git_delta paths:
  ontology, ontology/README.md`; the sensitivity harness reports expected rejection.
- Fixture receipt gate results are deliberately mocked authority data, **not evidence
  that the required consumer L1 gate commands were executed**.

## Full gate and residuals

- Direct `bash scripts/check-l0.sh` was **not run**: its adversarial leaf invokes
  `git worktree add --detach` at `scripts/check-l0-adversarial.sh:136`, which writes
  the source `.git/worktrees` registry outside this task's allowed effect scope.
- Safe leaves run individually: docs-reference, session-checkpoint, and supply-chain
  checks pass. Guardrails runs all 17 transition tests successfully, then fails:
  `error: template source contains generated python cache/metadata directories`.
- Observed residue: `copier-template/copier/tpl-agent-repo/scripts/lib/__pycache__`,
  directory timestamp 2026-08-31, predating this execution. It is outside task scope;
  no cleanup or fixture regeneration was attempted. These leaf results are not a
  passing full-gate substitute. Parent must handle residue and authorize a full-gate
  execution environment before acceptance.
- Protected tracked paths pass their before/after SHA-256 comparison; the source
  index listing is unchanged. Forbidden `.ontology/` was not traversed or changed.

## Evidence and budgets

Logs: `/home/tryinget/.local/state/pi-quests/tmp/task5652.O0VCjS/`:
`focused.log`, `baseline-sensitivity.log`, `full-gate-preflight.log`,
`check-l0-guardrails.log`, `cache-findings.log`, `safe-leaves-summary.log`, and
individual safe-leaf logs. Initial focused logs retain test-harness failures fixed
before the final passing run (forced fixture `.gitmodules` removal and initializing
its restored local submodule).

Source budgets: engine 449 lines / 25,523 bytes; delta helper 78 / 3,669.
Test budgets: existing module 358 / 19,300; new reverse module 326 / 17,344.
All are below their per-file budgets. Final whitespace/protection/budget checks are
recorded in `final-checks.log` in the same log directory.

## Crystallization candidates

The deterministic regression suite captures the reusable lesson: a topology-specific
ancestor exception must not become general overlap permission. No additional docs or
propagation surfaces are authorized by this task. Patch awaits independent parent review.
