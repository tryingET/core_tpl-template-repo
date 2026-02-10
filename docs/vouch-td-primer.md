# Vouch `.td` primer for AI Society templates

## What is a `.td` file here?
In this context, `.td` is a **plain text trust-data file** consumed by vouch workflows.

Example file name used by the reference template:
- `.github/VOUCHED.td`

It is not a universal standard format by itself; it is repository policy data for the vouch actions.

## Typical content
- `github:<handle>` -> vouched/trusted contributor
- `-github:<handle>` (or denounce action) -> blocked contributor
- `# ...` -> comments/metadata

## Where it is used
In `~/programming/pi-extensions/template`, vouch trust gating is implemented with:
- `.github/VOUCHED.td`
- `.github/workflows/vouch-check-pr.yml`
- `.github/workflows/vouch-manage.yml`

## AI Society L0/L1/L2 stance
Current state in `core/tpl-template-repo`:
- vouch baseline files are scaffolded for generated L1/L2 repos
- activation is controlled by `enable_vouch_gate` (default: `false`)
- recursion/layer contracts and fixture/supply-chain controls remain enforced

Recommended layering:
- **L0**: keep vouch optional and policy-driven by profile/risk level
- **L1**: expose/propagate `enable_vouch_gate` clearly in docs and scripts
- **L2**: enforce vouch where external/public contribution trust gating is needed
