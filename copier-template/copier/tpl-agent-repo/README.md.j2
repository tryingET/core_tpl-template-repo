---
summary: "README for generated agent repositories."
read_when:
  - "Read when changing generated tpl-agent-repo overview guidance."
type: "reference"
---

# tpl-agent-repo

L2 template for AI agent repositories: one repository per agent and one role per repository.

## Purpose

Creating a real agent requires an AK task naming the role, recurring pain removed, and differentiation from existing agents. The L1 render wrapper fails closed unless that exact task exists and is visible; the owner must review that its content satisfies those semantic requirements before rendering.

Generate individual agent repositories with:
- An `ai-society.agent/1` manifest (`agent.json`)
- Six agent-owned canonical persona inputs compiled into `docs/person/system-prompt.md`
- An explicit ownership contract (`contracts/template-ownership.yml`)
- Plan-by-default template propagation that never writes agent-owned paths
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
  -d agent_role=<role-card> \
  -d creation_task_id=AK-<TASK-ID> \
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
│   │   ├── reason.md
│   │   └── system-prompt.md  # compiled; do not edit
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
├── agent.json             # Agent-owned manifest values
├── contracts/template-ownership.yml # Explicit template/agent ownership map
└── scripts/               # Prompt compiler, propagation, and CI
```

## Customization

- `repo_slug` / `agent_name`: repository slug and canonical manifest name (for example `agent-triage`)
- `agent_role`: required single canonical role-card name
- `creation_task_id`: required AK creation task (`AK-<number>`)
- `system_prompt_file`: compiled prompt path (normally `docs/person/system-prompt.md`)
- `skill_profile`, `skill_extras`: published profile key plus a JSON array of extra skills
- `agent_tools`, `agent_extensions`: JSON arrays of runtime capability names
- `agent_model`, `agent_thinking`: runtime defaults; an empty model delegates selection
- `agent_scope`: JSON object describing advisory scope; it grants no authority
- `agent_owner_handle`: CODEOWNERS entry for agent paths
- `core_owner_handle`: CODEOWNERS entry for template-owned paths
- `enable_community_pack`, `enable_release_pack`, `enable_vouch_gate`:
  inherited compatibility flags from the parent L1 profile; currently metadata-only in `tpl-agent-repo` (no extra file overlays)

## Identity compilation

The six Markdown files listed in `docs/person/README.md` are agent-owned canonical inputs. Compile after changing any persona input or `agent.json`:

```bash
./scripts/compile-system-prompt.py
./scripts/compile-system-prompt.py --check
```

## Template propagation

A Copier render is for birth, not refresh. Refreshes render the current L1 template from `.copier-answers.yml` provenance and affect only paths marked `template_owned` in `contracts/template-ownership.yml`:

```bash
./scripts/propagate-template.sh          # plan and diff only
./scripts/propagate-template.sh --apply  # explicit application, then review git diff
```

Unknown or ambiguous ownership and symlinked destination ancestors fail closed. Preview renders use Copier's `--skip-tasks`, so template tasks do not execute during planning. Agent-owned bytes, including all persona inputs, the manifest, diary, learnings, decisions, and activities, are never changed by propagation.

## Optional explicit task-scope snapshots

When a repo-local AK task carries explicit scope, author/update that scope in AK and keep repo copies as frozen exports only:

```bash
ak task scope show <TASK-ID>
mkdir -p governance/task-scopes && ak task scope export <TASK-ID> > governance/task-scopes/AK-<TASK-ID>.snapshot.json
```

Treat `governance/task-scopes/AK-<TASK-ID>.snapshot.json` as repo-consumption artifacts for operators/agents/CI, not as hand-authored authority. When snapshots are checked in, `./scripts/check-task-scope-snapshots.sh` and `./scripts/ci/full.sh` verify repo ownership + drift against live AK state.
If you are retiring a legacy `governance/task-scopes/AK-*.json` file, export the snapshot first, keep the legacy file only as temporary compatibility fallback, and remove it from the primary workflow once the snapshot checks pass. If the task stays on repo-default scope, do not invent either file.

## Validation

```bash
./scripts/compile-system-prompt.py --check # verify generated identity is current
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
