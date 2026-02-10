# fixture-template-repo

Generated L2 repository scaffold.

- Owner: ``
- Source: L1 template profile `template-repo`

## Quickstart

```bash
git init -b main
./scripts/install-hooks.sh
./scripts/ci/smoke.sh
```

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
