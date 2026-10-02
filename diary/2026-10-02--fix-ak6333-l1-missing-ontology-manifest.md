---
summary: "AK6333: L1 full CI refuses tracked ontology content without its manifest; red/green entrypoint checks and isolated-source boundaries."
read_when:
  - "Reconstructing the decision 168 missing-manifest prerequisite and its checks."
type: "diary"
---

# 2026-10-02 — AK6333: L1 missing-manifest refusal

## What I did

- The operator explicitly selected AK6328, AK6333 and AK6330 through the scope form, including bounded implementation, declared checks, clean-clone commits/admitted push and verified AK completion. No fold or live AK install/source-admission authority was granted.
- Claimed only AK6333 and worked in a clean clone of remote main `c1d4b235d4ebfcbb32a20043e2f6416c33aaf0c1`. The canonical checkout's other session documentation branch was untouched.
- Added a refusal when the index tracks an ontology path other than `.gitkeep` but no regular manifest exists. Existing gitlink and symlink refusals remain.
- Added fifteen behavioural cases through the actual L1 full-CI entrypoint, with unrelated helpers and ROCS stubbed: empty, placeholder, untracked local content, tracked content, worktree/staged manifest deletion, wrong extension/actual rename, spaced path, content inside a `.gitkeep` directory, materialized manifest, symlink, unmaterialized gitlink, non-repository and corrupt index.
- Integrated the cases into the ROCS consumer check and regenerated fixtures with the declared synchronizer; only the L1 full-CI fixture changed.

## Observed checks

- Red before implementation: `content unexpectedly passed full.sh`, exit 1.
- Independent inspection caught a real pathspec defect: excluding `.gitkeep` also excluded its descendants. The added directory-content regression failed before repair, then passed after replacing the pathspec exclusion with an exact whole-list comparison.
- Green after repair: all fifteen entrypoint cases passed; the valid case recorded ROCS version, cleanup, validate and build in order. This uses a stub, not real ontology acceptance.
- An invocation with inherited caller Git-directory/worktree/index variables passed all cases and left the caller index byte-identical.
- The first aggregate run failed: one ownership test required a clean committed L0, the new refusal exposed a non-Git generation-hook probe, and the docs reference checker rejected an illustrative missing path. The hook probe now initializes its own real index and the prose is corrected. Final aggregate verification must run at the clean candidate commit; the initial failures are retained in the scratch logs, not described as passing.
- Shell syntax and the focused ROCS consumer check passed. Full L0 verification and independent inspection are recorded separately in AK; these focused checks are not a claim of landing or consumer adoption.

## Boundaries and follow-up

- AK6333 supplies L0 source behavior; a company must still adopt it through its supported refresh route. No holdingco refresh, ontology edit, fold, quarantine or AK source-admission operation was performed.
- AK6328 remains the separate company-owned ontology/reverse-route prerequisite. AK6330 retains the accepted plan's phase constraints; a source patch is not evidence that its disposition has been admitted or landed.
- No reusable knowledge promotion is claimed. The regression check records the recurring missing-input failure deterministically.
