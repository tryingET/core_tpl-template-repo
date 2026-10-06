# Test-owned generation implementation; sourced, never a public selector.

generation_shell_launchers() {
assert_command_fails "root ROCS doctor must fail closed when ROCS_BIN is invalid" env ROCS_BIN=/definitely/missing "$repo_root/scripts/rocs.sh" --doctor
assert_command_fails "root ROCS which must fail closed when ROCS_BIN is invalid" env ROCS_BIN=/definitely/missing "$repo_root/scripts/rocs.sh" --which
profile_phase rocs-launchers
# Generated L2 ROCS launcher: runs the workspace rocs-cli core pinned by rocs_cli_version.
# A stub `uv` records the exec so these checks need neither network nor a real core.
rocs_stub_bin="$tmp_root/rocs-stub-bin"
mkdir -p "$rocs_stub_bin"
cat >"$rocs_stub_bin/uv" <<'EOF'
#!/bin/sh
printf 'stub-uv:%s\n' "$*"
printf 'workspace:%s\n' "$ROCS_WORKSPACE_ROOT"
printf 'resolve-refs:%s\n' "$ROCS_RESOLVE_REFS"
printf 'output-root:%s\n' "${ROCS_OUTPUT_ROOT:-}"
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

# Generated L1 root ROCS launcher: the same pinned-core model as L2, plus company
# settings sourced from the target-only local/rocs.env.
l1_rocs="$tmp_root/l1-template-sample"
assert_file_contains "$l1_rocs/scripts/rocs.sh" 'rocs_cli_pin="0.4.4"' "generated L1 ROCS launcher must pin rocs-cli 0.4.4"
assert_path_absent "$l1_rocs/tools/rocs-cli" "generated L1 repos must not vendor rocs-cli"
rocs_output="$(cd "$l1_rocs" && env -u ROCS_OUTPUT_ROOT PATH="$rocs_stub_bin:$PATH" ROCS_CORE_PROJECT="$tmp_root/rocs-core-0.4.4" ./scripts/rocs.sh validate --repo .)" ||
	fail "generated L1 ROCS launcher must run a compatible core"
printf '%s\n' "$rocs_output" | grep -qxF "stub-uv:run --frozen --project $tmp_root/rocs-core-0.4.4 python -m rocs_cli validate --repo ." ||
	fail "generated L1 ROCS launcher must exec uv run --frozen against the pinned core (got: $rocs_output)"
printf '%s\n' "$rocs_output" | grep -qxF "output-root:" || fail "generated L1 ROCS launcher must not invent an output root (got: $rocs_output)"
assert_command_fails "generated L1 ROCS launcher must reject an incompatible core" env PATH="$rocs_stub_bin:$PATH" ROCS_CORE_PROJECT="$tmp_root/rocs-core-0.4.3" "$l1_rocs/scripts/rocs.sh" version
mkdir -p "$l1_rocs/local"
printf 'ROCS_OUTPUT_ROOT=governance/ontology-dist\n' >"$l1_rocs/local/rocs.env"
rocs_output="$(cd "$l1_rocs" && env -u ROCS_OUTPUT_ROOT PATH="$rocs_stub_bin:$PATH" ROCS_CORE_PROJECT="$tmp_root/rocs-core-0.4.4" ./scripts/rocs.sh validate --repo .)"
printf '%s\n' "$rocs_output" | grep -qxF "output-root:governance/ontology-dist" ||
	fail "generated L1 ROCS launcher must export company settings from local/rocs.env (got: $rocs_output)"
printf 'echo "company guard: $1" >&2\nexit 3\n' >"$l1_rocs/local/rocs.env"
set +e
rocs_stderr="$(cd "$l1_rocs" && PATH="$rocs_stub_bin:$PATH" ROCS_CORE_PROJECT="$tmp_root/rocs-core-0.4.4" ./scripts/rocs.sh validate --repo . 2>&1 >/dev/null)"
rocs_status=$?
set -e
[ "$rocs_status" -eq 3 ] || fail "a failing local/rocs.env must abort the L1 ROCS launcher (got $rocs_status)"
printf '%s\n' "$rocs_stderr" | grep -qxF "company guard: validate" || fail "local/rocs.env must see the launcher arguments (got: $rocs_stderr)"
rm -rf "$l1_rocs/local"

profile_phase local-hooks
# Company-owned local/ extension points: every L1 root entry script runs its local/
# counterpart from the repo root, and the hook's failure fails the entry script.
l1_hooks="$tmp_root/l1-local-hooks"
cp -R "$tmp_root/l1-template-sample" "$l1_hooks"
init_ontology_probe_index "$l1_hooks"
l1_hooks_real="$(cd "$l1_hooks" && pwd -P)"
local_hook_log="$tmp_root/l1-local-hooks.log"
write_local_hook() {
	mkdir -p "$(dirname -- "$l1_hooks/$1")"
	cat >"$l1_hooks/$1" <<EOF
#!/bin/sh
echo "$1 \$(pwd -P) \$*" >>"$local_hook_log"
exit "\${LOCAL_HOOK_STATUS:-0}"
EOF
	chmod +x "$l1_hooks/$1"
}
run_l1_entry() {
	(cd "$tmp_root" && env AK_CMD=false "$@" </dev/null >/dev/null 2>&1)
}
for local_case in \
	"scripts/ci/smoke.sh:local/ci/smoke.sh" \
	"scripts/ci/full.sh:local/ci/full.sh" \
	".githooks/pre-commit:local/githooks/pre-commit" \
	".githooks/pre-push:local/githooks/pre-push" \
	"scripts/install-hooks.sh:local/install-hooks.sh"; do
	entry="${local_case%%:*}"
	hook="${local_case#*:}"
	run_l1_entry "$l1_hooks/$entry" || fail "L1 $entry must pass without a company hook"
	write_local_hook "$hook"
	: >"$local_hook_log"
	run_l1_entry LOCAL_HOOK_STATUS=0 "$l1_hooks/$entry" || fail "L1 $entry must pass when $hook passes"
	grep -qF "$hook $l1_hooks_real" "$local_hook_log" ||
		fail "L1 $entry must run $hook from the repo root (log: $(cat "$local_hook_log"))"
	if run_l1_entry LOCAL_HOOK_STATUS=1 "$l1_hooks/$entry"; then
		fail "L1 $entry must fail when $hook fails"
	fi
	chmod a-x "$l1_hooks/$hook"
	if run_l1_entry "$l1_hooks/$entry"; then
		fail "L1 $entry must fail when $hook exists but is not executable"
	fi
	rm -f "$l1_hooks/$hook"
done
(cd "$tmp_root" && env AK_CMD=false "$l1_hooks/scripts/ci/full.sh" --deep-typo >/dev/null 2>&1) &&
	fail "L1 full.sh must keep rejecting unknown arguments"
write_local_hook local/githooks/pre-push
: >"$local_hook_log"
(cd "$tmp_root" && env AK_CMD=false "$l1_hooks/.githooks/pre-push" origin https://example.invalid/repo.git </dev/null >/dev/null 2>&1) ||
	fail "L1 pre-push must pass with a passing company hook"
grep -qxF "local/githooks/pre-push $l1_hooks_real origin https://example.invalid/repo.git" "$local_hook_log" ||
	fail "L1 pre-push must forward git's arguments to local/githooks/pre-push (log: $(cat "$local_hook_log"))"
rm -f "$l1_hooks/local/githooks/pre-push"
write_local_hook local/ci/check-template-ci.sh
: >"$local_hook_log"
if run_l1_entry LOCAL_HOOK_STATUS=1 "$l1_hooks/scripts/check-template-ci.sh"; then
	fail "L1 check-template-ci.sh must fail when local/ci/check-template-ci.sh fails"
fi
grep -qF "local/ci/check-template-ci.sh $l1_hooks_real" "$local_hook_log" ||
	fail "L1 check-template-ci.sh must run local/ci/check-template-ci.sh first (log: $(cat "$local_hook_log"))"
rm -rf "$l1_hooks"

# Staged-file UBS pre-commit (port of softwareco b46f03a/e8d3851): new project/monorepo copies
# self-initialize git and point core.hooksPath at .githooks; the hook degrades gracefully when
# the helper is missing or reports the scanner unavailable (exit 2) and blocks on findings.
ubs_stub_dir="$tmp_root/ubs-stub"
mkdir -p "$ubs_stub_dir"
for ubs_status in 0 1 2; do
	printf '#!/bin/sh\necho ubs-stub-ran\nexit %s\n' "$ubs_status" >"$ubs_stub_dir/ubs-$ubs_status.sh"
	chmod +x "$ubs_stub_dir/ubs-$ubs_status.sh"
done
for generated_hook_repo in "$matrix_project_python" "$matrix_monorepo"; do
	[ -x "$generated_hook_repo/.githooks/pre-commit" ] || fail "generated repo must ship an executable .githooks/pre-commit: $generated_hook_repo"
	[ -x "$generated_hook_repo/scripts/install-hooks.sh" ] || fail "generated repo must ship an executable scripts/install-hooks.sh: $generated_hook_repo"
	[ -d "$generated_hook_repo/.git" ] || fail "new project/monorepo copies must self-initialize git: $generated_hook_repo"
	[ "$(git -C "$generated_hook_repo" config --get core.hooksPath)" = ".githooks" ] || fail "new project/monorepo copies must enable .githooks automatically: $generated_hook_repo"
	assert_file_contains "$generated_hook_repo/.githooks/pre-commit" '$HOME/ai-society/holdingco/scripts/ubs-staged.sh' "generated pre-commit must resolve the company workspace UBS helper"
	hook_stderr="$(cd "$generated_hook_repo" && UBS_STAGED="$tmp_root/ubs-missing.sh" ./.githooks/pre-commit 2>&1 >/dev/null)" ||
		fail "generated pre-commit must not block when the UBS helper is missing"
	printf '%s\n' "$hook_stderr" | grep -qF "UBS helper not found at $tmp_root/ubs-missing.sh" || fail "generated pre-commit must explain a missing UBS helper (got: $hook_stderr)"
	(cd "$generated_hook_repo" && UBS_STAGED="$ubs_stub_dir/ubs-0.sh" ./.githooks/pre-commit >/dev/null 2>&1) || fail "generated pre-commit must pass a clean UBS run"
	(cd "$generated_hook_repo" && UBS_STAGED="$ubs_stub_dir/ubs-2.sh" ./.githooks/pre-commit >/dev/null 2>&1) || fail "generated pre-commit must not block when UBS reports the scanner unavailable (exit 2)"
	assert_command_fails "generated pre-commit must block on UBS findings" sh -c 'cd "$1" && UBS_STAGED="$2" ./.githooks/pre-commit' sh "$generated_hook_repo" "$ubs_stub_dir/ubs-1.sh"
done
nested_hook_parent="$tmp_root/hook-parent"
mkdir -p "$nested_hook_parent"
git -C "$nested_hook_parent" init -q -b main
cp -R "$matrix_project_python" "$nested_hook_parent/child"
rm -rf "$nested_hook_parent/child/.git"
(cd "$nested_hook_parent/child" && ./scripts/install-hooks.sh >/dev/null 2>&1) || true
[ -z "$(git -C "$nested_hook_parent" config --get core.hooksPath || true)" ] || fail "install-hooks.sh must not reconfigure an enclosing parent repository"
# Template refreshes rerun _tasks: an existing repo's own hooks path (e.g. .git/ubs-chain-hooks) must survive.
custom_hook_repo="$tmp_root/hook-custom"
cp -R "$matrix_project_python" "$custom_hook_repo"
git -C "$custom_hook_repo" config core.hooksPath .git/ubs-chain-hooks
(cd "$custom_hook_repo" && ./scripts/install-hooks.sh >/dev/null 2>&1) || fail "install-hooks.sh must succeed when a custom hooks path is set"
[ "$(git -C "$custom_hook_repo" config --get core.hooksPath)" = ".git/ubs-chain-hooks" ] || fail "install-hooks.sh must not replace an existing custom core.hooksPath"

}
