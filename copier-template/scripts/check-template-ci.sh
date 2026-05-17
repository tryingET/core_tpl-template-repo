#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root"

need_cmd() {
	command -v "$1" >/dev/null 2>&1 || {
		echo "error: missing dependency: $1" >&2
		exit 2
	}
}

need_cmd awk
need_cmd cp
need_cmd find
need_cmd git
need_cmd grep
need_cmd mktemp
need_cmd python3
need_cmd sort

answers_lib="$repo_root/scripts/lib/copier-answers.sh"
[ -f "$answers_lib" ] || {
	echo "error: missing dependency: $answers_lib" >&2
	exit 2
}
# shellcheck source=/dev/null
. "$answers_lib"

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

assert_files_equal() {
	left="$1"
	right="$2"
	label="$3"

	set +e
	git diff --no-index --quiet -- "$left" "$right"
	status=$?
	set -e

	if [ "$status" -eq 0 ]; then
		return
	fi
	if [ "$status" -eq 1 ]; then
		echo "error: $label" >&2
		git --no-pager diff --no-index -- "$left" "$right" >&2 || true
		exit 1
	fi

	fail "$label (diff command failed)"
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
		rel_path="${abs_path#"$template_dir"/}"
		case "$rel_path" in
		*/__pycache__/* | *.pyc)
			continue
			;;
		esac
		printf '%s\n' "$rel_path"
	done | LC_ALL=C sort
}

value_from_answers() {
	answers_file="$1"
	key="$2"
	value=""
	status=0

	value="$(copier_answers_try_scalar "$answers_file" "$key" 2>/dev/null)" || status=$?

	if [ "$status" -eq 0 ]; then
		printf '%s\n' "$value"
		return 0
	fi

	echo "error: unable to parse '$key' from $answers_file; install python3/python with PyYAML for multiline or escaped Copier answers" >&2
	return "$status"
}

bool_from_answers() {
	value=""
	value_status=0

	value="$(value_from_answers "$1" "$2")" || value_status=$?
	case "$value_status" in
	0) ;;
	1)
		return 1
		;;
	*)
		return "$value_status"
		;;
	esac

	[ -n "$value" ] || return 0
	printf '%s\n' "$value" | tr '[:upper:]' '[:lower:]'
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
scripts/check-task-scope-snapshots.sh
scripts/rocs.sh
scripts/check-template-ci.sh
scripts/install-hooks.sh
scripts/lib/check-template-ak.py
scripts/lib/check-task-scope-snapshots.py
scripts/lib/copier-answers.sh
scripts/lib/repo-surface.sh
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

assert_not_file "scripts/ak.sh"
assert_not_file "scripts/cargo-operator.sh"

for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo; do
	assert_files_equal "scripts/lib/copier-answers.sh" "copier/$tpl/scripts/lib/copier-answers.sh" "generated copier-answers helper must stay identical in $tpl"
	assert_files_equal "scripts/lib/repo-surface.sh" "copier/$tpl/scripts/lib/repo-surface.sh.j2" "generated repo-surface helper must stay identical in $tpl"
done

# L2 embedded templates required
for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo tpl-package; do
	assert_dir "copier/$tpl"
	assert_file "copier/$tpl/copier.yml"
	assert_file "copier/$tpl/contracts/layer-contract.yml"
	assert_file "copier/$tpl/AGENTS.md.j2"
	assert_file "copier/$tpl/CODEOWNERS.j2"
	assert_file "copier/$tpl/.copier-answers.yml.j2"
	assert_contains "copier/$tpl/.copier-answers.yml.j2" "to_nice_yaml" "L2 template $tpl answers template should use canonical Copier YAML emission"
	if [ "$tpl" != "tpl-package" ]; then
		assert_not_file "copier/$tpl/scripts/ak.sh"
		assert_not_file "copier/$tpl/scripts/cargo-operator.sh"
		assert_file "copier/$tpl/scripts/lib/check-task-scope-snapshots.py"
		assert_file "copier/$tpl/scripts/lib/copier-answers.sh"
		assert_file "copier/$tpl/scripts/lib/repo-surface.sh.j2"
	fi
	if [ "$tpl" != "tpl-package" ]; then
		assert_file "copier/$tpl/scripts/check-task-scope-snapshots.sh"
		assert_file "copier/$tpl/scripts/preflight-repo-census.sh.j2"
		assert_exec "copier/$tpl/scripts/check-task-scope-snapshots.sh"
	fi
	assert_file "copier/$tpl/scripts/rocs.sh.j2"
	assert_exec "copier/$tpl/scripts/rocs.sh.j2"
	if [ "$tpl" = "tpl-package" ]; then
		assert_contains "copier/$tpl/scripts/rocs.sh.j2" "ROCS commands should be run from the monorepo root." "L2 template $tpl ROCS wrapper should remain a monorepo-root placeholder"
		assert_contains "copier/$tpl/scripts/rocs.sh.j2" "Use: ../../scripts/rocs.sh <args>" "L2 template $tpl ROCS wrapper should redirect to the monorepo-root launcher"
	fi
	assert_contains "copier/$tpl/contracts/layer-contract.yml" "layer: L2" "L2 template $tpl contract must declare layer L2"
	assert_contains "copier/$tpl/contracts/layer-contract.yml" "L1 -> L2" "L2 template $tpl contract must include allowed L1 -> L2 transition"
	assert_contains "copier/$tpl/contracts/layer-contract.yml" "L2 -> L1" "L2 template $tpl contract must include forbidden L2 -> L1 transition"
	assert_contains "copier/$tpl/contracts/layer-contract.yml" "max_layer_depth: 2" "L2 template $tpl contract must cap layer depth"
	assert_file "copier/$tpl/scripts/ci/smoke.sh"
	if [ "$tpl" = "tpl-project-repo" ]; then
		assert_file "copier/$tpl/scripts/ci/fast.sh"
	fi
	assert_file "copier/$tpl/scripts/ci/full.sh"
	assert_file "copier/$tpl/diary/README.md"
	assert_contains "copier/$tpl/diary/README.md" "YYYY-MM-DD--type-scope-summary.md" "L2 template $tpl diary README should enforce descriptive filename convention"
	assert_not_dir "copier/$tpl/docs/diary"
	assert_contains "copier/$tpl/AGENTS.md.j2" "Deterministic tooling policy" "L2 template $tpl AGENTS should include deterministic tooling policy"
	assert_contains "copier/$tpl/AGENTS.md.j2" "scripts/rocs.sh" "L2 template $tpl AGENTS should reference scripts/rocs.sh"
	assert_contains "copier/$tpl/AGENTS.md.j2" "diary/" "L2 template $tpl AGENTS should reference repo-local diary"
	assert_contains "copier/$tpl/README.md.j2" "ROCS command flow" "L2 template $tpl README should include ROCS command flow section"
	if [ "$tpl" != "tpl-package" ]; then
		assert_contains "copier/$tpl/README.md.j2" "check-task-scope-snapshots.sh" "L2 template $tpl README should document task-scope snapshot validation"
		assert_contains "copier/$tpl/scripts/check-task-scope-snapshots.sh" "scripts/lib/check-task-scope-snapshots.py" "L2 template $tpl task-scope checker should use the shared parser-backed helper"
		assert_contains "copier/$tpl/scripts/preflight-repo-census.sh.j2" "scripts/lib/repo-surface.sh" "L2 template $tpl repo census helper should source the shared repo-surface helper"
		assert_contains "copier/$tpl/scripts/ci/full.sh" "work-items check" "L2 template $tpl full CI should run AK work-items projection checks"
		assert_not_contains "copier/$tpl/scripts/ci/full.sh" "crates/ak-cli/Cargo.toml" "L2 template $tpl full CI must not gate AK checks on vendored ak-cli"
		assert_contains "copier/$tpl/scripts/ci/full.sh" "check-task-scope-snapshots.sh" "L2 template $tpl full CI should enforce task-scope snapshot checks"
	fi
	assert_contains "copier/$tpl/scripts/ci/full.sh" "scripts/rocs.sh" "L2 template $tpl full CI should use scripts/rocs.sh when ontology is present"
done
for tpl in tpl-agent-repo tpl-org-repo; do
	assert_file "copier/$tpl/governance/README.md"
	assert_contains "copier/$tpl/governance/README.md" "check-task-scope-snapshots.sh" "L2 template $tpl governance README should document task-scope snapshot validation"
	assert_contains "copier/$tpl/governance/README.md" "transitional scaffolding" "L2 template $tpl governance README should keep non-authoritative task-scope wording"
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
assert_contains "copier/tpl-project-repo/copier.yml" 'default: "<repo:core/ontology-kernel@main>"' "tpl-project-repo should default core ontology refs to workspace repo locators"
assert_contains "copier/tpl-project-repo/copier.yml" 'default: "<repo:{{ company_slug }}/ontology@main>"' "tpl-project-repo should default company ontology refs to workspace repo locators"
assert_contains "copier/tpl-project-repo/tools/rocs-cli/README.md" 'Legacy `<gitlab:...>` locators are no longer supported.' "tpl-project-repo vendored rocs-cli README should document workspace-only ref resolution"
assert_contains "copier/tpl-project-repo/tools/rocs-cli/src/rocs_cli/layers.py" "legacy gitlab ref locators are no longer supported" "tpl-project-repo vendored rocs-cli should reject legacy gitlab locators"
assert_file "copier/tpl-project-repo/tools/rocs-cli/src/rocs_cli/workspace.py"
assert_not_file "copier/tpl-project-repo/tools/rocs-cli/src/rocs_cli/gitlab.py"

check_multi_pass_suffix_policy

required_exec="
scripts/new-repo-from-copier.sh
scripts/bootstrap-lane-root.sh
scripts/check-task-scope-snapshots.sh
scripts/rocs.sh
scripts/check-template-ci.sh
scripts/install-hooks.sh
scripts/lib/check-template-ak.py
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
assert_contains "AGENTS.md" 'AK CLI: `ak <ak args...>`' "L1 AGENTS should document plain ak as the canonical operator path"
assert_contains "AGENTS.md" "scripts/rocs.sh" "L1 AGENTS should reference scripts/rocs.sh"
assert_contains "README.md" "check-task-scope-snapshots.sh" "L1 README should document task-scope snapshot validation"
assert_contains "governance/README.md" "check-task-scope-snapshots.sh" "L1 governance README should document task-scope snapshot validation"
assert_contains "AGENTS.md" "diary/" "L1 AGENTS should require repo-local diary"
assert_contains "AGENTS.md" "L2 Templates" "L1 AGENTS should document L2 templates"
assert_contains "AGENTS.md" "bootstrap-lane-root.sh" "L1 AGENTS should document lane bootstrap helper"
assert_contains "README.md" "Organization docs profile" "L1 README should describe organization docs profile"
assert_contains "README.md" "Governance layering" "L1 README should describe governance layering"
assert_contains "README.md" "Community profile" "L1 README should describe community profile toggle"
assert_contains "README.md" "Release profile" "L1 README should describe release profile toggle"
assert_contains "README.md" "Baseline structure" "L1 README should describe baseline directory structure"
assert_contains "README.md" "Deterministic ROCS launcher" "L1 README should document deterministic ROCS launcher"
assert_contains "README.md" "Agent Kernel command flow" "L1 README should document plain ak command flow"
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
assert_contains ".copier-answers.yml" "l2_org_docs_default:" "L1 answers file should persist default L2 org-context profile"
assert_contains ".copier-answers.yml" "l1_profile:" "L1 answers file should persist a resolved profile label"
assert_not_contains "README.md" '- Profile: ``' "L1 README should not render an empty profile label"
assert_not_contains "README.md" '- Default L2 project/monorepo org-context profile: ``' "L1 README should not render an empty default L2 org-context profile"
if grep -Eq '^  profile:[[:space:]]*$' "$provenance"; then
	fail "L1 provenance seal must not render an empty profile label"
fi

# Check L2 template copier configs
for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo; do
	assert_contains "copier/$tpl/copier.yml" "company_slug" "L2 template $tpl must expose company_slug"
	assert_contains "copier/$tpl/copier.yml" "repo_slug" "L2 template $tpl must expose repo_slug"
	assert_contains "copier/$tpl/copier.yml" "enable_community_pack" "L2 template $tpl must expose community pack toggle"
	assert_contains "copier/$tpl/copier.yml" "enable_release_pack" "L2 template $tpl must expose release pack toggle"
	assert_contains "copier/$tpl/copier.yml" "enable_vouch_gate" "L2 template $tpl must expose vouch gate toggle"
done
assert_contains "copier/tpl-project-repo/copier.yml" "org_docs_profile" "tpl-project-repo must expose org-context profile"
assert_contains "copier/tpl-monorepo/copier.yml" "org_docs_profile" "tpl-monorepo must expose org-context profile"

assert_contains "scripts/new-repo-from-copier.sh" "tpl-agent-repo" "L1 wrapper must list tpl-agent-repo template"
assert_contains "scripts/new-repo-from-copier.sh" "tpl-org-repo" "L1 wrapper must list tpl-org-repo template"
assert_contains "scripts/new-repo-from-copier.sh" "tpl-project-repo" "L1 wrapper must list tpl-project-repo template"
assert_contains "scripts/new-repo-from-copier.sh" "tpl-monorepo" "L1 wrapper must list tpl-monorepo template"
assert_contains "scripts/new-repo-from-copier.sh" "tpl-package" "L1 wrapper must list tpl-package template"
assert_contains "scripts/bootstrap-lane-root.sh" "--init-lane-git" "lane bootstrap helper must support lane git initialization"
assert_contains "scripts/bootstrap-lane-root.sh" "tpl-project-repo" "lane bootstrap helper must render tpl-project-repo baseline"
assert_contains "scripts/bootstrap-lane-root.sh" "scripts/lib/repo-surface.sh" "lane bootstrap helper should source the shared repo-surface helper"
assert_contains "scripts/bootstrap-lane-root.sh" "repo_surface_lane_root_src_path" "lane bootstrap helper should derive a stable lane-root source path"
assert_contains "scripts/bootstrap-lane-root.sh" "!contracts/**" "lane bootstrap helper should track layer contracts in lane-root baselines"
assert_contains "scripts/bootstrap-lane-root.sh" '!$lane/contracts/**' "lane bootstrap helper should unignore lane-root contracts in parent gitignore"
assert_not_contains "scripts/bootstrap-lane-root.sh" "sed -i" "lane bootstrap helper must not rely on GNU sed -i"

expected_pin="COPIER_VERSION=\"\${COPIER_VERSION:-9.11.1}\""
expected_uvx="uvx --from \"copier==\${COPIER_VERSION}\" copier"
expected_uvtool="uv tool run --from \"copier==\${COPIER_VERSION}\" copier"
fallback_warning='warning: uvx/uv not found; falling back to unpinned copier on PATH'
uvx_guard='if command -v uvx >/dev/null 2>&1; then'
uv_guard='if command -v uv >/dev/null 2>&1; then'
copier_guard='if command -v copier >/dev/null 2>&1; then'

assert_contains "scripts/new-repo-from-copier.sh" "$expected_pin" "L1 wrapper must pin Copier version"
assert_contains "scripts/new-repo-from-copier.sh" "scripts/lib/copier-answers.sh" "L1 wrapper should source the shared copier answers helper"
assert_contains "scripts/new-repo-from-copier.sh" "assert_repo_layer \"\$repo_root\" \"L1\"" "L1 wrapper should verify it is running from an L1 contract root"
assert_contains "scripts/new-repo-from-copier.sh" "destination already declares layer" "L1 wrapper should fail closed on destination layer mismatches"
assert_contains "scripts/new-repo-from-copier.sh" "$expected_uvx" "L1 wrapper must use pinned uvx invocation"
assert_contains "scripts/new-repo-from-copier.sh" "$expected_uvtool" "L1 wrapper must use pinned uv tool invocation"
assert_contains "scripts/new-repo-from-copier.sh" "$fallback_warning" "L1 wrapper must surface unpinned fallback warning"
assert_not_contains "scripts/new-repo-from-copier.sh" "uvx copier" "L1 wrapper must not call unpinned uvx copier"
assert_line_precedes "scripts/new-repo-from-copier.sh" "$uvx_guard" "$uv_guard" "L1 wrapper must prefer uvx before uv tool run"
assert_line_precedes "scripts/new-repo-from-copier.sh" "$uv_guard" "$copier_guard" "L1 wrapper must prefer pinned runtimes before unpinned copier"
assert_contains "scripts/check-task-scope-snapshots.sh" "scripts/lib/check-task-scope-snapshots.py" "L1 task-scope checker should use the shared parser-backed helper"
assert_contains "scripts/check-template-ci.sh" "scripts/lib/copier-answers.sh" "L1 template CI should source the shared copier answers helper"
assert_contains "scripts/check-template-ci.sh" "scripts/lib/repo-surface.sh" "L1 template CI should require the shared repo-surface helper"

workflow=".github/workflows/template-check.yml"
assert_contains "$workflow" "pull_request:" "template-check workflow must run on pull requests"
assert_contains "$workflow" "push:" "template-check workflow must run on pushes"
assert_contains "$workflow" "./scripts/check-template-ci.sh" "template-check workflow must run template checks"

ci_workflow=".github/workflows/ci.yml"
assert_contains "$ci_workflow" "Setup uv (full lane)" "ci full lane must provision uv before running full checks"
assert_contains "$ci_workflow" "Run full lane" "ci workflow must expose full lane"

assert_contains ".githooks/pre-commit" "scripts/ci/smoke.sh" "pre-commit must run smoke lane"
assert_contains ".githooks/pre-push" "scripts/ci/full.sh" "pre-push must run full lane"
assert_contains "scripts/ci/full.sh" "work-items check" "L1 full CI should run AK work-items projection checks"
assert_contains "scripts/ci/full.sh" "check-task-scope-snapshots.sh" "L1 full CI should enforce task-scope snapshot checks"
assert_not_contains "scripts/ci/full.sh" "crates/ak-cli/Cargo.toml" "L1 full CI must not gate AK checks on vendored ak-cli"
assert_contains "scripts/ci/full.sh" "scripts/rocs.sh" "L1 full CI should use scripts/rocs.sh when ontology is present"
assert_not_contains "scripts/install-hooks.sh" "copier/template-repo" "install-hooks must not reference removed legacy template-repo path"
assert_contains "scripts/install-hooks.sh" "scripts/bootstrap-lane-root.sh" "install-hooks must normalize executable bit for lane bootstrap helper"
assert_contains "scripts/install-hooks.sh" "scripts/rocs.sh" "install-hooks must normalize executable bit for the L1 ROCS wrapper"
assert_contains "scripts/install-hooks.sh" "scripts/check-task-scope-snapshots.sh" "install-hooks must normalize executable bit for the L1 task-scope checker"
for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo tpl-package; do
	if [ "$tpl" != "tpl-package" ]; then
		assert_contains "scripts/install-hooks.sh" "copier/$tpl/scripts/check-task-scope-snapshots.sh" "install-hooks must include executable bit normalization for $tpl task-scope checker"
	fi
	assert_contains "scripts/install-hooks.sh" "copier/$tpl/scripts/rocs.sh.j2" "install-hooks must include executable bit normalization for $tpl rocs wrapper"
	assert_contains "scripts/install-hooks.sh" "copier/$tpl/scripts/ci/smoke.sh" "install-hooks must include executable bit normalization for $tpl smoke lane"
	if [ "$tpl" = "tpl-project-repo" ]; then
		assert_contains "scripts/install-hooks.sh" "copier/$tpl/scripts/ci/fast.sh" "install-hooks must include executable bit normalization for $tpl fast lane"
	fi
	assert_contains "scripts/install-hooks.sh" "copier/$tpl/scripts/ci/full.sh" "install-hooks must include executable bit normalization for $tpl full lane"
done
assert_not_contains "scripts/ci/smoke.sh" "copier/template-repo/copier.yml" "L1 smoke lane must not lint removed legacy template-repo path"
assert_contains "scripts/ci/smoke.sh" "copier.yml copier/*/copier.yml" "L1 smoke lane should lint nested copier configs"

vouch_enabled=""
vouch_enabled_status=0
vouch_enabled="$(bool_from_answers .copier-answers.yml enable_vouch_gate)" || vouch_enabled_status=$?
case "$vouch_enabled_status" in
0 | 1) ;;
*)
	exit "$vouch_enabled_status"
	;;
esac
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

community_enabled=""
community_enabled_status=0
community_enabled="$(bool_from_answers .copier-answers.yml enable_community_pack)" || community_enabled_status=$?
case "$community_enabled_status" in
0 | 1) ;;
*)
	exit "$community_enabled_status"
	;;
esac
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

release_enabled=""
release_enabled_status=0
release_enabled="$(bool_from_answers .copier-answers.yml enable_release_pack)" || release_enabled_status=$?
case "$release_enabled_status" in
0 | 1) ;;
*)
	exit "$release_enabled_status"
	;;
esac
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

l1_profile=""
l1_profile_status=0
l1_profile="$(value_from_answers .copier-answers.yml l1_profile)" || l1_profile_status=$?
case "$l1_profile_status" in
0)
	case "$l1_profile" in
	internal-lean | internal-standard | internal-governed | public-collaboration | public-trust-gated | public-rich-org | custom) ;;
	*)
		fail "L1 answers file must persist a recognized resolved profile label (got: ${l1_profile:-<empty>})"
		;;
	esac
	;;
*)
	exit "$l1_profile_status"
	;;
esac

l1_org_docs_profile=""
l1_org_docs_profile_status=0
l1_org_docs_profile="$(value_from_answers .copier-answers.yml l1_org_docs_profile)" || l1_org_docs_profile_status=$?
case "$l1_org_docs_profile_status" in
0 | 1) ;;
*)
	exit "$l1_org_docs_profile_status"
	;;
esac
[ -n "$l1_org_docs_profile" ] || l1_org_docs_profile="rich"

l2_org_docs_default=""
l2_org_docs_default_status=0
l2_org_docs_default="$(value_from_answers .copier-answers.yml l2_org_docs_default)" || l2_org_docs_default_status=$?
case "$l2_org_docs_default_status" in
0)
	case "$l2_org_docs_default" in
	compact | rich) ;;
	*)
		fail "L1 answers file must persist a recognized default L2 org-context profile (got: ${l2_org_docs_default:-<empty>})"
		;;
	esac
	;;
*)
	exit "$l2_org_docs_default_status"
	;;
esac

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
l1_task_scopes_dir="$repo_root/governance/task-scopes"
l1_task_scopes_backup="$tmp_root/l1-task-scopes-backup"
l1_task_scopes_had_existing=0

restore_l1_task_scope_dir() {
	rm -rf "$l1_task_scopes_dir"

	if [ "$l1_task_scopes_had_existing" != "1" ]; then
		return 0
	fi

	mkdir -p "$l1_task_scopes_dir"
	if [ -n "$(find "$l1_task_scopes_backup" -mindepth 1 -print -quit)" ]; then
		cp -R "$l1_task_scopes_backup/." "$l1_task_scopes_dir/"
	fi
}

cleanup() {
	restore_l1_task_scope_dir
	rm -rf "$tmp_root"
}
trap cleanup EXIT INT TERM

no_yaml_bin="$tmp_root/no-yaml-bin"
mkdir -p "$no_yaml_bin"
for fake_python in python3 python; do
	cat >"$no_yaml_bin/$fake_python" <<'EOF'
#!/usr/bin/env sh
exit 1
EOF
	chmod +x "$no_yaml_bin/$fake_python"
done

ak_db="$tmp_root/check-template-ci.ak.db"
ak_test_double="$repo_root/scripts/lib/check-template-ak.py"
[ -x "$ak_test_double" ] || fail "missing executable AK test double: $ak_test_double"
ak_test_double_bin="$tmp_root/ak-test-double-bin"
mkdir -p "$ak_test_double_bin"
ln -s "$ak_test_double" "$ak_test_double_bin/ak"
export PATH="$ak_test_double_bin:$PATH"
export AK_BIN="ak"
export AK_DB="$ak_db"
ak -d "$ak_db" init >/dev/null

ensure_registered_repo() {
	repo_path="$1"

	if "$AK_BIN" -d "$ak_db" repo show "$repo_path" >/dev/null 2>&1; then
		return 0
	fi

	"$AK_BIN" -d "$ak_db" repo register "$repo_path" --company templateci >/dev/null
}

extract_created_task_id() {
	printf '%s\n' "$1" | awk '
    /^Created task [0-9]+:/ {
      line = $0
      sub(/^Created task /, "", line)
      sub(/:.*/, "", line)
      print line
      exit
    }
  '
}

create_scoped_task() {
	repo_path="$1"
	title="$2"

	ensure_registered_repo "$repo_path"
	create_output="$("$AK_BIN" -d "$ak_db" task create --repo "$repo_path" "$title")"
	task_id="$(extract_created_task_id "$create_output")"
	[ -n "$task_id" ] || fail "unable to parse task id from AK output: $create_output"

	"$AK_BIN" -d "$ak_db" task scope set "$task_id" --allowed README.md 'src/**' --required README.md >/dev/null
	printf '%s\n' "$task_id"
}

write_task_scope_snapshot() {
	repo_path="$1"
	task_id="$2"

	mkdir -p "$repo_path/governance/task-scopes"
	(
		cd "$repo_path"
		ak task scope export "$task_id" >"governance/task-scopes/AK-$task_id.snapshot.json"
	)
}

run_repo_cmd() {
	repo_path="$1"
	shift
	(
		cd "$repo_path"
		"$@"
	)
}

assert_command_fails() {
	label="$1"
	shift
	if "$@" >/dev/null 2>&1; then
		fail "$label"
	fi
}

assert_command_fails_with_stderr() {
	label="$1"
	needle="$2"
	shift 2

	stderr_file="$(mktemp "$tmp_root/assert-command-fails.XXXXXX")"
	if "$@" >/dev/null 2>"$stderr_file"; then
		rm -f "$stderr_file"
		fail "$label"
	fi

	if ! grep -qF -- "$needle" "$stderr_file"; then
		echo "error: $label (missing '$needle' in stderr)" >&2
		cat "$stderr_file" >&2 || true
		rm -f "$stderr_file"
		exit 1
	fi

	rm -f "$stderr_file"
}

prepare_full_ci_probe() {
	repo_path="$1"

	if [ -f "$repo_path/governance/work-items.json" ]; then
		run_repo_cmd "$repo_path" ak work-items export --repo . --path governance/work-items.json >/dev/null
	fi

	if [ -x "$repo_path/scripts/rocs.sh" ]; then
		cat >"$repo_path/scripts/rocs.sh" <<'EOF'
#!/usr/bin/env sh
exit 0
EOF
		chmod +x "$repo_path/scripts/rocs.sh"
	fi
}

if [ -d "$l1_task_scopes_dir" ]; then
	mkdir -p "$l1_task_scopes_backup"
	cp -R "$l1_task_scopes_dir/." "$l1_task_scopes_backup/"
	l1_task_scopes_had_existing=1
fi

l1_task_scope_id="$(create_scoped_task "$repo_root" "template-ci: generated L1 task-scope snapshot")"
write_task_scope_snapshot "$repo_root" "$l1_task_scope_id"
run_repo_cmd "$repo_root" ./scripts/check-task-scope-snapshots.sh >/dev/null
run_repo_cmd "$repo_root" ./scripts/ci/full.sh >/dev/null
restore_l1_task_scope_dir
assert_command_fails_with_stderr "generated L1 wrapper should reject L1 destinations" "destination already declares layer L1" ./scripts/new-repo-from-copier.sh tpl-project-repo "$repo_root" -d repo_slug=forbidden-l1-destination --defaults --overwrite

for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo; do
	l2_dir="$tmp_root/$tpl"
	./scripts/new-repo-from-copier.sh "$tpl" "$l2_dir" \
		-d repo_slug="$tpl" \
		--defaults --overwrite >/dev/null

	# Basic L2 checks
	assert_file "$l2_dir/.copier-answers.yml"
	assert_file "$l2_dir/contracts/layer-contract.yml"
	assert_contains "$l2_dir/contracts/layer-contract.yml" "layer: L2" "generated $tpl contract must declare layer L2"
	assert_file "$l2_dir/AGENTS.md"
	assert_file "$l2_dir/CODEOWNERS"
	assert_not_file "$l2_dir/scripts/ak.sh"
	assert_not_file "$l2_dir/scripts/cargo-operator.sh"
	assert_file "$l2_dir/scripts/lib/copier-answers.sh"
	assert_file "$l2_dir/scripts/lib/repo-surface.sh"
	if [ "$tpl" != "tpl-package" ]; then
		assert_file "$l2_dir/scripts/lib/check-task-scope-snapshots.py"
	fi
	assert_file "$l2_dir/scripts/rocs.sh"
	assert_file "$l2_dir/scripts/ci/smoke.sh"
	assert_file "$l2_dir/scripts/ci/full.sh"
	assert_file "$l2_dir/diary/README.md"
	if [ "$tpl" != "tpl-package" ]; then
		assert_file "$l2_dir/scripts/check-task-scope-snapshots.sh"
		assert_file "$l2_dir/scripts/preflight-repo-census.sh"
	fi
	if [ "$tpl" = "tpl-project-repo" ] || [ "$tpl" = "tpl-monorepo" ]; then
		assert_file "$l2_dir/governance/work-items.cue"
		assert_file "$l2_dir/governance/work-items.json"
		assert_contains "$l2_dir/.copier-answers.yml" "org_docs_profile: $l2_org_docs_default" "generated $tpl should inherit the parent L1 org-context default"
		assert_file "$l2_dir/docs/org_context/README.md"
		assert_file "$l2_dir/docs/org_context/org-summary.md"
		if [ "$l2_org_docs_default" = "rich" ]; then
			assert_file "$l2_dir/docs/org_context/mission.md"
			assert_file "$l2_dir/docs/org_context/purpose.md"
			assert_file "$l2_dir/docs/org_context/vision.md"
			assert_file "$l2_dir/docs/org_context/strategic_objectives.md"
			assert_file "$l2_dir/docs/org_context/governance.md"
		else
			assert_not_file "$l2_dir/docs/org_context/mission.md"
			assert_not_file "$l2_dir/docs/org_context/purpose.md"
			assert_not_file "$l2_dir/docs/org_context/vision.md"
			assert_not_file "$l2_dir/docs/org_context/strategic_objectives.md"
			assert_not_file "$l2_dir/docs/org_context/governance.md"
		fi
	fi
	assert_contains "$l2_dir/diary/README.md" "YYYY-MM-DD--type-scope-summary.md" "generated $tpl diary README should enforce descriptive filename convention"
	assert_not_dir "$l2_dir/docs/diary"
	if [ "$tpl" != "tpl-package" ]; then
		assert_exec "$l2_dir/scripts/check-task-scope-snapshots.sh"
		assert_contains "$l2_dir/scripts/check-task-scope-snapshots.sh" "scripts/lib/check-task-scope-snapshots.py" "generated $tpl task-scope checker should use the shared parser-backed helper"
	fi
	assert_exec "$l2_dir/scripts/rocs.sh"
	assert_contains "$l2_dir/AGENTS.md" "Deterministic tooling policy" "generated $tpl AGENTS should include deterministic tooling policy"
	assert_contains "$l2_dir/AGENTS.md" "scripts/rocs.sh" "generated $tpl AGENTS should reference scripts/rocs.sh"
	assert_contains "$l2_dir/AGENTS.md" "diary/" "generated $tpl AGENTS should reference repo-local diary"
	assert_contains "$l2_dir/README.md" "ROCS command flow" "generated $tpl README should include ROCS command flow section"
	if [ "$tpl" = "tpl-project-repo" ] || [ "$tpl" = "tpl-monorepo" ]; then
		assert_contains "$l2_dir/AGENTS.md" "policy/engineering-lane.json" "generated $tpl AGENTS should point to the pinned engineering contract"
		assert_contains "$l2_dir/AGENTS.md" "docs/engineering.local.md" "generated $tpl AGENTS should point to the local engineering override doc"
	fi
	if [ "$tpl" = "tpl-project-repo" ]; then
		assert_not_file "$l2_dir/policy/engineering-lane.json"
		assert_not_file "$l2_dir/docs/engineering.local.md"
	fi
	if [ "$tpl" != "tpl-package" ]; then
		assert_contains "$l2_dir/README.md" "check-task-scope-snapshots.sh" "generated $tpl README should document task-scope snapshot validation"
	fi
	if [ "$tpl" = "tpl-agent-repo" ] || [ "$tpl" = "tpl-org-repo" ]; then
		assert_file "$l2_dir/governance/README.md"
		assert_contains "$l2_dir/governance/README.md" "check-task-scope-snapshots.sh" "generated $tpl governance README should document task-scope snapshot validation"
	fi
	if [ "$tpl" = "tpl-project-repo" ] || [ "$tpl" = "tpl-monorepo" ]; then
		assert_contains "$l2_dir/README.md" "Agent Kernel work-items flow" "generated $tpl README should document the AK work-items workflow"
		assert_contains "$l2_dir/governance/README.md" "work-items export" "generated $tpl governance README should document projection export"
		assert_contains "$l2_dir/governance/README.md" "check-task-scope-snapshots.sh" "generated $tpl governance README should document task-scope snapshot validation"
	fi
	if [ "$tpl" = "tpl-monorepo" ]; then
		assert_not_contains "$l2_dir/README.md" "L2 → L3" "generated tpl-monorepo README must not advertise forbidden L3 recursion"
		assert_not_contains "$l2_dir/AGENTS.md" "L2 -> L3" "generated tpl-monorepo AGENTS must not advertise forbidden L3 recursion"
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
		if [ "$tpl" = "tpl-project-repo" ] || [ "$tpl" = "tpl-monorepo" ]; then
			ensure_registered_repo "$l2_dir"
			ak work-items check --repo . --path governance/work-items.json >/dev/null
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

bootstrap_smoke_dir="$tmp_root/tpl-project-repo-bootstrap-smoke"
./scripts/new-repo-from-copier.sh tpl-project-repo "$bootstrap_smoke_dir" \
	-d repo_slug=tpl-project-repo-bootstrap-smoke \
	--defaults --overwrite >/dev/null
(
	cd "$bootstrap_smoke_dir"
	git init -b work >/dev/null
	git config user.name "l1-template ci" >/dev/null
	git config user.email "ci@l1-template.local" >/dev/null
	git add . >/dev/null
	git commit -m "bootstrap smoke" >/dev/null
	./scripts/ci/smoke.sh >/dev/null 2>/dev/null
)

quoted_project_repo="$tmp_root/tpl-project-repo-quote\"repo"
./scripts/new-repo-from-copier.sh tpl-project-repo "$quoted_project_repo" \
	-d repo_slug=tpl-project-repo-quote-repo \
	--defaults --overwrite >/dev/null
quoted_project_task_id="$(create_scoped_task "$quoted_project_repo" "template-ci: quoted project task-scope snapshot")"
write_task_scope_snapshot "$quoted_project_repo" "$quoted_project_task_id"
run_repo_cmd "$quoted_project_repo" ./scripts/check-task-scope-snapshots.sh >/dev/null

newline_task_scope_repo="$tmp_root/tpl-agent-repo-newline-snapshot"
./scripts/new-repo-from-copier.sh tpl-agent-repo "$newline_task_scope_repo" \
	-d repo_slug=tpl-agent-repo-newline-snapshot \
	--defaults --overwrite >/dev/null
newline_task_scope_id="$(create_scoped_task "$newline_task_scope_repo" "template-ci: newline snapshot filename")"
mkdir -p "$newline_task_scope_repo/governance/task-scopes"
newline_snapshot_path="$newline_task_scope_repo/governance/task-scopes/AK-${newline_task_scope_id}
extra.snapshot.json"
(
	cd "$newline_task_scope_repo"
	ak task scope export "$newline_task_scope_id" >"$newline_snapshot_path"
)
assert_command_fails_with_stderr "generated task-scope checker should fail clearly for newline-bearing snapshot filenames" "numeric task id" run_repo_cmd "$newline_task_scope_repo" ./scripts/check-task-scope-snapshots.sh

serial_full_repo="$tmp_root/tpl-project-repo-serial-full"
./scripts/new-repo-from-copier.sh tpl-project-repo "$serial_full_repo" \
	-d repo_slug=tpl-project-repo-serial-full \
	--defaults --overwrite >/dev/null
(
	cd "$serial_full_repo"
	git init -b main >/dev/null
	git config user.name "l1-template ci" >/dev/null
	git config user.email "ci@l1-template.local" >/dev/null
	git add . >/dev/null
	git commit -m "serial full" >/dev/null
)
serial_full_task_id="$(create_scoped_task "$serial_full_repo" "template-ci: serial full task-scope snapshot")"
write_task_scope_snapshot "$serial_full_repo" "$serial_full_task_id"
prepare_full_ci_probe "$serial_full_repo"
serial_lock_ak="$tmp_root/serial-lock-ak.sh"
cat >"$serial_lock_ak" <<EOF
#!/usr/bin/env sh
set -eu
lock="$tmp_root/serial-lock-ak"
repo="$serial_full_repo"
snapshot="$serial_full_repo/governance/task-scopes/AK-$serial_full_task_id.snapshot.json"
if ! mkdir "\$lock" 2>/dev/null; then
	echo "error: concurrent ak invocation detected" >&2
	exit 99
fi
cleanup() {
	rmdir "\$lock"
}
trap cleanup EXIT INT TERM
sleep 1
if [ "\${1:-}" = "work-items" ] && [ "\${2:-}" = "check" ]; then
	exit 0
fi
if [ "\${1:-}" = "task" ] && [ "\${2:-}" = "show" ]; then
	printf '{\n  "repo": "%s"\n}\n' "\$repo"
	exit 0
fi
if [ "\${1:-}" = "task" ] && [ "\${2:-}" = "scope" ] && [ "\${3:-}" = "export" ]; then
	cat "\$snapshot"
	exit 0
fi
echo "error: unexpected ak invocation: \$*" >&2
exit 2
EOF
chmod +x "$serial_lock_ak"
run_repo_cmd "$serial_full_repo" env AK_CMD="$serial_lock_ak" ./scripts/ci/full.sh >/dev/null

project_rich_dir="$tmp_root/tpl-project-repo-rich-org-context"
./scripts/new-repo-from-copier.sh tpl-project-repo "$project_rich_dir" \
	-d repo_slug=tpl-project-repo-rich-org-context \
	-d org_docs_profile=rich \
	--defaults --overwrite >/dev/null
assert_file "$project_rich_dir/docs/org_context/org-summary.md"
assert_file "$project_rich_dir/docs/org_context/mission.md"
assert_file "$project_rich_dir/docs/org_context/purpose.md"
assert_file "$project_rich_dir/docs/org_context/vision.md"
assert_file "$project_rich_dir/docs/org_context/strategic_objectives.md"
assert_file "$project_rich_dir/docs/org_context/governance.md"

monorepo_rich_dir="$tmp_root/tpl-monorepo-rich-org-context"
./scripts/new-repo-from-copier.sh tpl-monorepo "$monorepo_rich_dir" \
	-d repo_slug=tpl-monorepo-rich-org-context \
	-d org_docs_profile=rich \
	--defaults --overwrite >/dev/null
assert_file "$monorepo_rich_dir/docs/org_context/org-summary.md"
assert_file "$monorepo_rich_dir/docs/org_context/mission.md"
assert_file "$monorepo_rich_dir/docs/org_context/purpose.md"
assert_file "$monorepo_rich_dir/docs/org_context/vision.md"
assert_file "$monorepo_rich_dir/docs/org_context/strategic_objectives.md"
assert_file "$monorepo_rich_dir/docs/org_context/governance.md"
assert_not_contains "$monorepo_rich_dir/README.md" "L2 → L3" "rich tpl-monorepo README must not advertise forbidden L3 recursion"
assert_not_contains "$monorepo_rich_dir/AGENTS.md" "L2 -> L3" "rich tpl-monorepo AGENTS must not advertise forbidden L3 recursion"

agent_task_scope_repo="$tmp_root/tpl-agent-repo"
agent_task_scope_id="$(create_scoped_task "$agent_task_scope_repo" "template-ci: generated agent task-scope snapshot")"
write_task_scope_snapshot "$agent_task_scope_repo" "$agent_task_scope_id"
prepare_full_ci_probe "$agent_task_scope_repo"
run_repo_cmd "$agent_task_scope_repo" ./scripts/check-task-scope-snapshots.sh >/dev/null
run_repo_cmd "$agent_task_scope_repo" ./scripts/ci/full.sh >/dev/null
agent_task_scope_symlink="$tmp_root/tpl-agent-repo-symlink"
ln -s "$agent_task_scope_repo" "$agent_task_scope_symlink"
run_repo_cmd "$agent_task_scope_symlink" ./scripts/check-task-scope-snapshots.sh >/dev/null
run_repo_cmd "$agent_task_scope_symlink" ./scripts/ci/full.sh >/dev/null

foreign_agent_repo="$tmp_root/foreign-agent-task-scope-repo"
mkdir -p "$foreign_agent_repo"
foreign_agent_task_id="$(create_scoped_task "$foreign_agent_repo" "template-ci: foreign agent task-scope snapshot")"
(
	cd "$agent_task_scope_repo"
	ak task scope export "$foreign_agent_task_id" >"governance/task-scopes/AK-$foreign_agent_task_id.snapshot.json"
)
assert_command_fails "generated tpl-agent-repo task-scope checker should reject foreign snapshots" run_repo_cmd "$agent_task_scope_repo" ./scripts/check-task-scope-snapshots.sh
assert_command_fails "generated tpl-agent-repo full CI should reject foreign task-scope snapshots" run_repo_cmd "$agent_task_scope_repo" ./scripts/ci/full.sh

org_task_scope_repo="$tmp_root/tpl-org-repo"
org_task_scope_id="$(create_scoped_task "$org_task_scope_repo" "template-ci: generated org task-scope snapshot")"
write_task_scope_snapshot "$org_task_scope_repo" "$org_task_scope_id"
prepare_full_ci_probe "$org_task_scope_repo"
run_repo_cmd "$org_task_scope_repo" ./scripts/check-task-scope-snapshots.sh >/dev/null
run_repo_cmd "$org_task_scope_repo" ./scripts/ci/full.sh >/dev/null

printf '{"schema_version":1}\n' >"$org_task_scope_repo/governance/task-scopes/AK-$org_task_scope_id.snapshot.json"
assert_command_fails "generated tpl-org-repo task-scope checker should reject drifted snapshots" run_repo_cmd "$org_task_scope_repo" ./scripts/check-task-scope-snapshots.sh
assert_command_fails "generated tpl-org-repo full CI should reject drifted task-scope snapshots" run_repo_cmd "$org_task_scope_repo" ./scripts/ci/full.sh

project_task_scope_repo="$tmp_root/tpl-project-repo"
project_task_scope_id="$(create_scoped_task "$project_task_scope_repo" "template-ci: generated project task-scope snapshot")"
write_task_scope_snapshot "$project_task_scope_repo" "$project_task_scope_id"
prepare_full_ci_probe "$project_task_scope_repo"
run_repo_cmd "$project_task_scope_repo" ./scripts/check-task-scope-snapshots.sh >/dev/null
run_repo_cmd "$project_task_scope_repo" ./scripts/ci/full.sh >/dev/null
project_task_scope_symlink="$tmp_root/tpl-project-repo-symlink"
ln -s "$project_task_scope_repo" "$project_task_scope_symlink"
run_repo_cmd "$project_task_scope_symlink" ./scripts/check-task-scope-snapshots.sh >/dev/null
run_repo_cmd "$project_task_scope_symlink" ./scripts/ci/full.sh >/dev/null
printf '{"schema_version":1}\n' >"$project_task_scope_repo/governance/work-items.json"
assert_command_fails "generated tpl-project-repo work-items check should reject drifted projections" run_repo_cmd "$project_task_scope_repo" ak work-items check --repo . --path governance/work-items.json
assert_command_fails "generated tpl-project-repo full CI should reject drifted work-items projections" run_repo_cmd "$project_task_scope_repo" ./scripts/ci/full.sh
run_repo_cmd "$project_task_scope_repo" ak work-items export --repo . --path governance/work-items.json >/dev/null

foreign_project_repo="$tmp_root/foreign-project-task-scope-repo"
mkdir -p "$foreign_project_repo"
foreign_project_task_id="$(create_scoped_task "$foreign_project_repo" "template-ci: foreign project task-scope snapshot")"
(
	cd "$project_task_scope_repo"
	ak task scope export "$foreign_project_task_id" >"governance/task-scopes/AK-$foreign_project_task_id.snapshot.json"
)
assert_command_fails "generated tpl-project-repo task-scope checker should reject foreign snapshots" run_repo_cmd "$project_task_scope_repo" ./scripts/check-task-scope-snapshots.sh
assert_command_fails "generated tpl-project-repo full CI should reject foreign task-scope snapshots" run_repo_cmd "$project_task_scope_repo" ./scripts/ci/full.sh

monorepo_task_scope_repo="$tmp_root/tpl-monorepo"
monorepo_task_scope_id="$(create_scoped_task "$monorepo_task_scope_repo" "template-ci: generated monorepo task-scope snapshot")"
write_task_scope_snapshot "$monorepo_task_scope_repo" "$monorepo_task_scope_id"
prepare_full_ci_probe "$monorepo_task_scope_repo"
run_repo_cmd "$monorepo_task_scope_repo" ./scripts/check-task-scope-snapshots.sh >/dev/null
run_repo_cmd "$monorepo_task_scope_repo" ./scripts/ci/full.sh >/dev/null
printf '{"schema_version":1}\n' >"$monorepo_task_scope_repo/governance/work-items.json"
assert_command_fails "generated tpl-monorepo work-items check should reject drifted projections" run_repo_cmd "$monorepo_task_scope_repo" ak work-items check --repo . --path governance/work-items.json
assert_command_fails "generated tpl-monorepo full CI should reject drifted work-items projections" run_repo_cmd "$monorepo_task_scope_repo" ./scripts/ci/full.sh
run_repo_cmd "$monorepo_task_scope_repo" ak work-items export --repo . --path governance/work-items.json >/dev/null

printf '{"schema_version":1}\n' >"$monorepo_task_scope_repo/governance/task-scopes/AK-$monorepo_task_scope_id.snapshot.json"
assert_command_fails "generated tpl-monorepo task-scope checker should reject drifted snapshots" run_repo_cmd "$monorepo_task_scope_repo" ./scripts/check-task-scope-snapshots.sh
assert_command_fails "generated tpl-monorepo full CI should reject drifted task-scope snapshots" run_repo_cmd "$monorepo_task_scope_repo" ./scripts/ci/full.sh

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
assert_contains "$l2_dir/scripts/rocs.sh" "ROCS commands should be run from the monorepo root." "generated $tpl ROCS wrapper should remain a monorepo-root placeholder"
assert_contains "$l2_dir/scripts/rocs.sh" "Use: ../../scripts/rocs.sh <args>" "generated $tpl ROCS wrapper should redirect to the monorepo-root launcher"
assert_contains "$l2_dir/AGENTS.md" "Deterministic tooling policy" "generated $tpl AGENTS should include deterministic tooling policy"
assert_contains "$l2_dir/AGENTS.md" "scripts/rocs.sh" "generated $tpl AGENTS should reference scripts/rocs.sh"
assert_contains "$l2_dir/AGENTS.md" "diary/" "generated $tpl AGENTS should reference repo-local diary"
assert_contains "$l2_dir/AGENTS.md" "policy/engineering-lane.json" "generated $tpl AGENTS should point to the pinned engineering contract"
assert_contains "$l2_dir/AGENTS.md" "docs/engineering.local.md" "generated $tpl AGENTS should point to the local engineering override doc"
assert_not_contains "$l2_dir/AGENTS.md" "This is L3" "generated $tpl AGENTS must not invent an L3 render layer"
assert_contains "$l2_dir/AGENTS.md" "internal member of an L2 monorepo" "generated $tpl AGENTS should describe package membership without inventing a new render layer"
assert_contains "$l2_dir/README.md" "ROCS command flow" "generated $tpl README should include ROCS command flow section"

# tpl-package idempotency check (no git required)
./scripts/new-repo-from-copier.sh "$tpl" "$l2_dir" \
	-d package_name="$tpl" \
	-d package_type=library \
	-d language=python \
	--defaults --overwrite >/dev/null

# Stack-contract smoke for project templates across software-pack languages.
elixir_project_dir="$tmp_root/tpl-project-repo-elixir"
./scripts/new-repo-from-copier.sh tpl-project-repo "$elixir_project_dir" \
	-d repo_slug=fixture-project-elixir \
	-d language=elixir \
	-d enable_software_pack=true \
	--defaults --overwrite >/dev/null
assert_file "$elixir_project_dir/mix.exs"
assert_file "$elixir_project_dir/policy/engineering-lane.json"
assert_file "$elixir_project_dir/docs/engineering.local.md"
assert_contains "$elixir_project_dir/policy/engineering-lane.json" '"lane": "elixir"' "generated elixir project should declare the elixir engineering lane"
assert_contains "$elixir_project_dir/policy/engineering-lane.json" '"ref": "workspace-local-unpinned"' "generated elixir project should record honest workspace-local provenance"
assert_not_contains "$elixir_project_dir/policy/engineering-lane.json" "--prefer-repo" "generated elixir project should not pin repo-preferred lane resolution"
assert_contains "$elixir_project_dir/docs/engineering.local.md" "engineering_core.command" "generated elixir project should point operators to the declared lane command"
assert_not_contains "$elixir_project_dir/docs/engineering.local.md" "pins the upstream lane" "generated elixir project docs should not overstate lane pinning"
assert_not_contains "$elixir_project_dir/docs/engineering.local.md" "--prefer-repo" "generated elixir project docs should not hardcode repo-preferred lane resolution"
ensure_registered_repo "$elixir_project_dir"
(
	cd "$elixir_project_dir"
	ak work-items check --repo . --path governance/work-items.json >/dev/null
)

node_project_dir="$tmp_root/tpl-project-repo-node"
./scripts/new-repo-from-copier.sh tpl-project-repo "$node_project_dir" \
	-d repo_slug=fixture-project-node \
	-d language=node \
	-d enable_software_pack=true \
	--defaults --overwrite >/dev/null
assert_file "$node_project_dir/package.json"
assert_not_file "$node_project_dir/tsconfig.json"
assert_file "$node_project_dir/policy/engineering-lane.json"
assert_file "$node_project_dir/docs/engineering.local.md"
assert_contains "$node_project_dir/policy/engineering-lane.json" '"lane": "ts"' "generated node project should declare the ts engineering lane"
assert_contains "$node_project_dir/policy/engineering-lane.json" '"ref": "workspace-local-unpinned"' "generated node project should record honest workspace-local provenance"
assert_contains "$node_project_dir/docs/engineering.local.md" "engineering_core.command" "generated node project should point operators to the declared lane command"
assert_not_contains "$node_project_dir/docs/engineering.local.md" "pins the upstream lane" "generated node project docs should not overstate lane pinning"
assert_not_contains "$node_project_dir/docs/engineering.local.md" "--prefer-repo" "generated node project docs should not hardcode repo-preferred lane resolution"

typescript_project_dir="$tmp_root/tpl-project-repo-typescript"
./scripts/new-repo-from-copier.sh tpl-project-repo "$typescript_project_dir" \
	-d repo_slug=fixture-project-typescript \
	-d language=typescript \
	-d enable_software_pack=true \
	--defaults --overwrite >/dev/null
assert_file "$typescript_project_dir/package.json"
assert_file "$typescript_project_dir/tsconfig.json"
assert_file "$typescript_project_dir/policy/engineering-lane.json"
assert_file "$typescript_project_dir/docs/engineering.local.md"
assert_contains "$typescript_project_dir/policy/engineering-lane.json" '"lane": "ts"' "generated typescript project should declare the ts engineering lane"
assert_contains "$typescript_project_dir/policy/engineering-lane.json" '"ref": "workspace-local-unpinned"' "generated typescript project should record honest workspace-local provenance"
assert_contains "$typescript_project_dir/docs/engineering.local.md" "engineering_core.command" "generated typescript project should point operators to the declared lane command"
assert_not_contains "$typescript_project_dir/docs/engineering.local.md" "pins the upstream lane" "generated typescript project docs should not overstate lane pinning"
assert_not_contains "$typescript_project_dir/docs/engineering.local.md" "--prefer-repo" "generated typescript project docs should not hardcode repo-preferred lane resolution"

bash_project_dir="$tmp_root/tpl-project-repo-bash"
./scripts/new-repo-from-copier.sh tpl-project-repo "$bash_project_dir" \
	-d repo_slug=fixture-project-bash \
	-d language=bash \
	-d enable_software_pack=true \
	--defaults --overwrite >/dev/null
assert_not_file "$bash_project_dir/policy/engineering-lane.json"
assert_not_file "$bash_project_dir/docs/engineering.local.md"
assert_contains "$bash_project_dir/README.md" "Bash project scaffolded with:" "generated bash project README should describe the bash software-pack contract"
assert_contains "$bash_project_dir/README.md" "no shared \`engineering-core\` lane is emitted yet for bash" "generated bash project README should explain the current bash lane boundary honestly"
assert_not_contains "$bash_project_dir/README.md" "pretending a pinned lane exists" "generated bash project README should not claim nonexistent lane pinning"

elixir_package_dir="$tmp_root/tpl-package-elixir"
./scripts/new-repo-from-copier.sh tpl-package "$elixir_package_dir" \
	-d package_name=fixture-elixir-core \
	-d package_type=library \
	-d language=elixir \
	--defaults --overwrite >/dev/null
assert_file "$elixir_package_dir/policy/engineering-lane.json"
assert_file "$elixir_package_dir/docs/engineering.local.md"
assert_contains "$elixir_package_dir/policy/engineering-lane.json" '"lane": "elixir"' "generated elixir package should pin the elixir engineering lane"
assert_contains "$elixir_package_dir/policy/engineering-lane.json" '"ref": "workspace-local-unpinned"' "generated elixir package should record honest workspace-local provenance"
assert_not_contains "$elixir_package_dir/policy/engineering-lane.json" "--prefer-repo" "generated elixir package should not pin repo-preferred lane resolution"
assert_contains "$elixir_package_dir/docs/engineering.local.md" "engineering_core.command" "generated elixir package should point operators to the declared lane command"
assert_not_contains "$elixir_package_dir/docs/engineering.local.md" "pins the upstream lane" "generated elixir package docs should not overstate lane pinning"
assert_not_contains "$elixir_package_dir/docs/engineering.local.md" "--prefer-repo" "generated elixir package docs should not hardcode repo-preferred lane resolution"

# Detailed check for tpl-project-repo (primary template)
l2_dir="$tmp_root/tpl-project-repo"
assert_contains "$l2_dir/AGENTS.md" "Recursion policy" "generated L2 AGENTS.md must include recursion section"
assert_contains "$l2_dir/AGENTS.md" "Deterministic tooling policy" "generated L2 AGENTS.md must include deterministic tooling policy"
assert_contains "$l2_dir/AGENTS.md" "scripts/rocs.sh" "generated L2 AGENTS.md must reference scripts/rocs.sh"
assert_contains "$l2_dir/AGENTS.md" "diary/" "generated L2 AGENTS.md must reference repo-local diary"

echo "ok: template ci"
