#!/bin/bash
set -eu
umask 022
export PYTHONDONTWRITEBYTECODE=1
e=/home/tryinget/.local/state/pi-quests/tmp/ak6351-ci-01a0ffd7-c705-7ed4-87ea-1eb822a5bb16
w=/home/tryinget/.local/state/pi-quests/tmp/ak6351-l0-01a0f678-716c-785f-a310-9a0d2ff48667
core="$TMPDIR/rocs-ci"
git init -q "$core"
git -C "$core" fetch --depth=1 https://github.com/tryingET/rocs-cli.git ac75e95e30d66b3543abca27cb79d69a9dc01e93
git -C "$core" checkout --detach -q FETCH_HEAD
uv sync --project "$core" --frozen
uv run --project "$core" --frozen rocs version
mkdir "$TMPDIR/hosted-bin" "$TMPDIR/hosted-home"
for name in uv uvx; do cp "$(readlink -f "$(command -v "$name")")" "$TMPDIR/hosted-bin/$name"; done
git clone --quiet --no-hardlinks --no-checkout "$w" "$TMPDIR/red-owner"
git -C "$TMPDIR/red-owner" checkout --quiet --detach b09ce28707eaf2164cc7e88dec7970b685b3472c
export ROCS_CORE_PROJECT="$core"
export HOME="$TMPDIR/hosted-home"
export UV_CACHE_DIR="$TMPDIR/hosted-home/.cache/uv"
export PATH="$TMPDIR/hosted-bin:/usr/local/bin:/usr/bin:/bin"
unset AK_CMD AI_SOCIETY_WORKSPACE DOC_REF_CHECK_SCRIPT AGENT_SCRIPTS_DOC_REF_CHECK GITHUB_ACTOR PROJECT_OWNER_HANDLE PI_PROJECT_OWNER_HANDLE
if command -v ak; then exit 2; fi
cd "$w"
export L0_TEMPLATE_ROOT="$PWD"
set +e
uvx --from copier==9.11.1 python -B - "$TMPDIR/red-owner" <<'PY' > "$e/tdd-red-owner.log" 2>&1
import sys,unittest
from pathlib import Path
from tests import test_hosted_ci as scenarios
scenarios.ROOT=Path(sys.argv[1])
suite=unittest.TestSuite([scenarios.HostedCiTests('test_golden_births_bind_owner_instead_of_ambient_git_or_actor')])
result=unittest.TextTestRunner().run(suite)
raise SystemExit(not result.wasSuccessful())
PY
rc=$?
set -e
printf '%s\n' "$rc" > "$e/tdd-red-owner.exit"
test "$rc" -eq 1
grep -q 'project_owner_handle=@tryinget' "$e/tdd-red-owner.log"
grep -q 'FAILED (failures=1)' "$e/tdd-red-owner.log"
cat "$e/tdd-red-owner.log"
TIMEFORMAT='real %R user %U sys %S'
git rev-parse HEAD > "$e/final-subject.txt"
date -u +%FT%TZ > "$e/final-start.txt"
{ time uvx --from copier==9.11.1 python -B -m unittest tests.test_hosted_ci tests.test_ci_red_green \
  tests.test_l1_template_company_ownership.CompanyOntologyTests.test_real_full_ci_binds_fixture_ak_without_ambient_runtime \
  tests.test_l1_template_company_ownership.CompanyOntologyTests.test_old_readers_upgrade_through_a_receipted_preparatory_refresh \
  tests.test_l1_template_company_ownership.CompanyOntologyTests.test_real_forward_and_receipted_reverse_restore_ownership \
  > "$e/final-focused.log" 2>&1; } 2> "$e/final-focused.time"
printf '0\n' > "$e/final-focused.exit"
cat "$e/final-focused.log" "$e/final-focused.time"
{ time bash scripts/check-l0-fixtures.sh > "$e/final-fixtures-focused.log" 2>&1; } 2> "$e/final-fixtures-focused.time"
printf '0\n' > "$e/final-fixtures-focused.exit"
cat "$e/final-fixtures-focused.log" "$e/final-fixtures-focused.time"
test -z "$(find copier-template -name __pycache__ -print)"
{ time bash scripts/check-l0.sh > "$e/final-full.log" 2>&1; } 2> "$e/final-full.time"
printf '0\n' > "$e/final-full.exit"
date -u +%FT%TZ > "$e/final-end.txt"
cat "$e/final-full.log" "$e/final-full.time"
test -z "$(find copier-template -name __pycache__ -print)"
git diff --check
test -z "$(git status --porcelain)"
