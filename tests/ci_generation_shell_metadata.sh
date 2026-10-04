# Test-owned generation implementation; sourced, never a public selector.

generation_shell_metadata() {
profile_phase rocs-workspace-and-real-core
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
git -C "$rocs_workspace/core/ontology-kernel" -c tag.gpgsign=false tag v0.4.0
make_rocs_ref_repo "$rocs_workspace/holdingco/ontology"
assert_file_contains "$matrix_project_python/ontology/manifest.yaml" "<repo:core/ontology-kernel@v0.4.0>" "generated tpl-project-repo must layer the protected kernel release"
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

profile_phase metadata-assertions
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

}
