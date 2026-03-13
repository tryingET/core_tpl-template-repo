# Monorepo Work Items

`governance/work-items.json` is the checked-in deterministic projection/mirror for this monorepo's Agent Kernel work-items state.

## Authority model

| Surface | Role | Authority |
|---|---|---|
| Agent Kernel work-items state | Live operational backlog for this monorepo | **Authoritative** |
| `governance/work-items.json` | Checked-in projection for review, diffs, and compatibility | Mirror only |
| `governance/work-items.cue` | Projection shape validation | Contract for the mirror |

Do not treat manual JSON edits as the live source of truth.
If you are migrating a legacy JSON-first monorepo, import once, then continue from AK and re-export the projection.

## Workflow

Diagnose AK resolution:

```bash
./scripts/ak.sh --doctor
./scripts/ak.sh --which
```

Bootstrap legacy JSON into AK:

```bash
./scripts/ak.sh work-items import --repo . --path governance/work-items.json
```

Refresh the checked-in projection from AK:

```bash
./scripts/ak.sh work-items export --repo . --path governance/work-items.json
```

Check that the committed projection matches AK (used by `./scripts/ci/full.sh`):

```bash
./scripts/ak.sh work-items check --repo . --path governance/work-items.json
```

Optional schema-only validation:

```bash
cue vet governance/work-items.json governance/work-items.cue
```

## State machine

```
triage → queued → doing → review → done
```

## Program vs project/monorepo

| Type | Location | Scope | Authority |
|------|----------|-------|-----------|
| **Program** | governance-kernel/governance/programs/ | Cross-company | L0 scheduler / FCOS |
| **Program** | company-templates/governance/programs/ | Company | Planning only |
| **Monorepo** | repo/governance/work-items.json (this file) | This repo | AK authoritative; JSON is the projection |

## Non-negotiable

- Do not leave deferred work as ad-hoc TODO comments or scattered markdown notes.
- Do not repair operational drift by hand-editing `governance/work-items.json` and pretending the JSON is authoritative.
- For legacy/manual JSON slices, import to AK and then export the projection back out.
