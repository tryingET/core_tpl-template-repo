# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start work immediately.
Do not ask for permission to begin.

## READ-FIRST ALLOWLIST (ONLY THESE, HARD)
1. `~/ai-society/holdingco/governance-kernel/governance/fcos/fcos-work-items.json` (canonical issue backlog + per-issue execution contracts)

Do not read `fleet-state.yaml`, `loops-registry.json`, or projection markdown during startup unless the selected issue contract requires them.

## EXECUTION CONTEXT PRE-FLIGHT (REQUIRED)
Use explicit root context so commands are runnable from any repo:

```bash
GK_ROOT=~/ai-society/holdingco/governance-kernel
[ -d "$GK_ROOT" ] || { echo "Missing $GK_ROOT"; exit 1; }
[ -f "$GK_ROOT/governance/fcos/fcos-work-items.json" ] || { echo "Missing FCOS canonical model"; exit 1; }
```

## NEXUS GUARDRAIL (HARD) — EXECUTE-FIRST BUDGET GATE
Single highest-leverage intervention to prevent overreading:

Phase A (startup, required):
1. Max **8 tool calls**.
2. Max **500 lines read**.
3. Only targeted reads from the read-first allowlist.
4. Select issue first, then use its contract-defined read scope.

Context Gap Note (only if blocked in Phase A):
- missing fact/decision
- exact extra files needed (max 3)
- estimated extra lines

Phase B (only with Context Gap Note):
- Additional max **700 lines read** (absolute cap **1200** before implementation)
- Targeted reads only; no broad workspace scans

Forbidden before first implementation edit:
- workspace-wide discovery scans (`find`, broad `rg` from workspace root)
- broad file reads in non-target repos
- reads outside selected issue contract scope unless blocked and recorded in Context Gap Note

By end of Phase A, do exactly one:
- start implementation in the selected issue’s target repo, or
- ask one concise blocker question.

## AUTHORITY SPLIT (NON-NEGOTIABLE)
- Canonical issue status authority: `~/ai-society/holdingco/governance-kernel/governance/fcos/fcos-work-items.json`.
- Canonical policy/state authority: `~/ai-society/holdingco/governance-kernel/governance/fcos/fleet-state.yaml`.
- Canonical loop/plugin extensibility authority: `~/ai-society/holdingco/governance-kernel/governance/fcos/loops-registry.json`.
- Human-readable projections (issue-set/PRD/views/loops/readmes) are derived artifacts only.
- This file's Session Checkpoint is a transient mirror for local continuity only; canonical model state wins on conflict.
- Program naming is `FCOS`; canonical issue IDs are `FCOS-*`.
- `ROCS` is reserved for the CLI/tool namespace (`core/rocs-cli`).

## EXECUTION MODE (ONE SESSION = ONE ISSUE)
Apply cognitive frameworks from `~/steve/prompts/prompt-snippets.md` (at minimum: INVERSION, TELESCOPIC, NEXUS, ESCAPE HATCH, KNOWLEDGE CRYSTALLIZATION) to the selected issue only; frameworks do not authorize extra discovery.
1. Parse `$GK_ROOT/governance/fcos/fcos-work-items.json`.
2. Pick the first issue where `status == "todo"` and dependencies are satisfied (lowest milestone first).
3. In multi-agent mode, claim the issue lease first (`just fcos-claim <ISSUE> <owner> <ttl_hours>`) and confirm `just fcos-check` is green.
4. Read only `issue.contract.context.read_first[]`.
5. If blocked by missing context, read only `issue.contract.context.read_if_blocked[]` (or file a Context Gap Note).
6. Execute that issue end-to-end (not partial planning only).
7. Run deterministic validation/acceptance checks.
8. Update canonical model(s) first, then refresh projections, then mirror here.
9. If claimed (and currently `status=doing` under your owner), release lease with explicit final status (`just fcos-release <ISSUE> <owner> <todo|done>`) and run `just fcos-check`.

## TOKEN-EFFICIENT MODEL OPS (PREDEFINED)
Use structured model tooling first; avoid verbose file reads unless needed.

Available local tools (remember):
- `jq` (JSON query/patch)
- `yq` (YAML via jq wrapper, supports in-place edits)
- `uv run python` (preferred scripted transforms; fallback `python3`)
- `uvx` (ephemeral CLI tooling when needed)
- `node` (optional scripted transforms)

Predefined workflow snippets:
1. Targeted inspect first (no full-file scan):
   - `jq '[ .milestones[].issues[] ] as $all | ($all | map(select(.status=="done") | .id)) as $done | $all | map(select(.status == "todo")) | map(select((.depends_on // []) as $deps | ($deps | map(. as $d | ($done | index($d) != null)) | all))) | sort_by(.id) | map({id, depends_on, repo, lock_keys:.contract.lock_keys, parallel_mode:.contract.parallel_mode, read_first:.contract.context.read_first, read_if_blocked:.contract.context.read_if_blocked})' "$GK_ROOT/governance/fcos/fcos-work-items.json"`
   - `cd "$GK_ROOT" && just fcos-runnable`
   - `cd "$GK_ROOT" && just fcos-parallel`
   - `cd "$GK_ROOT" && just fcos-context <FCOS-ISSUE-ID>`
   - `cd "$GK_ROOT" && just fcos-claim <FCOS-ISSUE-ID> <owner> 4` (multi-agent mode)
   - `cd "$GK_ROOT" && just fcos-release <FCOS-ISSUE-ID> <owner> <todo|done>` (only for currently claimed issue)
   - `cd "$GK_ROOT" && just fcos-check`
2. Model edit (atomic):
   - `tmp=$(mktemp) && jq '<filter>' "$GK_ROOT/governance/fcos/<in>.json" > "$tmp" && mv "$tmp" "$GK_ROOT/governance/fcos/<in>.json"`
   - `yq -y --in-place '<filter>' "$GK_ROOT/governance/fcos/<in>.yaml"`
   - use `uv run python` for multi-field or cross-structure updates (fallback `python3`)
3. Re-render projections + run gates immediately after edits:
   - `cd "$GK_ROOT" && scripts/rocs/render-fcos-issue-set.py`
   - `cd "$GK_ROOT" && scripts/rocs/render-holdingco-projections.py`
   - `cd "$GK_ROOT" && scripts/rocs/render-loops-plugin-system.py`

Minimal read policy:
- Read only fields needed for the selected issue contract.
- Prefer canonical model files over projection markdown.
- Escalate to contract-declared `read_if_blocked` paths before any broader reads.

## ENDGAME MODE (CLOSEOUT BIAS)
- We are in late-stage convergence: avoid new side-quests.
- Prioritize the first runnable issue from canonical model (`cd "$GK_ROOT" && just fcos-runnable`) and activation of real modeling-language enforcement.
- Keep markdown as projection layer; move authority into models/contracts/policies.

## NON-NEGOTIABLES
- Control-plane authority remains in `holdingco/governance-kernel`.
- Deterministic checks are acceptance gates.
- In blocking enforcement stages, run strict model-language gate:
  - `FCOS_REQUIRE_MODEL_LANG_TOOLS=1 bash scripts/rocs/check-model-language-conformance.sh`
- Mainline-safe behavior: no irreversible actions without rollback path.
- `softwareco/owned/testers` is proving lane only, never policy authority.

## CURRENT PRIORITY (CANONICAL, DO NOT HARDCODE)
Resolve at runtime from canonical model:
- `cd "$GK_ROOT" && just fcos-runnable | jq -r '.[0].id // "none"'`
Use the returned issue ID for claim/execute/release; treat mirrored IDs in this file as non-authoritative.

## ANTI-DRIFT CADENCE (LAYERED)
- Required each session (cheap): resolve runnable issue once before claim/execute.
- Required at closeout: run deterministic gates (`just fcos-check`, drift checks, strict model-language gate where required).
- Optional periodic fleet loop (ops hygiene, e.g. every 15m):
  - `cd ~/ai-society/core/rocs-cli && uv run python scripts/audit-fleet.py --workspace-root ~/ai-society --policy ~/ai-society/holdingco/governance-kernel/governance/fcos/fleet-state.yaml --json /tmp/fcos-audit.json --markdown /tmp/fcos-audit.md --report-only`
- Canonical loop definition: `governance/fcos/loops-registry.json` seed plugin `loop.fcos.drift.audit` (projection: `docs/dev/loops-plugin-system.md`).

## SESSION CHECKPOINT (UPDATE BEFORE /commit)
- Issue executed: FCOS-M1-05 (done; lease released with explicit `status=done`)
- Outcome:
  - canonical mainline queue contract is now defined in `fleet-state.yaml` (`submit`, lock, deterministic gates, acceptance artifact, rollback semantics)
  - rollback command contract is defined per repo class (`required|optional|ontology_repo`)
  - queue MVP runner + canonical queue model added (`scripts/rocs/mainline-queue.py`, `governance/fcos/mainline-queue.json`)
  - acceptance artifact format is explicitly templated (`governance/fcos/templates/mainline-acceptance-artifact.template.json`)
  - model-language coverage extended for queue model (`mainline-queue.cue`) and wired into conformance gate
  - issue contract/projection updated to reflect completion (`FCOS-M1-05` tasks + validation + status)
- Major artifacts added/updated:
  - queue runner + checks: `~/ai-society/holdingco/governance-kernel/scripts/rocs/mainline-queue.py`, `~/ai-society/holdingco/governance-kernel/scripts/rocs/check-model-language-conformance.sh`, `~/ai-society/holdingco/governance-kernel/justfile`
  - canonical models/contracts: `~/ai-society/holdingco/governance-kernel/governance/fcos/fleet-state.yaml`, `~/ai-society/holdingco/governance-kernel/governance/fcos/mainline-queue.json`, `~/ai-society/holdingco/governance-kernel/governance/fcos/model-languages/contract/mainline-queue.cue`, `~/ai-society/holdingco/governance-kernel/governance/fcos/templates/mainline-acceptance-artifact.template.json`, `~/ai-society/holdingco/governance-kernel/governance/fcos/fcos-work-items.json`
  - docs/projections: `~/ai-society/holdingco/governance-kernel/docs/dev/mainline-cicd.md`, `~/ai-society/holdingco/governance-kernel/governance/fcos/README.md`, `~/ai-society/holdingco/governance-kernel/docs/dev/fcos-convergence-issue-set.md`
- Validation run:
  - `cd ~/ai-society/holdingco/governance-kernel && python3 -m py_compile scripts/rocs/fcos-scheduler.py scripts/rocs/mainline-queue.py scripts/rocs/render-fcos-issue-set.py scripts/rocs/render-loops-plugin-system.py`
  - `cd ~/ai-society/holdingco/governance-kernel && tmp_queue=$(mktemp) && cp governance/fcos/mainline-queue.json "$tmp_queue" && tmp_artifacts=$(mktemp -d) && python3 scripts/rocs/mainline-queue.py --fleet-state governance/fcos/fleet-state.yaml --queue-model "$tmp_queue" submit --batch-id dryrun-fcos-m1-05 --repo-path ai-society/holdingco/governance-kernel --repo-class optional --commit-range deadbeef..feedface --risk high --consent-ref FCOS-M1-05 && python3 scripts/rocs/mainline-queue.py --fleet-state governance/fcos/fleet-state.yaml --queue-model "$tmp_queue" process-next --dry-run --simulate gate-fail --artifact-dir "$tmp_artifacts" && jq -e '.rollback_proof.executed == true and .status == "rolled_back" and .lock_proof.lock_file == "governance/fcos/mainline-queue.lock"' "$tmp_artifacts/dryrun-fcos-m1-05.json" >/dev/null`
  - `cd ~/ai-society/holdingco/governance-kernel && scripts/rocs/render-fcos-issue-set.py --check`
  - `cd ~/ai-society/holdingco/governance-kernel && bash scripts/rocs/check-fcos-doc-drift.sh`
  - `cd ~/ai-society/holdingco/governance-kernel && bash scripts/rocs/check-holdingco-model-drift.sh`
  - `cd ~/ai-society/holdingco/governance-kernel && FCOS_REQUIRE_MODEL_LANG_TOOLS=1 bash scripts/rocs/check-model-language-conformance.sh`
  - `cd ~/ai-society/holdingco/governance-kernel && bash scripts/rocs/check-naming-boundaries.sh`
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-check`
- Next issue (resolve live): `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`
- Blockers/risks:
  - queue runner currently requires `yq` for fleet-state parsing; keep this available in execution environments.

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).

`/commit` must:
- sync this file’s Session Checkpoint,
- keep model-first authority ordering,
- keep `GK_ROOT`-safe command paths,
- create clear logical commit(s),
- include why + validation in commit body.
