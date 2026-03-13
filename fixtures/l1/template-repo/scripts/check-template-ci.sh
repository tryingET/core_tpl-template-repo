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
need_cmd find
need_cmd git
need_cmd grep
need_cmd mktemp
need_cmd sort

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

assert_line_precedes() {
  path="$1"
  first="$2"
  second="$3"
  label="$4"

  first_line="$(grep -nF -- "$first" "$path" | awk -F ':' 'NR == 1 { print $1 }')"
  second_line="$(grep -nF -- "$second" "$path" | awk -F ':' 'NR == 1 { print $1 }')"

  [ -n "$first_line" ] || fail "$label (missing '$first' in $path)"
  [ -n "$second_line" ] || fail "$label (missing '$second' in $path)"
  [ "$first_line" -lt "$second_line" ] || fail "$label (expected '$first' before '$second' in $path)"
}

suffix_policy_lib="$repo_root/scripts/lib/suffix-policy.sh"
[ -f "$suffix_policy_lib" ] || fail "missing file: $suffix_policy_lib"
# shellcheck source=/dev/null
. "$suffix_policy_lib"

check_multi_pass_suffix_policy() {
  self_test_untemplated_jinja_matcher || fail "suffix-policy matcher regression: expected to ignore GitHub expressions and detect unsuffixed Jinja markers"

  for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo tpl-package; do
    tpl_suffix="$(yaml_scalar_value "copier/$tpl/copier.yml" "_templates_suffix")"
    [ "$tpl_suffix" = ".j2" ] || fail "L2 template $tpl copier config must use .j2 suffix (found ${tpl_suffix:-<missing>})"
  done

  nested_jinja="$(first_suffix_match "copier" "*.jinja")"
  [ -z "$nested_jinja" ] || fail "pass-boundary suffix policy violated: nested L2 templates must not use .jinja (found $nested_jinja)"

  outer_j2="$(first_suffix_match "." "*.j2" "./copier/*")"
  [ -z "$outer_j2" ] || fail "pass-boundary suffix policy violated: L1 surface must not use .j2 outside copier/ (found $outer_j2)"

  nested_untemplated_jinja="$(first_untemplated_jinja_match "copier" ".j2")"
  [ -z "$nested_untemplated_jinja" ] || fail "pass-boundary suffix policy violated: nested L2 template file contains Jinja markers but is not suffixed .j2 (found $nested_untemplated_jinja)"
}

list_template_files() {
  template_dir="$1"

  find "$template_dir" -type f | while IFS= read -r abs_path; do
    rel_path="${abs_path#$template_dir/}"
    case "$rel_path" in
      */__pycache__/*|*.pyc)
        continue
        ;;
    esac
    printf '%s\n' "$rel_path"
  done | LC_ALL=C sort
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
scripts/bootstrap-lane-root.sh
scripts/ak.sh
scripts/rocs.sh
scripts/check-template-ci.sh
scripts/install-hooks.sh
scripts/lib/suffix-policy.sh
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
docs/dev/tpl-project-repo-file-contract.md
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
for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo tpl-package; do
  assert_dir "copier/$tpl"
  assert_file "copier/$tpl/copier.yml"
  assert_file "copier/$tpl/AGENTS.md.j2"
  assert_file "copier/$tpl/CODEOWNERS.j2"
  if [ "$tpl" != "tpl-package" ]; then
    assert_file "copier/$tpl/scripts/ak.sh"
    assert_exec "copier/$tpl/scripts/ak.sh"
  fi
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
  if [ "$tpl" != "tpl-package" ]; then
    assert_contains "copier/$tpl/scripts/ci/full.sh" "scripts/ak.sh" "L2 template $tpl full CI should use scripts/ak.sh for work-items projection checks"
    assert_not_contains "copier/$tpl/scripts/ci/full.sh" "crates/ak-cli/Cargo.toml" "L2 template $tpl full CI must not gate AK checks on vendored ak-cli"
  fi
  assert_contains "copier/$tpl/scripts/ci/full.sh" "scripts/rocs.sh" "L2 template $tpl full CI should use scripts/rocs.sh when ontology is present"
done
for tpl in tpl-project-repo tpl-monorepo; do
  assert_file "copier/$tpl/governance/work-items.cue"
  assert_file "copier/$tpl/governance/work-items.json.j2"
  assert_contains "copier/$tpl/README.md.j2" "Agent Kernel work-items flow" "L2 template $tpl README should document the AK work-items workflow"
  assert_contains "copier/$tpl/governance/README.md" "work-items export" "L2 template $tpl governance README should document projection export"
  assert_contains "copier/$tpl/governance/README.md" "work-items check" "L2 template $tpl governance README should document projection drift checks"
  assert_contains "copier/$tpl/governance/README.md" "work-items import" "L2 template $tpl governance README should document legacy import bootstrap"
done
assert_contains "copier/tpl-project-repo/next_session_prompt.md" "Agent Kernel" "tpl-project-repo next-session prompt should describe AK-backed work-items authority"
assert_not_contains "copier/tpl-project-repo/scripts/ci/full.sh" "uvx -n --from ./tools/rocs-cli rocs" "tpl-project-repo CI should not hardcode uvx vendored invocation"

check_multi_pass_suffix_policy

required_exec="
scripts/new-repo-from-copier.sh
scripts/bootstrap-lane-root.sh
scripts/ak.sh
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
assert_contains "AGENTS.md" "scripts/ak.sh" "L1 AGENTS should reference scripts/ak.sh when repo-local work-items projection is in scope"
assert_contains "AGENTS.md" "scripts/rocs.sh" "L1 AGENTS should reference scripts/rocs.sh"
assert_contains "AGENTS.md" "diary/" "L1 AGENTS should require repo-local diary"
assert_contains "AGENTS.md" "L2 Templates" "L1 AGENTS should document L2 templates"
assert_contains "AGENTS.md" "bootstrap-lane-root.sh" "L1 AGENTS should document lane bootstrap helper"
assert_contains "README.md" "Organization docs profile" "L1 README should describe organization docs profile"
assert_contains "README.md" "Governance layering" "L1 README should describe governance layering"
assert_contains "README.md" "Community profile" "L1 README should describe community profile toggle"
assert_contains "README.md" "Release profile" "L1 README should describe release profile toggle"
assert_contains "README.md" "Baseline structure" "L1 README should describe baseline directory structure"
assert_contains "README.md" "Deterministic ROCS launcher" "L1 README should document deterministic ROCS launcher"
assert_contains "README.md" "Deterministic Agent Kernel launcher" "L1 README should document deterministic Agent Kernel launcher"
assert_contains "README.md" "Multi-pass template suffix policy" "L1 README should document multi-pass suffix policy"
assert_contains "README.md" "repo-local diary" "L1 README should document repo-local diary contract"
assert_contains "README.md" "no automatic in-place migrator" "L1 README should describe deterministic migration limitation"
assert_contains "README.md" ".gitattributes" "L1 README should mention git baseline files"
assert_contains "README.md" "tpl-project-repo-file-contract.md" "L1 README should link canonical tpl-project-repo file contract"
assert_contains "README.md" "bootstrap-lane-root.sh" "L1 README should document lane bootstrap workflow"
assert_contains ".gitignore" "!owned/.gitignore" "L1 parent .gitignore must unignore owned lane-root .gitignore"
assert_contains ".gitignore" "!contrib/.gitignore" "L1 parent .gitignore must unignore contrib lane-root .gitignore"
assert_contains ".gitignore" "!infra/.gitignore" "L1 parent .gitignore must unignore infra lane-root .gitignore"
assert_contains ".gitignore" "!agents/.gitignore" "L1 parent .gitignore must unignore agents lane-root .gitignore"
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
for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo; do
  assert_contains "copier/$tpl/copier.yml" "company_slug" "L2 template $tpl must expose company_slug"
  assert_contains "copier/$tpl/copier.yml" "repo_slug" "L2 template $tpl must expose repo_slug"
  assert_contains "copier/$tpl/copier.yml" "enable_community_pack" "L2 template $tpl must expose community pack toggle"
  assert_contains "copier/$tpl/copier.yml" "enable_release_pack" "L2 template $tpl must expose release pack toggle"
  assert_contains "copier/$tpl/copier.yml" "enable_vouch_gate" "L2 template $tpl must expose vouch gate toggle"
done

assert_contains "scripts/new-repo-from-copier.sh" "tpl-agent-repo" "L1 wrapper must list tpl-agent-repo template"
assert_contains "scripts/new-repo-from-copier.sh" "tpl-org-repo" "L1 wrapper must list tpl-org-repo template"
assert_contains "scripts/new-repo-from-copier.sh" "tpl-project-repo" "L1 wrapper must list tpl-project-repo template"
assert_contains "scripts/new-repo-from-copier.sh" "tpl-monorepo" "L1 wrapper must list tpl-monorepo template"
assert_contains "scripts/new-repo-from-copier.sh" "tpl-package" "L1 wrapper must list tpl-package template"
assert_contains "scripts/bootstrap-lane-root.sh" "--init-lane-git" "lane bootstrap helper must support lane git initialization"
assert_contains "scripts/bootstrap-lane-root.sh" "tpl-project-repo" "lane bootstrap helper must render tpl-project-repo baseline"

expected_pin='COPIER_VERSION="${COPIER_VERSION:-9.11.1}"'
expected_uvx='uvx --from "copier==${COPIER_VERSION}" copier'
expected_uvtool='uv tool run --from "copier==${COPIER_VERSION}" copier'
fallback_warning='warning: uvx/uv not found; falling back to unpinned copier on PATH'
uvx_guard='if command -v uvx >/dev/null 2>&1; then'
uv_guard='if command -v uv >/dev/null 2>&1; then'
copier_guard='if command -v copier >/dev/null 2>&1; then'

assert_contains "scripts/new-repo-from-copier.sh" "$expected_pin" "L1 wrapper must pin Copier version"
assert_contains "scripts/new-repo-from-copier.sh" "$expected_uvx" "L1 wrapper must use pinned uvx invocation"
assert_contains "scripts/new-repo-from-copier.sh" "$expected_uvtool" "L1 wrapper must use pinned uv tool invocation"
assert_contains "scripts/new-repo-from-copier.sh" "$fallback_warning" "L1 wrapper must surface unpinned fallback warning"
assert_not_contains "scripts/new-repo-from-copier.sh" "uvx copier" "L1 wrapper must not call unpinned uvx copier"
assert_line_precedes "scripts/new-repo-from-copier.sh" "$uvx_guard" "$uv_guard" "L1 wrapper must prefer uvx before uv tool run"
assert_line_precedes "scripts/new-repo-from-copier.sh" "$uv_guard" "$copier_guard" "L1 wrapper must prefer pinned runtimes before unpinned copier"
assert_contains "scripts/ak.sh" "deterministic resolution order" "L1 AK wrapper should document deterministic resolution order"
assert_contains "scripts/ak.sh" "work-items check" "L1 AK wrapper should document work-items projection commands"

workflow=".github/workflows/template-check.yml"
assert_contains "$workflow" "pull_request:" "template-check workflow must run on pull requests"
assert_contains "$workflow" "push:" "template-check workflow must run on pushes"
assert_contains "$workflow" "./scripts/check-template-ci.sh" "template-check workflow must run template checks"

ci_workflow=".github/workflows/ci.yml"
assert_contains "$ci_workflow" "Setup uv (full lane)" "ci full lane must provision uv before running full checks"
assert_contains "$ci_workflow" "Run full lane" "ci workflow must expose full lane"

assert_contains ".githooks/pre-commit" "scripts/ci/smoke.sh" "pre-commit must run smoke lane"
assert_contains ".githooks/pre-push" "scripts/ci/full.sh" "pre-push must run full lane"
assert_contains "scripts/ci/full.sh" "scripts/ak.sh" "L1 full CI should use scripts/ak.sh for work-items projection checks"
assert_not_contains "scripts/ci/full.sh" "crates/ak-cli/Cargo.toml" "L1 full CI must not gate AK checks on vendored ak-cli"
assert_contains "scripts/ci/full.sh" "scripts/rocs.sh" "L1 full CI should use scripts/rocs.sh when ontology is present"
assert_not_contains "scripts/install-hooks.sh" "copier/template-repo" "install-hooks must not reference removed legacy template-repo path"
assert_contains "scripts/install-hooks.sh" "scripts/bootstrap-lane-root.sh" "install-hooks must normalize executable bit for lane bootstrap helper"
assert_contains "scripts/install-hooks.sh" "scripts/ak.sh" "install-hooks must normalize executable bit for the L1 AK wrapper"
for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo tpl-package; do
  if [ "$tpl" != "tpl-package" ]; then
    assert_contains "scripts/install-hooks.sh" "copier/$tpl/scripts/ak.sh" "install-hooks must include executable bit normalization for $tpl AK wrapper"
  fi
  assert_contains "scripts/install-hooks.sh" "copier/$tpl/scripts/rocs.sh.j2" "install-hooks must include executable bit normalization for $tpl rocs wrapper"
  assert_contains "scripts/install-hooks.sh" "copier/$tpl/scripts/ci/smoke.sh" "install-hooks must include executable bit normalization for $tpl smoke lane"
  assert_contains "scripts/install-hooks.sh" "copier/$tpl/scripts/ci/full.sh" "install-hooks must include executable bit normalization for $tpl full lane"
done
assert_not_contains "scripts/ci/smoke.sh" "copier/template-repo/copier.yml" "L1 smoke lane must not lint removed legacy template-repo path"
assert_contains "scripts/ci/smoke.sh" "copier.yml copier/*/copier.yml" "L1 smoke lane should lint nested copier configs"

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

# Ensure no generated Python build/cache artifacts are committed in embedded templates
if find copier -type d \( -name '__pycache__' -o -name '*.egg-info' \) | grep -q .; then
  fail "embedded template source contains generated python cache/metadata directories"
fi
if find copier -type f -name '*.pyc' | grep -q .; then
  fail "embedded template source contains generated python bytecode files"
fi
if find copier -type d -path '*/tools/rocs-cli/build' | grep -q .; then
  fail "embedded template source contains rocs-cli build output directory"
fi

# Test L2 generation for each template
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo; do
  l2_dir="$tmp_root/$tpl"
  ./scripts/new-repo-from-copier.sh "$tpl" "$l2_dir" \
    -d repo_slug="$tpl" \
    --defaults --overwrite >/dev/null

  # Basic L2 checks
  assert_file "$l2_dir/.copier-answers.yml"
  assert_file "$l2_dir/AGENTS.md"
  assert_file "$l2_dir/CODEOWNERS"
  assert_file "$l2_dir/scripts/ak.sh"
  assert_file "$l2_dir/scripts/rocs.sh"
  assert_file "$l2_dir/scripts/ci/smoke.sh"
  assert_file "$l2_dir/scripts/ci/full.sh"
  assert_file "$l2_dir/diary/README.md"
  if [ "$tpl" = "tpl-project-repo" ] || [ "$tpl" = "tpl-monorepo" ]; then
    assert_file "$l2_dir/governance/work-items.cue"
    assert_file "$l2_dir/governance/work-items.json"
  fi
  assert_contains "$l2_dir/diary/README.md" "YYYY-MM-DD--type-scope-summary.md" "generated $tpl diary README should enforce descriptive filename convention"
  assert_not_dir "$l2_dir/docs/diary"
  assert_exec "$l2_dir/scripts/ak.sh"
  assert_exec "$l2_dir/scripts/rocs.sh"
  assert_contains "$l2_dir/AGENTS.md" "Deterministic tooling policy" "generated $tpl AGENTS should include deterministic tooling policy"
  assert_contains "$l2_dir/AGENTS.md" "scripts/rocs.sh" "generated $tpl AGENTS should reference scripts/rocs.sh"
  assert_contains "$l2_dir/AGENTS.md" "diary/" "generated $tpl AGENTS should reference repo-local diary"
  assert_contains "$l2_dir/README.md" "ROCS command flow" "generated $tpl README should include ROCS command flow section"
  if [ "$tpl" = "tpl-project-repo" ] || [ "$tpl" = "tpl-monorepo" ]; then
    assert_contains "$l2_dir/README.md" "Agent Kernel work-items flow" "generated $tpl README should document the AK work-items workflow"
    assert_contains "$l2_dir/governance/README.md" "work-items export" "generated $tpl governance README should document projection export"
  fi

  # Initialize git for smoke + idempotency test (smoke requires git repo)
  (
    cd "$l2_dir"
    git init -b main >/dev/null
    git config user.name "l1-template ci" >/dev/null
    git config user.email "ci@l1-template.local" >/dev/null
    git add . >/dev/null
    git commit -m "initial L2 render" >/dev/null
    ./scripts/ci/smoke.sh >/dev/null
    if command -v ak >/dev/null 2>&1 && { [ "$tpl" = "tpl-project-repo" ] || [ "$tpl" = "tpl-monorepo" ]; }; then
      ./scripts/ak.sh work-items check --repo . --path governance/work-items.json >/dev/null
    fi
  )

  ./scripts/new-repo-from-copier.sh "$tpl" "$l2_dir" \
    -d repo_slug="$tpl" \
    --defaults --overwrite >/dev/null

  (
    cd "$l2_dir"
    if [ -n "$(git status --porcelain)" ]; then
      echo "error: non-idempotent L1 -> L2 generation ($tpl)" >&2
      git status --short >&2
      exit 1
    fi
  )
done

# Test tpl-package separately (different parameters, no git required)
tpl="tpl-package"
l2_dir="$tmp_root/$tpl"
./scripts/new-repo-from-copier.sh "$tpl" "$l2_dir" \
  -d package_name="$tpl" \
  -d package_type=library \
  -d language=python \
  --defaults --overwrite >/dev/null

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

# tpl-package idempotency check (no git required)
./scripts/new-repo-from-copier.sh "$tpl" "$l2_dir" \
  -d package_name="$tpl" \
  -d package_type=library \
  -d language=python \
  --defaults --overwrite >/dev/null

# Elixir stack-contract smoke for project + package templates.
elixir_project_dir="$tmp_root/tpl-project-repo-elixir"
./scripts/new-repo-from-copier.sh tpl-project-repo "$elixir_project_dir" \
  -d repo_slug=fixture-project-elixir \
  -d language=elixir \
  -d enable_software_pack=true \
  --defaults --overwrite >/dev/null
assert_file "$elixir_project_dir/mix.exs"
assert_file "$elixir_project_dir/policy/stack-lane.json"
assert_file "$elixir_project_dir/docs/tech-stack.local.md"
assert_contains "$elixir_project_dir/policy/stack-lane.json" '"lane": "elixir"' "generated elixir project should pin the elixir stack lane"
assert_contains "$elixir_project_dir/docs/tech-stack.local.md" "tech-stack-core show elixir --prefer-repo" "generated elixir project should reference the elixir lane command"
if command -v ak >/dev/null 2>&1; then
  (
    cd "$elixir_project_dir"
    ./scripts/ak.sh work-items check --repo . --path governance/work-items.json >/dev/null
  )
fi

elixir_package_dir="$tmp_root/tpl-package-elixir"
./scripts/new-repo-from-copier.sh tpl-package "$elixir_package_dir" \
  -d package_name=fixture-elixir-core \
  -d package_type=library \
  -d language=elixir \
  --defaults --overwrite >/dev/null
assert_file "$elixir_package_dir/policy/stack-lane.json"
assert_file "$elixir_package_dir/docs/tech-stack.local.md"
assert_contains "$elixir_package_dir/policy/stack-lane.json" '"lane": "elixir"' "generated elixir package should pin the elixir stack lane"
assert_contains "$elixir_package_dir/docs/tech-stack.local.md" "tech-stack-core show elixir --prefer-repo" "generated elixir package should reference the elixir lane command"

# Detailed check for tpl-project-repo (primary template)
l2_dir="$tmp_root/tpl-project-repo"
assert_contains "$l2_dir/AGENTS.md" "Recursion policy" "generated L2 AGENTS.md must include recursion section"
assert_contains "$l2_dir/AGENTS.md" "Deterministic tooling policy" "generated L2 AGENTS.md must include deterministic tooling policy"
assert_contains "$l2_dir/AGENTS.md" "scripts/rocs.sh" "generated L2 AGENTS.md must reference scripts/rocs.sh"
assert_contains "$l2_dir/AGENTS.md" "diary/" "generated L2 AGENTS.md must reference repo-local diary"

echo "ok: template ci"
