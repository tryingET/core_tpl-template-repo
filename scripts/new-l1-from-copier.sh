#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF' >&2
usage: new-l1-from-copier.sh <template-repo> <dest-dir> [copier args...]

Example:
  ./scripts/new-l1-from-copier.sh template-repo /tmp/holdingco-templates \
    -d repo_slug=holdingco-templates \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite

Notes:
  - Copier is pinned by default via COPIER_VERSION (default: 9.11.1).
  - Set `-d enable_community_pack=true` for public/community-facing collaboration intake.
  - Set `-d enable_release_pack=true` for release-please/publish automation baseline.
  - Set `-d enable_vouch_gate=true` for trust-gated/public contribution templates.
EOF
}

COPIER_VERSION="${COPIER_VERSION:-9.11.1}"

run_copier() {
  if command -v uvx >/dev/null 2>&1; then
    uvx --from "copier==${COPIER_VERSION}" copier "$@"
    return
  fi
  if command -v copier >/dev/null 2>&1; then
    copier "$@"
    return
  fi
  if command -v uv >/dev/null 2>&1; then
    uv tool run --from "copier==${COPIER_VERSION}" copier "$@"
    return
  fi
  echo "error: missing dependency: copier (or uvx/uv)" >&2
  exit 2
}

template_name="${1:-}"
dest_dir="${2:-}"
shift 2 2>/dev/null || true

if [ -z "$template_name" ] || [ -z "$dest_dir" ]; then
  usage
  exit 2
fi

if [ "$template_name" != "template-repo" ]; then
  echo "error: unsupported L1 profile: $template_name" >&2
  echo "hint: only 'template-repo' is available in the first slice" >&2
  exit 2
fi

have_answers=0
for arg in "$@"; do
  case "$arg" in
    -a|--answers-file|--answers-file=*) have_answers=1; break ;;
  esac
done

if [ "$have_answers" = "0" ]; then
  set -- -a .copier-answers.yml "$@"
fi

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
run_copier copy --trust -d l1_profile="$template_name" "$@" "$repo_root" "$dest_dir"
