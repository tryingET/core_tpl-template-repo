# Project Work Items

`governance/work-items.json` is the checked-in deterministic projection/mirror for this repository's Agent Kernel work-items state.

## Authority model

| Surface | Role | Authority |
|---|---|---|
| Agent Kernel work-items state | Live operational backlog for this repo | **Authoritative** |
| `governance/work-items.json` | Checked-in projection for review, diffs, and compatibility | Mirror only |
| `governance/work-items.cue` | Projection shape validation | Contract for the mirror |

Do not treat manual JSON edits as the live source of truth.
If you are migrating a legacy JSON-first repo, import once, then continue from AK and re-export the projection.

## Fresh-repo baseline

This template ships the empty projection that matches a fresh AK export for this repo identity.
That keeps `./scripts/ci/full.sh` honest: if `ak` is available, CI can validate drift immediately instead of silently skipping the check.

## Workflow

Diagnose AK resolution:

```bash
./scripts/ak.sh --doctor
./scripts/ak.sh --which
```

Bootstrap legacy JSON into AK (migration/import path):

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

`./scripts/ak.sh` derives stable `--owner` / `--project-name` defaults from `.copier-answers.yml`, so the projection stays reproducible even when the checkout folder name differs from the repo slug.

## Projection contract

Core fields:
- `schema_version`
- `updated_at`
- `owner`
- `project_name`
- `milestones[]`

Issue state machine:
- `triage -> queued -> doing -> review -> done`

Optional schema-only validation:

```bash
cue vet governance/work-items.json governance/work-items.cue
```

## Use this vs alternatives

| Use this projection when | Use alternative when |
|---|---|
| You need a reviewable, checked-in mirror of repo-local AK state | Work spans multiple repos/programs (use FCOS/L0 program models) |
| You are migrating legacy repo-local JSON work-items into AK | You only need lightweight conversational triage (use notes/issues) |

## Non-negotiable

- Do not leave deferred work as ad-hoc TODO comments or scattered markdown notes.
- Do not repair operational drift by hand-editing `governance/work-items.json` and pretending the JSON is authoritative.
- For legacy/manual JSON slices, import to AK and then export the projection back out.
