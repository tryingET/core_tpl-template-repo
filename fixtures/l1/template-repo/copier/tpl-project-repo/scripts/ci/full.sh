#!/bin/sh
set -eu

script_dir="$(cd "$(dirname "$0")" && pwd)"

"$script_dir/smoke.sh"

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "error: not a git repo" >&2; exit 1; }
cd "$repo_root"

if [ -d "./tools/rocs-cli" ]; then
  command -v uvx >/dev/null 2>&1 || { echo "error: missing dependency: uvx" >&2; exit 1; }
  uvx -n --from ./tools/rocs-cli rocs version
  uvx -n --from ./tools/rocs-cli rocs build --repo . --resolve-refs --clean
  uvx -n --from ./tools/rocs-cli rocs validate --repo . --resolve-refs
fi
