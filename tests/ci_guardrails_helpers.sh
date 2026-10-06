fail() {
	echo "error: $*" >&2
	exit 1
}

assert_file() {
	path="$1"
	[ -f "$path" ] || fail "missing required file: $path"
}

assert_exec() {
	path="$1"
	[ -x "$path" ] || fail "expected executable file: $path"
}

assert_dir() {
	path="$1"
	[ -d "$path" ] || fail "missing required directory: $path"
}

assert_absent() {
	path="$1"
	[ ! -e "$path" ] || fail "legacy path must be absent: $path"
}

assert_contains() {
	path="$1"
	needle="$2"
	label="$3"
	grep -qF -- "$needle" "$path" || fail "$label (missing '$needle' in $path)"
}

assert_not_contains() {
	path="$1"
	needle="$2"
	label="$3"
	if grep -qF -- "$needle" "$path"; then
		fail "$label (found '$needle' in $path)"
	fi
}


assert_yaml_default() {
	path="$1"
	section="$2"
	expected="$3"
	label="$4"
	actual="$(awk -v section="$section:" '''
		$0 == section { inside = 1; next }
		inside && /^[^[:space:]]/ { exit }
		inside && $1 == "default:" {
			sub(/^[[:space:]]*default:[[:space:]]*/, "")
			gsub(/^"|"$/, "")
			print
			exit
		}
	''' "$path")"
	[ "$actual" = "$expected" ] || fail "$label (found ${actual:-<missing>} in $path)"
}

assert_files_equal() {
	left="$1"
	right="$2"
	label="$3"

	set +e
	git diff --no-index --quiet -- "$left" "$right"
	status=$?
	set -e

	if [ "$status" -eq 0 ]; then
		return
	fi
	if [ "$status" -eq 1 ]; then
		echo "error: $label" >&2
		git --no-pager diff --no-index -- "$left" "$right" >&2 || true
		exit 1
	fi

	fail "$label (diff command failed)"
}

checkout_full_history_ok() {
	python3 -I -S -B - "$1" <<'PY'
import re
import sys
from pathlib import Path

lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
if any("\t" in line for line in lines):
    raise SystemExit(1)
job_re = re.compile(r"  [A-Za-z0-9_-]+:\Z")
name_re = re.compile(r"      - name: .+\Z")
uses_re = re.compile(r"        uses: ([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([A-Za-z0-9_.-]+)\Z")
run_re = re.compile(r"        run: [^|>].*\Z")
option_re = re.compile(r"          ([A-Za-z0-9_-]+): (.+)\Z")

jobs = steps = checkouts = 0
in_jobs = in_steps = False
current = None

def finish_step() -> None:
    global current, checkouts
    if current is None:
        return
    if current["driver"] not in {"uses", "run"}:
        raise ValueError("step lacks one exact driver")
    action = current.get("action") or ""
    if action.lower().startswith("actions/checkout@"):
        if action != "actions/checkout@v4":
            raise ValueError("checkout must use the approved v4 ref")
        if current["options"].get("fetch-depth") != "0":
            raise ValueError("checkout lacks exact fetch-depth zero")
        checkouts += 1
    current = None

try:
    for line in lines:
        indent = len(line) - len(line.lstrip(" "))
        if line == "jobs:":
            if in_jobs:
                raise ValueError("duplicate jobs mapping")
            in_jobs = True
            continue
        if not in_jobs:
            continue
        if line and indent == 0:
            finish_step()
            in_jobs = in_steps = False
            continue
        if line and indent == 2:
            finish_step()
            if not job_re.fullmatch(line):
                raise ValueError("unsupported job key syntax")
            jobs += 1
            in_steps = False
            continue
        if line == "    steps:":
            finish_step()
            steps += 1
            in_steps = True
            continue
        if not in_steps or not line:
            continue
        if name_re.fullmatch(line):
            finish_step()
            current = {"driver": None, "action": None, "options": {}, "with": False}
            continue
        if current is None:
            raise ValueError("unsupported steps syntax")
        match = uses_re.fullmatch(line)
        if match:
            if current["driver"] is not None:
                raise ValueError("duplicate step driver")
            current.update({"driver": "uses", "action": f"{match.group(1)}@{match.group(2)}", "with": False})
            continue
        if run_re.fullmatch(line):
            if current["driver"] is not None:
                raise ValueError("duplicate step driver")
            current.update({"driver": "run", "with": False})
            continue
        if line == "        with:":
            if current["driver"] != "uses" or current["with"]:
                raise ValueError("misplaced with mapping")
            current["with"] = True
            continue
        match = option_re.fullmatch(line)
        if match and current["with"]:
            key, value = match.groups()
            if key in current["options"]:
                raise ValueError("duplicate action option")
            current["options"][key] = value
            continue
        raise ValueError("unsupported step property or scalar encoding")
    finish_step()
except (OSError, UnicodeError, ValueError):
    raise SystemExit(1)
if jobs == 0 or steps != jobs or checkouts == 0:
    raise SystemExit(1)
PY
}

assert_checkout_full_history() {
	checkout_full_history_ok "$1" || fail "workflow must use strict steps syntax and full-history checkout: $1"
}

self_test_checkout_full_history() {
	test_root="$(mktemp -d "${TMPDIR:-$repo_root}/l0-checkout-history.XXXXXX")"
	cat >"$test_root/valid.yml" <<'EOF'
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
EOF
	cat >"$test_root/scalar-bypass.yml" <<'EOF'
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Forged checkout text
        run: |
          uses: actions/checkout@v4
          with:
            fetch-depth: 0
      - name: Actual shallow checkout
        uses: actions/checkout@v4 # actual shallow checkout
EOF
	cat >"$test_root/escaped-bypass.yml" <<'EOF'
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Escaped shallow checkout
        uses: "actions/checkout@v\u0034"
EOF
	cat >"$test_root/old-ref-bypass.yml" <<'EOF'
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Old shallow checkout
        uses: actions/checkout@v3
EOF
	cat >"$test_root/case-bypass.yml" <<'EOF'
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Case-variant shallow checkout
        uses: Actions/Checkout@v4
EOF
	checkout_full_history_ok "$test_root/valid.yml" || fail "full-history workflow matcher rejected a valid checkout"
	if checkout_full_history_ok "$test_root/scalar-bypass.yml"; then
		rm -rf "$test_root"
		fail "full-history workflow matcher accepted a block-scalar checkout forgery"
	fi
	if checkout_full_history_ok "$test_root/escaped-bypass.yml"; then
		rm -rf "$test_root"
		fail "full-history workflow matcher accepted an escaped checkout action"
	fi
	if checkout_full_history_ok "$test_root/old-ref-bypass.yml"; then
		rm -rf "$test_root"
		fail "full-history workflow matcher accepted a non-v4 checkout action"
	fi
	if checkout_full_history_ok "$test_root/case-bypass.yml"; then
		rm -rf "$test_root"
		fail "full-history workflow matcher accepted a case-variant checkout action"
	fi
	rm -rf "$test_root"
}

# end of preserved guardrail source range
