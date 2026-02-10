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
- no vouch trust gate baseline yet
- recursion/layer contracts and fixture/supply-chain controls are already in place

Recommended layering for future adoption:
- **L0**: define optional vouch policy contract and required checks
- **L1**: provide vouch-enabled profile/feature flag
- **L2**: enforce vouch only where external/public contribution trust gating is needed
