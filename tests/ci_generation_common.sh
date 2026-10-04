# Test-owned shared generation context and original assertion helpers.

need_cmd() {
	command -v "$1" >/dev/null 2>&1 || {
		echo "error: missing dependency: $1" >&2
		exit 2
	}
}
fail() {
	echo "error: $*" >&2
	exit 1
}

# Opt-in observation only: named phase boundaries, no scheduling/coverage changes.
profile_phase() {
	[ -n "${L0_PROFILE_DIR:-}" ] || return 0
	if [ -z "$profile_phase_file" ]; then
		profile_phase_file="$L0_PROFILE_DIR/generation-phases-$$.tsv"
		"$python_exec" -B "$repo_root/tests/ci_profile_io.py" --initialize "$profile_phase_file" "$1"
	else
		"$python_exec" -B "$repo_root/tests/ci_profile_io.py" "$profile_phase_file" "$1"
	fi
}

# These generated L1 entrypoint probes need a real index, not the caller's Git state.
init_ontology_probe_index() (
	unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
	git -C "$1" init -q
	git -C "$1" add -- ontology/.gitkeep
)

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

generation_context() {
cd "$repo_root"
# Scratch L1s have no enclosing workspace; bind births to this exact L0 source.
export L0_TEMPLATE_ROOT="$repo_root"


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

profile_phase_file=""
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

}
