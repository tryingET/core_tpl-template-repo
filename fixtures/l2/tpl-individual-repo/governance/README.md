# Project Work Items

This file tracks project-specific work (features, bugs, improvements).

## Ontology

```
Milestone > Issue > Task
```

## State Machine

```
triage → queued → doing → review → done
```

## Structure

| Field | Description |
|-------|-------------|
| `id` | Issue ID (e.g., `{{ repo_slug|upper|replace('-', '')[:8] }}-M1-01`) |
| `title` | Short description |
| `state` | `triage` \| `queued` \| `doing` \| `review` \| `done` |
| `tasks` | List of tasks with `text` and `done` |
| `dod` | Definition of done |

## Commands

```bash
# List runnable issues
jq '.milestones[].issues[] | select(.state == "queued")' governance/work-items.json

# Check invariants (if scheduler installed)
just fcos-check
```

## Program vs Project

| Type | Location | Scope |
|------|----------|-------|
| **Program** | governance-kernel/governance/programs/ | Cross-repo initiatives |
| **Project** | repo/governance/work-items.json | This repo only |

## Related

- State machine: `governance-kernel/governance/fcos/state-machine.yaml`
- Glossary: `governance-kernel/docs/core/glossary.md`
