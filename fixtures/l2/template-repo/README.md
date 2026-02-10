# fixture-product-repo

Generated L2 repository scaffold.

- Owner: `@repo-owner`
- Source: L1 template profile `template-repo`
- Vouch trust gate: **disabled**

## Quickstart

```bash
git init -b main
./scripts/install-hooks.sh
./scripts/ci/smoke.sh
```

Contribution workflow:
- [CONTRIBUTING.md](CONTRIBUTING.md)

## Baseline structure

This scaffold includes common working directories:
- `docs/`, `examples/`, `external/`, `ontology/`, `policy/`, `src/`, `tests/`

Git baseline files included:
- `.github/`, `.githooks/`, `.gitignore`, `.gitattributes`

## Recursion policy (explicit)

Current layer: **L2**

Allowed edge:
- `L1 -> L2`

Forbidden edges:
- `L2 -> L1`
- `L2 -> L0`
- any cycle

Answers-file policy:
- Keep `.copier-answers.yml` committed.
- Do not add nested Copier runs to `_tasks`.
