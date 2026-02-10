#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$repo_root"

fail() {
  echo "error: $*" >&2
  exit 1
}

[ -f "contracts/layer-contract.yml" ] || fail "missing contracts/layer-contract.yml"
grep -qF "layer: L2" contracts/layer-contract.yml || fail "contract layer must be L2"
grep -qF "L2 -> L1" contracts/layer-contract.yml || fail "contract must forbid L2 -> L1"
grep -qF "L2 -> L0" contracts/layer-contract.yml || fail "contract must forbid L2 -> L0"

echo "ok: ci smoke"
