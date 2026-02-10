#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "error: missing dependency: $1" >&2
    exit 2
  }
}

need_cmd git

chmod +x \
  "$repo_root/scripts/new-repo-from-copier.sh" \
  "$repo_root/scripts/check-template-ci.sh" \
  "$repo_root/scripts/install-hooks.sh" \
  "$repo_root/scripts/ci/smoke.sh" \
  "$repo_root/scripts/ci/full.sh" \
  "$repo_root/.githooks/pre-commit" \
  "$repo_root/.githooks/pre-push" \
  "$repo_root/copier/template-repo/scripts/install-hooks.sh" \
  "$repo_root/copier/template-repo/scripts/ci/smoke.sh" \
  "$repo_root/copier/template-repo/scripts/ci/full.sh" \
  "$repo_root/copier/template-repo/.githooks/pre-commit" \
  "$repo_root/copier/template-repo/.githooks/pre-push"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git config core.hooksPath .githooks
  echo "Configured git hooks path: .githooks"
else
  echo "warning: not inside a git repository; hook path not configured" >&2
fi
