# AGENTS.md — L1 template repo

## Intent
Provide one stable, guarded template surface that generates compliant L2 repositories and participate in KES (Knowledge Evolution System).

## Templates Provided

| Template | Purpose | Generates |
|----------|---------|-----------|
| `copier/tpl-agent-repo/` | AI agent repositories | `agent-<slug>/` |
| `copier/tpl-project-repo/` | Delivery projects | `<project>/` |
| `copier/tpl-org-repo/` | Organization handbooks | `<org>-handbook/` |

## Guardrails
- No secrets in git.
- Keep `.copier-answers.yml` committed.
- Run `./scripts/check-template-ci.sh` before merge.
- Keep `contracts/layer-contract.yml` in sync with README recursion policy.
- Preserve baseline structure folders and git baseline files unless intentionally changed by policy.
- Treat `l1_org_docs_profile` as a profile decision (default rich; compact allowed for lightweight internal template lines).
- Treat `l2_org_docs_default` as a profile decision (default compact; rich when L2 repos should carry full org docs).
- Keep L2 archetype explicit (`project|agent|org|owned`) and avoid changing archetype semantics without updating checks/fixtures.
- Keep L2 governance layering explicit:
  - `project|owned`: org baseline + `docs/project/governance_overlay.md`
  - `org`: governance primary in `docs/org/` + `governance/`
  - `agent`: local persona/system governance
- Treat `enable_community_pack` as a profile decision (default disabled, enable for public/community-facing contribution surfaces).
- Treat `enable_release_pack` as a profile decision (default disabled, enable where release automation is required).
- Treat `enable_vouch_gate` as a profile decision (default disabled, enable for trust-gated/public contribution surfaces).

## KES Infrastructure (Knowledge Evolution System)

This L1 participates in KES for learning propagation:

```
tips/
├── _templates/tip.yml     # TIP genome template
├── domain/                # Domain-specific TIPs (stay local)
└── meta/                  # Meta TIPs (escalate to L0)

governance/
└── README.md              # TIP review authority and consent model

metrics/
└── README.md              # Template effectiveness tracking
```

### TIP Flow

```
L2 learns → TIP proposed → L1 review → merge → propagate → L0 (if meta)
```

- **Domain TIPs**: Stay in this L1
- **Meta TIPs**: Escalate to `core/tpl-template-repo` (L0)
- **Infrastructure TIPs**: Escalate to L0

## Diary policy (repo-local, mandatory)

- Keep raw session capture in `./diary/YYYY-MM-DD--type-scope-summary.md` for this repo.
- Every generated L2 archetype must include the same root diary contract at `./diary/README.md`.
- Structural scope for KES diary parity: `tpl-agent-repo`, `tpl-org-repo`, `tpl-project-repo`, and `tpl-individual-repo` when introduced.

### Read Order for TIPs

1. `tips/README.md` — TIP process overview
2. `tips/_templates/tip.yml` — TIP structure
3. `governance/README.md` — Review authority

## Shared tooling
- Docs discovery/scoping: `./scripts/docs-list.sh --task "<task>" --top 8`
- Prompt read-scope allowlist: `./scripts/docs-list.sh --from-prompt <prompt-file> --paths-only --wikilink`
- ROCS command launcher (deterministic + portable): `./scripts/rocs.sh <rocs args...>`

## Deterministic tooling policy (ROCS-first)
- Prefer deterministic wrappers (`./scripts/rocs.sh`, repo `scripts/*`) over ad-hoc inline scripts.
- For ontology/policy checks, run ROCS before custom Python one-offs.
- Use inline Python only as an explicit escape hatch when no deterministic command exists.

## Recursion policy
Allowed:
- `L0 -> L1`
- `L1 -> L2`

Forbidden:
- `L1 -> L0`
- `L2 -> L1`
- any cycle
