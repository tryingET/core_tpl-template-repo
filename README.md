# tpl-template-repo (L0)

`core/tpl-template-repo` is the **L0 meta-template** that scaffolds **L1 template repos**.

First validated slice:
- one L1 profile: `template-repo`
- generated L1 repos include CI, hooks, contracts, and a single L2 copier profile (`template-repo`)

## Quickstart

Generate an L1 repo from L0:

```bash
./scripts/new-l1-from-copier.sh template-repo /tmp/holdingco-templates \
  -d repo_slug=holdingco-templates \
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

## Pi local session flow

- Start session with: `read @next_session_prompt.md`
- End session with: `/commit` (project-local template at `.pi/prompts/commit.md`)

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
  ./scripts/preview-l1-diff.sh /path/to/holdingco-templates
  ./scripts/preview-l1-diff.sh /path/to/softwareco-templates
  ```
- Contributing guide: `CONTRIBUTING.md`
- Release/compatibility policy: `docs/release-compatibility-policy.md`
- L1 rollout playbook: `docs/l1-adoption-playbook.md`
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

## Structure baseline (L1/L2)

To reduce drift with richer template ecosystems, generated repositories now seed:
- folders: `docs/`, `examples/`, `external/`, `ontology/`, `policy/`, `src/`, `tests/`
- git baseline: `.github/`, `.githooks/`, `.gitignore`, `.gitattributes`

This is still a minimal L0 slice; deeper ecosystem-specific packs can be layered by profile.
