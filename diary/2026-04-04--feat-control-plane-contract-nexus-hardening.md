---
summary: "Session note: 2026 04 04 Feat Control Plane Contract Nexus Hardening."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 04 04 feat control plane contract nexus hardening."
type: "reference"
---

# 2026-04-04 — Control-plane contract nexus hardening

## What I Did
- Reproduced and fixed the deep-review issues where L1 profile/default metadata rendered blank, L1->L2 org-context defaults were advertised but weakly enforced, and staged L1 migrations clobbered newly rendered provenance.
- Added the missing L0 `l2_org_docs_default` question, derived a non-empty `l1_profile` label from the governed toggle bundle, and propagated those values into generated README/provenance/answers output.
- Scoped L1->L2 `org_docs_profile` inheritance to `tpl-project-repo` / `tpl-monorepo`, added real compact/rich org-context surfaces there, and aligned monorepo docs/CODEOWNERS/recursion wording with the actual layer contract.
- Fixed `scripts/migrate-l1-structure.sh` to render staged repos with legacy profile flags first, then merge only approved legacy answers keys so `l0_source_sha` and newly required contract fields survive.
- Added semantic guardrails: missing-`node` preflight for docs reference checks, non-empty profile/default assertions in generated L1 template CI, richer migration adversarial checks, bash/software-pack honesty checks, and synced fixtures.
- Re-ran `bash ./scripts/check-l0.sh` to verify the full stack after regeneration.

## What Surprised Me
- The shipped checks were green while the primary operator-facing L1 README/provenance were already blank on fresh renders.
- The migration bug was deeper than a bad copy step: preserving legacy render flags had to happen before the staged render, otherwise the staged files and merged answers would disagree.
- `tpl-project-repo` had been emitting empty stack-contract files in non-software-pack paths for a while; the bash review surfaced that the real issue was “conditional files rendered as empty placeholders,” not just missing bash prose.

## Patterns
- Control-plane checks must validate semantic values, not just key/file presence.
- Migration logic must preserve render inputs before preserving history or answers snapshots.
- If a template advertises a knob, descendant renders need a concrete surface difference or the docs must narrow the claim.
- Empty generated files are usually a hidden contract bug, not harmless noise.

## Crystallization Candidates
- → docs/learnings/: semantic assertions for template control planes and merge-safe migrations are durable enough to codify.
- → tips/meta/: future template deep-reviews should explicitly probe for blank rendered metadata, dead knobs, and empty conditional files.
- → scripts/: keep expanding adversarial checks where render-time flags and migration-time preservation can drift.
