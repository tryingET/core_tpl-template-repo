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
  - `enable_vouch_gate`, `enable_community_pack`, and `enable_release_pack`
    are inherited from this L1 repo `.copier-answers.yml` unless overridden.
  - `repo_archetype` defaults to `project` and can be overridden with:
    `-d repo_archetype=project|agent|org|owned`.
  - `org_docs_profile` defaults to this L1 policy (`l2_org_docs_default`) and
    can be overridden with `-d org_docs_profile=compact|rich`.
  - Optional canonical org source can be passed via:
    `-d org_docs_canonical_ref=<url-or-path>`.
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

has_data_override() {
  key="$1"
  shift

  expect_data_value=0
  for arg in "$@"; do
    if [ "$expect_data_value" = "1" ]; then
      case "$arg" in
        "$key="*) return 0 ;;
      esac
      expect_data_value=0
      continue
    fi

    case "$arg" in
      -d|--data)
        expect_data_value=1
        ;;
      -d"$key="*|--data="$key="*)
        return 0
        ;;
    esac
  done

  return 1
}

read_inherited_value() {
  answers_file="$1"
  key="$2"

  [ -f "$answers_file" ] || return 1

  awk -F':' -v key="$key" '
    $1 ~ "^" key "$" {
      v=$2
      gsub(/[ \t"]/, "", v)
      gsub(/\047/, "", v)
      print tolower(v)
      exit
    }
  ' "$answers_file"
}

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
answers_file="$repo_root/.copier-answers.yml"

for key in enable_vouch_gate enable_community_pack enable_release_pack; do
  if has_data_override "$key" "$@"; then
    continue
  fi

  inherited_value="$(read_inherited_value "$answers_file" "$key" || true)"
  case "$inherited_value" in
    true|false)
      set -- -d "$key=$inherited_value" "$@"
      ;;
  esac
done

if ! has_data_override org_docs_profile "$@"; then
  inherited_org_profile="$(read_inherited_value "$answers_file" l2_org_docs_default || true)"
  case "$inherited_org_profile" in
    compact|rich)
      set -- -d "org_docs_profile=$inherited_org_profile" "$@"
      ;;
  esac
fi

template_dir="$repo_root/copier/$template_name"

[ -d "$template_dir" ] || {
  echo "error: missing copier template: $template_dir" >&2
  exit 2
}

run_copier copy --trust "$@" "$template_dir" "$dest_dir"
