#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$repo_root"

fail() {
  echo "error: $*" >&2
  exit 1
}

[ -f "contracts/layer-contract.yml" ] || fail "missing contracts/layer-contract.yml"
grep -qF "layer: L1" contracts/layer-contract.yml || fail "contract layer must be L1"
grep -qF "L1 -> L2" contracts/layer-contract.yml || fail "contract must allow L1 -> L2"
grep -qF "L1 -> L0" contracts/layer-contract.yml || fail "contract must forbid L1 -> L0"

[ -f "contracts/provenance-seal.yml" ] || fail "missing contracts/provenance-seal.yml"
grep -qF "schema: ai-society.template-provenance.v1" contracts/provenance-seal.yml || fail "provenance schema mismatch"
grep -qF "layer: L1" contracts/provenance-seal.yml || fail "provenance layer must be L1"
if grep -q "__RENDER_HASH__" contracts/provenance-seal.yml; then
  fail "provenance render hash placeholder must be resolved"
fi

if grep -nE 'copier[[:space:]]+(copy|update)' copier/template-repo/copier.yml >/dev/null 2>&1; then
  fail "nested copier invocations are forbidden in L1 template config"
fi

echo "ok: ci smoke"
