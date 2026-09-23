#!/usr/bin/env sh
# ROCS consumer-model guardrails for the L2 templates (split out of check-l0-guardrails.sh
# to keep that file within its line budget). Asserts the pinned-core ROCS launcher (no
# vendored bundle), the cleanup -> validate -> build CI gate, ROCS output ignores,
# LF-only launcher/CI scripts, and workspace ref defaults.
set -eu

repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root"

fail() {
	echo "error: $*" >&2
	exit 1
}

assert_file() {
	path="$1"
	[ -f "$path" ] || fail "missing required file: $path"
}

assert_exec() {
	path="$1"
	[ -x "$path" ] || fail "expected executable file: $path"
}

assert_dir() {
	path="$1"
	[ -d "$path" ] || fail "missing required directory: $path"
}

assert_absent() {
	path="$1"
	[ ! -e "$path" ] || fail "legacy path must be absent: $path"
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


assert_yaml_default() {
	path="$1"
	section="$2"
	expected="$3"
	label="$4"
	actual="$(awk -v section="$section:" '''
		$0 == section { inside = 1; next }
		inside && /^[^[:space:]]/ { exit }
		inside && $1 == "default:" {
			sub(/^[[:space:]]*default:[[:space:]]*/, "")
			gsub(/^"|"$/, "")
			print
			exit
		}
	''' "$path")"
	[ "$actual" = "$expected" ] || fail "$label (found ${actual:-<missing>} in $path)"
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

for tpl in tpl-project-repo tpl-monorepo tpl-package; do
	assert_yaml_default "copier-template/copier/$tpl/copier.yml" kernel_ontology_ref '<repo:core/ontology-kernel@v0.2.1>' "$tpl should default core ontology refs to the protected release tag"
	assert_contains "copier-template/copier/$tpl/copier.yml" 'default: "<repo:{{ company_slug }}/ontology@main>"' "$tpl should default company ontology refs to workspace repo locators"
	assert_not_contains "copier-template/copier/$tpl/copier.yml" "<gitlab:" "$tpl must not default to legacy gitlab locators rejected by rocs-cli"
done
assert_file "copier-template/copier/tpl-monorepo/ontology/manifest.yaml.j2"
assert_file "copier-template/copier/tpl-monorepo/ontology/src/system4d.yaml"
assert_contains "copier-template/copier/tpl-monorepo/ontology/manifest.yaml.j2" '{{ kernel_ontology_ref }}' "tpl-monorepo manifest must layer the core ontology"
assert_contains "copier-template/copier/tpl-monorepo/ontology/manifest.yaml.j2" '{{ company_ontology_ref }}' "tpl-monorepo manifest must layer the company ontology"

# ROCS launcher: runs the workspace rocs-cli core checkout pinned by rocs_cli_version;
# no vendored tools/rocs-cli bundle and no uvx/PATH fallbacks.
rocs_expected_pin="0.4.3"
rocs_launcher_source="copier-template/copier/tpl-project-repo/scripts/rocs.sh.j2"
assert_contains "$rocs_launcher_source" 'rocs_cli_pin="{{ rocs_cli_version }}"' "ROCS launcher must render the rocs_cli_version pin"
assert_contains "$rocs_launcher_source" 'core="${ROCS_CORE_PROJECT:-$HOME/ai-society/core/rocs-cli}"' "ROCS launcher must default to the workspace rocs-cli core"
assert_contains "$rocs_launcher_source" 'exec uv run --frozen --project "$core" python -m rocs_cli "$@"' "ROCS launcher must run the pinned core through uv run --frozen"
assert_contains "$rocs_launcher_source" 'ROCS_WORKSPACE_ROOT="$HOME/ai-society"' "ROCS launcher must fall back to the ai-society workspace root"
assert_contains "$rocs_launcher_source" '[ ! -d "$ws/${ref#*/}" ]' "ROCS launcher must mirror rocs-cli workspace discovery incl. the prefix case"
assert_contains "$rocs_launcher_source" 'ROCS_RESOLVE_REFS="${ROCS_RESOLVE_REFS:-1}"' "ROCS launcher must resolve workspace refs by default"
assert_contains "$rocs_launcher_source" "--doctor)" "ROCS launcher must keep a --doctor mode"
for forbidden in uvx ROCS_ALLOW_PATH_FALLBACK tools/rocs-cli ROCS_BIN; do
	assert_not_contains "$rocs_launcher_source" "$forbidden" "ROCS launcher must not keep legacy fallbacks"
done
if grep -nE '\{%|\{#' "$rocs_launcher_source" >/dev/null; then
	fail "ROCS launcher contains Jinja block/comment delimiters: $rocs_launcher_source"
fi
for tpl in tpl-project-repo tpl-agent-repo tpl-org-repo tpl-monorepo; do
	assert_absent "copier-template/copier/$tpl/tools/rocs-cli"
	assert_yaml_default "copier-template/copier/$tpl/copier.yml" rocs_cli_version "$rocs_expected_pin" "$tpl must pin rocs-cli $rocs_expected_pin"
	if [ "$tpl" != "tpl-project-repo" ]; then
		assert_files_equal "$rocs_launcher_source" "copier-template/copier/$tpl/scripts/rocs.sh.j2" "ROCS launcher must be identical in $tpl"
	fi
done
for rocs_launcher in \
	fixtures/l2/tpl-project-repo/scripts/rocs.sh \
	fixtures/l2/tpl-agent-repo/scripts/rocs.sh \
	fixtures/l2/tpl-org-repo/scripts/rocs.sh \
	fixtures/l2/tpl-monorepo/scripts/rocs.sh \
	fixtures/matrix/tpl-project-repo/python/scripts/rocs.sh \
	fixtures/matrix/tpl-monorepo/root/scripts/rocs.sh; do
	assert_contains "$rocs_launcher" "rocs_cli_pin=\"$rocs_expected_pin\"" "rendered ROCS launcher must carry the rendered pin"
	assert_absent "$(dirname -- "$(dirname -- "$rocs_launcher")")/tools/rocs-cli"
done
for rocs_launcher in fixtures/l1/template-repo/copier/tpl-project-repo/scripts/rocs.sh.j2 fixtures/l1/template-repo/copier/tpl-monorepo/scripts/rocs.sh.j2; do
	assert_files_equal "$rocs_launcher_source" "$rocs_launcher" "L1 fixture ROCS launcher must match the L0 source"
done

# ROCS CI gate: cleanup -> validate -> build, never a destructive --clean/rm of ontology/dist,
# and ROCS outputs stay untracked.
for tpl in tpl-project-repo tpl-agent-repo tpl-org-repo tpl-monorepo; do
	full_sh="copier-template/copier/$tpl/scripts/ci/full.sh"
	assert_contains "$full_sh" "./scripts/rocs.sh cleanup --repo ." "$tpl full CI must clean managed ROCS outputs through the launcher"
	assert_contains "$full_sh" "./scripts/rocs.sh validate --repo . \$rocs_ref_mode_args" "$tpl full CI must validate through the sealed launcher"
	assert_contains "$full_sh" "./scripts/rocs.sh build --repo . \$rocs_ref_mode_args" "$tpl full CI must build through the sealed launcher"
	assert_contains "$full_sh" 'main-strict | branch-ci) rocs_ref_mode_args="--workspace-ref-mode strict"' "$tpl full CI must pin strict workspace ref matching under CI profiles"
	if grep -nE -- '--clean|rm -rf[^#]*ontology/dist' "$full_sh" | grep -v '^[0-9]*:[[:space:]]*#' | grep -q .; then
		fail "$tpl full CI must not wipe ontology/dist (--clean or rm): $full_sh"
	fi
	assert_not_contains "$full_sh" "--resolve-refs" "$tpl full CI should rely on the sealed launcher's default ref resolution"
	validate_line="$(grep -n 'rocs.sh validate' "$full_sh" | head -n 1 | cut -d: -f1)"
	build_line="$(grep -n 'rocs.sh build' "$full_sh" | head -n 1 | cut -d: -f1)"
	cleanup_line="$(grep -n 'rocs.sh cleanup' "$full_sh" | head -n 1 | cut -d: -f1)"
	[ "$cleanup_line" -lt "$validate_line" ] && [ "$validate_line" -lt "$build_line" ] || fail "$tpl full CI must run ROCS cleanup -> validate -> build in order"
	assert_file "copier-template/copier/$tpl/.gitignore"
	assert_contains "copier-template/copier/$tpl/.gitignore" "/ontology/dist/" "$tpl must gitignore generated ROCS outputs"
	assert_file "copier-template/copier/$tpl/.gitattributes"
	for lf_pattern in "*.sh text eol=lf" "scripts/rocs.sh text eol=lf" "scripts/ci/*.sh text eol=lf"; do
		assert_contains "copier-template/copier/$tpl/.gitattributes" "$lf_pattern" "$tpl must force LF on ROCS launcher and CI scripts"
	done
done
for rocs_gitignore in \
	fixtures/l2/tpl-project-repo/.gitignore \
	fixtures/l2/tpl-agent-repo/.gitignore \
	fixtures/l2/tpl-org-repo/.gitignore \
	fixtures/l2/tpl-monorepo/.gitignore \
	fixtures/matrix/tpl-project-repo/python/.gitignore \
	fixtures/matrix/tpl-monorepo/root/.gitignore; do
	assert_contains "$rocs_gitignore" "/ontology/dist/" "rendered L2 repo must gitignore generated ROCS outputs"
done
assert_contains "copier-template/.gitignore" "/ontology/dist/" "generated L1 must gitignore its ROCS outputs"
assert_contains "copier-template/.gitignore" "/*/ontology/dist/" "generated L1 must keep lane-root ROCS outputs ignored after lane re-includes"
if git ls-files | grep -E '(^|/)ontology/dist/' | grep -q .; then
	fail "ROCS generated outputs (ontology/dist) must not be tracked"
fi

echo "ok: l0 rocs consumer model"
