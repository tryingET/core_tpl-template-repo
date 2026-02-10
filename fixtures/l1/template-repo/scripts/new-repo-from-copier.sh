#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF' >&2
usage: new-repo-from-copier.sh <template-repo> <dest-dir> [copier args...]

Example:
  ./scripts/new-repo-from-copier.sh template-repo /tmp/my-product \
    -d repo_slug=my-product --defaults --overwrite

Notes:
  - Copier is pinned by default via COPIER_VERSION (default: 9.11.1).
  - `enable_vouch_gate` is inherited from this L1 repo `.copier-answers.yml` unless overridden.
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
  echo "error: unknown template profile: $template_name" >&2
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

have_vouch_setting=0
for arg in "$@"; do
  case "$arg" in
    -d)
      have_vouch_setting_next=1
      ;;
    enable_vouch_gate=* )
      if [ "${have_vouch_setting_next:-0}" -eq 1 ]; then
        have_vouch_setting=1
      fi
      have_vouch_setting_next=0
      ;;
    -d*=enable_vouch_gate=*|-d*enable_vouch_gate=* )
      have_vouch_setting=1
      have_vouch_setting_next=0
      ;;
    *)
      have_vouch_setting_next=0
      ;;
  esac
done

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
if [ "$have_vouch_setting" = "0" ] && [ -f "$repo_root/.copier-answers.yml" ]; then
  inherited_vouch="$(awk -F':' '/^enable_vouch_gate:/{v=$2; gsub(/[ \t"]/, "", v); gsub(/\047/, "", v); print tolower(v); exit }' "$repo_root/.copier-answers.yml" || true)"
  case "$inherited_vouch" in
    true|false)
      set -- -d "enable_vouch_gate=$inherited_vouch" "$@"
      ;;
  esac
fi

template_dir="$repo_root/copier/$template_name"

[ -d "$template_dir" ] || {
  echo "error: missing copier template: $template_dir" >&2
  exit 2
}

run_copier copy --trust "$@" "$template_dir" "$dest_dir"
