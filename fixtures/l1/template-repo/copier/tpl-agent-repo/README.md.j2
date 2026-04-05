# tpl-agent-repo

L2 template for AI agent repositories.

## Purpose

Generate individual agent repositories with:
- Persona documentation (`docs/person/`)
- Activity prompts (`prompts/activities/`)
- Learnings capture (`docs/learnings/`)
- Decision records (`docs/decisions/`)
- Optional AK task-scope snapshots (`governance/task-scopes/`)
- CI baseline (`scripts/ci/`)

## Usage

From an L1 templates repository:

```bash
./scripts/new-repo-from-copier.sh tpl-agent-repo /path/to/agent-<slug> \
  -d repo_slug=agent-<slug> \
  -d agent_owner_handle=@<owner> \
  --defaults --overwrite
```

## Structure

```
agent-<slug>/
├── AGENTS.md              # Agent-specific instructions
├── docs/
│   ├── _core/             # Vendored governance (immutable)
│   ├── person/            # Persona definition
│   │   ├── identity.md
│   │   ├── main_task.md
│   │   ├── behavior_rules.md
│   │   ├── dream_goal.md
│   │   └── reason.md
│   ├── decisions/         # ADR-style decision records
│   ├── learnings/         # Captured learnings (TIP candidates)
│   └── system4d/          # System 4D context
├── diary/                 # Repo-local session capture (KES raw input)
├── governance/            # Optional AK task-scope snapshots + rules
│   ├── README.md          # AK task-scope snapshot guidance
│   └── task-scopes/       # Optional frozen AK task-scope snapshots
├── prompts/
│   └── activities/        # Domain activity prompts
├── policy/
│   └── do-not-touch.md    # Safety guardrails
└── scripts/ci/            # CI scripts
```

## Customization

- `repo_slug`: Agent identifier (e.g., `agent-triage`)
- `agent_owner_handle`: CODEOWNERS entry for agent paths
- `core_owner_handle`: CODEOWNERS entry for core paths
- `enable_community_pack`, `enable_release_pack`, `enable_vouch_gate`:
  inherited compatibility flags from the parent L1 profile; currently metadata-only in `tpl-agent-repo` (no extra file overlays)

## Optional explicit task-scope snapshots

When a repo-local AK task carries explicit scope, author/update that scope in AK and keep repo copies as frozen exports only:

```bash
./scripts/ak.sh task scope show <TASK-ID>
mkdir -p governance/task-scopes && ./scripts/ak.sh task scope export <TASK-ID> > governance/task-scopes/AK-<TASK-ID>.snapshot.json
```

Treat `governance/task-scopes/AK-<TASK-ID>.snapshot.json` as repo-consumption artifacts for operators/agents/CI, not as hand-authored authority. When snapshots are checked in, `./scripts/check-task-scope-snapshots.sh` and `./scripts/ci/full.sh` verify repo ownership + drift against live AK state.
If you are retiring a legacy `governance/task-scopes/AK-*.json` file, export the snapshot first, keep the legacy file only as temporary compatibility fallback, and remove it from the primary workflow once the snapshot checks pass. If the task stays on repo-default scope, do not invent either file.

## Validation

```bash
./scripts/check-task-scope-snapshots.sh # verify checked-in AK task-scope snapshots when present
./scripts/ci/full.sh                    # smoke + optional task-scope + ROCS checks
```

## ROCS command flow

Use deterministic wrapper commands before ad-hoc scripts:

```bash
./scripts/rocs.sh --doctor
./scripts/rocs.sh --which
```

If this repo includes ontology artifacts, run validation through the same wrapper.

## Knowledge Evolution

Agents capture raw sessions in `diary/` and crystallize durable patterns in `docs/learnings/`. Learnings that generalize should be proposed as TIPs:
- Domain learnings → L1 domain TIPs
- Meta learnings → L0 meta TIPs

See parent L1 `tips/` directory for TIP templates and process.
