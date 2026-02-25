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

need_cmd cp
need_cmd git
need_cmd grep
need_cmd mktemp

"$repo_root/scripts/check-l0-guardrails.sh"

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

render_l1_case() {
  case_name="$1"
  enable_community_pack="$2"
  enable_release_pack="$3"
  enable_vouch_gate="$4"
  l1_org_docs_profile="$5"
  l1_dir="$tmp_root/$case_name"

  "$repo_root/scripts/new-l1-from-copier.sh" "$l1_dir" \
    -d repo_slug="$case_name" \
    -d maintainer_handle=@template-owner \
    -d l1_org_docs_profile="$l1_org_docs_profile" \
    -d enable_community_pack="$enable_community_pack" \
    -d enable_release_pack="$enable_release_pack" \
    -d enable_vouch_gate="$enable_vouch_gate" \
    --defaults --overwrite >/dev/null

  (
    cd "$l1_dir"
    git init -b main >/dev/null
    git config user.name "tpl-template-repo ci" >/dev/null
    git config user.email "ci@tpl-template-repo.local" >/dev/null
    ./scripts/install-hooks.sh >/dev/null
    ./scripts/ci/smoke.sh >/dev/null
    ./scripts/check-template-ci.sh
    git add .
    git commit -m "initial render ($case_name)" >/dev/null
  )

  "$repo_root/scripts/new-l1-from-copier.sh" "$l1_dir" \
    -d repo_slug="$case_name" \
    -d maintainer_handle=@template-owner \
    -d l1_org_docs_profile="$l1_org_docs_profile" \
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

  if [ "$case_name" = "l1-template-sample" ]; then
    preview_target="$tmp_root/l1-preview-target"
    "$repo_root/scripts/new-l1-from-copier.sh" "$preview_target" \
      -d repo_slug="$case_name" \
      --defaults --overwrite >/dev/null

    alias_target="$tmp_root/l1-preview-alias"
    rm -rf "$alias_target"
    cp -R "$preview_target" "$alias_target"

    preview_output="$("$repo_root/scripts/preview-l1-diff.sh" "$alias_target")"
    printf '%s\n' "$preview_output" | grep -qF "ok: no diff between rendered L1 and target" || {
      echo "error: preview-l1-diff did not produce clean no-diff output for sample alias target" >&2
      printf '%s\n' "$preview_output" >&2
      exit 1
    }
  fi
}

render_l1_case "l1-template-sample" false false false rich
render_l1_case "l1-template-community" true false false rich
render_l1_case "l1-template-release" false true false rich
render_l1_case "l1-template-vouch" false false true rich
render_l1_case "l1-template-compact-org" false false false compact

echo "ok: l0 generation smoke + idempotency"
