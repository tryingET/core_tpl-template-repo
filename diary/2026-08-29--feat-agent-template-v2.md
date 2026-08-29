---
summary: "AK 5105 implementation record for source-first tpl-agent-repo v2."
read_when:
  - "Reviewing the manifest, compiled persona, ownership, or propagation contracts added by AK 5105."
type: "diary"
---

# AK 5105 — tpl-agent-repo v2

## Scope

Implemented the ratified L0 source-first agent template slice without mutating external L1 or L2 repositories. The checked-in L1/L2 fixtures are generated evidence mirrors. Five pre-existing operator-owned dirty paths were excluded from edits and staging.

## Delivered

- `ai-society.agent/1` manifest shell with required one-role and exact visible AK creation-task gates.
- Six agent-owned persona inputs compiled deterministically into a marked `docs/person/system-prompt.md`; generated full CI checks freshness and manifest validity.
- Two-category `contracts/template-ownership.yml` with fail-closed overlap and unknown-path handling.
- Plan-first `scripts/propagate-template.sh` that renders the current L1 source with tasks skipped, diffs template-owned paths, requires `--apply`, preserves agent-owned bytes, and refuses symlink escape paths.
- Source/L1-fixture/L2-fixture synchronization plus manifest, freshness, propagation, duplicate-input, unknown-task, ownership ambiguity, and symlink adversarial gates.

## Review-driven hardening

Independent review found and then verified fixes for two real hazards: destination-parent symlink escape during propagation and duplicate Copier data overrides bypassing the AK task gate. Both now have deterministic regression coverage.

## Focused evidence observed before commit

- `bash ./scripts/check-l0-guardrails.sh` — passed.
- `bash ./scripts/check-l0-generation.sh` — passed, including five agent-template behavior tests.
- `python3 -m unittest tests/test_agent_template_v2.py` — passed (5 tests).
- Shell syntax checks, task-only `git diff --check`, and source-to-fixture byte comparisons — passed.
- `bash ./scripts/check-l0-fixtures.sh` in the dirty operator worktree reports only the protected `copier-template/scripts/docs-list.sh` change propagating into the generated L1 fixture. Full clean-commit validation is therefore run from an isolated worktree after the scoped commit.

## Rollback

Revert the scoped AK 5105 commit. No external L1/L2 repository was mutated.
