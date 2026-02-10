# fixture-template-repo

This is an **L1 template repository** generated from `core/tpl-template-repo` (L0).

- Profile: `template-repo`
- Maintainer: `@template-owner`

## What this repo provides

- A Copier profile at `copier/template-repo` for generating L2 repositories.
- Opinionated local hooks (`.githooks/`) and CI lane scripts (`scripts/ci/`).
- Layer contract enforcement via `contracts/layer-contract.yml`.

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
