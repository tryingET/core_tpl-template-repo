---
summary: "L0 owner session 2026-09-27/28: coordinated the softwareco L1 refresh and infra birth proof with template-propagator, resolved the dirty L0 docs-list WIP, the kernel ref mismatch (rocs-cli 0.4.5 tree identity), cleanup, and AK 6085."
read_when:
  - "Reconstructing why L0 moved from 69f032f to f5c0bb8 on 2026-09-27/28."
  - "Before another L0 -> L1 -> L2 rollout, or when an L0 checkout carries old uncommitted WIP."
  - "When a pinned ontology-kernel ref fails with 'workspace ref mismatch in strict mode'."
type: "reference"
---

# 2026-09-27 — ops(l0): rollout coordination and cleanup

Claude session tpl-template-repo-d6 (9b99016e). It started read-only, as the L0 owner session, to
coordinate with template-propagator-7a before infra/mele, infra/s8 and infra/s21ultra were created.
The Pi controller read a shared receipt, because Claude sessions cannot reach Pi intercom.

## What I did
- **Ownership:** agreed the split with template-propagator-7a over native SendMessage. The
  propagator took L0 readiness, the softwareco L1 refresh and the infra birth proof; this session
  took coordination and L0 analysis.
- **Audit correction:** L0 origin was already ef2d9c0. The local checkout read "behind 9" only
  because of dirty files.
- **Dirty L0 WIP traced:** the files came from Pi session logs.
  - It was the operator's own docs-list wrapper retirement of 2026-08-16 (Pi session 01a0092c,
    "no commits were created").
  - On 2026-08-22, Pi session 01a02581 turned its deletions into empty files.
  - The operator chose to finish it. The propagator landed it as AK 6100 (904a554, f62c019,
    b450175), and this session synced the checkout: stash, `pull --rebase`, pop, resolve
    modify/delete by keeping the deletion, verify no diff against origin.
- **Overlap caught:** AK 6118 (the "MRs only" rule) was editing this checkout and
  softwareco/copier/** directly while the refresh was pending. It was published from clones
  instead (945c001, softwareco 738b8e0).
- **Kernel ref mismatch adjudicated** (many-of-the-greats; operator approved option 1):
  - the kernel checkout sat past v0.2.1 on engineering-core chores only, with an identical
    `ontology/` tree;
  - rocs-cli 0.4.5 (AK 6159) now resolves pins by tree identity, reading a snapshot when the
    trees differ.
- **Verified before release:** the softwareco refresh (AK 6127, fdfff87, 8048899) and the birth
  proof against the real workspace. The HOLD on device-repo creation was released.
- **Cleanup:**
  - removed the stale worktree/branch `candidatepeer/sf3-iw7-ak-route-guardrails-agents` (b3cdd4d,
    superseded);
  - closed AK 5519 as superseded, with its CI obligation moved to AK 6160;
  - softwareco 793f7ac drops the retired `copier/tpl-agent-repo/governance/work-items.json.j2`;
  - kept `check-document-policy.sh` (a live opt-in tool, wired in 3 repos).
- **Workspace `AGENTS.md`:** ff32986 (the "proceed" rule and projections) and 60d7115 (the
  docs-list comment).
- **Kernel release:** AK 6167 filed in core/ontology-kernel (v0.3.0 MoSCoW), and a new Claude
  window opened for its orientation.
- **L0 commits:** f80de95 ignores `.ontology/`. f5c0bb8 is AK 6085: the ADR-0008 §9 staging
  contract in tpl-project-repo and tpl-monorepo, plus a regression test that `owners:` stays
  unset. `check-l0.sh` passed 7/7 on the clean tree.

## What surprised me
- **Stale dirty files were operator intent, not junk.** Two separate sessions preserved and
  mangled them for five weeks.
- **A refresh silently tightened runtime behaviour.** softwareco launchers defaulted to
  `ROCS_WORKSPACE_REF_MODE=loose`; the L0 pinned-core launcher sets nothing, so rocs went strict.
- **Strict ref mode was wrong both ways.** It compared commits and never checked for dirty trees:
  it failed on byte-identical content and would pass on modified content.
- **The pre-push hook's `GIT_*` environment leaked into a test** (`test_ontology_materializer`)
  and rewrote the real softwareco `.git`: bare repo, junk `main`, injected config. Repaired;
  fixed in 78ce572.
- **L0 hosted CI (l0-check) has been red since 2026-09-03.** The runner lacks the workspace
  (`ak`, agent-scripts) and does a shallow checkout. Local checks passed throughout.
- **704 manifests pin `ontology-kernel@main`,** although the kernel's RELEASING.md says to avoid
  `@main`.

## Patterns
- In canonical checkouts shared with other sessions:
  - sync with `reset --keep` or stash/rebase/pop;
  - commit single paths through a temporary index when others have staged changes;
  - never leave unpushed commits: they diverge for everyone.
- Before deleting a "leftover" file, grep for its users.
- A pin names a tree; the resolver has to prove the tree, not a commit.
- Coordination receipts in a shared transport directory work across harnesses, if every claim
  is marked verified or peer-reported.

## Crystallization candidates
- → docs/learnings/: git hook environments (`GIT_DIR`, `GIT_INDEX_FILE`, `GIT_WORK_TREE`) must be
  scrubbed in every test that runs git subprocesses (025366c, 78ce572).
- → docs/learnings/: L1 refresh previews should diff effective launcher defaults, such as the
  ref mode, not only files.
- → tips/meta/: trace old dirty files through session logs before stashing or discarding.

## Open items (owners named)
- AK 6160 (P1, L0): restore green hosted CI. Recommended: `fetch-depth: 0` plus explicit
  workspace-only skips under GitHub Actions.
- AK 6167 (P2, ontology-kernel): v0.3.0 scope and release; a separate Claude window is working
  on the orientation.
- Follow-up: the staging contract for tpl-agent-repo and tpl-org-repo needs an ownership-map
  classification first.
- The controller creates infra/mele, infra/s8 and infra/s21ultra; the HOLD is released.
