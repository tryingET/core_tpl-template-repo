# fixture-template-repo

This is an **L1 template repository** generated from `core/tpl-template-repo` (L0).

- Profile: ``
- Maintainer: `@template-owner`
- L1 organization docs profile: `rich`
- Default L2 organization docs profile: ``
- Default L2 archetype: `project`

## What this repo provides

- **L2 Templates**:
  - `copier/tpl-agent-repo/` — AI agent repositories
  - `copier/tpl-project-repo/` — Delivery projects
  - `copier/tpl-org-repo/` — Organization handbooks
- Opinionated local hooks (`.githooks/`) and CI lane scripts (`scripts/ci/`).
- Layer contract enforcement via `contracts/layer-contract.yml`.
- Baseline structure seed for generated repos: `docs/`, `examples/`, `external/`, `ontology/`, `policy/`, `src/`, `tests/`.
- Git hygiene files in generated repos: `.github/`, `.githooks/`, `.gitignore`, `.gitattributes`.
- **KES Infrastructure**: `tips/`, `governance/`, `metrics/` for knowledge evolution.

## Quickstart

Validate this L1 template repo:

```bash
bash ./scripts/check-template-ci.sh
```

Generate an L2 **agent** repository:

```bash
./scripts/new-repo-from-copier.sh tpl-agent-repo /path/to/agent-<slug> \
  -d repo_slug=agent-<slug> \
  -d agent_owner_handle=@<owner> \
  --defaults --overwrite
```

Generate an L2 **project** repository:

```bash
./scripts/new-repo-from-copier.sh tpl-project-repo /path/to/<project> \
  -d repo_slug=<project> \
  -d project_owner_handle=@<owner> \
  --defaults --overwrite
```

Generate an L2 **org** handbook:

```bash
./scripts/new-repo-from-copier.sh tpl-org-repo /path/to/<org>-handbook \
  -d repo_slug=<org>-handbook \
  -d org_owner_handle=@<owner> \
  --defaults --overwrite
```

Install local hooks in a generated repo:

```bash
./scripts/install-hooks.sh
```

Contribution workflow:
- [CONTRIBUTING.md](CONTRIBUTING.md)

## Knowledge Evolution System (KES)

This L1 participates in KES for compound learning:

```
tips/
├── _templates/tip.yml     # TIP genome
├── domain/                # Domain TIPs (local)
└── meta/                  # Meta TIPs (→ L0)

governance/README.md       # Review process
metrics/README.md          # Effectiveness tracking
```

**TIP Flow**: L2 learns → TIP proposed → review → merge → propagate

- Domain TIPs improve this L1
- Meta TIPs escalate to L0
- All L2 inherit improvements

See `tips/README.md` for TIP process.

## Archetype profile

- L2 repos can be generated as `project`, `agent`, `org`, or `owned`.
- Set with: `-d repo_archetype=project|agent|org|owned`
- Defaults to `project` for backward compatibility with existing L2 usage.

## Organization docs profile

- This L1 repository currently ships **rich** organization docs in `docs/org/`.
- Generated L2 repositories default to **** via `scripts/new-repo-from-copier.sh` inheritance from `.copier-answers.yml` (`l2_org_docs_default`).
- Override at L2 generation time with:
  - `-d org_docs_profile=compact`
  - `-d org_docs_profile=rich`

## Governance layering

L2 governance is archetype-dependent:
- `project` / `owned`: org baseline + `docs/project/governance_overlay.md` for local deviations.
- `org`: governance primary in `docs/org/` + `governance/`.
- `agent`: lightweight local governance in persona/system docs.

Default rule for `project`/`owned`: overlay may specialize/tighten org baseline; weakening requires explicit consent recorded in the overlay.

## Community profile

- Community collaboration pack is currently **disabled**.
- When enabled, this repo includes:
  - `.github/ISSUE_TEMPLATE/`
  - `.github/pull_request_template.md`
  - `CODE_OF_CONDUCT.md`
  - `SUPPORT.md`
- L2 generation inherits `enable_community_pack` from this L1 unless you override with `-d enable_community_pack=true|false`.

## Release profile

- Release automation pack is currently **disabled**.
- When enabled, this repo includes:
  - `.github/workflows/release-please.yml`
  - `.github/workflows/release-check.yml`
  - `.github/workflows/publish.yml`
  - `.release-please-config.json`, `.release-please-manifest.json`
  - `CHANGELOG.md`, `SECURITY.md`
  - `scripts/release/check.sh`, `scripts/release/publish.sh`
- L2 generation inherits `enable_release_pack` from this L1 unless you override with `-d enable_release_pack=true|false`.

## Trust-gate profile

- Vouch trust gate baseline is currently **disabled**.
- Files are scaffolded at `.github/VOUCHED.td`, `.github/workflows/vouch-check-pr.yml`, `.github/workflows/vouch-manage.yml`.
- L2 generation inherits `enable_vouch_gate` from this L1 unless you override with `-d enable_vouch_gate=true|false`.

## Recursion policy (explicit)

Current layer: **L1**

Allowed edges:
- `L0 -> L1`
- `L1 -> L2`

Forbidden edges:
- `L1 -> L0`
- `L2 -> L1`
- any cycle

Answers-file policy:
- Keep `.copier-answers.yml` versioned in git for reproducibility.
- Do not invoke nested Copier runs from `_tasks`.
