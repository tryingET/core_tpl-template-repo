#!/usr/bin/env sh
set -eu

usage() {
	cat <<'EOF' >&2
usage: preview-l1-diff.sh <target-l1-repo-path> [repo-slug]

Renders a fresh L1 repo from this L0 into a temp directory and shows
non-destructive diff against the target L1 repository.
EOF
}

target_repo="${1:-}"
repo_slug="${2:-}"

if [ -z "$target_repo" ]; then
	usage
	exit 2
fi

if [ ! -d "$target_repo" ]; then
	echo "error: target repo path does not exist: $target_repo" >&2
	exit 2
fi

need_cmd() {
	command -v "$1" >/dev/null 2>&1 || {
		echo "error: missing dependency: $1" >&2
		exit 2
	}
}

need_cmd awk
need_cmd basename
need_cmd cp
need_cmd find
need_cmd git
need_cmd grep
need_cmd mkdir
need_cmd mktemp
need_cmd rm
need_cmd sort

repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
answers_lib="$repo_root/scripts/lib/copier-answers.sh"
[ -f "$answers_lib" ] || {
	echo "error: missing dependency: $answers_lib" >&2
	exit 2
}
repo_surface_lib="$repo_root/scripts/lib/repo-surface.sh"
[ -f "$repo_surface_lib" ] || {
	echo "error: missing dependency: $repo_surface_lib" >&2
	exit 2
}
# shellcheck source=/dev/null
. "$answers_lib"
# shellcheck source=/dev/null
. "$repo_surface_lib"

is_lane_root_baseline_dir() {
	dir="$1"

	[ -d "$dir" ] || return 1
	[ -f "$dir/.gitignore" ] || return 1
	[ -f "$dir/.copier-answers.yml" ] || return 1
	grep -qF "# Track lane baseline only." "$dir/.gitignore" || return 1

	src_path=""
	src_status=0
	src_path="$(copier_answers_try_scalar "$dir/.copier-answers.yml" _src_path 2>/dev/null)" || src_status=$?
	[ "$src_status" -eq 0 ] || return 1

	repo_surface_is_tpl_project_src_path "$src_path"
}

materialize_lane_root_baselines() {
	render_tree="$1"
	target_tree="$2"
	materialized=0

	top_level_dirs="$(find "$target_tree" -mindepth 1 -maxdepth 1 -type d | LC_ALL=C sort || true)"
	if [ -n "$top_level_dirs" ]; then
		while IFS= read -r dir; do
			[ -n "$dir" ] || continue
			if ! is_lane_root_baseline_dir "$dir"; then
				continue
			fi

			lane_name="$(basename "$dir")"
			project_owner_handle=""
			project_owner_status=0
			preserve_missing_project_owner_handle=0
			if ! yaml_key_present "$dir/.copier-answers.yml" project_owner_handle; then
				preserve_missing_project_owner_handle=1
			fi
			project_owner_handle="$(read_lane_project_owner_handle "$dir")" || project_owner_status=$?
			[ "$project_owner_status" -eq 0 ] || return "$project_owner_status"
			(
				cd "$render_tree"
				if [ -n "$project_owner_handle" ] && [ "$preserve_missing_project_owner_handle" -eq 1 ]; then
					PROJECT_OWNER_HANDLE="$project_owner_handle" PRESERVE_MISSING_PROJECT_OWNER_HANDLE=1 ./scripts/bootstrap-lane-root.sh "$lane_name" >/dev/null
				elif [ -n "$project_owner_handle" ]; then
					PROJECT_OWNER_HANDLE="$project_owner_handle" ./scripts/bootstrap-lane-root.sh "$lane_name" >/dev/null
				elif [ "$preserve_missing_project_owner_handle" -eq 1 ]; then
					DISABLE_PROJECT_OWNER_HANDLE_INFERENCE=1 PRESERVE_MISSING_PROJECT_OWNER_HANDLE=1 ./scripts/bootstrap-lane-root.sh "$lane_name" >/dev/null
				else
					./scripts/bootstrap-lane-root.sh "$lane_name" >/dev/null
				fi
			)
			materialized=$((materialized + 1))
		done <<EOF
$top_level_dirs
EOF
	fi

	printf '%s\n' "$materialized"
}

prune_nested_child_repos() {
	tree="$1"
	pruned=0

	nested_repo_dirs="$(repo_surface_find_nested_repo_roots "$tree" || true)"
	if [ -n "$nested_repo_dirs" ]; then
		while IFS= read -r child_repo_dir; do
			[ -n "$child_repo_dir" ] || continue
			[ -d "$child_repo_dir" ] || continue
			rm -rf "$child_repo_dir"
			pruned=$((pruned + 1))
		done <<EOF
$nested_repo_dirs
EOF
	fi

	printf '%s\n' "$pruned"
}

yaml_key_present() {
	answers_path="$1"
	key="$2"

	[ -f "$answers_path" ] || return 1
	grep -q "^[[:space:]]*$key:[[:space:]]*" "$answers_path"
}

read_preview_json_string_value() {
	json_path="$1"
	key="$2"

	[ -f "$json_path" ] || return 1

	awk -v key="$key" '
    BEGIN {
      status = 1
      pattern = "\"" key "\"[[:space:]]*:[[:space:]]*\"[^\"]*\""
    }

    {
      if ($0 !~ pattern) {
        next
      }

      value = $0
      sub("^.*\"" key "\"[[:space:]]*:[[:space:]]*\"", "", value)
      sub("\".*$", "", value)
      print value
      status = 0
      exit
    }

    END {
      exit status
    }
  ' "$json_path"
}

read_lane_project_owner_handle() {
	lane_dir="$1"
	answers_path="$lane_dir/.copier-answers.yml"
	work_items_path="$lane_dir/governance/work-items.json"
	value=""
	status=0

	if yaml_key_present "$answers_path" project_owner_handle; then
		value="$(copier_answers_try_scalar "$answers_path" project_owner_handle 2>/dev/null)" || status=$?
		if [ "$status" -eq 0 ]; then
			printf '%s\n' "$value"
			return 0
		fi
		return "$status"
	fi

	value="$(read_preview_json_string_value "$work_items_path" owner 2>/dev/null)" || status=$?
	case "$status" in
	0)
		printf '%s\n' "$value"
		return 0
		;;
	1)
		printf '\n'
		return 0
		;;
	*)
		return "$status"
		;;
	esac
}

read_preview_answer_value() {
	answers_path="$1"
	key="$2"
	value=""
	status=0

	value="$(copier_answers_try_scalar "$answers_path" "$key" 2>/dev/null)" || status=$?

	if [ "$status" -eq 0 ]; then
		printf '%s\n' "$value"
		return 0
	fi

	echo "error: unable to parse '$key' from $answers_path; install python3/python with PyYAML for multiline or escaped Copier answers" >&2
	return "$status"
}

answers_file="$target_repo/.copier-answers.yml"

if [ -z "$repo_slug" ] && [ -f "$answers_file" ]; then
	repo_slug_from_answers=""
	repo_slug_status=0
	repo_slug_from_answers="$(read_preview_answer_value "$answers_file" repo_slug)" || repo_slug_status=$?
	[ "$repo_slug_status" -eq 0 ] || exit "$repo_slug_status"
	if [ -n "$repo_slug_from_answers" ]; then
		repo_slug="$repo_slug_from_answers"
	fi
fi

if [ -z "$repo_slug" ]; then
	repo_slug="$(basename "$target_repo")"
fi

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

render_dir="$tmp_root/l1-render"

set -- --defaults --overwrite

if [ -f "$answers_file" ]; then
	for key in $(copier_answers_l1_preview_keys); do
		value=""
		value_status=0
		value="$(read_preview_answer_value "$answers_file" "$key")" || value_status=$?
		[ "$value_status" -eq 0 ] || exit "$value_status"
		if [ -n "$value" ]; then
			set -- "$@" -d "$key=$value"
		fi
	done
fi

set -- "$@" -d "repo_slug=$repo_slug"

"$repo_root/scripts/new-l1-from-copier.sh" "$render_dir" "$@" >/dev/null

echo "==> rendered: $render_dir"
echo "==> target:   $target_repo"

if repo_surface_is_git_repo "$target_repo"; then
	if [ -n "$(git -C "$target_repo" status --porcelain)" ]; then
		echo "warning: target repo has uncommitted changes; diff may include local edits" >&2
	fi
fi

compare_render_dir="$tmp_root/l1-render-compare"
compare_target_dir="$tmp_root/l1-target-compare"
mkdir -p "$compare_render_dir" "$compare_target_dir"
cp -R "$render_dir/." "$compare_render_dir/"
cp -R "$target_repo/." "$compare_target_dir/"
rm -rf "$compare_render_dir/.git" "$compare_target_dir/.git"

materialized_lane_roots="$(materialize_lane_root_baselines "$compare_render_dir" "$compare_target_dir")"
if [ "$materialized_lane_roots" -gt 0 ]; then
	echo "note: materialized canonical lane-root baselines: $materialized_lane_roots"
fi

pruned_surfaces="$(prune_nested_child_repos "$compare_target_dir")"
if [ "$pruned_surfaces" -gt 0 ]; then
	echo "note: ignored nested child repos: $pruned_surfaces"
fi

set +e
git --no-pager diff --no-index -- "$compare_render_dir" "$compare_target_dir"
status=$?
set -e

# git diff --no-index exits 1 when differences are found.
if [ "$status" -gt 1 ]; then
	echo "error: diff command failed" >&2
	exit "$status"
fi

if [ "$status" -eq 0 ]; then
	echo "ok: no diff between rendered L1 and target"
else
	echo "info: differences detected (expected during adoption)"
fi
