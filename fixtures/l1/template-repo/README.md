# fixture-template-repo

This is an **L1 template repository** generated from `core/tpl-template-repo` (L0).

- Profile: `template-repo`
- Maintainer: `@template-owner`

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
  --defaults --overwrite
```

Install local hooks in a generated repo:

```bash
./scripts/install-hooks.sh
```

Contribution workflow:
- [CONTRIBUTING.md](CONTRIBUTING.md)

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
