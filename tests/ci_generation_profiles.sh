# Original profile proof, preprofile negatives, and scratch fixtures.

generation_preprofile_probes() {
missing_node_bin="$tmp_root/missing-node-bin"
mkdir -p "$missing_node_bin"
for tool_name in sh dirname pwd; do
	ln -s "$(command -v "$tool_name")" "$missing_node_bin/$tool_name"
done
missing_node_checker="$tmp_root/docs-ref-check.mjs"
printf 'console.log("ok")\n' >"$missing_node_checker"
assert_command_fails_with_stderr "check-doc-references should fail closed on invalid DOC_REF_CHECK_SCRIPT overrides" "docs-ref-check override points to missing file" env DOC_REF_CHECK_SCRIPT=/definitely/missing sh "$repo_root/scripts/check-doc-references.sh"
assert_command_fails_with_stderr "check-doc-references should fail clearly when node is unavailable" "missing dependency: node" env PATH="$missing_node_bin" DOC_REF_CHECK_SCRIPT="$missing_node_checker" sh "$repo_root/scripts/check-doc-references.sh"

}

generation_profile_fixtures() {
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


}

render_l1_case() {
	case_name="$1"
	enable_community_pack="$2"
	enable_release_pack="$3"
	enable_vouch_gate="$4"
	l1_org_docs_profile="$5"
	l1_dir="$tmp_root/$case_name"
	profile_phase "profile-$case_name"

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
	profile_phase "profile-$case_name-complete"
}

generation_rich_org_doc() {
	[ -s "$rich_l1/docs/org/$org_doc" ] || fail "fresh rich L1 must render docs/org/$org_doc"
}

generation_compact_org_doc() {
	assert_path_absent "$compact_l1/docs/org/$org_doc" "fresh compact L1 must omit rich-only docs/org/$org_doc"
}

generation_compact_operating_model() {
[ -s "$compact_l1/docs/org/operating_model.md" ] || fail "fresh compact L1 must retain docs/org/operating_model.md"
}

generation_rich_docs() {
	rich_l1="$tmp_root/l1-template-sample"
	for org_doc in purpose.md mission.md vision.md strategic_objectives.md values_ethics.md governance.md glossary.md; do
		generation_rich_org_doc
	done
}

generation_compact_docs() {
	compact_l1="$tmp_root/l1-template-compact-org"
	for org_doc in purpose.md mission.md vision.md strategic_objectives.md values_ethics.md governance.md glossary.md; do
		generation_compact_org_doc
	done
	generation_compact_operating_model
}
