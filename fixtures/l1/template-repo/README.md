# fixture-template-repo

This is an **L1 template repository** generated from `core/tpl-template-repo` (L0).

- Profile: `template-repo`
- Maintainer: `@template-owner`
- L1 organization docs profile: `rich`
- Default L2 organization docs profile: `compact`
- Default L2 archetype: `project`

## What this repo provides

- A Copier profile at `copier/template-repo` for generating L2 repositories.
- Opinionated local hooks (`.githooks/`) and CI lane scripts (`scripts/ci/`).
- Layer contract enforcement via `contracts/layer-contract.yml`.
- Baseline structure seed for generated repos: `docs/`, `examples/`, `external/`, `ontology/`, `policy/`, `src/`, `tests/`.
- Git hygiene files in generated repos: `.github/`, `.githooks/`, `.gitignore`, `.gitattributes`.

## Quickstart

Validate this L1 template repo:

```bash
bash ./scripts/check-template-ci.sh
```

Generate an L2 repository:

```bash
./scripts/new-repo-from-copier.sh template-repo /tmp/my-product \
  -d repo_slug=my-product \
  -d repo_archetype=project \
  -d org_docs_profile=compact \
  --defaults --overwrite
```

Install local hooks in a generated repo:

```bash
./scripts/install-hooks.sh
```

Contribution workflow:
- [CONTRIBUTING.md](CONTRIBUTING.md)

## Archetype profile

- L2 repos can be generated as `project`, `agent`, `org`, or `owned`.
- Set with: `-d repo_archetype=project|agent|org|owned`
- Defaults to `project` for backward compatibility with existing L2 usage.

## Organization docs profile

- This L1 repository currently ships **rich** organization docs in `docs/org/`.
- Generated L2 repositories default to **compact** via `scripts/new-repo-from-copier.sh` inheritance from `.copier-answers.yml` (`l2_org_docs_default`).
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
