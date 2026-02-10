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
need_cmd mktemp

"$repo_root/scripts/check-l0-guardrails.sh"

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

l1_dir="$tmp_root/l1-template-sample"

render_l1() {
  "$repo_root/scripts/new-l1-from-copier.sh" template-repo "$l1_dir" \
    -d repo_slug=l1-template-sample \
    -d maintainer_handle=@template-owner \
    --defaults --overwrite >/dev/null
}

render_l1

(
  cd "$l1_dir"
  ./scripts/check-template-ci.sh
)

(
  cd "$l1_dir"
  git init -b main >/dev/null
  git config user.name "tpl-template-repo ci" >/dev/null
  git config user.email "ci@tpl-template-repo.local" >/dev/null
  git add .
  git commit -m "initial render" >/dev/null
)

render_l1

(
  cd "$l1_dir"
  if [ -n "$(git status --porcelain)" ]; then
    echo "error: non-idempotent L0 -> L1 generation" >&2
    git status --short >&2
    exit 1
  fi
)

echo "ok: l0 generation smoke + idempotency"
