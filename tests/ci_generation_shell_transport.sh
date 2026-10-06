# Test-owned generation implementation; sourced, never a public selector.

generation_shell_transport() {
# Regression check: inherited string values must preserve punctuation and quoting.
profile_phase transport
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

profile_phase defaults-and-bootstrap
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
init_ontology_probe_index "$suffix_l1"
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
	chmod a-x scripts/rocs.sh
	./scripts/install-hooks.sh >/dev/null
	[ -x scripts/rocs.sh ] || {
		echo "error: install-hooks should restore executable bit for the generated L1 ROCS wrapper" >&2
		exit 1
	}
)

}
