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
mkdir "$TMPDIR/hosted-bin" "$TMPDIR/hosted-home" "$TMPDIR/hosted-home/.cache"
for name in uv uvx; do cp "$(readlink -f "$(command -v "$name")")" "$TMPDIR/hosted-bin/$name"; done
for case_name in gates cache; do
  git clone --quiet --no-hardlinks --no-checkout "$w" "$TMPDIR/red-$case_name"
done
git -C "$TMPDIR/red-gates" checkout --quiet --detach dd067dd69445672ee3fad07bfb72b68403fe947d
git -C "$TMPDIR/red-cache" checkout --quiet --detach d6cf555
export ROCS_CORE_PROJECT="$core"
export HOME="$TMPDIR/hosted-home"
export UV_CACHE_DIR="$TMPDIR/hosted-home/.cache/uv"
export PATH="$TMPDIR/hosted-bin:/usr/local/bin:/usr/bin:/bin"
unset AK_CMD AI_SOCIETY_WORKSPACE DOC_REF_CHECK_SCRIPT AGENT_SCRIPTS_DOC_REF_CHECK
if command -v ak; then echo 'private AK leaked into hosted-like PATH' >&2; exit 2; fi
uvx --version
TIMEFORMAT='real %R user %U sys %S'
cd "$TMPDIR/red-gates"
export L0_TEMPLATE_ROOT="$PWD"
set +e
{ time uvx --from copier==9.11.1 python -B -m unittest \
  tests.test_l1_template_company_ownership.CompanyOntologyTests.test_old_readers_upgrade_through_a_receipted_preparatory_refresh \
  tests.test_l1_template_company_ownership.CompanyOntologyTests.test_real_forward_and_receipted_reverse_restore_ownership \
  > "$e/tdd-red-gates.log" 2>&1; } 2> "$e/tdd-red-gates.time"
rc=$?
set -e
printf '%s\n' "$rc" > "$e/tdd-red-gates.exit"
test "$rc" -eq 1
grep -q 'FAILED (failures=2)' "$e/tdd-red-gates.log"
test "$(grep -c 'error: missing ak command: ak' "$e/tdd-red-gates.log")" -eq 2
cat "$e/tdd-red-gates.log" "$e/tdd-red-gates.time"
cd "$TMPDIR/red-cache"
export L0_TEMPLATE_ROOT="$PWD"
set +e
{ time PYTHONPATH="$PWD" uvx --from copier==9.11.1 python -B "$w/tests/test_ci_red_green.py" \
  > "$e/tdd-red-cache.log" 2>&1; } 2> "$e/tdd-red-cache.time"
rc=$?
set -e
printf '%s\n' "$rc" > "$e/tdd-red-cache.exit"
test "$rc" -eq 1
grep -q 'focused gate subprocess contaminated clean template source' "$e/tdd-red-cache.log"
grep -q 'FAILED (failures=1)' "$e/tdd-red-cache.log"
cat "$e/tdd-red-cache.log" "$e/tdd-red-cache.time"
cd "$w"
export L0_TEMPLATE_ROOT="$PWD"
git rev-parse HEAD > "$e/tdd-green-subject.txt"
date -u +%FT%TZ > "$e/tdd-green-start.txt"
{ time uvx --from copier==9.11.1 python -B -m unittest tests.test_hosted_ci tests.test_ci_red_green \
  tests.test_l1_template_company_ownership.CompanyOntologyTests.test_real_full_ci_binds_fixture_ak_without_ambient_runtime \
  tests.test_l1_template_company_ownership.CompanyOntologyTests.test_old_readers_upgrade_through_a_receipted_preparatory_refresh \
  tests.test_l1_template_company_ownership.CompanyOntologyTests.test_real_forward_and_receipted_reverse_restore_ownership \
  > "$e/tdd-green-focused.log" 2>&1; } 2> "$e/tdd-green-focused.time"
printf '0\n' > "$e/tdd-green-focused.exit"
cat "$e/tdd-green-focused.log" "$e/tdd-green-focused.time"
test -z "$(find copier-template -name __pycache__ -print)"
{ time bash scripts/check-l0.sh > "$e/tdd-green-full.log" 2>&1; } 2> "$e/tdd-green-full.time"
printf '0\n' > "$e/tdd-green-full.exit"
date -u +%FT%TZ > "$e/tdd-green-end.txt"
cat "$e/tdd-green-full.log" "$e/tdd-green-full.time"
test -z "$(find copier-template -name __pycache__ -print)"
git diff --check
test -z "$(git status --porcelain)"
