#!/usr/bin/env sh

# Shared helpers for reasoning about git repos, worktrees, and lane-root
# control-plane surfaces. Intended to be sourced by other shell scripts.

repo_surface_is_git_repo() {
  repo_path="$1"
  git -C "$repo_path" rev-parse --git-dir >/dev/null 2>&1
}

repo_surface_find_repo_roots() {
  scope="$1"
  [ -d "$scope" ] || return 1

  find "$scope" \( -type d -o -type f \) -name .git -print | while IFS= read -r git_marker; do
    [ -n "$git_marker" ] || continue
    repo_path="${git_marker%/.git}"
    repo_surface_is_git_repo "$repo_path" || continue
    printf '%s\n' "$repo_path"
  done | LC_ALL=C sort -u
}

repo_surface_find_nested_repo_roots() {
  scope="$1"
  [ -d "$scope" ] || return 1

  find "$scope" -mindepth 2 \( -type d -o -type f \) -name .git -print | while IFS= read -r git_marker; do
    [ -n "$git_marker" ] || continue
    repo_path="${git_marker%/.git}"
    repo_surface_is_git_repo "$repo_path" || continue
    printf '%s\n' "$repo_path"
  done | LC_ALL=C sort -u
}

repo_surface_lane_root_src_path() {
  printf '../copier/tpl-project-repo\n'
}

repo_surface_is_tpl_project_src_path() {
  case "$1" in
    ../copier/tpl-project-repo|./copier/tpl-project-repo|copier/tpl-project-repo|*/copier/tpl-project-repo|__VOLATILE_SRC_PATH__)
      return 0
      ;;
  esac

  return 1
}
