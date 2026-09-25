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
need_cmd git
need_cmd grep
need_cmd mktemp
need_cmd mv

python_exec=""
if command -v python3 >/dev/null 2>&1; then
	python_exec="python3"
elif command -v python >/dev/null 2>&1; then
	python_exec="python"
else
	echo "error: missing dependency: python3 or python" >&2
	exit 2
fi

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

assert_file_contains() {
	path="$1"
	needle="$2"
	label="$3"

	grep -qF -- "$needle" "$path" || fail "$label (missing '$needle' in $path)"
}

assert_path_absent() {
	path="$1"
	label="$2"

	[ ! -e "$path" ] || fail "$label (unexpected path: $path)"
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

	stderr_file="$(mktemp "$tmp_root/assert-failure.XXXXXX")"
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

yaml_scalar_value() {
	yaml_file="$1"
	key="$2"

	copier_answers_scalar "$yaml_file" "$key"
}

replace_first_match_in_file() {
	file="$1"
	pattern="$2"
	replacement="$3"
	tmp_file="$file.tmp"

	awk -v pattern="$pattern" -v replacement="$replacement" '
    !done {
      pos = index($0, pattern)
      if (pos > 0) {
        prefix = substr($0, 1, pos - 1)
        suffix = substr($0, pos + length(pattern))
        print prefix replacement suffix
        done = 1
        next
      }
    }
    { print }
  ' "$file" >"$tmp_file"
	mv "$tmp_file" "$file"
}

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

prepare_tree_without_answers() {
	src="$1"
	dst="$2"

	rm -rf "$dst"
	mkdir -p "$dst"
	cp -R "$src/." "$dst/"
	rm -f "$dst/.copier-answers.yml"
}

assert_trees_equal_without_answers() {
	left="$1"
	right="$2"
	label="$3"
	left_copy="$(mktemp -d "$tmp_root/left-tree.XXXXXX")"
	right_copy="$(mktemp -d "$tmp_root/right-tree.XXXXXX")"

	prepare_tree_without_answers "$left" "$left_copy"
	prepare_tree_without_answers "$right" "$right_copy"

	set +e
	git diff --no-index --quiet -- "$left_copy" "$right_copy"
	status=$?
	set -e

	if [ "$status" -eq 0 ]; then
		rm -rf "$left_copy" "$right_copy"
		return
	fi
	if [ "$status" -eq 1 ]; then
		echo "error: $label" >&2
		git --no-pager diff --no-index -- "$left_copy" "$right_copy" >&2 || true
		rm -rf "$left_copy" "$right_copy"
		exit 1
	fi

	rm -rf "$left_copy" "$right_copy"
	fail "$label (diff command failed)"
}

missing_node_bin="$tmp_root/missing-node-bin"
mkdir -p "$missing_node_bin"
for tool_name in sh dirname pwd; do
	ln -s "$(command -v "$tool_name")" "$missing_node_bin/$tool_name"
done
missing_node_checker="$tmp_root/docs-ref-check.mjs"
printf 'console.log("ok")\n' >"$missing_node_checker"
assert_command_fails_with_stderr "check-doc-references should fail closed on invalid DOC_REF_CHECK_SCRIPT overrides" "docs-ref-check override points to missing file" env DOC_REF_CHECK_SCRIPT=/definitely/missing sh "$repo_root/scripts/check-doc-references.sh"
assert_command_fails_with_stderr "check-doc-references should fail clearly when node is unavailable" "missing dependency: node" env PATH="$missing_node_bin" DOC_REF_CHECK_SCRIPT="$missing_node_checker" sh "$repo_root/scripts/check-doc-references.sh"

dummy_ak_dir="$tmp_root/dummy-ak-bin"
mkdir -p "$dummy_ak_dir"
cat >"$dummy_ak_dir/ak" <<'EOF'
#!/usr/bin/env sh
echo "error: ambient ak should not be used by check-template-ci" >&2
exit 127
EOF
chmod +x "$dummy_ak_dir/ak"

no_yaml_bin="$tmp_root/no-yaml-bin"
mkdir -p "$no_yaml_bin"
for fake_python in python3 python; do
	cat >"$no_yaml_bin/$fake_python" <<'EOF'
#!/usr/bin/env sh
exit 1
EOF
	chmod +x "$no_yaml_bin/$fake_python"
done


render_l1_case() {
	case_name="$1"
	enable_community_pack="$2"
	enable_release_pack="$3"
	enable_vouch_gate="$4"
	l1_org_docs_profile="$5"
	l1_dir="$tmp_root/$case_name"

	"$repo_root/scripts/new-l1-from-copier.sh" "$l1_dir" \
		-d repo_slug="$case_name" \
		-d maintainer_handle=@template-owner \
		-d l1_org_docs_profile="$l1_org_docs_profile" \
		-d enable_community_pack="$enable_community_pack" \
		-d enable_release_pack="$enable_release_pack" \
		-d enable_vouch_gate="$enable_vouch_gate" \
		--defaults --overwrite >/dev/null

	(
		cd "$l1_dir"
		git init -b main >/dev/null
		git config user.name "tpl-template-repo ci" >/dev/null
		git config user.email "ci@tpl-template-repo.local" >/dev/null
		./scripts/install-hooks.sh >/dev/null
		./scripts/ci/smoke.sh >/dev/null
		if [ "$case_name" = "l1-template-sample" ]; then
			mkdir -p governance/task-scopes
			printf 'do not delete\n' >governance/task-scopes/KEEP.txt
			PATH="$dummy_ak_dir:$PATH" ./scripts/check-template-ci.sh
			[ -f governance/task-scopes/KEEP.txt ] || fail "generated L1 check-template-ci should preserve existing task-scope files"
			rm -rf governance/task-scopes
		else
			PATH="$dummy_ak_dir:$PATH" ./scripts/check-template-ci.sh
		fi
		git add .
		git commit -m "initial render ($case_name)" >/dev/null
	)

	"$repo_root/scripts/new-l1-from-copier.sh" "$l1_dir" \
		-d repo_slug="$case_name" \
		-d maintainer_handle=@template-owner \
		-d l1_org_docs_profile="$l1_org_docs_profile" \
		-d enable_community_pack="$enable_community_pack" \
		-d enable_release_pack="$enable_release_pack" \
		-d enable_vouch_gate="$enable_vouch_gate" \
		--defaults --overwrite >/dev/null

	(
		cd "$l1_dir"
		if [ -n "$(git status --porcelain)" ]; then
			echo "error: non-idempotent L0 -> L1 generation ($case_name)" >&2
			git status --short >&2
			exit 1
		fi
	)

	if [ "$case_name" = "l1-template-sample" ]; then
		preview_target="$tmp_root/l1-preview-target"
		"$repo_root/scripts/new-l1-from-copier.sh" "$preview_target" \
			-d repo_slug="$case_name" \
			--defaults --overwrite >/dev/null

		alias_target="$tmp_root/l1-preview-alias"
		rm -rf "$alias_target"
		cp -R "$preview_target" "$alias_target"

		preview_output="$("$repo_root/scripts/preview-l1-diff.sh" "$alias_target")"
		printf '%s\n' "$preview_output" | grep -qF "ok: no diff between rendered L1 and target" || {
			echo "error: preview-l1-diff did not produce clean no-diff output for sample alias target" >&2
			printf '%s\n' "$preview_output" >&2
			exit 1
		}
	fi

	if [ "$case_name" = "l1-template-release" ]; then
		preview_output="$("$repo_root/scripts/preview-l1-diff.sh" "$l1_dir")"
		printf '%s\n' "$preview_output" | grep -qF "ok: no diff between rendered L1 and target" || {
			echo "error: preview-l1-diff did not preserve non-default profile settings for release case" >&2
			printf '%s\n' "$preview_output" >&2
			exit 1
		}

		(
			cd "$l1_dir"
			replace_first_match_in_file .release-please-manifest.json '"0.1.0"' '"0.1.1"'
			replace_first_match_in_file CHANGELOG.md '## [0.1.0]' '## [0.1.1]'
			./scripts/release/check.sh >/dev/null
		)
	fi
}

render_l1_case "l1-template-sample" false false false rich
render_l1_case "l1-template-community" true false false rich
render_l1_case "l1-template-release" false true false rich
render_l1_case "l1-template-vouch" false false true rich
render_l1_case "l1-template-compact-org" false false false compact

rich_l1="$tmp_root/l1-template-sample"
compact_l1="$tmp_root/l1-template-compact-org"
for org_doc in purpose.md mission.md vision.md strategic_objectives.md values_ethics.md governance.md glossary.md; do
	[ -s "$rich_l1/docs/org/$org_doc" ] || fail "fresh rich L1 must render docs/org/$org_doc"
	assert_path_absent "$compact_l1/docs/org/$org_doc" "fresh compact L1 must omit rich-only docs/org/$org_doc"
done
[ -s "$compact_l1/docs/org/operating_model.md" ] || fail "fresh compact L1 must retain docs/org/operating_model.md"

# Regression check: inherited string values must preserve punctuation and quoting.
colon_l1="$tmp_root/l1-template-colon"
colon_l2="$tmp_root/l2-template-colon"
"$repo_root/scripts/new-l1-from-copier.sh" "$colon_l1" \
	-d repo_slug=l1-template-colon \
	-d maintainer_handle=@template-owner \
	-d company_name='Foo: Labs' \
	--defaults --overwrite >/dev/null
(
	cd "$colon_l1"
	./scripts/new-repo-from-copier.sh tpl-project-repo "$colon_l2" \
		-d repo_slug=l2-template-colon \
		--defaults --overwrite >/dev/null
)
colon_company_name="$(yaml_scalar_value "$colon_l2/.copier-answers.yml" company_name)"
[ "$colon_company_name" = "Foo: Labs" ] || {
	echo "error: inherited company_name should preserve colon characters (expected 'Foo: Labs', got '$colon_company_name')" >&2
	exit 1
}
assert_file_contains "$colon_l2/contracts/layer-contract.yml" "layer: L2" "generated tpl-project-repo should declare layer L2"
assert_command_fails_with_stderr "L0 wrapper should reject L2 destinations" "destination already declares layer L2" "$repo_root/scripts/new-l1-from-copier.sh" "$colon_l2" -d repo_slug=forbidden-l1-over-l2 --defaults --overwrite

apostrophe_l1="$tmp_root/l1-template-apostrophe"
apostrophe_l2="$tmp_root/l2-template-apostrophe"
"$repo_root/scripts/new-l1-from-copier.sh" "$apostrophe_l1" \
	-d repo_slug=l1-template-apostrophe \
	-d maintainer_handle=@template-owner \
	-d company_name="O'Connor Labs" \
	--defaults --overwrite >/dev/null
if grep -qF "company_name: 'O'Connor Labs'" "$apostrophe_l1/.copier-answers.yml"; then
	echo "error: L1 answers rendering must not emit invalid single-quoted YAML for apostrophes" >&2
	exit 1
fi
(
	cd "$apostrophe_l1"
	./scripts/new-repo-from-copier.sh tpl-project-repo "$apostrophe_l2" \
		-d repo_slug=l2-template-apostrophe \
		--defaults --overwrite >/dev/null
)
apostrophe_company_name="$(yaml_scalar_value "$apostrophe_l2/.copier-answers.yml" company_name)"
[ "$apostrophe_company_name" = "O'Connor Labs" ] || {
	echo "error: inherited company_name should preserve apostrophes (expected O'Connor Labs, got '$apostrophe_company_name')" >&2
	exit 1
}

quote_l1="$tmp_root/l1-template-quote"
quote_l2="$tmp_root/l2-template-quote"
"$repo_root/scripts/new-l1-from-copier.sh" "$quote_l1" \
	-d repo_slug=l1-template-quote \
	-d maintainer_handle=@template-owner \
	-d company_name='Acme "Lab"' \
	--defaults --overwrite >/dev/null
(
	cd "$quote_l1"
	./scripts/new-repo-from-copier.sh tpl-project-repo "$quote_l2" \
		-d repo_slug=l2-template-quote \
		--defaults --overwrite >/dev/null
)
quote_company_name="$(yaml_scalar_value "$quote_l2/.copier-answers.yml" company_name)"
[ "$quote_company_name" = 'Acme "Lab"' ] || {
	echo "error: inherited company_name should preserve embedded double quotes (expected 'Acme \"Lab\"', got '$quote_company_name')" >&2
	exit 1
}

hash_l1="$tmp_root/l1-template-hash"
hash_l2="$tmp_root/l2-template-hash"
"$repo_root/scripts/new-l1-from-copier.sh" "$hash_l1" \
	-d repo_slug=l1-template-hash \
	-d maintainer_handle=@template-owner \
	-d company_name='Foo #1' \
	--defaults --overwrite >/dev/null
(
	cd "$hash_l1"
	./scripts/new-repo-from-copier.sh tpl-project-repo "$hash_l2" \
		-d repo_slug=l2-template-hash \
		--defaults --overwrite >/dev/null
)
hash_company_name="$(yaml_scalar_value "$hash_l2/.copier-answers.yml" company_name)"
[ "$hash_company_name" = 'Foo #1' ] || {
	echo "error: inherited company_name should preserve hash characters (expected 'Foo #1', got '$hash_company_name')" >&2
	exit 1
}

hash_preview_output="$("$repo_root/scripts/preview-l1-diff.sh" "$hash_l1")"
printf '%s\n' "$hash_preview_output" | grep -qF "ok: no diff between rendered L1 and target" || {
	echo "error: preview-l1-diff must preserve quoted hash values from .copier-answers.yml" >&2
	printf '%s\n' "$hash_preview_output" >&2
	exit 1
}
assert_command_fails_with_stderr "ownership-aware preview should require functional stdlib Python" "missing dependency: functional python3 or python" env PATH="$no_yaml_bin:$PATH" "$repo_root/scripts/preview-l1-diff.sh" "$hash_l1"

multiline_l1="$tmp_root/l1-template-multiline"
multiline_l2="$tmp_root/l2-template-multiline"
multiline_expected="$(printf 'Line1\nLine2')"
"$repo_root/scripts/new-l1-from-copier.sh" "$multiline_l1" \
	-d repo_slug=l1-template-multiline \
	-d maintainer_handle=@template-owner \
	-d company_name="$multiline_expected" \
	--defaults --overwrite >/dev/null
(
	cd "$multiline_l1"
	./scripts/new-repo-from-copier.sh tpl-project-repo "$multiline_l2" \
		-d repo_slug=l2-template-multiline \
		--defaults --overwrite >/dev/null
)
multiline_company_name="$(yaml_scalar_value "$multiline_l2/.copier-answers.yml" company_name)"
[ "$multiline_company_name" = "$multiline_expected" ] || {
	echo "error: inherited company_name should preserve multiline values" >&2
	printf 'expected:\n%s\n---\nactual:\n%s\n' "$multiline_expected" "$multiline_company_name" >&2
	exit 1
}
multiline_preview_output="$("$repo_root/scripts/preview-l1-diff.sh" "$multiline_l1")"
printf '%s\n' "$multiline_preview_output" | grep -qF "ok: no diff between rendered L1 and target" || {
	echo "error: preview-l1-diff must preserve multiline values from .copier-answers.yml" >&2
	printf '%s\n' "$multiline_preview_output" >&2
	exit 1
}
multiline_fallback_l2="$tmp_root/l2-template-multiline-no-yaml"
assert_command_fails_with_stderr "generated L1 render should fail closed on unsupported multiline answers when PyYAML is unavailable" "unable to parse 'company_name'" env PATH="$no_yaml_bin:$PATH" sh -c "cd \"\$1\" && ./scripts/new-repo-from-copier.sh tpl-project-repo \"\$2\" -d repo_slug=l2-template-multiline-no-yaml --defaults --overwrite" sh "$multiline_l1" "$multiline_fallback_l2"
assert_command_fails_with_stderr "preview-l1-diff should fail closed on unsupported multiline answers when PyYAML is unavailable" "unable to parse 'company_name'" env PATH="$no_yaml_bin:$PATH" "$repo_root/scripts/preview-l1-diff.sh" "$multiline_l1"

tagged_l1="$tmp_root/l1-template-tagged"
tagged_l2="$tmp_root/l2-template-tagged-no-yaml"
"$repo_root/scripts/new-l1-from-copier.sh" "$tagged_l1" \
	-d repo_slug=l1-template-tagged \
	-d maintainer_handle=@template-owner \
	--defaults --overwrite >/dev/null
replace_first_match_in_file "$tagged_l1/.copier-answers.yml" "company_name: Holding Company" "company_name: !!str Holding Company"
assert_command_fails_with_stderr "generated L1 render should fail closed on tagged YAML answers when PyYAML is unavailable" "unable to parse 'company_name'" env PATH="$no_yaml_bin:$PATH" sh -c "cd \"\$1\" && ./scripts/new-repo-from-copier.sh tpl-project-repo \"\$2\" -d repo_slug=l2-template-tagged-no-yaml --defaults --overwrite" sh "$tagged_l1" "$tagged_l2"
assert_command_fails_with_stderr "preview-l1-diff should fail closed on tagged YAML answers when PyYAML is unavailable" "unable to parse 'company_name'" env PATH="$no_yaml_bin:$PATH" "$repo_root/scripts/preview-l1-diff.sh" "$tagged_l1"

tab_l1="$tmp_root/l1-template-tab"
tab_l2="$tmp_root/l2-template-tab"
tab_expected="$(printf 'Tab\tCo')"
"$repo_root/scripts/new-l1-from-copier.sh" "$tab_l1" \
	-d repo_slug=l1-template-tab \
	-d maintainer_handle=@template-owner \
	-d company_name="$tab_expected" \
	--defaults --overwrite >/dev/null
(
	cd "$tab_l1"
	./scripts/new-repo-from-copier.sh tpl-project-repo "$tab_l2" \
		-d repo_slug=l2-template-tab \
		--defaults --overwrite >/dev/null
)
tab_company_name="$(yaml_scalar_value "$tab_l2/.copier-answers.yml" company_name)"
[ "$tab_company_name" = "$tab_expected" ] || {
	echo "error: inherited company_name should preserve escaped tab values" >&2
	printf 'expected:\n%s\n---\nactual:\n%s\n' "$tab_expected" "$tab_company_name" >&2
	exit 1
}

org_default_l1="$tmp_root/l1-template-org-default"
"$repo_root/scripts/new-l1-from-copier.sh" "$org_default_l1" \
	-d repo_slug=l1-template-org-default \
	-d maintainer_handle=@template-owner \
	-d l2_org_docs_default=compact \
	--defaults --overwrite >/dev/null
org_default_preview_output="$("$repo_root/scripts/preview-l1-diff.sh" "$org_default_l1")"
printf '%s\n' "$org_default_preview_output" | grep -qF "ok: no diff between rendered L1 and target" || {
	echo "error: preview-l1-diff must replay l2_org_docs_default from .copier-answers.yml" >&2
	printf '%s\n' "$org_default_preview_output" >&2
	exit 1
}

suffix_l1="$tmp_root/l1-template-suffix-allowlist"
"$repo_root/scripts/new-l1-from-copier.sh" "$suffix_l1" \
	-d repo_slug=l1-template-suffix-allowlist \
	-d maintainer_handle=@template-owner \
	--defaults --overwrite >/dev/null
mkdir -p "$suffix_l1/owned/demo"
touch "$suffix_l1/owned/demo/stray.j2"
printf 'repo_slug: {{ repo_slug }}\n' >"$suffix_l1/owned/demo/stray.txt"
(
	cd "$suffix_l1"
	./scripts/check-template-ci.sh >/dev/null
)

bootstrap_l1="$tmp_root/l1-template-bootstrap-portable"
"$repo_root/scripts/new-l1-from-copier.sh" "$bootstrap_l1" \
	-d repo_slug=l1-template-bootstrap-portable \
	-d maintainer_handle=@template-owner \
	--defaults --overwrite >/dev/null
bootstrap_fake_bin="$tmp_root/bootstrap-fake-bin"
mkdir -p "$bootstrap_fake_bin"
cat >"$bootstrap_fake_bin/sed" <<'EOF'
#!/usr/bin/env sh
if [ "${1:-}" = "-i" ]; then
  echo "error: bootstrap-lane-root.sh must not rely on sed -i" >&2
  exit 99
fi
exec /usr/bin/sed "$@"
EOF
chmod +x "$bootstrap_fake_bin/sed"
(
	cd "$bootstrap_l1"
	PATH="$bootstrap_fake_bin:$PATH" ./scripts/bootstrap-lane-root.sh owned >/dev/null
)
assert_file_contains "$bootstrap_l1/owned/.copier-answers.yml" "location: owned" "portable lane bootstrap should stamp lane location without sed"
assert_file_contains "$bootstrap_l1/owned/contracts/layer-contract.yml" "layer: L2" "portable lane bootstrap should preserve L2 layer contract in built-in lane baselines"
assert_file_contains "$bootstrap_l1/owned/.gitignore" "!contracts/**" "portable lane bootstrap should track contracts in built-in lane .gitignore"
assert_file_contains "$bootstrap_l1/owned/README.md" "**Location**: owned" "portable lane bootstrap should update README location without sed"
assert_command_fails "lane bootstrap should reject regex-bearing lane names" env PATH="$bootstrap_fake_bin:$PATH" sh -c "cd \"\$1\" && ./scripts/bootstrap-lane-root.sh \"[foo\"" sh "$bootstrap_l1"
assert_command_fails "lane bootstrap should reject whitespace lane names" env PATH="$bootstrap_fake_bin:$PATH" sh -c "cd \"\$1\" && ./scripts/bootstrap-lane-root.sh \"data lane\"" sh "$bootstrap_l1"
assert_command_fails "lane bootstrap should reject reserved L1 control-plane lane names" env PATH="$bootstrap_fake_bin:$PATH" sh -c "cd \"\$1\" && ./scripts/bootstrap-lane-root.sh docs" sh "$bootstrap_l1"
(
	cd "$bootstrap_l1"
	PROJECT_OWNER_HANDLE=@lane-owner PATH="$bootstrap_fake_bin:$PATH" ./scripts/bootstrap-lane-root.sh data-lane >/dev/null
	PROJECT_OWNER_HANDLE=@lane-owner PATH="$bootstrap_fake_bin:$PATH" ./scripts/bootstrap-lane-root.sh data-lane >/dev/null
)
assert_file_contains "$bootstrap_l1/data-lane/.copier-answers.yml" "location: data-lane" "portable lane bootstrap should stamp custom lane location in answers"
assert_file_contains "$bootstrap_l1/data-lane/contracts/layer-contract.yml" "layer: L2" "portable lane bootstrap should preserve L2 layer contract in custom lane baselines"
assert_file_contains "$bootstrap_l1/data-lane/.gitignore" "!contracts/**" "portable lane bootstrap should track contracts in custom lane .gitignore"
assert_file_contains "$bootstrap_l1/data-lane/README.md" "**Location**: data-lane" "portable lane bootstrap should render custom lane location in README"
assert_file_contains "$bootstrap_l1/data-lane/CODEOWNERS" "# Location: data-lane" "portable lane bootstrap should render custom lane location in CODEOWNERS"
assert_file_contains "$bootstrap_l1/data-lane/CODEOWNERS" "docs/project/** @lane-owner" "portable lane bootstrap should fall back to project owner handle for custom lanes"
assert_file_contains "$bootstrap_l1/.gitignore" "!data-lane/contracts/**" "portable lane bootstrap should unignore contracts in parent gitignore"
data_lane_block_count="$(grep -cF '# Lane root: data-lane' "$bootstrap_l1/.gitignore" || true)"
[ "$data_lane_block_count" = "1" ] || {
	echo "error: lane bootstrap should remain idempotent for safe custom lane names" >&2
	exit 1
}
(
	cd "$bootstrap_l1"
	PROJECT_OWNER_HANDLE='@acme/platform-team' PATH="$bootstrap_fake_bin:$PATH" ./scripts/bootstrap-lane-root.sh team-data >/dev/null
	PATH="$bootstrap_fake_bin:$PATH" ./scripts/bootstrap-lane-root.sh team-data >/dev/null
)
assert_file_contains "$bootstrap_l1/team-data/.copier-answers.yml" "project_owner_handle: '@acme/platform-team'" "lane bootstrap should preserve structured team owner handles verbatim in answers"
assert_file_contains "$bootstrap_l1/team-data/CODEOWNERS" "docs/project/** @acme/platform-team" "lane bootstrap should preserve structured team owner handles verbatim in CODEOWNERS"
(
	cd "$bootstrap_l1"
	git init -b main >/dev/null
	git config user.name "tpl-template-repo hooks check" >/dev/null
	git config user.email "ci@tpl-template-repo.local" >/dev/null
	chmod -x scripts/rocs.sh
	./scripts/install-hooks.sh >/dev/null
	[ -x scripts/rocs.sh ] || {
		echo "error: install-hooks should restore executable bit for the generated L1 ROCS wrapper" >&2
		exit 1
	}
)

# Language-matrix smoke: project language cases plus monorepo member-language cases.
matrix_l1="$tmp_root/l1-template-matrix"
matrix_project_python="$tmp_root/l2-project-python-matrix"
matrix_project_node="$tmp_root/l2-project-node-matrix"
matrix_project_typescript="$tmp_root/l2-project-typescript-matrix"
matrix_project_rust="$tmp_root/l2-project-rust-matrix"
matrix_project_elixir="$tmp_root/l2-project-elixir-matrix"
matrix_agent="$tmp_root/l2-agent-matrix"
matrix_org="$tmp_root/l2-org-matrix"
matrix_monorepo="$tmp_root/l2-monorepo-matrix"
"$repo_root/scripts/new-l1-from-copier.sh" "$matrix_l1" \
	-d repo_slug=l1-template-matrix \
	-d maintainer_handle=@template-owner \
	--defaults --overwrite >/dev/null
(
	cd "$matrix_l1"
	./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_project_python" \
		-d repo_slug=fixture-project-python \
		-d language=python \
		-d enable_software_pack=true \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_project_node" \
		-d repo_slug=fixture-project-node \
		-d language=node \
		-d enable_software_pack=true \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_project_typescript" \
		-d repo_slug=fixture-project-typescript \
		-d language=typescript \
		-d enable_software_pack=true \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_project_rust" \
		-d repo_slug=fixture-project-rust \
		-d language=rust \
		-d enable_software_pack=true \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_project_elixir" \
		-d repo_slug=fixture-project-elixir \
		-d language=elixir \
		-d enable_software_pack=true \
		--defaults --overwrite >/dev/null

	assert_command_fails "tpl-agent-repo must require exactly one role" \
		./scripts/new-repo-from-copier.sh tpl-agent-repo "$tmp_root/l2-agent-missing-role" \
		-d repo_slug=agent-missing-role -d creation_task_id=AK-5105 --defaults --overwrite
	assert_command_fails "tpl-agent-repo must require an AK creation task" \
		./scripts/new-repo-from-copier.sh tpl-agent-repo "$tmp_root/l2-agent-missing-task" \
		-d repo_slug=agent-missing-task -d agent_role=fixture-role --defaults --overwrite
	assert_command_fails "tpl-agent-repo must reject an unknown AK creation task" \
		./scripts/new-repo-from-copier.sh tpl-agent-repo "$tmp_root/l2-agent-unknown-task" \
		-d repo_slug=agent-unknown-task -d agent_role=fixture-role \
		-d creation_task_id=AK-999999999 --defaults --overwrite
	assert_command_fails "tpl-agent-repo must reject conflicting AK creation tasks" \
		./scripts/new-repo-from-copier.sh tpl-agent-repo "$tmp_root/l2-agent-duplicate-task" \
		-d repo_slug=agent-duplicate-task -d agent_role=fixture-role \
		-d creation_task_id=AK-5105 -d creation_task_id=AK-999999999 \
		--defaults --overwrite
	assert_command_fails "tpl-agent-repo must reject multiple role overrides" \
		./scripts/new-repo-from-copier.sh tpl-agent-repo "$tmp_root/l2-agent-duplicate-role" \
		-d repo_slug=agent-duplicate-role -d agent_role=role-one -d agent_role=role-two \
		-d creation_task_id=AK-5105 --defaults --overwrite

	./scripts/new-repo-from-copier.sh tpl-agent-repo "$matrix_agent" \
		-d repo_slug=fixture-agent \
		-d agent_name=agent-fixture-manifest \
		-d agent_role=fixture-agent-role \
		-d creation_task_id=AK-5105 \
		-d skill_profile=fixture-profile \
		-d skill_extras='["fixture-extra"]' \
		-d agent_tools='["read","bash"]' \
		-d agent_extensions='["fixture-extension"]' \
		-d agent_model=fixture-model \
		-d agent_thinking=high \
		-d agent_scope='{"repos":["fixture/repo"],"forbidden":["secret"],"note":"advisory"}' \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-org-repo "$matrix_org" \
		-d repo_slug=fixture-org \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-monorepo "$matrix_monorepo" \
		-d repo_slug=fixture-monorepo-matrix \
		-d package_manager=uv \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-package "$matrix_monorepo/packages/fixture-py-core" \
		-d package_name=fixture-py-core \
		-d package_type=library \
		-d language=python \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-package "$matrix_monorepo/packages/fixture-ts-core" \
		-d package_name=fixture-ts-core \
		-d package_type=library \
		-d language=typescript \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-package "$matrix_monorepo/packages/fixture-rust-core" \
		-d package_name=fixture-rust-core \
		-d package_type=library \
		-d language=rust \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-package "$matrix_monorepo/packages/fixture-elixir-core" \
		-d package_name=fixture-elixir-core \
		-d package_type=library \
		-d language=elixir \
		--defaults --overwrite >/dev/null
)

assert_file_contains "$matrix_agent/agent.json" '"name": "agent-fixture-manifest"' "agent manifest should render configured name"
assert_file_contains "$matrix_agent/agent.json" '"role": "fixture-agent-role"' "agent manifest should render exactly one role"
assert_file_contains "$matrix_agent/agent.json" '"profile": "fixture-profile"' "agent manifest should render skill profile"
assert_file_contains "$matrix_agent/agent.json" '"fixture-extra"' "agent manifest should render extra skills"
assert_file_contains "$matrix_agent/agent.json" '"fixture-extension"' "agent manifest should render extensions"
assert_file_contains "$matrix_agent/agent.json" '"model": "fixture-model"' "agent manifest should render model default"
assert_file_contains "$matrix_agent/agent.json" '"thinking": "high"' "agent manifest should render thinking default"
assert_file_contains "$matrix_agent/agent.json" '"fixture/repo"' "agent manifest should render scope"
"$matrix_agent/scripts/compile-system-prompt.py" --check >/dev/null

toggle_contract_l1="$tmp_root/l1-template-toggle-contract"
toggle_agent_default="$tmp_root/l2-agent-toggle-default"
toggle_agent_enabled="$tmp_root/l2-agent-toggle-enabled"
toggle_org_default="$tmp_root/l2-org-toggle-default"
toggle_org_enabled="$tmp_root/l2-org-toggle-enabled"
toggle_project_default="$tmp_root/l2-project-toggle-default"
toggle_project_enabled="$tmp_root/l2-project-toggle-enabled"
toggle_monorepo_default="$tmp_root/l2-monorepo-toggle-default"
toggle_monorepo_enabled="$tmp_root/l2-monorepo-toggle-enabled"
"$repo_root/scripts/new-l1-from-copier.sh" "$toggle_contract_l1" \
	-d repo_slug=l1-template-toggle-contract \
	-d maintainer_handle=@template-owner \
	--defaults --overwrite >/dev/null
(
	cd "$toggle_contract_l1"
	./scripts/new-repo-from-copier.sh tpl-agent-repo "$toggle_agent_default" \
		-d repo_slug=fixture-agent-toggle-contract \
		-d agent_role=fixture-agent-toggle-role \
		-d creation_task_id=AK-5105 \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite >/dev/null
	./scripts/new-repo-from-copier.sh tpl-agent-repo "$toggle_agent_enabled" \
		-d repo_slug=fixture-agent-toggle-contract \
		-d agent_role=fixture-agent-toggle-role \
		-d creation_task_id=AK-5105 \
		-d enable_community_pack=true \
		-d enable_release_pack=true \
		-d enable_vouch_gate=true \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-org-repo "$toggle_org_default" \
		-d repo_slug=fixture-org-toggle-contract \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite >/dev/null
	./scripts/new-repo-from-copier.sh tpl-org-repo "$toggle_org_enabled" \
		-d repo_slug=fixture-org-toggle-contract \
		-d enable_community_pack=true \
		-d enable_release_pack=true \
		-d enable_vouch_gate=true \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-project-repo "$toggle_project_default" \
		-d repo_slug=fixture-project-toggle-contract \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite >/dev/null
	./scripts/new-repo-from-copier.sh tpl-project-repo "$toggle_project_enabled" \
		-d repo_slug=fixture-project-toggle-contract \
		-d enable_community_pack=true \
		-d enable_release_pack=true \
		-d enable_vouch_gate=true \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-monorepo "$toggle_monorepo_default" \
		-d repo_slug=fixture-monorepo-toggle-contract \
		-d package_manager=uv \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite >/dev/null
	./scripts/new-repo-from-copier.sh tpl-monorepo "$toggle_monorepo_enabled" \
		-d repo_slug=fixture-monorepo-toggle-contract \
		-d package_manager=uv \
		-d enable_community_pack=true \
		-d enable_release_pack=true \
		-d enable_vouch_gate=true \
		--defaults --overwrite >/dev/null
)

assert_file_contains "$toggle_agent_enabled/README.md" "metadata-only in \`tpl-agent-repo\`" "generated tpl-agent-repo README should describe profile toggles as metadata-only"
assert_file_contains "$toggle_org_enabled/README.md" "metadata-only in \`tpl-org-repo\`" "generated tpl-org-repo README should describe profile toggles as metadata-only"
assert_file_contains "$toggle_project_enabled/README.md" "metadata-only in \`tpl-project-repo\`" "generated tpl-project-repo README should describe profile toggles as metadata-only"
assert_file_contains "$toggle_monorepo_enabled/README.md" "metadata-only in \`tpl-monorepo\`" "generated tpl-monorepo README should describe profile toggles as metadata-only"
assert_trees_equal_without_answers "$toggle_agent_default" "$toggle_agent_enabled" "tpl-agent-repo profile toggles should remain metadata-only at L2"
assert_trees_equal_without_answers "$toggle_org_default" "$toggle_org_enabled" "tpl-org-repo profile toggles should remain metadata-only at L2"
assert_trees_equal_without_answers "$toggle_project_default" "$toggle_project_enabled" "tpl-project-repo profile toggles should remain metadata-only at L2"
assert_trees_equal_without_answers "$toggle_monorepo_default" "$toggle_monorepo_enabled" "tpl-monorepo profile toggles should remain metadata-only at L2"

assert_command_fails "root ROCS doctor must fail closed when ROCS_BIN is invalid" env ROCS_BIN=/definitely/missing "$repo_root/scripts/rocs.sh" --doctor
assert_command_fails "root ROCS which must fail closed when ROCS_BIN is invalid" env ROCS_BIN=/definitely/missing "$repo_root/scripts/rocs.sh" --which
(
	cd "$tmp_root/l1-template-sample"
	assert_command_fails "generated L1 ROCS doctor must fail closed when ROCS_BIN is invalid" env ROCS_BIN=/definitely/missing ./scripts/rocs.sh --doctor
	assert_command_fails "generated L1 ROCS which must fail closed when ROCS_BIN is invalid" env ROCS_BIN=/definitely/missing ./scripts/rocs.sh --which
)
# Generated L2 ROCS launcher: runs the workspace rocs-cli core pinned by rocs_cli_version.
# A stub `uv` records the exec so these checks need neither network nor a real core.
rocs_stub_bin="$tmp_root/rocs-stub-bin"
mkdir -p "$rocs_stub_bin"
cat >"$rocs_stub_bin/uv" <<'EOF'
#!/bin/sh
printf 'stub-uv:%s\n' "$*"
printf 'workspace:%s\n' "$ROCS_WORKSPACE_ROOT"
printf 'resolve-refs:%s\n' "$ROCS_RESOLVE_REFS"
EOF
chmod +x "$rocs_stub_bin/uv"
make_fake_rocs_core() {
	fake_core="$tmp_root/rocs-core-$1"
	mkdir -p "$fake_core/src/rocs_cli"
	printf '[project]\nname = "rocs-cli"\nversion = "%s"\n' "$1" >"$fake_core/pyproject.toml"
}
for rocs_version in 0.4.4 0.4.9 0.4.3 0.3.9 0.5.0 1.4.4; do
	make_fake_rocs_core "$rocs_version"
done
for generated_rocs_repo in "$matrix_project_python" "$matrix_agent" "$matrix_org" "$matrix_monorepo"; do
	assert_file_contains "$generated_rocs_repo/scripts/rocs.sh" 'rocs_cli_pin="0.4.4"' "generated L2 ROCS launcher must render the rocs_cli_version pin"
	if [ "$generated_rocs_repo" != "$matrix_monorepo" ]; then
		assert_file_contains "$generated_rocs_repo/.copier-answers.yml" "rocs_cli_version: 0.4.4" "generated L2 answers must persist the rocs-cli pin"
	fi
	assert_path_absent "$generated_rocs_repo/tools/rocs-cli" "generated L2 repos must not vendor rocs-cli"
	assert_file_contains "$generated_rocs_repo/.gitignore" "/ontology/dist/" "generated L2 repo must gitignore ROCS outputs"
	for rocs_version in 0.4.4 0.4.9; do
		rocs_output="$(cd "$generated_rocs_repo" && PATH="$rocs_stub_bin:$PATH" ROCS_CORE_PROJECT="$tmp_root/rocs-core-$rocs_version" ./scripts/rocs.sh validate --repo .)" ||
			fail "generated L2 ROCS launcher must run a compatible core $rocs_version: $generated_rocs_repo"
		printf '%s\n' "$rocs_output" | grep -qxF "stub-uv:run --frozen --project $tmp_root/rocs-core-$rocs_version python -m rocs_cli validate --repo ." ||
			fail "generated L2 ROCS launcher must exec uv run --frozen against the pinned core (got: $rocs_output)"
		printf '%s\n' "$rocs_output" | grep -qxF "resolve-refs:1" || fail "generated L2 ROCS launcher must resolve refs by default"
	done
	for rocs_version in 0.4.3 0.3.9 0.5.0 1.4.4; do
		set +e
		rocs_stderr="$(cd "$generated_rocs_repo" && PATH="$rocs_stub_bin:$PATH" ROCS_CORE_PROJECT="$tmp_root/rocs-core-$rocs_version" ./scripts/rocs.sh version 2>&1 >/dev/null)"
		rocs_status=$?
		set -e
		[ "$rocs_status" -eq 2 ] || fail "generated L2 ROCS launcher must exit 2 for incompatible core $rocs_version (got $rocs_status)"
		printf '%s\n' "$rocs_stderr" | grep -qF "is $rocs_version but this repo pins 0.4.4" ||
			fail "generated L2 ROCS launcher must name both versions for core $rocs_version (got: $rocs_stderr)"
	done
	set +e
	rocs_stderr="$(cd "$generated_rocs_repo" && PATH="$rocs_stub_bin:$PATH" ROCS_CORE_PROJECT="$tmp_root/rocs-core-missing" ./scripts/rocs.sh version 2>&1 >/dev/null)"
	rocs_status=$?
	set -e
	[ "$rocs_status" -eq 2 ] || fail "generated L2 ROCS launcher must exit 2 when the core checkout is missing (got $rocs_status)"
	printf '%s\n' "$rocs_stderr" | grep -qF "rocs-cli core checkout not found at $tmp_root/rocs-core-missing" ||
		fail "generated L2 ROCS launcher must explain a missing core (got: $rocs_stderr)"
	(cd "$generated_rocs_repo" && PATH="$rocs_stub_bin:$PATH" ROCS_CORE_PROJECT="$tmp_root/rocs-core-0.4.4" ./scripts/rocs.sh --doctor) | grep -qF "pin: 0.4.4" ||
		fail "generated L2 ROCS launcher --doctor must report the pin"
done

# Workspace discovery: inside a workspace holding every <repo:PATH@ref> layer the launcher
# defaults ROCS_WORKSPACE_ROOT to that ancestor; outside it falls back to $HOME/ai-society.
rocs_workspace="$tmp_root/rocs-workspace"
make_rocs_ref_repo() {
	ref_repo="$1"
	mkdir -p "$ref_repo/ontology/src"
	printf 'rocs:\n  layers:\n    - name: repo\n      path: ontology/src\n' >"$ref_repo/ontology/manifest.yaml"
	printf 'system4d: {}\n' >"$ref_repo/ontology/src/system4d.yaml"
	git -C "$ref_repo" init -q -b main
	git -C "$ref_repo" add -A
	git -C "$ref_repo" -c user.name=l0-check -c user.email=l0-check@example.invalid -c commit.gpgsign=false commit -q -m init
}
make_rocs_ref_repo "$rocs_workspace/core/ontology-kernel"
git -C "$rocs_workspace/core/ontology-kernel" -c tag.gpgsign=false tag v0.2.1
make_rocs_ref_repo "$rocs_workspace/holdingco/ontology"
assert_file_contains "$matrix_project_python/ontology/manifest.yaml" "<repo:core/ontology-kernel@v0.2.1>" "generated tpl-project-repo must layer the protected kernel release"
assert_file_contains "$matrix_project_python/ontology/manifest.yaml" "<repo:holdingco/ontology@main>" "generated tpl-project-repo must layer the company ontology"
assert_file_contains "$matrix_monorepo/ontology/manifest.yaml" "<repo:holdingco/ontology@main>" "generated tpl-monorepo must layer the company ontology"
mkdir -p "$rocs_workspace/holdingco/owned"
for rocs_case in project:"$matrix_project_python" monorepo:"$matrix_monorepo"; do
	rocs_case_name="${rocs_case%%:*}"
	rocs_consumer="$rocs_workspace/holdingco/owned/rocs-$rocs_case_name"
	cp -R "${rocs_case#*:}" "$rocs_consumer"
	rocs_output="$(cd "$rocs_consumer" && env -u ROCS_WORKSPACE_ROOT -u ROCS_RESOLVE_REFS PATH="$rocs_stub_bin:$PATH" ROCS_CORE_PROJECT="$tmp_root/rocs-core-0.4.4" ./scripts/rocs.sh validate --repo .)"
	printf '%s\n' "$rocs_output" | grep -qxF "workspace:$rocs_workspace" ||
		fail "generated $rocs_case_name launcher must discover the enclosing workspace (got: $rocs_output)"
done
rocs_fake_home="$tmp_root/rocs-home"
mkdir -p "$rocs_fake_home"
rocs_output="$(cd "$matrix_project_python" && env -u ROCS_WORKSPACE_ROOT HOME="$rocs_fake_home" PATH="$rocs_stub_bin:$PATH" ROCS_CORE_PROJECT="$tmp_root/rocs-core-0.4.4" ./scripts/rocs.sh validate --repo .)"
printf '%s\n' "$rocs_output" | grep -qxF "workspace:$rocs_fake_home/ai-society" ||
	fail "generated launcher outside a workspace must fall back to \$HOME/ai-society (got: $rocs_output)"

# End-to-end with the real workspace core when a compatible checkout exists: plain
# `./scripts/rocs.sh validate --repo .` resolves every layer, and the managed full.sh gate
# (cleanup -> validate -> build, strict under main-strict) leaves the tree clean.
rocs_real_core="${ROCS_CORE_PROJECT:-$HOME/ai-society/core/rocs-cli}"
if [ -f "$rocs_real_core/pyproject.toml" ] && command -v uv >/dev/null 2>&1 &&
	grep -Eq '^version = "0\.4\.([4-9]|[1-9][0-9]+)"' "$rocs_real_core/pyproject.toml"; then
	for rocs_case in project monorepo; do
		rocs_consumer="$rocs_workspace/holdingco/owned/rocs-$rocs_case"
		git -C "$rocs_consumer" init -q -b main
		git -C "$rocs_consumer" add -A
		git -C "$rocs_consumer" -c user.name=l0-check -c user.email=l0-check@example.invalid -c commit.gpgsign=false commit -q -m init
		(
			cd "$rocs_consumer"
			env -u ROCS_WORKSPACE_ROOT -u ROCS_RESOLVE_REFS -u ROCS_REPO ROCS_CORE_PROJECT="$rocs_real_core" ./scripts/rocs.sh validate --repo . >/dev/null ||
				fail "generated $rocs_case repo inside a workspace must validate all layers with plain ./scripts/rocs.sh validate --repo ."
			env -u ROCS_WORKSPACE_ROOT -u ROCS_RESOLVE_REFS -u ROCS_REPO ROCS_CORE_PROJECT="$rocs_real_core" ROCS_CI_PROFILE=main-strict AK_CMD=false ./scripts/ci/full.sh >/dev/null 2>&1 ||
				fail "generated $rocs_case full CI must pass the ROCS cleanup -> validate -> build gate under main-strict"
			[ -f ontology/dist/authority-receipt.json ] || fail "generated $rocs_case full CI must build ROCS outputs"
			[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "generated $rocs_case ROCS outputs must be gitignored (dirty tree after full CI)"
		)
	done
else
	echo "warning: skipping real-core ROCS end-to-end check (no compatible rocs-cli 0.4.x>=0.4.4 core at $rocs_real_core or uv missing)" >&2
fi

[ -s "$matrix_project_node/package.json" ] || fail "expected node project software-pack manifest"
[ ! -e "$matrix_project_node/tsconfig.json" ] || fail "node project should not emit tsconfig.json"
[ -s "$matrix_project_typescript/package.json" ] || fail "expected typescript project software-pack manifest"
[ -s "$matrix_project_typescript/tsconfig.json" ] || fail "expected typescript project tsconfig"

for required_file in \
	"$matrix_project_python/policy/engineering-lane.json" \
	"$matrix_project_python/docs/engineering.local.md" \
	"$matrix_project_node/package.json" \
	"$matrix_project_node/policy/engineering-lane.json" \
	"$matrix_project_node/docs/engineering.local.md" \
	"$matrix_project_typescript/package.json" \
	"$matrix_project_typescript/tsconfig.json" \
	"$matrix_project_typescript/policy/engineering-lane.json" \
	"$matrix_project_typescript/docs/engineering.local.md" \
	"$matrix_project_rust/policy/engineering-lane.json" \
	"$matrix_project_rust/docs/engineering.local.md" \
	"$matrix_project_elixir/mix.exs" \
	"$matrix_project_elixir/policy/engineering-lane.json" \
	"$matrix_project_elixir/docs/engineering.local.md" \
	"$matrix_monorepo/docs/engineering.local.md" \
	"$matrix_monorepo/packages/fixture-py-core/policy/engineering-lane.json" \
	"$matrix_monorepo/packages/fixture-py-core/docs/engineering.local.md" \
	"$matrix_monorepo/packages/fixture-ts-core/policy/engineering-lane.json" \
	"$matrix_monorepo/packages/fixture-ts-core/docs/engineering.local.md" \
	"$matrix_monorepo/packages/fixture-rust-core/policy/engineering-lane.json" \
	"$matrix_monorepo/packages/fixture-rust-core/docs/engineering.local.md" \
	"$matrix_monorepo/packages/fixture-elixir-core/policy/engineering-lane.json" \
	"$matrix_monorepo/packages/fixture-elixir-core/docs/engineering.local.md"; do
	[ -s "$required_file" ] || {
		echo "error: expected non-empty engineering contract artifact in language matrix: $required_file" >&2
		exit 1
	}
done

for generated_policy in \
	"$matrix_project_python/policy/engineering-lane.json" \
	"$matrix_project_node/policy/engineering-lane.json" \
	"$matrix_project_typescript/policy/engineering-lane.json" \
	"$matrix_project_rust/policy/engineering-lane.json" \
	"$matrix_project_elixir/policy/engineering-lane.json" \
	"$matrix_monorepo/packages/fixture-py-core/policy/engineering-lane.json" \
	"$matrix_monorepo/packages/fixture-ts-core/policy/engineering-lane.json" \
	"$matrix_monorepo/packages/fixture-rust-core/policy/engineering-lane.json" \
	"$matrix_monorepo/packages/fixture-elixir-core/policy/engineering-lane.json"; do
	grep -qF '"ref": "workspace-local-unpinned"' "$generated_policy" || {
		echo "error: expected workspace-local-unpinned engineering provenance in $generated_policy" >&2
		exit 1
	}
	if grep -qF -- "--prefer-repo" "$generated_policy"; then
		echo "error: generated stack policy should not pin repo-preferred lane resolution: $generated_policy" >&2
		exit 1
	fi
done

for generated_doc in \
	"$matrix_project_python/docs/engineering.local.md" \
	"$matrix_project_node/docs/engineering.local.md" \
	"$matrix_project_typescript/docs/engineering.local.md" \
	"$matrix_project_rust/docs/engineering.local.md" \
	"$matrix_project_elixir/docs/engineering.local.md" \
	"$matrix_monorepo/packages/fixture-py-core/docs/engineering.local.md" \
	"$matrix_monorepo/packages/fixture-ts-core/docs/engineering.local.md" \
	"$matrix_monorepo/packages/fixture-rust-core/docs/engineering.local.md" \
	"$matrix_monorepo/packages/fixture-elixir-core/docs/engineering.local.md"; do
	grep -qF "engineering_core.command" "$generated_doc" || {
		echo "error: generated stack override doc should point to the declared lane command: $generated_doc" >&2
		exit 1
	}
	if grep -qF "pins the upstream lane" "$generated_doc"; then
		echo "error: generated stack override doc should not overstate lane pinning: $generated_doc" >&2
		exit 1
	fi
	if grep -qF -- "--prefer-repo" "$generated_doc"; then
		echo "error: generated stack override doc should not hardcode repo-preferred lane resolution: $generated_doc" >&2
		exit 1
	fi
done

grep -qF "policy/engineering-lane.json" "$matrix_monorepo/docs/engineering.local.md" || {
	echo "error: monorepo stack doc should point packages/apps at policy/engineering-lane.json" >&2
	exit 1
}
if grep -qF "pinned upstream lane" "$matrix_monorepo/docs/engineering.local.md"; then
	echo "error: monorepo stack doc should not overstate lane pinning" >&2
	exit 1
fi
if grep -qF -- "--prefer-repo" "$matrix_monorepo/docs/engineering.local.md"; then
	echo "error: monorepo stack doc should not hardcode repo-preferred lane resolution" >&2
	exit 1
fi

# Regression: generated descendant surfaces must keep AK-native task-scope guidance aligned.
for generated_project in \
	"$colon_l2" \
	"$matrix_project_python" \
	"$matrix_project_node" \
	"$matrix_project_typescript" \
	"$matrix_project_rust" \
	"$matrix_project_elixir"; do
	assert_file_contains "$generated_project/README.md" "governance/task-scopes/AK-<TASK-ID>.snapshot.json" "generated tpl-project-repo README should describe frozen AK task-scope snapshots"
	assert_file_contains "$generated_project/governance/README.md" "transitional scaffolding" "generated tpl-project-repo governance README should describe non-authoritative hand-authored task-scope files"
	assert_file_contains "$generated_project/next_session_prompt.md" "Refresh task-scope snapshot" "generated tpl-project-repo next-session prompt should document AK task-scope refresh"
done

for generated_repo in \
	"$matrix_agent" \
	"$matrix_org"; do
	assert_file_contains "$generated_repo/README.md" "check-task-scope-snapshots.sh" "generated agent/org README should document task-scope snapshot validation"
	assert_file_contains "$generated_repo/governance/README.md" "transitional scaffolding" "generated agent/org governance README should describe non-authoritative hand-authored task-scope files"
done

generated_monorepo="$matrix_monorepo"
assert_file_contains "$generated_monorepo/README.md" "Packages/apps consume the monorepo-root snapshot" "generated tpl-monorepo README should keep member task-scope authority at the root"
assert_file_contains "$generated_monorepo/AGENTS.md" "packages/apps do not create standalone AK task-scope files" "generated tpl-monorepo AGENTS should forbid standalone member task-scope files"
assert_file_contains "$generated_monorepo/governance/README.md" "monorepo-root snapshot" "generated tpl-monorepo governance README should point members at the root snapshot"

for generated_package in \
	"$matrix_monorepo/packages/fixture-py-core" \
	"$matrix_monorepo/packages/fixture-ts-core" \
	"$matrix_monorepo/packages/fixture-rust-core" \
	"$matrix_monorepo/packages/fixture-elixir-core"; do
	assert_file_contains "$generated_package/README.md" "inherit deferred-work and explicit task-scope authority from the parent monorepo root" "generated tpl-package README should point task-scope authority back to the monorepo root"
	assert_file_contains "$generated_package/AGENTS.md" "Deferred work and explicit task scope live at the monorepo root" "generated tpl-package AGENTS should keep task-scope authority at the monorepo root"
	assert_path_absent "$generated_package/scripts/ak.sh" "generated tpl-package members must not ship a standalone AK wrapper"
	assert_path_absent "$generated_package/governance/task-scopes" "generated tpl-package members must not ship standalone task-scope snapshot directories"
done

"$python_exec" -m unittest tests/test_agent_template_v2.py tests/test_l1_template_ownership.py

echo "ok: l0 generation smoke + idempotency + ownership-aware template propagation"
