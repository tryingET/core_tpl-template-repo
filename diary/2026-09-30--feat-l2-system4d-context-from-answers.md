---
summary: "AK 6133: tpl-project-repo and tpl-monorepo render ontology/src/system4d.yaml from copier answers and mark every open value FILL IN, instead of shipping 33 literal <...> tokens; L1 retires the old plain copies on refresh."
read_when:
  - "Changing the System4D context file the L2 templates generate."
  - "Planning the fleet sweep of placeholder system4d.yaml files (AK 6135)."
  - "Renaming an L2 template source (a plain file becoming .j2) that L1s already carry."
type: "reference"
---

# 2026-09-30 — feat(l2): system4d context from answers

Claude session f5044d4b, AK 6133. Evidence in: 11073 (fleet census, 47 repos byte-identical to
the template, md5 36347f74decf) and 11118 (operator direction of 2026-09-27: agents read
system4d.yaml, so do not blank it to `system4d: {}`; render what the answers know, leave explicit
fill-in guidance, never literal `<...>` tokens; worked example replay-fabric d738302).

## What I did
- Found the placeholder in two L2 templates, not one: tpl-monorepo ships the same bytes as
  tpl-project-repo (and 11 fixture copies mirror them).
- Renamed both sources to `ontology/src/system4d.yaml.j2`. Only `.j2` files render in the L1 -> L2
  pass, and the L2 destination path stays `ontology/src/system4d.yaml`.
- Rendered from answers:
  - `name` (repo_slug);
  - a header naming company and lane (project) or company (monorepo);
  - the language (project) or package manager (monorepo);
  - the boundaries every generated repo shares: AK owns task, direction, decision and evidence
    state; the shared vocabulary comes from the core and company ontology layers;
  - the dependencies every generated repo has: ak, the ontology layers, rocs-cli, and
    engineering-core exactly when `policy/engineering-lane.json` is emitted;
  - ids with a prefix from the slug's initials (replay-fabric -> RF, agent_kernel -> AK, a
    single-word slug in full).
- Every other value is `FILL IN: ...` guidance naming the repo's own sources (the creating task,
  README.md, docs/project/, docs/decisions/, src/, tests/). The header says FILL IN values are
  instructions, not facts, and gives the grep that lists what is still open.
- Kept the ontology refs and the rocs-cli pin out of the file. They point at
  `ontology/manifest.yaml` and `scripts/rocs.sh`, so a repin (as in AK 6257) cannot leave a stale
  copy behind, and the `<repo:...>` locators cannot pass for placeholders.
- Pointed `ontology/index.md` at the FILL IN values.
- Added `tests/test_l2_system4d_context.py`, wired into check-l0-guardrails:
  - the templates carry no `<...>` token;
  - every rendered fixture names its own repo_slug and marks each open value with a leading
    FILL IN;
  - engineering-core appears exactly when the lane file is emitted;
  - the id prefix and lane follow the answers.
- Added L1 retirement entries for `copier/tpl-{project-repo,monorepo}/ontology/src/system4d.yaml`
  in a second commit, because `retired_by` has to be an L0 ancestor.

## What surprised me
- Nothing in an L1 refresh detects `X` and `X.j2` rendering the same L2 path. Without the
  retirement entry, softwareco would have kept the stale plain file next to the new `.j2`, and
  the L1 -> L2 render would have had two sources for one file.
- check-l0 refuses an uncommitted L0 ("L1 render requires a clean L0 worktree at an exact
  commit"), so the full gate only runs after the commit.

## How the fix reaches L1 and L2
- L1 (softwareco/copier/tpl-project-repo): `copier/**` is template-owned in softwareco's
  `contracts/template-ownership.yml`. The next L1 contract refresh from this L0 commit
  (template-propagator `scripts/l1-wave.py`, operator release, like AK 6267) adds the `.j2` and
  retires the plain file through `contracts/l1-template-retirements.json`. That wave needs its own
  AK task in softwareco; this session edited no other repo.
- L2: new repos get the rendered file at birth. Existing repos change only through the sweep
  (AK 6135, operator go). A `copier update` replaces the untouched placeholder cleanly but
  conflicts where a repo has already filled the file (replay-fabric), so the sweep has to keep
  filled files.

## Crystallization candidates
- -> docs/learnings/: renaming an L2 template source that L1s already carry needs a retirement
  entry in a follow-up commit; nothing else stops two sources from rendering one L2 path.
