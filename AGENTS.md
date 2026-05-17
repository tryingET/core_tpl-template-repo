---
summary: "AGENTS.md — tpl-template-repo."
read_when:
  - "Read when you need agents.md — tpl-template-repo."
type: "reference"
---

# AGENTS.md — tpl-template-repo

## Intent
Build and maintain the L0 meta-template that scaffolds compliant L1 template repositories.

## Working rules
- Keep recursion bounded: `L0 -> L1 -> L2` only.
- Never encode nested `copier copy` calls inside template `_tasks`.
- Keep `.copier-answers.yml` committed in generated repositories.
- Preserve baseline folder skeleton + git baseline files unless intentionally changed by policy.
- Treat `enable_community_pack` as profile policy (default disabled, enable for public/community-facing repos).
- Treat `enable_release_pack` as profile policy (default disabled, enable where release automation is required).
- Treat `enable_vouch_gate` as profile policy (default disabled, enable for trust-gated/public repos).
- Keep generated repo-local task/issue/work-item surfaces AK-first: Agent Kernel is authoritative, while checked-in files such as `governance/work-items.json` are deterministic projections/mirrors.
- When templates ship repo-local work-items, prefer plain installed `ak` as the canonical operator path in generated repos. Never reintroduce silent CI skips for projection drift checks.
- When templates teach explicit task scope, keep AK as the authoring surface and treat frozen `governance/task-scopes/AK-<TASK-ID>.snapshot.json` files as repo-consumption exports rather than hand-authored authority.
- Generic AK launcher/build wrapper distribution is being removed from template/generated repos; keep plain installed `ak` as the public path and do not reintroduce copied launcher-resolution bundles.
- No secrets in git.

## Recursion policy (explicit)
Allowed:
- `L0 -> L1`
- `L1 -> L2`

Forbidden:
- `L1 -> L0`
- `L2 -> L1`
- any cycle

## Shared tooling
- Docs discovery/scoping: `./scripts/docs-list.sh --task "<task>" --top 8`
- Prompt read-scope allowlist: `./scripts/docs-list.sh --from-prompt <prompt-file> --paths-only --wikilink`
- Repo census preflight: `./scripts/preflight-repo-census.sh [scope]`
- ROCS command launcher (deterministic + portable): `./scripts/rocs.sh <rocs args...>`
- Engineering contract authoring (when engineering guidance is in scope): generated repos should treat `policy/engineering-lane.json` as the source of truth for the declared upstream lane command and `docs/engineering.local.md` as the local override; do not emit `--prefer-repo` unless a repo ships trusted local `lanes/`

## Deterministic tooling policy (ROCS-first)
- Prefer deterministic wrappers (`./scripts/rocs.sh`, repo `scripts/*`) over ad-hoc inline scripts, but keep plain installed `ak` as the public operator path in generated repos.
- When task/work-item or task-scope surfaces are in scope, use `ak ...` by default, and keep repo-local task-scope files as frozen AK exports rather than hand-authored truth.
- For ontology/policy checks, run ROCS before custom Python one-offs.
- Use inline Python only as an explicit escape hatch when no deterministic command exists.

## Diary policy (repo-local, mandatory)
- Keep session capture in `./diary/YYYY-MM-DD--type-scope-summary.md` for this repo.
- Keep diary guidance in `./diary/README.md`.
- Apply the same diary contract per structural template (`tpl-agent-repo`, `tpl-org-repo`, `tpl-project-repo`).

## Knowledge crystallization flow (mandatory)
- Flow: `Session output -> diary/ (raw) -> docs/learnings/ (crystallized) -> tips/meta/ (propagated)`.
- `/deep-review` findings are raw input only until crystallized into `docs/learnings/`.
- When a learning is recurrent, encode a deterministic check in `scripts/` so regressions fail fast.

## Validation before merge
- `bash ./scripts/check-l0.sh`
- optional focused runs:
  - `bash ./scripts/check-supply-chain.sh`
  - `bash ./scripts/check-l0-generation.sh`
  - `bash ./scripts/check-l0-fixtures.sh`
