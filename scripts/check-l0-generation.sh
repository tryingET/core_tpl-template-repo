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

render_l1_case() {
  case_name="$1"
  enable_community_pack="$2"
  enable_release_pack="$3"
  enable_vouch_gate="$4"
  l1_dir="$tmp_root/$case_name"

  "$repo_root/scripts/new-l1-from-copier.sh" template-repo "$l1_dir" \
    -d repo_slug="$case_name" \
    -d maintainer_handle=@template-owner \
    -d enable_community_pack="$enable_community_pack" \
    -d enable_release_pack="$enable_release_pack" \
    -d enable_vouch_gate="$enable_vouch_gate" \
    --defaults --overwrite >/dev/null

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
    git commit -m "initial render ($case_name)" >/dev/null
  )

  "$repo_root/scripts/new-l1-from-copier.sh" template-repo "$l1_dir" \
    -d repo_slug="$case_name" \
    -d maintainer_handle=@template-owner \
    -d enable_community_pack="$enable_community_pack" \
    -d enable_release_pack="$enable_release_pack" \
    -d enable_vouch_gate="$enable_vouch_gate" \
    --defaults --overwrite >/dev/null

  (
    cd "$l1_dir"
    if [ -n "$(git status --porcelain)" ]; then
      echo "error: non-idempotent L0 -> L1 generation ($case_name)" >&2
      git status --short >&2
      exit 1
    fi
  )
}

render_l1_case "l1-template-sample" false false false
render_l1_case "l1-template-community" true false false
render_l1_case "l1-template-release" false true false
render_l1_case "l1-template-vouch" false false true

echo "ok: l0 generation smoke + idempotency"
