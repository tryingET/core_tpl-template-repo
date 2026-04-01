#!/usr/bin/env bash
# migrate-l1-structure.sh - Stage migration from old <company>-templates layout to company-root L1 layout.
#
# Usage:
#   ./scripts/migrate-l1-structure.sh <company_slug> [company_name]
#
# Example:
#   ./scripts/migrate-l1-structure.sh softwareco "Software Company"
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
	echo "  example: ./scripts/migrate-l1-structure.sh softwareco 'Software Company'" >&2
	exit 2
fi

workspace_root="${AI_SOCIETY_WORKSPACE:-$HOME/ai-society}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_surface_lib="$repo_root/scripts/lib/repo-surface.sh"
[ -f "$repo_surface_lib" ] || {
	echo "error: missing dependency: $repo_surface_lib" >&2
	exit 2
}
# shellcheck source=/dev/null
. "$repo_surface_lib"

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

clone_git_history_into_stage() {
	local src_repo="$1"
	local dst_repo="$2"
	local history_clone_dir="$tmp_root/history-clone"
	local src_common_dir
	local src_common_config

	rm -rf "$history_clone_dir"
	git clone --no-checkout "$src_repo" "$history_clone_dir" >/dev/null 2>&1 || die "unable to clone git history from $src_repo"

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

say "Step 1: Render fresh company-root L1 from L0 into stage"
cd "$repo_root"
./scripts/new-l1-from-copier.sh "$stage_dir" \
	-d repo_slug="$company_slug" \
	-d company_slug="$company_slug" \
	-d company_name="$company_name" \
	--defaults --overwrite

say "Step 2: Preserve L1 git history in stage"
clone_git_history_into_stage "$old_templates_dir" "$stage_dir"

say "Step 3: Preserve copier answers provenance"
if [[ -f "$old_templates_dir/.copier-answers.yml" ]]; then
	cp "$old_templates_dir/.copier-answers.yml" "$stage_dir/.copier-answers.yml"
	# normalize repo_slug to company-root naming
	if grep -q "^repo_slug:" "$stage_dir/.copier-answers.yml"; then
		rewrite_line_matching "$stage_dir/.copier-answers.yml" '^repo_slug:.*$' "repo_slug: '$company_slug'"
	fi
fi

say "Step 4: Copy lane folders (owned/contrib/infra/agents) into stage"
for lane in owned contrib infra agents; do
	copy_dir_if_exists "$old_company_dir/$lane" "$stage_dir/$lane"
	count=0
	[[ -d "$stage_dir/$lane" ]] && count="$(find "$stage_dir/$lane" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
	say "  - $lane: $count top-level dirs"
done

say "Step 5: Bootstrap copied lane roots with baseline control-plane + ignore policy"
for lane in owned contrib infra agents; do
	if [[ -d "$stage_dir/$lane" ]]; then
		(
			cd "$stage_dir"
			./scripts/bootstrap-lane-root.sh "$lane" >/dev/null
		)
		say "  - $lane: baseline bootstrapped"
	fi
done

say "Step 6: Copy additional company-root extras (except old templates and lanes)"
shopt -s dotglob nullglob
for entry in "$old_company_dir"/*; do
	base="$(basename "$entry")"
	case "$base" in
	. | .. | .pi | "${company_slug}-templates" | owned | contrib | infra | agents)
		continue
		;;
	esac
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
say "After switch + parent commit, initialize lane-root git repos (optional but recommended):"
say "  ./scripts/bootstrap-lane-root.sh owned --init-lane-git"
say "  ./scripts/bootstrap-lane-root.sh contrib --init-lane-git"
say "  ./scripts/bootstrap-lane-root.sh infra --init-lane-git"
say "  ./scripts/bootstrap-lane-root.sh agents --init-lane-git"
say ""
say "When ready to switch (manual, explicit):"
say "  mv $old_company_dir $workspace_root/${company_slug}-old"
say "  mv $stage_dir $old_company_dir"
say ""
say "Rollback before switch:"
say "  rm -rf $stage_dir"
