#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "error: missing dependency: $1" >&2
    exit 2
  }
}

need_cmd awk
need_cmd git
need_cmd grep
need_cmd mktemp

fail() {
  echo "error: $*" >&2
  exit 1
}

assert_file() {
  path="$1"
  [ -f "$path" ] || fail "missing file: $path"
}

assert_not_file() {
  path="$1"
  [ ! -f "$path" ] || fail "unexpected file present: $path"
}

assert_exec() {
  path="$1"
  [ -x "$path" ] || fail "missing executable bit: $path"
}

assert_dir() {
  path="$1"
  [ -d "$path" ] || fail "missing directory: $path"
}

assert_not_dir() {
  path="$1"
  [ ! -d "$path" ] || fail "unexpected directory present: $path"
}

assert_contains() {
  path="$1"
  needle="$2"
  label="$3"
  grep -qF -- "$needle" "$path" || fail "$label (missing '$needle' in $path)"
}

assert_not_contains() {
  path="$1"
  needle="$2"
  label="$3"
  if grep -qF -- "$needle" "$path"; then
    fail "$label (found '$needle' in $path)"
  fi
}

value_from_answers() {
  answers_file="$1"
  key="$2"

  awk -F':' -v key="$key" '
    $1 ~ "^" key "$" {
      v=$2
      gsub(/^[ \t]+|[ \t]+$/, "", v)
      gsub(/"/, "", v)
      gsub(/\047/, "", v)
      print tolower(v)
      exit
    }
  ' "$answers_file"
}

bool_from_answers() {
  value_from_answers "$1" "$2"
}

# L1-level required files
required_files="
README.md
AGENTS.md
CONTRIBUTING.md
.gitattributes
.copier-answers.yml
contracts/layer-contract.yml
contracts/provenance-seal.yml
scripts/new-repo-from-copier.sh
scripts/rocs.sh
scripts/check-template-ci.sh
scripts/install-hooks.sh
scripts/ci/smoke.sh
scripts/ci/full.sh
.github/VOUCHED.td
.github/workflows/template-check.yml
.github/workflows/ci.yml
.github/workflows/vouch-check-pr.yml
.github/workflows/vouch-manage.yml
.githooks/pre-commit
.githooks/pre-push
docs/.gitkeep
docs/org/operating_model.md
examples/.gitkeep
external/.gitkeep
ontology/.gitkeep
policy/.gitkeep
src/.gitkeep
tests/.gitkeep
diary/README.md
"

for path in $required_files; do
  assert_file "$path"
done

# L2 embedded templates required
for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo; do
  assert_dir "copier/$tpl"
  assert_file "copier/$tpl/copier.yml"
  assert_file "copier/$tpl/AGENTS.md.j2"
  assert_file "copier/$tpl/CODEOWNERS.j2"
  assert_file "copier/$tpl/scripts/rocs.sh.j2"
  assert_exec "copier/$tpl/scripts/rocs.sh.j2"
  assert_file "copier/$tpl/scripts/ci/smoke.sh"
  assert_file "copier/$tpl/scripts/ci/full.sh"
  assert_file "copier/$tpl/diary/README.md"
  assert_contains "copier/$tpl/diary/README.md" "YYYY-MM-DD--type-scope-summary.md" "L2 template $tpl diary README should enforce descriptive filename convention"
  assert_not_dir "copier/$tpl/docs/diary"
  assert_contains "copier/$tpl/AGENTS.md.j2" "Deterministic tooling policy" "L2 template $tpl AGENTS should include deterministic tooling policy"
  assert_contains "copier/$tpl/AGENTS.md.j2" "scripts/rocs.sh" "L2 template $tpl AGENTS should reference scripts/rocs.sh"
  assert_contains "copier/$tpl/AGENTS.md.j2" "diary/" "L2 template $tpl AGENTS should reference repo-local diary"
  assert_contains "copier/$tpl/README.md.j2" "ROCS command flow" "L2 template $tpl README should include ROCS command flow section"
  assert_contains "copier/$tpl/scripts/ci/full.sh" "scripts/rocs.sh" "L2 template $tpl full CI should use scripts/rocs.sh when ontology is present"
done
assert_not_contains "copier/tpl-project-repo/scripts/ci/full.sh" "uvx -n --from ./tools/rocs-cli rocs" "tpl-project-repo CI should not hardcode uvx vendored invocation"

required_exec="
scripts/new-repo-from-copier.sh
scripts/rocs.sh
scripts/check-template-ci.sh
scripts/install-hooks.sh
scripts/ci/smoke.sh
scripts/ci/full.sh
.githooks/pre-commit
.githooks/pre-push
"

for path in $required_exec; do
  assert_exec "$path"
done

for doc in README.md AGENTS.md; do
  assert_contains "$doc" "Recursion policy" "L1 docs must contain recursion policy section"
  assert_contains "$doc" "L1 -> L2" "L1 docs must allow L1 -> L2"
  assert_contains "$doc" "L1 -> L0" "L1 docs must forbid L1 -> L0"
  assert_contains "$doc" "L2 -> L1" "L1 docs must forbid L2 -> L1"
done
assert_contains "CONTRIBUTING.md" "check-template-ci.sh" "L1 contributing guide should reference template checks"
assert_contains "CONTRIBUTING.md" "scripts/rocs.sh --doctor" "L1 contributing guide should include deterministic ROCS wrapper usage"
assert_contains "AGENTS.md" "Deterministic tooling policy" "L1 AGENTS should document deterministic tooling policy"
assert_contains "AGENTS.md" "scripts/rocs.sh" "L1 AGENTS should reference scripts/rocs.sh"
assert_contains "AGENTS.md" "diary/" "L1 AGENTS should require repo-local diary"
assert_contains "README.md" "Organization docs profile" "L1 README should describe organization docs profile"
assert_contains "README.md" "Governance layering" "L1 README should describe governance layering"
assert_contains "README.md" "Community profile" "L1 README should describe community profile toggle"
assert_contains "README.md" "Release profile" "L1 README should describe release profile toggle"
assert_contains "README.md" "Baseline structure" "L1 README should describe baseline directory structure"
assert_contains "README.md" "Deterministic ROCS launcher" "L1 README should document deterministic ROCS launcher"
assert_contains "README.md" "repo-local diary" "L1 README should document repo-local diary contract"
assert_contains "README.md" ".gitattributes" "L1 README should mention git baseline files"
assert_contains "diary/README.md" "YYYY-MM-DD--type-scope-summary.md" "L1 diary README should enforce descriptive filename convention"

contract="contracts/layer-contract.yml"
assert_contains "$contract" "layer: L1" "L1 contract layer mismatch"
assert_contains "$contract" "L0 -> L1" "L1 contract must include L0 -> L1"
assert_contains "$contract" "L1 -> L2" "L1 contract must include L1 -> L2"
assert_contains "$contract" "L1 -> L0" "L1 contract must include forbidden reverse edge"
assert_contains "$contract" "L2 -> L1" "L1 contract must include forbidden reverse edge"
assert_contains "$contract" "nested_copier_tasks_allowed: false" "L1 contract must forbid nested copier tasks"

provenance="contracts/provenance-seal.yml"
assert_contains "$provenance" "schema: ai-society.template-provenance.v1" "L1 provenance seal schema mismatch"
assert_contains "$provenance" "layer: L1" "L1 provenance seal layer mismatch"
assert_contains "$provenance" "source_sha:" "L1 provenance seal must include source sha"
if grep -q "__RENDER_HASH__" "$provenance"; then
  fail "L1 provenance seal must not retain hash placeholder"
fi

assert_contains ".copier-answers.yml" "l0_source_sha:" "L1 answers file should persist L0 source sha"
assert_contains ".copier-answers.yml" "l1_org_docs_profile:" "L1 answers file should persist L1 org docs profile"

# Check L2 template copier configs
for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo; do
  assert_contains "copier/$tpl/copier.yml" "repo_slug" "L2 template $tpl must expose repo_slug"
  assert_contains "copier/$tpl/copier.yml" "enable_community_pack" "L2 template $tpl must expose community pack toggle"
  assert_contains "copier/$tpl/copier.yml" "enable_release_pack" "L2 template $tpl must expose release pack toggle"
  assert_contains "copier/$tpl/copier.yml" "enable_vouch_gate" "L2 template $tpl must expose vouch gate toggle"
done

assert_contains "scripts/new-repo-from-copier.sh" "tpl-agent-repo" "L1 wrapper must list tpl-agent-repo template"
assert_contains "scripts/new-repo-from-copier.sh" "tpl-org-repo" "L1 wrapper must list tpl-org-repo template"
assert_contains "scripts/new-repo-from-copier.sh" "tpl-project-repo" "L1 wrapper must list tpl-project-repo template"

workflow=".github/workflows/template-check.yml"
assert_contains "$workflow" "pull_request:" "template-check workflow must run on pull requests"
assert_contains "$workflow" "push:" "template-check workflow must run on pushes"
assert_contains "$workflow" "./scripts/check-template-ci.sh" "template-check workflow must run template checks"

assert_contains ".githooks/pre-commit" "scripts/ci/smoke.sh" "pre-commit must run smoke lane"
assert_contains ".githooks/pre-push" "scripts/ci/full.sh" "pre-push must run full lane"
assert_contains "scripts/ci/full.sh" "scripts/rocs.sh" "L1 full CI should use scripts/rocs.sh when ontology is present"

vouch_enabled="$(bool_from_answers .copier-answers.yml enable_vouch_gate || true)"
if [ "$vouch_enabled" = "true" ]; then
  assert_contains ".github/workflows/vouch-check-pr.yml" "pull_request_target" "vouch-check-pr must be active when enable_vouch_gate=true"
  assert_contains ".github/workflows/vouch-check-pr.yml" "mitchellh/vouch/action/check-pr@5713ce1baedf75e2f830afa3dac813a9c48bff12" "vouch-check-pr action must be SHA pinned"
  assert_contains ".github/workflows/vouch-check-pr.yml" "require-vouch: \"true\"" "vouch-check-pr must enforce vouched contributors"
  assert_contains ".github/workflows/vouch-manage.yml" "issue_comment" "vouch-manage must be active when enable_vouch_gate=true"
  assert_contains ".github/workflows/vouch-manage.yml" "mitchellh/vouch/action/manage-by-issue@5713ce1baedf75e2f830afa3dac813a9c48bff12" "vouch-manage action must be SHA pinned"
else
  assert_contains ".github/workflows/vouch-check-pr.yml" "workflow_dispatch:" "vouch-check-pr should be inactive when enable_vouch_gate=false"
  assert_contains ".github/workflows/vouch-check-pr.yml" "vouch gate disabled" "vouch-check-pr disabled workflow should explain status"
  assert_contains ".github/workflows/vouch-manage.yml" "workflow_dispatch:" "vouch-manage should be inactive when enable_vouch_gate=false"
  assert_contains ".github/workflows/vouch-manage.yml" "vouch manage workflow disabled" "vouch-manage disabled workflow should explain status"
fi

community_enabled="$(bool_from_answers .copier-answers.yml enable_community_pack || true)"
if [ "$community_enabled" = "true" ]; then
  assert_file "CODE_OF_CONDUCT.md"
  assert_file "SUPPORT.md"
  assert_file ".github/pull_request_template.md"
  assert_file ".github/ISSUE_TEMPLATE/config.yml"
  assert_file ".github/ISSUE_TEMPLATE/bug-report.yml"
  assert_file ".github/ISSUE_TEMPLATE/feature-request.yml"
  assert_contains ".github/ISSUE_TEMPLATE/config.yml" "blank_issues_enabled: false" "community issue-template config should disable blank issues"
else
  assert_not_file "CODE_OF_CONDUCT.md"
  assert_not_file "SUPPORT.md"
  assert_not_file ".github/pull_request_template.md"
  assert_not_file ".github/ISSUE_TEMPLATE/config.yml"
  assert_not_file ".github/ISSUE_TEMPLATE/bug-report.yml"
  assert_not_file ".github/ISSUE_TEMPLATE/feature-request.yml"
fi

release_enabled="$(bool_from_answers .copier-answers.yml enable_release_pack || true)"
if [ "$release_enabled" = "true" ]; then
  assert_file ".release-please-config.json"
  assert_file ".release-please-manifest.json"
  assert_file "CHANGELOG.md"
  assert_file "SECURITY.md"
  assert_file ".github/workflows/release-please.yml"
  assert_file ".github/workflows/release-check.yml"
  assert_file ".github/workflows/publish.yml"
  assert_exec "scripts/release/check.sh"
  assert_exec "scripts/release/publish.sh"
  assert_contains ".github/workflows/release-please.yml" "googleapis/release-please-action@v4" "release-please workflow should use release-please action"
  assert_contains ".github/workflows/publish.yml" "softprops/action-gh-release@v2" "publish workflow should upload release artifacts"
else
  assert_not_file ".release-please-config.json"
  assert_not_file ".release-please-manifest.json"
  assert_not_file "CHANGELOG.md"
  assert_not_file "SECURITY.md"
  assert_not_file ".github/workflows/release-please.yml"
  assert_not_file ".github/workflows/release-check.yml"
  assert_not_file ".github/workflows/publish.yml"
  assert_not_file "scripts/release/check.sh"
  assert_not_file "scripts/release/publish.sh"
fi

l1_org_docs_profile="$(value_from_answers .copier-answers.yml l1_org_docs_profile || true)"
[ -n "$l1_org_docs_profile" ] || l1_org_docs_profile="rich"

if [ "$l1_org_docs_profile" = "rich" ]; then
  assert_file "docs/org/purpose.md"
  assert_file "docs/org/mission.md"
  assert_file "docs/org/vision.md"
  assert_file "docs/org/strategic_objectives.md"
  assert_file "docs/org/values_ethics.md"
  assert_file "docs/org/governance.md"
  assert_file "docs/org/glossary.md"
else
  assert_not_file "docs/org/purpose.md"
  assert_not_file "docs/org/mission.md"
  assert_not_file "docs/org/vision.md"
  assert_not_file "docs/org/strategic_objectives.md"
  assert_not_file "docs/org/values_ethics.md"
  assert_not_file "docs/org/governance.md"
  assert_not_file "docs/org/glossary.md"
fi

# Test L2 generation for each template
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo; do
  l2_dir="$tmp_root/$tpl"
  ./scripts/new-repo-from-copier.sh "$tpl" "$l2_dir" \
    -d repo_slug="$tpl" \
    --defaults --overwrite >/dev/null

  # Basic L2 checks
  assert_file "$l2_dir/.copier-answers.yml"
  assert_file "$l2_dir/AGENTS.md"
  assert_file "$l2_dir/CODEOWNERS"
  assert_file "$l2_dir/scripts/rocs.sh"
  assert_file "$l2_dir/scripts/ci/smoke.sh"
  assert_file "$l2_dir/scripts/ci/full.sh"
  assert_file "$l2_dir/diary/README.md"
  assert_contains "$l2_dir/diary/README.md" "YYYY-MM-DD--type-scope-summary.md" "generated $tpl diary README should enforce descriptive filename convention"
  assert_not_dir "$l2_dir/docs/diary"
  assert_exec "$l2_dir/scripts/rocs.sh"
  assert_contains "$l2_dir/AGENTS.md" "Deterministic tooling policy" "generated $tpl AGENTS should include deterministic tooling policy"
  assert_contains "$l2_dir/AGENTS.md" "scripts/rocs.sh" "generated $tpl AGENTS should reference scripts/rocs.sh"
  assert_contains "$l2_dir/AGENTS.md" "diary/" "generated $tpl AGENTS should reference repo-local diary"
  assert_contains "$l2_dir/README.md" "ROCS command flow" "generated $tpl README should include ROCS command flow section"

  # Initialize git for smoke test (required by scripts/ci/smoke.sh)
  (
    cd "$l2_dir"
    git init -b main >/dev/null
    git config user.name "l1-template ci" >/dev/null
    git config user.email "ci@l1-template.local" >/dev/null
    git add . >/dev/null
    git commit -m "initial L2 render" >/dev/null
    ./scripts/ci/smoke.sh >/dev/null
  )
done

# Detailed check for tpl-project-repo (primary template)
l2_dir="$tmp_root/tpl-project-repo"
assert_contains "$l2_dir/AGENTS.md" "Recursion policy" "generated L2 AGENTS.md must include recursion section"
assert_contains "$l2_dir/AGENTS.md" "Deterministic tooling policy" "generated L2 AGENTS.md must include deterministic tooling policy"
assert_contains "$l2_dir/AGENTS.md" "scripts/rocs.sh" "generated L2 AGENTS.md must reference scripts/rocs.sh"
assert_contains "$l2_dir/AGENTS.md" "diary/" "generated L2 AGENTS.md must reference repo-local diary"

# Idempotency check
(
  cd "$l2_dir"
  git init -b main >/dev/null 2>&1 || true
  git config user.name "l1-template ci" >/dev/null
  git config user.email "ci@l1-template.local" >/dev/null
  git add .
  git commit -m "initial L2 render" >/dev/null 2>&1 || true
  [ -f ./scripts/install-hooks.sh ] && ./scripts/install-hooks.sh >/dev/null || true
)

./scripts/new-repo-from-copier.sh tpl-project-repo "$l2_dir" \
  -d repo_slug=tpl-project-repo \
  --defaults --overwrite >/dev/null

(
  cd "$l2_dir"
  if [ -n "$(git status --porcelain)" ]; then
    echo "error: non-idempotent L1 -> L2 generation" >&2
    git status --short >&2
    exit 1
  fi
)

echo "ok: template ci"
