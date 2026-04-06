---
summary: "Minimal ROCS CLI for ai-society, including commands, ref resolution, and CI profile behavior."
read_when:
  - "When using or vendoring rocs-cli"
  - "When checking supported commands or CI wrapper behavior"
---

# rocs-cli

Minimal ROCS CLI for ai-society.

Commands:
- `rocs version`
- `rocs rules [--json]`
- `rocs explain <rule_id> [--json]`
- `rocs resolve --repo . [--profile <name>] [--resolve-refs] [--json]`
- `rocs summary --repo . [--json]`
- `rocs validate --repo . [--profile <name>] [--resolve-refs] [--strict-placeholders] [--ruleset dev|strict]`
- `rocs validate --repo . [--validate-deps]` (optional: enforce strict schema on ref layers too)
- `rocs validate --repo . --only path|ref --layer <name>`
- `rocs diff --repo . --baseline <repo:...@ref> --resolve-refs [--profile <name>]`
- `rocs lint --repo . [--fail-on-warn] [--ruleset dev|strict]`
- `rocs check-inverses --repo . [--fix]`
- `rocs graph --repo . [--relation is_a] [--format excalidraw|excalidraw-cli-json|dot] [--json] [--out <path>]`
- `rocs cache dir|ls|prune|clear`
- `rocs normalize --repo . [--apply]`
- `rocs pack <ont_id> --repo . [--profile <name>] [--resolve-refs] [--json]` (`<ont_id>` may be a concept or relation id; fails closed if limits exclude the requested root doc)
- `rocs build --repo . [--profile <name>] [--resolve-refs] [--clean] [--json]` (fail-closed: refuses invalid ontology content and clears stale build artifacts before each run)

Scope (MVP):
- Validate ROCS repo structure + ontology front matter schema.
- Support both managed ontology layouts:
  - standard repo layout: `ontology/manifest.yaml`, `ontology/src/`, `ontology/dist/`
  - ontology-repo root layout: `manifest.yaml`, `src/`, `dist/`
- Build local artifacts into the managed `dist/` directory for the selected layout.
- Emit `authority-receipt.json` plus per-command `authority-receipt.<command>.json` artifacts inside that managed `dist/` directory for `build`/`validate` runs so local consumers can see authority mode and per-layer resolution sources without losing multi-step evidence.
- Resolve layered ontology refs from a local workspace only.

Layer refs (optional):
- Supported locator form: `<repo:<workspace-relative-project-path>@<ref>>`
  - example: `<repo:core/ontology-kernel@main>`
  - example: `<repo:softwareco/ontology@main>`
- Legacy `<gitlab:...>` locators are no longer supported.
- `--resolve-refs` enables resolving ref layers from the local workspace.
- Resolution source:
  1) workspace clone (offline)
- Workspace config:
  - `--workspace-root <path>` (or `ROCS_WORKSPACE_ROOT`): workspace root containing local clones (recommended: `~/ai-society`).
  - `--workspace-ref-mode strict|loose` (or `ROCS_WORKSPACE_REF_MODE`):
    - `strict` (default): use workspace only if `HEAD` matches the requested ref
    - `loose`: use workspace checkout even if it doesn’t match the requested ref
  - `repo:` locators bind by workspace layout, not remote origin URL.
- Diagnostics:
  - `--show-resolve-sources` adds `(source=workspace|path)` to `rocs resolve` / `rocs summary` text output.
  - `--show-resolve-details` adds workspace skip reasons in text output and includes per-layer `details` in JSON output.
- Selector contract:
  - Explicit selectors fail closed. If `--layer` names no declared layer, or `--only`/`--layer` together match nothing, commands return a non-zero error instead of silently operating on zero layers.
  - Each `rocs.layers[]` entry must declare exactly one of `path` or `ref`; mixed entries are rejected instead of silently preferring one.
- Dotenv loading (so you don’t need to `export` vars):
  - Highest priority: pass `--env-file <path>`.
  - Otherwise `rocs` auto-loads the first existing file from:
    - `ROCS_ENV_FILE`
    - `<repo>/.env` (where `<repo>` is `--repo`)
    - `holdingco/governance-kernel/.env` (when running inside the ai-society workspace)
- Cache location: `ROCS_CACHE_DIR` or `$XDG_CACHE_HOME/rocs` or `~/.cache/rocs`.
- Incremental doc/index cache (local-only): enabled by default; disable with `rocs --no-index-cache ...` or `ROCS_INDEX_CACHE=0`. Debug with `rocs --index-cache-debug ...` or `ROCS_INDEX_CACHE_DEBUG=1`.

Examples:
- `rocs resolve --repo . --resolve-refs --workspace-root ~/ai-society --workspace-ref-mode strict --show-resolve-sources`
- `rocs summary --repo . --resolve-refs --workspace-root ~/ai-society --json`
- `rocs diff --repo . --baseline <repo:core/ontology-kernel@main> --resolve-refs --workspace-root ~/ai-society`

AI Society convention (recommended):
- Set `ROCS_WORKSPACE_ROOT=~/ai-society`.
- Use `<repo:core/ontology-kernel@main>` and `<repo:softwareco/ontology@main>` in manifests for layered repos.
- Wire `scripts/ci/full.sh` into your preferred local gate runner (for example a Pi task or a git hook) instead of relying on remote ref fetches.

Graph export:
- `rocs graph` writes an `.excalidraw.json` file by default (open it in Excalidraw).
- For `excalidraw-cli` (external): use `--format excalidraw-cli-json`, then run `excalidraw-cli create <file> -o graph.excalidraw`.

Tests:
- `uv run python -m unittest discover -s tests -p 'test_*.py' -q`

CI profile wrapper (template-side policy contract):
- Script: `scripts/ci/full.sh`
- Layout note: ontology repos may live either at `ontology/` inside a normal repo or directly at repo root when the repo itself is the ontology container.
- Profiles via `ROCS_CI_PROFILE=local-dev|branch-ci|main-strict`
  - `local-dev`: offline-first default; runs `--only path` unless `ROCS_LOCAL_RESOLVE_REFS=1`, and that opt-in path enables `--resolve-refs` with workspace matching defaulting to `strict`
  - `branch-ci`: requires `--resolve-refs` and defaults workspace matching to `strict` (fail-closed)
  - `main-strict`: requires `--resolve-refs` and defaults workspace matching to `strict` (authoritative fail-closed gate)
- `ROCS_WORKSPACE_REF_MODE` remains an explicit override when a caller intentionally needs different behavior.
- This same wrapper is the recommended local hook/Pi entrypoint for pre-push or pre-merge checks.
- See `docs/ref-resolution-ci-strategy.md` for the architecture/policy rationale and migration guidance.
- Optional overrides:
  - `ROCS_CMD` (default: `uv run python -m rocs_cli`)
  - `ROCS_REPO` (default: `.`)
  - `ROCS_PROFILE` (optional manifest profile)

FCOS convergence scripts:
- `scripts/vendor-to.sh <target> [--version X.Y.Z] [--dry-run]`
  - syncs `pyproject.toml`, `README.md`, and `src/rocs_cli/` into `<target>`
  - writes/updates `<target>/VENDORED_HASHES.json` (hash coverage includes all files under `src/rocs_cli/`)
  - refuses targets that overlap the source repo tree or the source package tree
  - `--dry-run` uses the same preflight validation as apply mode
- `scripts/bootstrap-repo.sh <target> --class required|optional|ontology_repo [--company holdingco|softwareco|healthco] [--dry-run]`
  - class-based FCOS bootstrap (vendored `rocs-cli`, ontology scaffold, local gate wiring)
  - installs `scripts/ci/full.sh`, `.githooks/pre-push`, and `.githooks/README.md`
  - required repos default the generated pre-push hook to `ROCS_CI_PROFILE=local-dev`; ontology repos default to `main-strict`
  - generated hooks honor `ROCS_CMD` overrides and otherwise default to `uv run --project ./tools/rocs-cli python -m rocs_cli`
  - converges away legacy generated `gitlab/ci/rocs.yml` / `.gitlab-ci.yml` ROCS surfaces when present
  - emits a deterministic JSON report with `rollback_paths`
  - fails closed with a JSON blocker report when managed files are unreadable, not valid UTF-8, replaced by directories, or symlinked through managed paths
  - for ai-society workspace targets with ambiguous company ownership (for example `core/...`), pass `--company` explicitly instead of silently defaulting
  - blocker detection happens before vendoring/writes/chmod in apply mode
  - `--dry-run` validates and reports without writing files
- `scripts/audit-fleet.py --workspace-root <path> --policy <fleet-state.yaml> [--json [PATH]] [--markdown [PATH]] [--report-only]`
  - audits each policy ledger entry against observed capabilities (`rocs_cli_vendored`, `ontology_manifest`, `rocs_ci_gate`)
  - `rocs_ci_gate` checks concrete checked-in hook gate surfaces (`.githooks/pre-push` + `scripts/ci/full.sh` + explicit `ROCS_CI_PROFILE` call); template files and comments do not count as evidence
  - symlinked, unreadable, non-UTF-8, or otherwise blocked managed surfaces do not count as compliant evidence and are reported in scorecard evidence
  - manifest locator checks ignore commented migration notes and inspect live YAML values when possible
  - emits deterministic JSON/Markdown scorecards (stdout when PATH omitted)
  - stable exit codes: `0` pass, `2` required capability violations, `1` policy/usage error
- `scripts/open-remediation-batch.sh --input <audit.json> --mode patch|apply [--output [PATH]] [--workspace-root <path>]`
  - turns fleet-audit scorecards into deterministic remediation batches
  - recomputes repo targets from the authoritative workspace root instead of trusting scorecard `resolved_path`
  - may emit both a bootstrap action and a blocked manual follow-up for the same repo when file drift and declaration drift coexist
  - `patch` mode emits planned bootstrap/manual follow-up actions without mutating repos
  - `apply` mode runs `scripts/bootstrap-repo.sh` for bootstrap-managed required drift and records per-repo apply results
  - stable exit codes: `0` batch generated successfully or apply completed cleanly, `2` apply failures or blocked manual follow-up remains, `1` input/usage error
- `scripts/run-fleet-audit-nightly.py`
  - authoritative nightly control loop: runs the fleet audit, writes JSON/Markdown scorecards under `${XDG_STATE_HOME:-$HOME/.local/state}/fcos/nightly/<timestamp>/`, and emits a JSON `run-summary.json`
  - returns `0` only for `status=pass`; any detected drift or remediation outcome returns `2`; runtime/config failures return `1`
  - validates timestamps as `YYYYMMDDTHHMMSSZ`, clears stale remediation artifacts for reused run directories, and keeps `audit-only` decoupled from remediation-script availability
  - configure via `FCOS_WORKSPACE_ROOT`, `FCOS_POLICY_PATH`, `FCOS_AUDIT_ARTIFACT_ROOT`, `FCOS_REMEDIATION_MODE=audit-only|patch|apply`, optional `FCOS_BOOTSTRAP_SCRIPT`
- `scripts/run-fleet-audit-nightly.sh`
  - thin compatibility wrapper that executes `uv run python scripts/run-fleet-audit-nightly.py`
  - scheduling assets: `scripts/systemd/fcos-fleet-audit-nightly.{service,timer}` and `scripts/cron/fcos-fleet-audit-nightly.cron`

YAML tooling (optional, for shell-level policy inspection):
- Runtime YAML parsing in `rocs-cli` is already provided by `pyyaml`.
- Install CLI helpers via extras: `uv sync --extra tooling`
- Run query helper: `uv run --extra tooling yq --version`

Perf harness (synthetic, offline):
- `uv run python scripts/bench.py --cmd build --n-concepts 600 --runs 7 --out artifacts/perf/bench.json`
  - CI runs this as a non-gating job (artifact for trend visibility; allow_failure).

Exit codes:
- `0`: success
- `1`: error (invalid config/usage; schema/validation errors; malformed ontology content; internal errors)
- `2`: action required / partial success (e.g. `rocs normalize` changes needed; `rocs diff` breaking removals detected; `rocs pack` unknown ont_id)

JSON output:
- Prefer `--json` for machine output.
- When JSON output is selected, errors are emitted as `{"ok": false, "error": {...}}` and the process exits non-zero.

Lint (ruff):
- Tool pins: `scripts/tool_versions.json`
- Run: `uvx ruff==$(python -c 'import json; print(json.load(open(\"scripts/tool_versions.json\"))[\"ruff\"])') check .`

Type checking:
- Prefer `ty` (Astral). See `docs/ty.md`.

VHS recordings (documentation by recorded behavior):
- Install `vhs` (and its deps: `ttyd`, `ffmpeg`), then run: `core/rocs-cli/scripts/vhs-run.sh`
- Outputs land in `core/rocs-cli/artifacts/vhs/` (gitignored); share the `.gif` when reporting behavior regressions.
