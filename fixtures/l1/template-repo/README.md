# fixture-template-repo

This is an **L1 template repository** generated from `core/tpl-template-repo` (L0).

- Profile: ``
- Maintainer: `@template-owner`
- L1 organization docs profile: `rich`
- Default L2 organization docs profile: ``
- Baseline L2 template family: `agent`, `project`, `org`, `monorepo`, `package`

## What this repo provides

- **L2 Templates**:
  - `copier/tpl-agent-repo/` — AI agent repositories
  - `copier/tpl-project-repo/` — Delivery projects
  - `copier/tpl-org-repo/` — Organization handbooks
  - `copier/tpl-monorepo/` — Monorepo workspaces
  - `copier/tpl-package/` — Packages inside monorepos
- Opinionated local hooks (`.githooks/`) and CI lane scripts (`scripts/ci/`).
- Lane-root bootstrap helper: `scripts/bootstrap-lane-root.sh`.
- Layer contract enforcement via `contracts/layer-contract.yml`.
- Baseline structure in this generated L1 repo: `docs/`, `examples/`, `external/`, `ontology/`, `policy/`, `src/`, `tests/`.
- Git hygiene in this L1 repo: `.github/`, `.githooks/`, `.gitignore`, `.gitattributes`.
- Generated L2 repositories are archetype/profile-specific and do not all share identical folder/git baselines; GitHub assets are profile-gated.
- **KES Infrastructure**: `tips/`, `governance/`, `metrics/` for knowledge evolution.
- **Repo-local diary contract**: `diary/README.md` in L1 and all generated L2 archetypes.

## Quickstart

Validate this L1 template repo:

```bash
bash ./scripts/check-template-ci.sh
```

Generate an L2 **agent** repository:

```bash
./scripts/new-repo-from-copier.sh tpl-agent-repo /path/to/agent-<slug> \
  -d repo_slug=agent-<slug> \
  -d agent_owner_handle=@<owner> \
  --defaults --overwrite
```

Generate an L2 **project** repository:

```bash
./scripts/new-repo-from-copier.sh tpl-project-repo /path/to/<project> \
  -d repo_slug=<project> \
  -d project_owner_handle=@<owner> \
  --defaults --overwrite
```

Generate an L2 **org** handbook:

```bash
./scripts/new-repo-from-copier.sh tpl-org-repo /path/to/<org>-handbook \
  -d repo_slug=<org>-handbook \
  -d org_owner_handle=@<owner> \
  --defaults --overwrite
```

Generate an L2 **monorepo** workspace:

```bash
./scripts/new-repo-from-copier.sh tpl-monorepo /path/to/<monorepo> \
  -d repo_slug=<monorepo> \
  -d language=python \
  -d package_manager=uv \
  --defaults --overwrite
```

Generate an L2 **package** (inside monorepos):

```bash
./scripts/new-repo-from-copier.sh tpl-package /path/to/packages/<name> \
  -d package_name=<name> \
  -d package_type=library \
  -d language=python \
  --defaults --overwrite
```

### Lane root bootstrap (baseline tracked, child repos ignored)

Before nesting child repositories in a lane, bootstrap the lane root with a project-template control plane and lane-local ignore policy:

```bash
# Standard lane
./scripts/bootstrap-lane-root.sh owned
git add .gitignore owned
git commit -m "chore: bootstrap owned lane baseline"
./scripts/bootstrap-lane-root.sh owned --init-lane-git

# Custom lane
./scripts/bootstrap-lane-root.sh data
git add .gitignore data
git commit -m "chore: bootstrap data lane baseline"
./scripts/bootstrap-lane-root.sh data --init-lane-git
```

This keeps lane baseline files versioned while nested child repos are ignored by default (`<lane>/.gitignore`).

### Transition existing L2 repos (scaffold-first)

There is no automatic in-place migrator. Use this deterministic pattern:

1) Render baseline:
```bash
./scripts/new-repo-from-copier.sh tpl-project-repo /tmp/<repo>-template \
  -d repo_slug=<repo> \
  --defaults --overwrite
```

2) Diff against existing repo:
```bash
git diff --no-index -- /tmp/<repo>-template /absolute/path/to/<existing-repo>
```

3) Adopt control-plane first (`AGENTS.md`, `CODEOWNERS`, `scripts/`, `governance/`, `docs/`, `ontology/`), then reconcile product code.

4) Validate and open MR.

Install local hooks in a generated repo:

```bash
./scripts/install-hooks.sh
```

Deterministic ROCS launcher (use before ad-hoc scripting):

```bash
./scripts/rocs.sh --doctor
./scripts/rocs.sh --which
./scripts/rocs.sh version
```

## Multi-pass template suffix policy (`.jinja` vs `.j2`)

This L1 template repo has two template boundaries:

- **L0 -> L1 artifacts** in this repository use `.jinja` at authoring time (as rendered from L0).
- **L1 -> L2 artifacts** under `./copier/` use `_templates_suffix: .j2` in each L2 template `copier.yml`.

Pass-boundary rule:
- never place `.jinja` template files under `./copier/`
- never place `.j2` template files outside `./copier/`

`bash ./scripts/check-template-ci.sh` enforces this boundary so nested L2 templates cannot accidentally inherit the outer pass suffix, and fails if nested files contain Jinja markers without the `.j2` suffix.

Contribution workflow:
- [CONTRIBUTING.md](CONTRIBUTING.md)

## Knowledge Evolution System (KES)

This L1 participates in KES for compound learning:

```
tips/
├── _templates/tip.yml     # TIP genome
├── domain/                # Domain TIPs (local)
└── meta/                  # Meta TIPs (→ L0)

governance/README.md       # Review process
metrics/README.md          # Effectiveness tracking
```

**TIP Flow**: L2 learns → TIP proposed → review → merge → propagate

- Domain TIPs improve this L1
- Meta TIPs escalate to L0
- All L2 inherit improvements

Diary contract (repo-local diary for KES):
- L1 logs in `./diary/`
- each generated L2 archetype logs in `./diary/`
- no workspace-global diary authority

See `tips/README.md` for TIP process.

## Archetype profile

- L2 repos are generated via explicit template selection:
  - `tpl-agent-repo`
  - `tpl-project-repo`
  - `tpl-org-repo`
  - `tpl-monorepo`
  - `tpl-package`
- Detailed project-template file map (canonical):
  - `docs/dev/tpl-project-repo-file-contract.md`
  - wikilink: `[[docs/dev/tpl-project-repo-file-contract.md]]`

## Organization docs profile

- This L1 repository currently ships **rich** organization docs in `docs/org/`.
- Generated L2 repositories default to **** via `scripts/new-repo-from-copier.sh` inheritance from `.copier-answers.yml` (`l2_org_docs_default`).
- Override at L2 generation time with:
  - `-d org_docs_profile=compact`
  - `-d org_docs_profile=rich`

## Governance layering

L2 governance is archetype-dependent:
- `tpl-project-repo`: `governance/work-items.*` + `docs/project/` + `docs/system4d/`.
- `tpl-org-repo`: governance-primary docs in `docs/org/` + `governance/`.
- `tpl-agent-repo`: lightweight local governance in persona/system docs.
- `tpl-monorepo`: repo-level delivery governance with package/app decomposition.
- `tpl-package`: package-local governance and quality controls inside a monorepo.

For `tpl-project-repo`, the canonical file-by-file contract is:
- `docs/dev/tpl-project-repo-file-contract.md`
- wikilink: `[[docs/dev/tpl-project-repo-file-contract.md]]`

## Community profile

- Community collaboration pack is currently **disabled**.
- When enabled, this repo includes:
  - `.github/ISSUE_TEMPLATE/`
  - `.github/pull_request_template.md`
  - `CODE_OF_CONDUCT.md`
  - `SUPPORT.md`
- L2 generation inherits `enable_community_pack` from this L1 unless you override with `-d enable_community_pack=true|false`.

## Release profile

- Release automation pack is currently **disabled**.
- When enabled, this repo includes:
  - `.github/workflows/release-please.yml`
  - `.github/workflows/release-check.yml`
  - `.github/workflows/publish.yml`
  - `.release-please-config.json`, `.release-please-manifest.json`
  - `CHANGELOG.md`, `SECURITY.md`
  - `scripts/release/check.sh`, `scripts/release/publish.sh`
- L2 generation inherits `enable_release_pack` from this L1 unless you override with `-d enable_release_pack=true|false`.

## Trust-gate profile

- Vouch trust gate baseline is currently **disabled**.
- Files are scaffolded at `.github/VOUCHED.td`, `.github/workflows/vouch-check-pr.yml`, `.github/workflows/vouch-manage.yml`.
- L2 generation inherits `enable_vouch_gate` from this L1 unless you override with `-d enable_vouch_gate=true|false`.

## Recursion policy (explicit)

Current layer: **L1**

Allowed edges:
- `L0 -> L1`
- `L1 -> L2`

Forbidden edges:
- `L1 -> L0`
- `L2 -> L1`
- any cycle

Answers-file policy:
- Keep `.copier-answers.yml` versioned in git for reproducibility.
- Do not invoke nested Copier runs from `_tasks`.
