#!/usr/bin/env bash
# migrate-l1-structure.sh - Stage migration from old <company>-templates layout to company-root L1 layout.
#
# Usage:
#   ./scripts/migrate-l1-structure.sh <company_slug> [company_name]
#
# Example:
#   AI_SOCIETY_CUSTOM_LANES=data,ml-platform ./scripts/migrate-l1-structure.sh softwareco "Software Company"
#
# Safety model:
#   - Non-destructive: does NOT move/delete source folders.
#   - Creates a staged target at ~/ai-society/<company>-stage
#   - Copies lanes + extras with rsync (preserves nested .git repos)
#   - Bootstraps lane-root baseline control planes + lane ignore policy
#   - You swap manually after verification.

set -euo pipefail

company_slug="${1:-}"
company_name="${2:-${company_slug}}"

if [[ -z "$company_slug" ]]; then
	echo "usage: migrate-l1-structure.sh <company_slug> [company_name]" >&2
	echo "  example: AI_SOCIETY_CUSTOM_LANES=data,ml-platform ./scripts/migrate-l1-structure.sh softwareco 'Software Company'" >&2
	exit 2
fi

need_cmd() {
	command -v "$1" >/dev/null 2>&1 || {
		echo "error: missing dependency: $1" >&2
		exit 2
	}
}

need_cmd git
need_cmd rsync

workspace_root="${AI_SOCIETY_WORKSPACE:-$HOME/ai-society}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_surface_lib="$repo_root/scripts/lib/repo-surface.sh"
[ -f "$repo_surface_lib" ] || {
	echo "error: missing dependency: $repo_surface_lib" >&2
	exit 2
}
answers_lib="$repo_root/scripts/lib/copier-answers.sh"
[ -f "$answers_lib" ] || {
	echo "error: missing dependency: $answers_lib" >&2
	exit 2
}
# shellcheck source=/dev/null
. "$repo_surface_lib"
# shellcheck source=/dev/null
. "$answers_lib"

old_company_dir="$workspace_root/$company_slug"
old_templates_dir="$old_company_dir/${company_slug}-templates"
stage_dir="$workspace_root/${company_slug}-stage"
tmp_root="$(mktemp -d)"
cleanup() {
	rm -rf "$tmp_root"
}
trap cleanup EXIT INT TERM

say() { printf '%s\n' "$*"; }
die() {
	printf 'error: %s\n' "$*" >&2
	exit 2
}

rewrite_line_matching() {
	local file="$1"
	local pattern="$2"
	local replacement="$3"
	local tmp_file
	tmp_file="$(mktemp)"

	awk -v pattern="$pattern" -v replacement="$replacement" '
    !done && $0 ~ pattern {
      print replacement
      done = 1
      next
    }
    { print }
  ' "$file" >"$tmp_file" || {
		rm -f "$tmp_file"
		die "unable to rewrite $file"
	}

	mv "$tmp_file" "$file"
}

yaml_emit_scalar() {
	local value="$1"
	case "$value" in
	true | false)
		printf '%s' "$value"
		return 0
		;;
	esac

	escaped_value=$(printf '%s' "$value" | sed "s/'/''/g")
	printf "'%s'" "$escaped_value"
}

upsert_yaml_scalar() {
	local file="$1"
	local key="$2"
	local value="$3"
	local rendered_value

	rendered_value="$(yaml_emit_scalar "$value")"
	if grep -q "^$key:" "$file"; then
		rewrite_line_matching "$file" "^$key:.*$" "$key: $rendered_value"
		return 0
	fi

	printf '%s: %s\n' "$key" "$rendered_value" >>"$file"
}

merge_legacy_answers_into_stage() {
	local old_answers="$1"
	local stage_answers="$2"
	local key
	local value
	local status

	for key in maintainer_handle l1_org_docs_profile l2_org_docs_default enable_vouch_gate enable_community_pack enable_release_pack; do
		value=""
		status=0
		value="$(copier_answers_try_scalar "$old_answers" "$key" 2>/dev/null)" || status=$?
		case "$status" in
		0)
			[ -n "$value" ] || continue
			upsert_yaml_scalar "$stage_answers" "$key" "$value"
			;;
		1)
			continue
			;;
		*)
			die "unable to parse '$key' from legacy answers file: $old_answers"
			;;
		esac
	done

	upsert_yaml_scalar "$stage_answers" repo_slug "$company_slug"
}

append_legacy_render_arg_if_present() {
	local answers_file="$1"
	local key="$2"
	local value
	local status

	value=""
	status=0
	value="$(copier_answers_try_scalar "$answers_file" "$key" 2>/dev/null)" || status=$?
	case "$status" in
	0)
		[ -n "$value" ] || return 0
		legacy_render_args+=( -d "$key=$value" )
		;;
	1)
		return 0
		;;
	*)
		die "unable to parse '$key' from legacy answers file: $answers_file"
		;;
	esac
}

ensure_clean_git_repo() {
	local path="$1"
	repo_surface_is_git_repo "$path" || die "not a git repo: $path"
	if [[ -n "$(git -C "$path" status --porcelain)" ]]; then
		die "repo has uncommitted changes: $path"
	fi
}

copy_dir_if_exists() {
	local src="$1"
	local dst="$2"
	if [[ -d "$src" ]]; then
		mkdir -p "$dst"
		rsync -a "$src/" "$dst/"
	fi
}

parse_explicit_custom_lane_names() {
	local raw="${AI_SOCIETY_CUSTOM_LANES:-}"
	local lane_name

	[[ -n "$raw" ]] || return 0

	raw="${raw//,/ }"
	raw="${raw//:/ }"
	for lane_name in $raw; do
		[[ -n "$lane_name" ]] || continue
		repo_surface_lane_name_has_valid_syntax "$lane_name" || die "AI_SOCIETY_CUSTOM_LANES contains invalid lane name: $lane_name"
		repo_surface_lane_name_is_bootstrap_allowed "$lane_name" || die "AI_SOCIETY_CUSTOM_LANES contains reserved L1 control-plane path: $lane_name"
		printf '%s\n' "$lane_name"
	done
}

lane_dir_has_baseline_control_plane() {
	local lane_dir="$1"

	[[ -d "$lane_dir" ]] || return 1
	[[ -f "$lane_dir/.gitignore" ]] || return 1
	[[ -f "$lane_dir/.copier-answers.yml" ]] || return 1
	grep -qF "# Track lane baseline only." "$lane_dir/.gitignore"
}

lane_dir_has_nested_repos() {
	local lane_dir="$1"

	[[ -n "$(repo_surface_find_nested_repo_roots "$lane_dir" || true)" ]]
}

lane_dir_conflicts_with_reserved_control_plane() {
	local lane_dir="$1"
	local lane_name

	lane_name="$(basename "$lane_dir")"
	repo_surface_lane_name_has_valid_syntax "$lane_name" || return 1
	repo_surface_is_reserved_lane_name "$lane_name" || return 1

	lane_dir_has_baseline_control_plane "$lane_dir" && return 0
	lane_dir_has_nested_repos "$lane_dir"
}

lane_dir_should_migrate() {
	local lane_dir="$1"
	shift
	local lane_name

	lane_name="$(basename "$lane_dir")"
	repo_surface_lane_name_has_valid_syntax "$lane_name" || return 1
	repo_surface_is_builtin_lane_name "$lane_name" && return 0
	repo_surface_is_reserved_lane_name "$lane_name" && return 1
	lane_dir_has_baseline_control_plane "$lane_dir" && return 0
	repo_surface_lane_name_is_listed "$lane_name" "$@"
}

lane_dir_requires_explicit_custom_lane() {
	local lane_dir="$1"
	shift
	local lane_name

	lane_name="$(basename "$lane_dir")"
	repo_surface_lane_name_has_valid_syntax "$lane_name" || return 1
	repo_surface_is_builtin_lane_name "$lane_name" && return 1
	repo_surface_is_reserved_lane_name "$lane_name" && return 1
	lane_dir_has_baseline_control_plane "$lane_dir" && return 1
	repo_surface_lane_name_is_listed "$lane_name" "$@" && return 1
	lane_dir_has_nested_repos "$lane_dir"
}

discover_lane_names() {
	local company_dir="$1"
	local templates_dir_name="$2"
	shift 2
	local entry
	local lane_name

	shopt -s dotglob nullglob
	for entry in "$company_dir"/*; do
		[[ -d "$entry" ]] || continue
		lane_name="$(basename "$entry")"
		case "$lane_name" in
		. | .. | .pi | "$templates_dir_name")
			continue
			;;
		esac
		lane_dir_should_migrate "$entry" "$@" || continue
		printf '%s\n' "$lane_name"
	done
	shopt -u dotglob nullglob
}

discover_reserved_lane_conflicts() {
	local company_dir="$1"
	local templates_dir_name="$2"
	local entry
	local lane_name

	shopt -s dotglob nullglob
	for entry in "$company_dir"/*; do
		[[ -d "$entry" ]] || continue
		lane_name="$(basename "$entry")"
		case "$lane_name" in
		. | .. | .pi | "$templates_dir_name")
			continue
			;;
		esac
		lane_dir_conflicts_with_reserved_control_plane "$entry" || continue
		printf '%s\n' "$lane_name"
	done
	shopt -u dotglob nullglob
}

discover_unclassified_custom_lane_dirs() {
	local company_dir="$1"
	local templates_dir_name="$2"
	shift 2
	local entry
	local lane_name

	shopt -s dotglob nullglob
	for entry in "$company_dir"/*; do
		[[ -d "$entry" ]] || continue
		lane_name="$(basename "$entry")"
		case "$lane_name" in
		. | .. | .pi | "$templates_dir_name")
			continue
			;;
		esac
		lane_dir_requires_explicit_custom_lane "$entry" "$@" || continue
		printf '%s\n' "$lane_name"
	done
	shopt -u dotglob nullglob
}

discover_missing_explicit_custom_lanes() {
	local company_dir="$1"
	shift
	local lane_name

	for lane_name in "$@"; do
		[[ -d "$company_dir/$lane_name" ]] || printf '%s\n' "$lane_name"
	done
}

is_discovered_lane_name() {
	local lane_name="$1"
	shift
	local known_lane

	for known_lane in "$@"; do
		[[ "$lane_name" = "$known_lane" ]] && return 0
	done

	return 1
}

clone_git_history_into_stage() {
	local src_repo="$1"
	local dst_repo="$2"
	local history_clone_dir="$tmp_root/history-clone"
	local src_common_dir
	local src_common_config

	rm -rf "$history_clone_dir"
	git clone "$src_repo" "$history_clone_dir" >/dev/null 2>&1 || die "unable to clone git history from $src_repo"

	src_common_dir="$(cd "$src_repo" && common_dir="$(git rev-parse --git-common-dir)" && cd "$common_dir" && pwd)"
	src_common_config="$src_common_dir/config"
	if [[ -f "$src_common_config" ]]; then
		cp "$src_common_config" "$history_clone_dir/.git/config" || die "unable to preserve git config from $src_repo"
	fi

	rm -rf "$dst_repo/.git"
	mv "$history_clone_dir/.git" "$dst_repo/.git" || die "unable to transplant git history into $dst_repo"
	rm -rf "$history_clone_dir"
}

say "=== L1 Structure Migration (staged, non-destructive): $company_slug ==="
say ""

[[ -d "$old_company_dir" ]] || die "company folder not found: $old_company_dir"
[[ -d "$old_templates_dir" ]] || die "old templates dir not found: $old_templates_dir"
ensure_clean_git_repo "$old_templates_dir"

[[ ! -e "$stage_dir" ]] || die "stage dir already exists: $stage_dir (remove it first)"

legacy_answers_file="$old_templates_dir/.copier-answers.yml"
legacy_render_args=()
if [[ -f "$legacy_answers_file" ]]; then
	append_legacy_render_arg_if_present "$legacy_answers_file" maintainer_handle
	append_legacy_render_arg_if_present "$legacy_answers_file" l1_org_docs_profile
	append_legacy_render_arg_if_present "$legacy_answers_file" l2_org_docs_default
	append_legacy_render_arg_if_present "$legacy_answers_file" enable_vouch_gate
	append_legacy_render_arg_if_present "$legacy_answers_file" enable_community_pack
	append_legacy_render_arg_if_present "$legacy_answers_file" enable_release_pack
fi

say "Step 1: Render fresh company-root L1 from L0 into stage"
cd "$repo_root"
./scripts/new-l1-from-copier.sh "$stage_dir" \
	-d repo_slug="$company_slug" \
	-d company_slug="$company_slug" \
	-d company_name="$company_name" \
	"${legacy_render_args[@]}" \
	--defaults --overwrite

say "Step 2: Preserve L1 git history in stage"
clone_git_history_into_stage "$old_templates_dir" "$stage_dir"

say "Step 3: Preserve copier answers provenance"
if [[ -f "$legacy_answers_file" ]]; then
	merge_legacy_answers_into_stage "$legacy_answers_file" "$stage_dir/.copier-answers.yml"
fi

explicit_custom_lane_names_output="$(parse_explicit_custom_lane_names)" || exit $?
if [[ -n "$explicit_custom_lane_names_output" ]]; then
	mapfile -t explicit_custom_lane_names < <(printf '%s\n' "$explicit_custom_lane_names_output" | LC_ALL=C sort -u)
else
	explicit_custom_lane_names=()
fi

if [[ ${#explicit_custom_lane_names[@]} -gt 0 ]]; then
	mapfile -t missing_explicit_custom_lanes < <(discover_missing_explicit_custom_lanes "$old_company_dir" "${explicit_custom_lane_names[@]}" | LC_ALL=C sort -u)
	if [[ ${#missing_explicit_custom_lanes[@]} -gt 0 ]]; then
		die "AI_SOCIETY_CUSTOM_LANES lists non-existent top-level dirs: ${missing_explicit_custom_lanes[*]}"
	fi
fi

mapfile -t reserved_lane_conflicts < <(discover_reserved_lane_conflicts "$old_company_dir" "${company_slug}-templates" | LC_ALL=C sort -u)
if [[ ${#reserved_lane_conflicts[@]} -gt 0 ]]; then
	die "reserved L1 control-plane dirs contain lane-like state and must be repaired manually before migration: ${reserved_lane_conflicts[*]}"
fi

mapfile -t unclassified_custom_lane_names < <(discover_unclassified_custom_lane_dirs "$old_company_dir" "${company_slug}-templates" "${explicit_custom_lane_names[@]}" | LC_ALL=C sort -u)
if [[ ${#unclassified_custom_lane_names[@]} -gt 0 ]]; then
	suggested_custom_lanes="${unclassified_custom_lane_names[0]}"
	for lane in "${unclassified_custom_lane_names[@]:1}"; do
		suggested_custom_lanes="$suggested_custom_lanes,$lane"
	done
	die "top-level dirs with nested repos require explicit lane classification via AI_SOCIETY_CUSTOM_LANES=$suggested_custom_lanes"
fi

mapfile -t lane_names < <(discover_lane_names "$old_company_dir" "${company_slug}-templates" "${explicit_custom_lane_names[@]}" | LC_ALL=C sort -u)

say "Step 4: Copy lane folders (built-in + baseline + explicit custom lanes) into stage"
if [[ ${#lane_names[@]} -eq 0 ]]; then
	say "  - none discovered"
else
	for lane in "${lane_names[@]}"; do
		copy_dir_if_exists "$old_company_dir/$lane" "$stage_dir/$lane"
		count=0
		[[ -d "$stage_dir/$lane" ]] && count="$(find "$stage_dir/$lane" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
		say "  - $lane: $count top-level dirs"
	done
fi

say "Step 5: Bootstrap copied lane roots with baseline control-plane + ignore policy"
if [[ ${#lane_names[@]} -eq 0 ]]; then
	say "  - none discovered"
else
	for lane in "${lane_names[@]}"; do
		if [[ -d "$stage_dir/$lane" ]]; then
			(
				cd "$stage_dir"
				./scripts/bootstrap-lane-root.sh "$lane" >/dev/null
			)
			say "  - $lane: baseline bootstrapped"
		fi
	done
fi

say "Step 6: Copy additional company-root extras (except old templates and discovered lanes)"
shopt -s dotglob nullglob
for entry in "$old_company_dir"/*; do
	base="$(basename "$entry")"
	case "$base" in
	. | .. | .pi | "${company_slug}-templates")
		continue
		;;
	esac
	if is_discovered_lane_name "$base" "${lane_names[@]}"; then
		continue
	fi
	rsync -a "$entry" "$stage_dir/"
done
shopt -u dotglob nullglob

say "Step 7: Enforce no orphan tpl-owned-repo in staged L1"
rm -rf "$stage_dir/copier/tpl-owned-repo"

say "Step 8: Validate staged repo"
if ! (cd "$stage_dir" && bash ./scripts/check-template-ci.sh >/dev/null); then
	die "staged repo failed check-template-ci.sh: $stage_dir"
fi

say ""
say "=== Stage ready ==="
say "Staged repo: $stage_dir"
say ""
say "Review commands:"
say "  cd $stage_dir"
say "  git status"
say "  bash ./scripts/check-template-ci.sh"
say ""
say "note: git status should show the staged company-root migration diff against preserved history until you commit it."
say ""
say "After switch + parent commit, initialize lane-root git repos (optional but recommended):"
if [[ ${#lane_names[@]} -eq 0 ]]; then
	say "  # no lane roots detected"
else
	for lane in "${lane_names[@]}"; do
		say "  ./scripts/bootstrap-lane-root.sh $lane --init-lane-git"
	done
fi
say ""
say "When ready to switch (manual, explicit):"
say "  mv $old_company_dir $workspace_root/${company_slug}-old"
say "  mv $stage_dir $old_company_dir"
say ""
say "Rollback before switch:"
say "  rm -rf $stage_dir"
