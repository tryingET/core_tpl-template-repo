# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start work immediately.
Do not ask for permission to begin.

## READ-FIRST ALLOWLIST (ONLY THESE, HARD)
1. `~/ai-society/holdingco/governance-kernel/governance/fcos/fcos-work-items.json` (canonical issue backlog + per-issue execution contracts)
2. `~/ai-society/holdingco/governance-kernel/governance/fcos/state-machine.yaml` (state machine authority)

Do not read `fleet-state.yaml`, `loops-registry.json`, or projection markdown during startup unless the selected issue contract requires them.

## EXECUTION CONTEXT PRE-FLIGHT (REQUIRED)
Use explicit root context so commands are runnable from any repo:

```bash
GK_ROOT=~/ai-society/holdingco/governance-kernel
[ -d "$GK_ROOT" ] || { echo "Missing $GK_ROOT"; exit 1; }
[ -f "$GK_ROOT/governance/fcos/fcos-work-items.json" ] || { echo "Missing FCOS canonical model"; exit 1; }
[ -f "$GK_ROOT/governance/fcos/state-machine.yaml" ] || { echo "Missing state machine authority"; exit 1; }
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
- start implementation in the selected issue's target repo, or
- ask one concise blocker question.

## AUTHORITY SPLIT (NON-NEGOTIABLE)
- Canonical issue IDs follow pattern `FCOS-M<milestone>-<issue>` (e.g., FCOS-M1-01, FCOS-M2-03).
- Canonical issue state authority: `~/ai-society/holdingco/governance-kernel/governance/fcos/fcos-work-items.json`.
- State machine authority: `~/ai-society/holdingco/governance-kernel/governance/fcos/state-machine.yaml`.
- Valid states: `triage | queued | doing | review | done`
- States requiring lease: `doing`, `review`
- Claimable states: `queued` only
- Canonical policy/state authority: `~/ai-society/holdingco/governance-kernel/governance/fcos/fleet-state.yaml`.
- Canonical loop/plugin extensibility authority: `~/ai-society/holdingco/governance-kernel/governance/fcos/loops-registry.json`.
- Human-readable projections (issue-set/PRD/views/loops/readmes) are derived artifacts only.
- This file's Session Checkpoint is a transient mirror for local continuity only; canonical model state wins on conflict.
- Program naming is `FCOS`; canonical issue IDs are `FCOS-*`.
- `ROCS` is reserved for the CLI/tool namespace (`core/rocs-cli`).

## STATE MACHINE
```
triage → queued → doing → review → done
                  ↓       ↑
                  └───────┘ (gate fail)
```

| State | Claimable? | Lease Required? | Meaning |
|-------|------------|-----------------|---------|
| `triage` | No | No | Not yet shaped |
| `queued` | Yes | No | Shaped, claimable |
| `doing` | No | Yes | In progress, leased |
| `review` | No | Yes | Work done, awaiting gate |
| `done` | No | No | Gate passed, immutable |

## EXECUTION MODE (ONE SESSION = ONE ISSUE)
Apply cognitive frameworks from `~/steve/prompts/prompt-snippets.md` (at minimum: INVERSION, TELESCOPIC, NEXUS, ESCAPE HATCH, KNOWLEDGE CRYSTALLIZATION) to the selected issue only; frameworks do not authorize extra discovery.
1. Parse `$GK_ROOT/governance/fcos/fcos-work-items.json`.
2. Pick the first issue where `state == "queued"` and dependencies are satisfied (lowest milestone first).
3. In multi-agent mode, claim the issue lease first (`just fcos-claim <ISSUE> <owner> <ttl_hours>`) and confirm `just fcos-check` is green.
4. Read only `issue.contract.context.read_first[]`.
5. If blocked by missing context, read only `issue.contract.context.read_if_blocked[]` (or file a Context Gap Note).
6. Execute that issue end-to-end (not partial planning only).
7. Run deterministic validation/acceptance checks.
8. Update canonical model(s) first, then refresh projections, then mirror here.
9. If claimed (and currently `state=doing` or `state=review` under your owner), release lease with explicit final state (`just fcos-release <ISSUE> <owner> <queued|done|review>`) and run `just fcos-check`.

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
   - `jq '[ .milestones[].issues[] ] as $all | ($all | map(select(.state=="done") | .id)) as $done | $all | map(select(.state == "queued")) | map(select((.depends_on // []) as $deps | ($deps | map(. as $d | ($done | index($d) != null)) | all))) | sort_by(.id) | map({id, depends_on, repo, lock_keys:.contract.lock_keys, parallel_mode:.contract.parallel_mode, read_first:.contract.context.read_first, read_if_blocked:.contract.context.read_if_blocked})' "$GK_ROOT/governance/fcos/fcos-work-items.json"`
   - `cd "$GK_ROOT" && just fcos-runnable`
   - `cd "$GK_ROOT" && just fcos-parallel`
   - `cd "$GK_ROOT" && just fcos-context <FCOS-ISSUE-ID>`
   - `cd "$GK_ROOT" && just fcos-claim <FCOS-ISSUE-ID> <owner> 4` (multi-agent mode)
   - `cd "$GK_ROOT" && just fcos-release <FCOS-ISSUE-ID> <owner> <queued|done|review>` (only for currently claimed issue)
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
  - `bash scripts/rocs/check-model-language-conformance.sh`
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
- Issue executed this session:
  - non-FCOS maintenance in `core/tpl-template-repo` (wrapper semantics hardening, L1 helper-path drift repair, baseline contract doc alignment, fail-fast check runner control).
- Outcome (repo-local mirror only; canonical FCOS model remains source of truth):
  - hardened Copier wrapper runtime precedence + explicit unpinned fallback warning in:
    - `scripts/new-l1-from-copier.sh`
    - `copier-template/scripts/new-repo-from-copier.sh`
    - `fixtures/l1/template-repo/scripts/new-repo-from-copier.sh`
  - fixed helper-wrapper contracts and runtime coverage:
    - `scripts/preview-l1-diff.sh` positional arg contract fixed
    - default `repo_slug` inference now reads target `.copier-answers.yml` before basename fallback
    - `scripts/check-l0-generation.sh` now executes generated L1 `install-hooks` + `ci/smoke` and validates `preview-l1-diff` no-diff runtime path
  - repaired legacy path drift in generated L1 helpers:
    - `copier-template/scripts/install-hooks.sh`
    - `copier-template/scripts/ci/smoke.sh`
    - `fixtures/l1/template-repo/scripts/install-hooks.sh`
    - `fixtures/l1/template-repo/scripts/ci/smoke.sh`
  - expanded deterministic guardrails:
    - `scripts/check-supply-chain.sh`
    - `copier-template/scripts/check-template-ci.sh`
    - `scripts/check-l0-guardrails.sh`
    - `fixtures/l1/template-repo/scripts/check-template-ci.sh`
  - tightened aggregator signal + fail-fast control in consolidated checks:
    - `scripts/check-l0.sh` warning parser now matches diagnostic prefixes
    - `L0_CHECK_TIMEOUT_SECONDS` added (default `180`, `0` disables timeout)
    - `CONTRIBUTING.md` updated with timeout usage
  - baseline contract wording aligned with rendered output:
    - `README.md`
    - `copier-template/README.md.jinja`
    - `fixtures/l1/template-repo/README.md`
  - KES capture + crystallization + propagation added:
    - diary entries under `diary/2026-02-24--*.md`
    - learnings under `docs/learnings/2026-02-24-*.md`
    - TIPs:
      - `tips/meta/tip-0004-executable-wrapper-contract-guardrails.md`
      - `tips/meta/tip-0005-diagnostic-prefix-contracts-for-check-aggregators.md`
      - `tips/meta/tip-0006-fail-fast-timeout-conventions-for-check-runners.md`
      - `tips/meta/tip-0007-readme-baseline-claims-must-map-to-render-axes.md`
  - canonical model/projection sync:
    - none (no FCOS model edits in this repo session)
- Validation run:
  - `L0_CHECK_TIMEOUT_SECONDS=120 bash ./scripts/check-l0.sh`
  - `cd "$GK_ROOT" && just fcos-check`
- Current priority (resolve live from canonical model):
  - `cd "$GK_ROOT" && just fcos-runnable | jq -r '.[0].id // "none"'`
- Next issue (resolve live):
  - `cd "$GK_ROOT" && just fcos-runnable | jq -r '.[0].id // "none"'`
- Lease/lock sync:
  - `cd "$GK_ROOT" && just fcos-runnable | jq -r '.[0].id // "none"'` resolved `FCOS-M3-02` during validation.
  - no FCOS lease claimed/released in this repo session.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md`
- KES crystallization flow:
  - `Session output -> diary/YYYY-MM-DD--type-scope-summary.md -> docs/learnings/YYYY-MM-DD-*.md -> tips/meta/tip-*.md`
- Blockers/risks:
  - none.

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).

`/commit` must:
- sync this file's Session Checkpoint,
- keep model-first authority ordering,
- keep `GK_ROOT`-safe command paths,
- create clear logical commit(s),
- include why + validation in commit body.
