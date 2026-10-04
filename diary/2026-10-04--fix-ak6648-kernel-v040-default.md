---
summary: "AK6648: move generated kernel defaults to the immutable v0.4.0 release."
read_when:
  - "When tracing the v0.4.0 default pin and its consumer refresh."
type: "diary"
task_id: 6648
---

# Kernel v0.4.0 default repin

Authority: AK6648, standing owner decision AK6288; published release AK6538.
First consumer AK6453 is done. Release commit:
`763d70a9f20d3eb8ed829398e89539d692650aec`.

Move project, monorepo and package defaults, the matching checks and generated
fixtures from v0.3.0 to v0.4.0. Preserve company refs and ontology source content.
The historical ownership-reader test restores its historical copier defaults
alongside its historical checker; current release expectations belong after refresh.

Initial checks against the dirty worktree failed: Copier historical renders and
clean-source tests do not admit a dirty L0, and the historical checker rejected
the newer fixture default. Repeat the full check at the committed clean candidate.
Strict docs inventory also reports nine pre-existing metadata issues outside this
pin-only slice; no metadata exemptions or check thresholds were weakened.

Consumer execution remains governed by the ordinary L1 wave protocol and each
repo's declared check. A dirty or failing target receives an owner-bound AK task,
not forced mutation. Full command receipts are retained under
`$TMPDIR/ak6648-v040/evidence/`; AK6648 carries the final disposition.

Rebase onto main (2026-10-10): PR13 (AK6586) moved the generation assertions from
`scripts/check-l0-generation.sh` into `tests/ci_generation_shell_metadata.sh` and
pins their bytes in `tests/ci_generation_source_map.json`. The same two pin lines
moved there. The extraction baseline hash is now the 5acfd49 source with only this
substitution applied. The AK6658 commits are no longer underneath this PR because
main already has their hosted CI repairs.
