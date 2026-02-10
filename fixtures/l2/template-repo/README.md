# fixture-product-repo

Generated L2 repository scaffold.

- Owner: `@repo-owner`
- Source: L1 template profile `template-repo`
- Community pack: **disabled**
- Release pack: **disabled**
- Vouch trust gate: **disabled**

## Quickstart

```bash
git init -b main
./scripts/install-hooks.sh
./scripts/ci/smoke.sh
```

Contribution workflow:
- [CONTRIBUTING.md](CONTRIBUTING.md)

## Optional collaboration packs

When `enable_community_pack=true`, this scaffold includes:
- `.github/ISSUE_TEMPLATE/`
- `.github/pull_request_template.md`
- `CODE_OF_CONDUCT.md`
- `SUPPORT.md`

When `enable_release_pack=true`, this scaffold includes:
- `.github/workflows/release-please.yml`
- `.github/workflows/release-check.yml`
- `.github/workflows/publish.yml`
- `.release-please-config.json`, `.release-please-manifest.json`
- `CHANGELOG.md`, `SECURITY.md`
- `scripts/release/check.sh`, `scripts/release/publish.sh`

When `enable_vouch_gate=true`, this scaffold includes active vouch workflows and `.github/VOUCHED.td`.

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
