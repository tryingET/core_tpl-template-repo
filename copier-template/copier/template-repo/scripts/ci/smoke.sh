#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$repo_root"

fail() {
  echo "error: $*" >&2
  exit 1
}

[ -f "contracts/layer-contract.yml" ] || fail "missing contracts/layer-contract.yml"
[ -f ".copier-answers.yml" ] || fail "missing .copier-answers.yml"

grep -qF "layer: L2" contracts/layer-contract.yml || fail "contract layer must be L2"
grep -qF "L2 -> L1" contracts/layer-contract.yml || fail "contract must forbid L2 -> L1"
grep -qF "L2 -> L0" contracts/layer-contract.yml || fail "contract must forbid L2 -> L0"

repo_archetype="$(awk -F':' '$1 ~ /^repo_archetype$/ { v=$2; gsub(/^[ \t]+|[ \t]+$/, "", v); gsub(/"/, "", v); gsub(/\047/, "", v); print tolower(v); exit }' .copier-answers.yml)"
[ -n "$repo_archetype" ] || repo_archetype="project"

grep -qF "archetype: $repo_archetype" contracts/layer-contract.yml || fail "contract archetype mismatch"

case "$repo_archetype" in
  project|owned)
    grep -qF "governance_model: org-baseline-plus-project-overlay" contracts/layer-contract.yml || fail "contract must declare project/owned governance layering model"
    [ -f "docs/project/governance_overlay.md" ] || fail "missing project governance overlay doc"
    grep -qF "Approved deviations register" docs/project/governance_overlay.md || fail "project governance overlay must include deviation register"
    ;;
  org)
    grep -qF "governance_model: org-governance-primary" contracts/layer-contract.yml || fail "contract must declare org governance model"
    [ -f "docs/org/operating_model.md" ] || fail "missing docs/org/operating_model.md for org archetype"
    [ -f "governance/consent.md" ] || fail "missing governance/consent.md for org archetype"
    ;;
  agent)
    grep -qF "governance_model: agent-local-governance" contracts/layer-contract.yml || fail "contract must declare agent governance model"
    [ -f "docs/person/.gitkeep" ] || fail "missing docs/person/.gitkeep for agent archetype"
    [ -f "prompts/activities/.gitkeep" ] || fail "missing prompts/activities/.gitkeep for agent archetype"
    ;;
  *)
    fail "unsupported repo_archetype in answers file: $repo_archetype"
    ;;
esac

echo "ok: ci smoke"
