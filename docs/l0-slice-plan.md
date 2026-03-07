# L0 slice plan — tpl-template-repo

## 1) Abductive pass (observed state from existing L1 repos)
From `holdingco` and `softwareco` company-root L1 repos, the stable baseline patterns are:
- `scripts/check-template-ci.sh` exists and validates template invariants by rendering a sample.
- `scripts/new-repo-from-copier.sh` wraps Copier invocation and standardizes answers file handling.
- `.github/workflows/template-check.yml` runs template checks on PRs and pushes.
- `.githooks/pre-commit` and `.githooks/pre-push` wire local smoke/full lanes.
- `scripts/install-hooks.sh` configures `core.hooksPath=.githooks`.

Inferred L0 requirement: the meta-template must generate L1 repos that already include these enforcement points.

## 2) Deductive pass (strict DoD + artifacts)
DoD for first slice:
1. L0 source has a valid `copier.yml`.
2. L0 source has `copier-template/` with required baseline files.
3. Generated L1 includes an explicit layer contract file.
4. L0 has smoke + idempotency tests for generation.
5. Generated L1 README/AGENTS contain explicit recursion policy.

Required validation outcomes:
- L0 guardrail script passes.
- Generated L1 sample passes `scripts/check-template-ci.sh`.
- L0 generation idempotency passes.

## 3) Contrapositive pass (failure modes -> guards)
Failure mode: recursion drift (L1 starts generating L0 or chaining cycles).
- Guard: explicit transition DSL + README/AGENTS recursion sections + grep checks in guardrail scripts.

Failure mode: template drift (required files removed silently).
- Guard: required-file checks in `check-l0-guardrails.sh` and generated L1 `check-template-ci.sh`.

Failure mode: supply-chain fragility (Copier unavailable or untrusted source).
- Guard: local/trusted Copier source (`--trust`), command fallback (`copier` / `uvx` / `uv tool run copier`), and CI execution.

## 4) DSL scaffolding
Contract schema: `ai-society.layer-contract.v1`
Core fields:
- `layer`
- `transitions.allowed`
- `transitions.forbidden`
- `answers_file_policy`
- `guardrails`

Canonical bounded policy:
- Allowed: `L0 -> L1`, `L1 -> L2`
- Forbidden: `L1 -> L0`, `L2 -> L1`, `cycle`

## 5) Inductive pass (smallest validated slice)
1. Build L0 Copier source with one L1 profile (`template-repo`).
2. Render one L1 sample and run its checks.
3. Verify idempotency by re-rendering into committed sample output.
4. Expand to org-specific flavors only after this baseline stays stable.
