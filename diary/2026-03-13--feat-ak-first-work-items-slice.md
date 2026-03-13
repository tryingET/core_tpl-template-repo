# 2026-03-13 — AK-first work-items slice at L0

## What I Did
- Added a repo-local `scripts/ak.sh` wrapper to the L1 template surface and to the L2 `tpl-agent-repo`, `tpl-org-repo`, `tpl-project-repo`, and `tpl-monorepo` templates.
- Made `scripts/ci/full.sh` use `./scripts/ak.sh work-items check ...` whenever `governance/work-items.json` exists, removing the old silent skip keyed on `./crates/ak-cli/Cargo.toml`.
- Chose a clear failure mode when AK is unavailable: the wrapper now exits non-zero with an actionable message (`install 'ak' on PATH`, vendor `./crates/ak-cli`, or set `AK_BIN=...`).
- Made the wrapper derive stable `--owner` / `--project-name` defaults from committed `.copier-answers.yml`, so projection checks stay reproducible even when checkout directory names differ from repo slugs.
- Reframed `tpl-project-repo` docs and handoff guidance so Agent Kernel is authoritative and `governance/work-items.json` is the checked-in projection/mirror.
- Added the same AK-first repo-local work-items surface to `tpl-monorepo` (`governance/work-items.cue`, `governance/work-items.json`, updated README/governance docs).
- Changed template seed projections to match the empty AK export baseline (`updated_at=1970-01-01`, empty milestones), so fresh repos can pass AK drift checks immediately.
- Added regression guardrails in `copier-template/scripts/check-template-ci.sh` and `scripts/check-l0-guardrails.sh` to fail if template CI still gates on `crates/ak-cli/Cargo.toml` or if the new wrapper/doc surfaces disappear.
- Regenerated fixtures with `bash ./scripts/sync-l0-fixtures.sh`.
- Validated with `bash ./scripts/check-l0.sh`.

## What Surprised Me
- The most important missing piece was not just the CI gate; it was the seed shape. A JSON seed that did not match AK’s empty export would have made AK-first CI immediately noisy for fresh repos.
- Deriving projection defaults from `.copier-answers.yml` was the cleanest way to keep project identity stable without templating every CI script.
- `tpl-monorepo` docs already talked like repo-local work-items existed, so making that archetype actually ship the projection files was the most truthful fix.

## Patterns
- If a repo-local JSON file is supposed to be a projection, the template must encode that truth in three places at once: seed data, CI behavior, and operator docs.
- Silent dependency gates (`if local tool source exists then check, else skip`) create false-green integration theater; wrappers plus explicit failure messages are the safer pattern.
- For generated repos, committed answers files are a useful deterministic source for runtime defaults when path names are not stable identifiers.

## Crystallization Candidates
- → docs/learnings/: template rule for “authoritative DB state + checked-in deterministic projections” surfaces.
- → tips/meta/: prefer repo-local deterministic wrappers (`scripts/ak.sh`, `scripts/rocs.sh`) over raw tool invocations when generated repos need reproducible resolution behavior.

## Validation
- `bash ./scripts/check-l0-guardrails.sh`
- `bash ./scripts/check-l0-generation.sh`
- `bash ./scripts/check-l0-fixtures.sh`
- `bash ./scripts/check-l0.sh`
