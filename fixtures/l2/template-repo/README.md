# fixture-product-repo

Generated L2 repository scaffold.

- Archetype: `project`
- Owner: `@repo-owner`
- Source: L1 template profile `template-repo`
- Organization docs profile: **compact**
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

## Organization docs profile


- This repository currently uses **compact** org docs in `docs/org/`.
- Compact mode keeps org docs minimal and emphasizes execution docs.
- Rich mode adds purpose/mission/vision/governance artifacts in `docs/org/`.
- Optional canonical organization reference can be set via `-d org_docs_canonical_ref=<url-or-path>`.



## Governance layering


Governance in this scaffold uses a two-level model:
- **Organization baseline:** policy intent and non-negotiables in `docs/org/` and `docs/org_context/`.
- **Project overlay:** execution-level rules in `docs/project/governance_overlay.md`.

Project overlay rules should specialize or tighten org policy by default.
If a project needs to weaken an org control, record explicit consent in the overlay deviation register.


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
- `docs/`, `examples/`, `external/`, `policy/`, `scripts/`
- project runtime/code baseline: `src/`, `tests/`, `ontology/`
- governance overlay seed: `docs/project/governance_overlay.md`


Git baseline files included:
- `.github/`, `.githooks/`, `.gitignore`, `.gitattributes`, `CODEOWNERS`

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
