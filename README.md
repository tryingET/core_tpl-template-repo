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
  --defaults --overwrite
```

Run L0 validations:

```bash
bash ./scripts/check-l0-guardrails.sh
bash ./scripts/check-l0-generation.sh
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
- Release/compatibility policy: `docs/release-compatibility-policy.md`
- L1 rollout playbook: `docs/l1-adoption-playbook.md`
- Solo-builder cadence: `docs/solo-builder-operating-cadence.md`
