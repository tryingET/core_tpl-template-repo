---
summary: "Repair two pre-existing L0 full-gate failures exposed during protected-pin validation."
type: diary
---

# L0 baseline gate repairs

AK task `4966` restores the generated L1 plain-`ak` operator line required by its own contract and
uses the existing Python-backed JSON scalar reader when older lane baselines omit the YAML owner.
The latter decodes escaped JSON owner handles before re-materializing CODEOWNERS.
When modern baselines no longer have legacy work-items JSON, preview falls back to the canonical
`docs/project/**` owner in CODEOWNERS; legacy JSON remains the first decoded fallback when present.

Post-review safety hardening stops nested-repo discovery from following symlinks, verifies every
physical removal remains inside the temporary comparison tree, normalizes empty owner keys, and
adds regressions for symlink escape plus genuine JSON-before-CODEOWNERS precedence.
