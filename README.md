# tpl-template-repo (L0)

`core/tpl-template-repo` is the **L0 meta-template** that scaffolds **L1 template repos**.

First validated slice:
- one L1 profile: `template-repo`
- generated L1 repos include CI, hooks, contracts, and five L2 templates (`tpl-agent-repo`, `tpl-project-repo`, `tpl-monorepo`, `tpl-package`, `tpl-org-repo`)

## Operator entrypoint (setup + transition)

If you need one doc for "how do I create repos" and "how do I transition old repos":
- `docs/dev/README.md`
- wikilink: `[[docs/dev/README.md]]`

## Canonical tpl-project-repo map

For the detailed L0 -> L1 -> L2 file contract (deep review + what goes where):
- `copier-template/docs/dev/tpl-project-repo-file-contract.md`
- wikilink: `[[copier-template/docs/dev/tpl-project-repo-file-contract.md]]`

## Quickstart

Generate an L1 repo from L0:

```bash
./scripts/new-l1-from-copier.sh /tmp/holdingco \
  -d repo_slug=holdingco \
  -d l1_org_docs_profile=rich \
  -d l2_org_docs_default=compact \
  -d enable_community_pack=false \
  -d enable_release_pack=false \
  -d enable_vouch_gate=false \
  --defaults --overwrite
```

Set `-d l1_org_docs_profile=rich|compact` to choose how much org structure L1 repositories ship.
Set `-d l2_org_docs_default=compact|rich` to choose the default org structure L1 templates use for L2 repositories.
Set `-d enable_community_pack=true` for public/community-facing collaboration intake.
Set `-d enable_release_pack=true` for release-please/publish automation baseline.
Set `-d enable_vouch_gate=true` for trust-gated template lines.

## Multi-pass template suffix policy (`.jinja` vs `.j2`)

This repository runs two Copier passes with different template suffixes:

- **L0 -> L1 pass** uses `_templates_suffix: .jinja` (`./copier.yml`).
  - Files under `./copier-template/` that should render in this pass must use `.jinja`.
- **L1 -> L2 pass** uses `_templates_suffix: .j2` (each `./copier-template/copier/*/copier.yml`).
  - Files under `./copier-template/copier/` that should render in this pass must use `.j2`.

Pass-boundary rule:
- never place `.jinja` templates under `./copier-template/copier/`
- never place `.j2` templates directly under `./copier-template/` (outside `./copier-template/copier/`)

`bash ./scripts/check-l0-guardrails.sh` enforces this boundary to prevent accidental cross-pass suffix drift and fails if nested L2 files contain Jinja markers without the `.j2` suffix.

## Pi local session flow

- Start session with: `read @next_session_prompt.md`
- End session with: `/commit` (project-local template at `.pi/prompts/commit.md`)
- Capture raw session notes in `./diary/` (repo-local KES rule)
- Crystallize via KES flow: `Session output -> diary/ -> docs/learnings/ -> tips/meta/`

## Deterministic ROCS launcher (agent-safe)

Use the wrapper instead of ad-hoc inline scripting:

```bash
./scripts/rocs.sh version
./scripts/rocs.sh validate --repo .
```

Resolution order (automatic):
1. explicit `ROCS_BIN`
2. vendored `./tools/rocs-cli`
3. this repo if it is `rocs-cli`
4. workspace core `~/ai-society/core/rocs-cli`
5. `rocs` on `PATH`

Diagnostics:

```bash
./scripts/rocs.sh --doctor
./scripts/rocs.sh --which
```

## Organization docs profiles (L1 vs L2)

- `l1_org_docs_profile=rich` (default): generated L1 repositories include a richer `docs/org/` structure for organization-level governance and strategy artifacts.
- `l1_org_docs_profile=compact`: generated L1 repositories keep only a compact org baseline.
- `l2_org_docs_default=compact` (default): generated L1 templates default generated L2 repositories to compact org docs + project execution docs.
- `l2_org_docs_default=rich`: generated L1 templates default generated L2 repositories to rich org docs as well.

Generated L2 repositories can still override with `-d org_docs_profile=compact|rich` at generation time.

## Community pack (optional by profile)

When `enable_community_pack=true`, generated L1/L2 repositories include:
- `.github/ISSUE_TEMPLATE/` issue forms
- `.github/pull_request_template.md`
- `CODE_OF_CONDUCT.md`
- `SUPPORT.md`

Defaults stay conservative (`false`) for internal/private template lines.

## Release pack (optional by profile)

When `enable_release_pack=true`, generated L1/L2 repositories include:
- release workflows (`release-please`, `release-check`, `publish`)
- release metadata (`.release-please-config.json`, `.release-please-manifest.json`)
- baseline release/security docs (`CHANGELOG.md`, `SECURITY.md`)
- release helper scripts (`scripts/release/check.sh`, `scripts/release/publish.sh`)

Defaults stay conservative (`false`) and should be enabled when repository governance requires release automation.

Run full L0 validations:

```bash
bash ./scripts/check-l0.sh
```

Optional focused checks:

```bash
bash ./scripts/check-supply-chain.sh
bash ./scripts/check-l0-generation.sh
bash ./scripts/check-l0-fixtures.sh
```

## Recursion policy (bounded)

Layer map:
- **L0**: `tpl-template-repo`
- **L1**: template repos generated from L0
- **L2**: product repos generated from L1 templates

Allowed edges:
- `L0 -> L1`
- `L1 -> L2`

Forbidden edges:
- `L1 -> L0`
- `L2 -> L1`
- any cycle

## Guardrails encoded in this repo

- `scripts/check-l0-guardrails.sh`: validates required artifacts + recursion policy + contract presence.
- `scripts/check-l0-generation.sh`: renders a sample L1 repo, runs its checks, and verifies idempotency.
- `contracts/layer-contract.yml`: canonical L0 contract DSL for layer transitions.

## Adoption + release operations

- Preview L1 adoption diffs (non-destructive):
  ```bash
  ./scripts/preview-l1-diff.sh /path/to/holdingco
  ./scripts/preview-l1-diff.sh /path/to/softwareco
  ```
- Contributing guide: `CONTRIBUTING.md`
- Release/compatibility policy: `docs/release-compatibility-policy.md`
- L1 rollout playbook: `docs/l1-adoption-playbook.md`
- L2 transition playbook: `docs/l2-transition-playbook.md`
- Profile governance policy (internal vs public bundles): `docs/profile-governance-policy.md`
- Supply-chain policy: `docs/supply-chain-policy.md`
- Vouch `.td` primer: `docs/vouch-td-primer.md`
- Feature matrix (AI Society L0/L1/L2 vs pi template): `docs/feature-matrix-l0-l1-l2-vs-pi-template.md`
- Solo-builder cadence: `docs/solo-builder-operating-cadence.md`
- L0 contribution workflow: `CONTRIBUTING.md`
- Refresh deterministic fixtures:
  ```bash
  bash ./scripts/sync-l0-fixtures.sh
  ```

## Structure baseline (L1 vs L2)

To reduce drift with richer template ecosystems:
- generated **L1 template repositories** seed baseline folders: `docs/`, `examples/`, `external/`, `ontology/`, `policy/`, `src/`, `tests/`
- generated **L1 template repositories** also seed git baseline files: `.github/`, `.githooks/`, `.gitignore`, `.gitattributes`
- generated **L2 repositories** are archetype/profile-specific (from `tpl-agent-repo`, `tpl-org-repo`, `tpl-project-repo`, `tpl-monorepo`, `tpl-package`) and do not all ship identical folder/git baselines; GitHub assets are profile-gated (`enable_community_pack`, `enable_release_pack`, `enable_vouch_gate`)

Use `fixtures/` plus `bash ./scripts/check-l0-fixtures.sh` for the exact rendered baseline contract.
