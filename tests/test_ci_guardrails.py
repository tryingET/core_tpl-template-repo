"""Fast mechanical seam contracts; synthetic failures are not owner-check proof.

The Git object, not the map, supplies expected bytes. Runtime witnesses execute
real extracted shell commands in external scratch, never product unittest cohorts.
Only dispatch witnesses substitute an external command (and force it to fail).
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = "scripts/check-l0-guardrails.sh"
PRIVATE = "tests/ci_guardrails_static.sh"
MAP = "tests/ci_guardrails_source_map.json"
COMMIT = "1b92011ad09a25eb2510468be5c9d0244dbf84b1"
DIGEST = "8869dcb682ed6d6d5d6741820141b945a63f76bb5bf2cbad07f90115fca52bce"
PARTS = (
    ("helpers", 5, 259),
    ("context", 260, 301),
    ("root", 302, 504),
    ("l2", 508, 584),
    ("tail", 586, 951),
)
COHORT_LINES = (505, 506, 507, 585)
SOURCE_TERMINATOR = b"# end of preserved guardrail source range\n"
TERMINATED_PARTS = ("helpers", "context")
# Only these two literal additions; original cohort bytes remain pinned.
STATIC_COHORT = (
    b'sh "$repo_root/tests/ci_unittest.sh" guardrails-ci-static pinned-9.11.1 '
    b'tests.test_ci_guardrails >/dev/null || fail "static guardrail seam contracts failed"\n'
)
CANDIDATE_COHORT = (
    b'sh "$repo_root/tests/ci_unittest.sh" guardrails-ci-candidate pinned-9.11.1 '
    b'tests.test_ci_worker tests.test_ci_aggregate tests.test_ci_candidate_workflow '
    b'>/dev/null || fail "candidate execution contracts failed"\n'
)
ADDED_COHORTS = (STATIC_COHORT, CANDIDATE_COHORT)
DEFINITIONS = (
    "fail", "assert_file", "assert_exec", "assert_dir", "assert_absent",
    "assert_contains", "assert_not_contains", "assert_yaml_default",
    "assert_files_equal", "checkout_full_history_ok",
    "assert_checkout_full_history", "self_test_checkout_full_history",
    "check_multi_pass_suffix_policy", "list_template_files",
)


def lib(name):
    return f"tests/ci_guardrails_{name}.sh"


def source(name):
    return f'. "$repo_root/{lib(name)}"\n'.encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def shell_definitions(data):
    """Inspect the closed dialect, excluding complete standalone heredoc bodies.

    This is not a general shell parser or a reachability heuristic. Integrity is
    separately checked byte-for-byte; no executable bytes are admitted by parsing.
    In particular Python source inside <<'PY' must not become shell definitions.
    """
    result = []
    delimiter = None
    for number, line in enumerate(data.splitlines(keepends=True), 1):
        text = line.decode("utf-8").rstrip("\n")
        if delimiter is not None:
            if text == delimiter:
                delimiter = None
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\(\) \{", text)
        if match:
            result.append((match[1], number))
        heredoc = re.search(r"<<(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1$", text)
        if heredoc:
            delimiter = heredoc[2]
    if delimiter is not None:
        raise ValueError("unterminated standalone heredoc")
    return result


def expected_entries(lines):
    entries = [(1, 4, PUBLIC, 1, 4)]
    entries.extend((a, b, lib(n), 1, b - a + 1) for n, a, b in PARTS)
    entries.extend(((505, 507, PUBLIC, 8, 10), (585, 585, PUBLIC, 14, 14)))
    return [
        {"original": [a, b], "path": p, "destination": [c, d],
         "sha256": sha(b"".join(lines[a - 1:b]))}
        for a, b, p, c, d in sorted(entries)
    ]


def expected_wrappers(lines):
    public = (b"".join(lines[:4]) + source("helpers") + source("context")
              + source("root") + b"".join(lines[504:507]) + b"".join(ADDED_COHORTS)
              + source("l2") + lines[584] + source("tail"))
    private = (
        b"".join(lines[:2])
        + b'if [ "$#" -ne 0 ]; then\n'
        + b'\tprintf \'%s\\n\' "error: ci_guardrails_static.sh accepts no arguments" >&2\n'
        + b'\texit 2\nfi\n' + b"".join(lines[2:4])
        + b'export PYTHONDONTWRITEBYTECODE=1\n'
        + b"".join(source(n) for n, _, _ in PARTS)
    )
    return public, private


def validate(original, files, mapping):
    """Closed-byte contract: exact map, complete libraries, exact entrypoints."""
    lines = original.splitlines(keepends=True)
    if len(lines) != 951 or sha(original) != DIGEST:
        raise ValueError("unexpected source object")
    expected_map = {
        "version": 1, "commit": COMMIT, "source": PUBLIC,
        "source_lines": 951, "source_sha256": DIGEST,
        "segments": expected_entries(lines),
        "assertion_call_lines": [
            i for i, line in enumerate(lines, 1)
            if re.match(rb"^\s*assert_[A-Za-z0-9_]+[ \t]", line)
        ],
        "cohort_call_lines": list(COHORT_LINES),
        "additions": [{"path": PUBLIC, "destination": [number, number],
                       "sha256": sha(command), "command": command.decode().rstrip("\n")}
                      for number, command in zip((11, 12), ADDED_COHORTS)],
    }
    if mapping != expected_map:
        raise ValueError("noncanonical source map")
    expected_paths = {PUBLIC, PRIVATE} | {lib(n) for n, _, _ in PARTS}
    if set(files) != expected_paths:
        raise ValueError("nonclosed library set")
    definitions = []
    for name, a, b in PARTS:
        body = files[lib(name)]
        definitions.extend(n for n, _ in shell_definitions(body))
        expected_body = b"".join(lines[a - 1:b])
        if name in TERMINATED_PARTS:
            expected_body += SOURCE_TERMINATOR
        if body != expected_body:
            raise ValueError("unmapped, missing or changed library bytes")
        if len(body.splitlines()) >= 500 or len(body) > 50_000:
            raise ValueError("library budget exceeded")
    if tuple(definitions) != DEFINITIONS or len(set(definitions)) != len(definitions):
        raise ValueError("duplicate, missing or shadowed shell definition")
    public, private = expected_wrappers(lines)
    if files[PUBLIC] != public or files[PRIVATE] != private:
        raise ValueError("unmapped executable bytes or changed schedule")
    reconstructed = []
    coverage = []
    for entry in mapping["segments"]:
        a, b = entry["original"]
        c, d = entry["destination"]
        body = b"".join(files[entry["path"]].splitlines(keepends=True)[c - 1:d])
        if sha(body) != entry["sha256"]:
            raise ValueError("mapped range hash mismatch")
        reconstructed.append(body)
        coverage.extend(range(a, b + 1))
    if coverage != list(range(1, 952)) or b"".join(reconstructed) != original:
        raise ValueError("inexact line coverage/reconstruction")
    if len(public.splitlines()) > 951:
        raise ValueError("public budget exceeded")


class GuardrailsSeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Read-only object probes; never a Git mutation or a synthetic authority.
        # COMMIT was the actual held HEAD at extraction. Keep reading that object
        # after integration commits rather than comparing against a mutable file.
        resolved = subprocess.check_output(
            ["git", "rev-parse", f"{COMMIT}^{{commit}}"], cwd=ROOT,
        ).decode().strip()
        if resolved != COMMIT:
            raise AssertionError(f"expected source object {COMMIT}, found {resolved}")
        cls.original = subprocess.check_output(["git", "show", f"{COMMIT}:{PUBLIC}"], cwd=ROOT)
        cls.lines = cls.original.splitlines(keepends=True)
        cls.files = {p: (ROOT / p).read_bytes()
                     for p in (PUBLIC, PRIVATE, *(lib(n) for n, _, _ in PARTS))}
        cls.mapping = json.loads((ROOT / MAP).read_bytes())

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ci-guardrails-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.tmp = self.base / "tmp"
        self.tmp.mkdir()
        self.elsewhere = self.base / "elsewhere"
        self.elsewhere.mkdir()
        for path, body in self.files.items():
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
        self.env = dict(os.environ, TMPDIR=str(self.tmp))
        self.env.pop("PYTHONPATH", None)
        self.before = self.tree(self.repo)
        self.addCleanup(self.assert_source_unchanged)

    @staticmethod
    def tree(root):
        return {str(p.relative_to(root)): sha(p.read_bytes())
                for p in root.rglob("*") if p.is_file()}

    def assert_source_unchanged(self):
        self.assertEqual(self.before, self.tree(self.repo), "synthetic wrote source files")

    def run_shell(self, body, trace=False):
        flags = ["-e", "-u"] + (["-x"] if trace else [])
        return subprocess.run(
            ["sh", *flags, "-c", body], cwd=self.elsewhere, env=self.env,
            capture_output=True, text=True, timeout=10,
        )

    def helpers(self, body, trace=False):
        return self.run_shell(
            f'repo_root="{self.repo}"\ncd "$repo_root"\n'
            + source("helpers").decode() + body, trace=trace,
        )

    def install_command(self, name, body):
        directory = self.base / "bin"
        directory.mkdir(exist_ok=True)
        path = directory / name
        path.write_text("#!/bin/sh\n" + body)
        path.chmod(0o700)
        self.env["PATH"] = str(directory) + os.pathsep + os.environ["PATH"]
        return path

    def test_exact_head_reconstruction_and_limits(self):
        validate(self.original, self.files, self.mapping)
        self.assertEqual(8, len(self.mapping["segments"]))
        self.assertEqual(364, len(self.mapping["assertion_call_lines"]))
        self.assertEqual(14, len(DEFINITIONS))
        self.assertEqual(15, len(self.files[PUBLIC].splitlines()))
        self.assertEqual(2, len(self.mapping["additions"]))
        self.assertEqual(list(ADDED_COHORTS), self.files[PUBLIC].splitlines(keepends=True)[10:12])
        self.assertLess((ROOT / MAP).stat().st_size, 80_000)
        self.assertLess(Path(__file__).stat().st_size, 80_000)
        self.assertLess(len(Path(__file__).read_bytes().splitlines()), 1000)

    def test_map_refuses_gaps_duplicates_reordering_and_forged_hashes(self):
        mutations = []
        for key, value in (("commit", "0" * 40), ("source_sha256", "0" * 64),
                           ("source_lines", 950), ("assertion_call_lines", [])):
            changed = copy.deepcopy(self.mapping)
            changed[key] = value
            mutations.append(changed)
        changed = copy.deepcopy(self.mapping)
        changed["segments"].pop()
        mutations.append(changed)
        changed = copy.deepcopy(self.mapping)
        changed["segments"].append(changed["segments"][0])
        mutations.append(changed)
        changed = copy.deepcopy(self.mapping)
        changed["segments"].reverse()
        mutations.append(changed)
        for key, value in (("original", [5, 260]), ("destination", [2, 255]),
                           ("sha256", "0" * 64), ("path", "../shadow.sh")):
            changed = copy.deepcopy(self.mapping)
            changed["segments"][1][key] = value
            mutations.append(changed)
        for additions in ([], self.mapping["additions"] * 2):
            changed = copy.deepcopy(self.mapping)
            changed["additions"] = additions
            mutations.append(changed)
        changed = copy.deepcopy(self.mapping)
        changed["additions"][0]["destination"] = [12, 12]
        mutations.append(changed)
        for changed in mutations:
            with self.assertRaises(ValueError):
                validate(self.original, self.files, changed)

    def test_closed_sources_refuse_empty_shadow_and_unmapped_bytes(self):
        mutations = []
        for path in self.files:
            for replacement in (b"", self.files[path] + b"assert_file() { :; }\n",
                                self.files[path] + b'touch "$repo_root/forged"\n',
                                b":\n" + self.files[path], self.files[path] + b"# padding\n"):
                changed = dict(self.files)
                changed[path] = replacement
                mutations.append(changed)
        changed = dict(self.files)
        changed["tests/ci_guardrails_shadow.sh"] = b"fail() { :; }\n"
        mutations.append(changed)
        changed = dict(self.files)
        changed[PUBLIC] = changed[PUBLIC].replace(source("root"), source("l2"))
        mutations.append(changed)
        changed = dict(self.files)
        changed[lib("l2")] = changed[lib("l2")].replace(
            b'\tassert_dir "$path"', b'#\tassert_dir "$path"',
        )
        mutations.append(changed)
        for command in ADDED_COHORTS:
            for replacement in (b"", command * 2, b"# " + command,
                                command.replace(b"pinned-9.11.1", b"pinned"),
                                command.replace(b"tests.test_ci_", b"tests.shadow_ci_")):
                changed = dict(self.files)
                changed[PUBLIC] = changed[PUBLIC].replace(command, replacement)
                mutations.append(changed)
        for before, after in ((STATIC_COHORT + CANDIDATE_COHORT,
                               CANDIDATE_COHORT + STATIC_COHORT),
                              (CANDIDATE_COHORT + source("l2"),
                               source("l2") + CANDIDATE_COHORT)):
            changed = dict(self.files)
            changed[PUBLIC] = changed[PUBLIC].replace(before, after)
            mutations.append(changed)
        for name in TERMINATED_PARTS:
            path = lib(name)
            preserved = self.files[path][:-len(SOURCE_TERMINATOR)]
            for replacement in (preserved, preserved + SOURCE_TERMINATOR * 2,
                                SOURCE_TERMINATOR + preserved,
                                preserved + b"# another terminator\n",
                                preserved + b": # end of preserved guardrail source range\n"):
                changed = dict(self.files)
                changed[path] = replacement
                mutations.append(changed)
        for changed in mutations:
            with self.assertRaises(ValueError):
                validate(self.original, changed, self.mapping)
        doubled = shell_definitions(self.files[lib("helpers")] + b"fail() {\n}\n")
        self.assertGreater(len(doubled), len({n for n, _ in doubled}))

    def test_heredoc_python_scope_and_bytes_are_not_shell_shadows(self):
        body = (b"outer() {\npython3 -I -S -B - <<'PY'\n"
                b"# standalone Python source\nshadow() {\n}\nPY\n}\n")
        self.assertEqual([("outer", 1)], shell_definitions(body))
        with self.assertRaises(ValueError):
            shell_definitions(body.replace(b"\nPY\n", b"\n"))
        names = [n for part, _, _ in PARTS
                 for n, _ in shell_definitions(self.files[lib(part)])]
        self.assertEqual(list(DEFINITIONS), names)
        helper = self.files[lib("helpers")]
        self.assertIn(b"def finish_step() -> None:\n", helper)
        self.assertEqual(6, helper.count(b"<<'"))

    def test_private_arguments_refused_before_sources_or_cwd_effects(self):
        # No library need exist at this location: refusal precedes root discovery.
        entry = self.elsewhere / "ci_guardrails_static.sh"
        entry.write_bytes(self.files[PRIVATE])
        for args in (("--unknown",), ("",), ("--", "extra")):
            result = subprocess.run(["sh", str(entry), *args], cwd=self.elsewhere,
                                    env=self.env, capture_output=True, text=True, timeout=10)
            self.assertEqual(2, result.returncode)
            self.assertEqual("", result.stdout)
            self.assertEqual("error: ci_guardrails_static.sh accepts no arguments\n", result.stderr)
            self.assertEqual([], list(self.tmp.iterdir()))

    def test_public_ignores_arguments_and_both_runners_keep_source_preconditions(self):
        # Actual parser self-test runs, then the unchanged missing-source guard fails.
        outputs = []
        for entry, args in ((PUBLIC, ()), (PUBLIC, ("--unknown", "extra")), (PRIVATE, ())):
            result = subprocess.run(["sh", str(self.repo / entry), *args], cwd=self.elsewhere,
                                    env=self.env, capture_output=True, text=True, timeout=10)
            self.assertEqual(1, result.returncode)
            self.assertEqual("", result.stdout)
            self.assertEqual(
                f"error: missing required file: {self.repo}/copier-template/scripts/lib/suffix-policy.sh\n",
                result.stderr,
            )
            outputs.append(result.stderr)
            self.assertEqual([], list(self.tmp.iterdir()))
        self.assertEqual(outputs[0], outputs[1])
        self.assertNotIn(b"PYTHONDONTWRITEBYTECODE", self.files[PUBLIC])
        self.assertIn(b"export PYTHONDONTWRITEBYTECODE=1\n", self.files[PRIVATE])
        for part, _, _ in PARTS:
            self.assertNotIn(b"ci_unittest.sh", self.files[lib(part)])

    def test_real_assertion_commands_pass_and_fail_without_function_spies(self):
        sample = self.base / "sample"
        sample.write_text('section:\n  default: "value"\nneedle\n')
        sample.chmod(0o700)
        missing = self.base / "missing"
        good = (
            f'assert_file "{sample}"\nassert_exec "{sample}"\n'
            f'assert_dir "{self.base}"\nassert_absent "{missing}"\n'
            f'assert_contains "{sample}" needle label\n'
            f'assert_not_contains "{sample}" forbidden label\n'
            f'assert_yaml_default "{sample}" section value label\n'
        )
        result = self.helpers(good, trace=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("+ grep -qF -- needle", result.stderr)
        self.assertIn("+ awk -v section=section:", result.stderr)
        failures = (
            f'assert_file "{missing}"', f'assert_exec "{missing}"',
            f'assert_dir "{missing}"', f'assert_absent "{sample}"',
            f'assert_contains "{sample}" absent label',
            f'assert_not_contains "{sample}" needle label',
            f'assert_yaml_default "{sample}" section wrong label',
        )
        for command in failures:
            result = self.helpers(command + '\nprintf "UNREACHABLE\\n"\n')
            self.assertEqual(1, result.returncode, command)
            self.assertIn("error:", result.stderr)
            self.assertNotIn("UNREACHABLE", result.stdout)
        # Force a command-level diff failure; do not run any Git state operation.
        log = self.base / "git.log"
        self.install_command("git", f'printf "%s\\n" "$*" >>"{log}"\nexit 73\n')
        result = self.helpers(f'assert_files_equal "{sample}" "{sample}" label\n')
        self.assertEqual(1, result.returncode)
        self.assertIn("diff command failed", result.stderr)
        self.assertEqual(f"diff --no-index --quiet -- {sample} {sample}\n", log.read_text())

    def test_checkout_negative_cases_command_witness_and_cleanup(self):
        log = self.base / "python.log"
        python = shutil.which("python3")
        self.assertIsNotNone(python)
        self.install_command(
            "python3", f'printf "%s\\n" "$*" >>"{log}"\nexec "{python}" "$@"\n',
        )
        result = self.helpers("self_test_checkout_full_history\n", trace=True)
        self.assertEqual(0, result.returncode, result.stderr)
        calls = log.read_text().splitlines()
        self.assertEqual(5, len(calls))
        for call, leaf in zip(calls, ("valid.yml", "scalar-bypass.yml", "escaped-bypass.yml",
                                     "old-ref-bypass.yml", "case-bypass.yml")):
            self.assertTrue(call.startswith("-I -S -B - "), call)
            self.assertTrue(call.endswith("/" + leaf), call)
        self.assertIn("+ rm -rf ", result.stderr)
        self.assertEqual([], list(self.tmp.iterdir()))
        # An accepted forgery must fail AND remove scratch, using the real body.
        self.install_command("python3", "exit 0\n")
        result = self.helpers("self_test_checkout_full_history\nprintf UNREACHABLE\n")
        self.assertEqual(1, result.returncode)
        self.assertIn("accepted a block-scalar checkout forgery", result.stderr)
        self.assertNotIn("UNREACHABLE", result.stdout)
        self.assertEqual([], list(self.tmp.iterdir()))
        # Preserve, rather than silently improve, original early-failure cleanup.
        self.install_command("python3", "exit 71\n")
        result = self.helpers("self_test_checkout_full_history\n")
        self.assertEqual(1, result.returncode)
        self.assertIn("rejected a valid checkout", result.stderr)
        self.assertEqual(1, len(list(self.tmp.iterdir())))

    def test_real_shell_blocks_fail_at_command_anchors_and_stop(self):
        for part, message, trace in (
            ("root", "missing required file: CODEOWNERS", "+ assert_file CODEOWNERS"),
            ("l2", "missing required directory: copier-template/copier/tpl-agent-repo",
             "+ assert_dir copier-template/copier/tpl-agent-repo"),
            ("tail", "ROCS consumer-model guardrails failed", "/scripts/check-l0-rocs-consumer.sh"),
        ):
            result = self.helpers(source(part).decode() + "printf UNREACHABLE\n", trace=True)
            self.assertEqual(1, result.returncode)
            self.assertIn(message, result.stderr)
            self.assertIn(trace, result.stderr)
            self.assertNotIn("UNREACHABLE", result.stdout)
            self.assertNotIn("ok: l0 guardrails", result.stdout)

    def test_exact_cohort_selectors_dispatch_and_failure_propagation(self):
        log = self.base / "dispatch.log"
        self.install_command("sh", f'printf "%s\\n" "$*" >>"{log}"\nexit 19\n')
        labels = ("guardrails-main", "guardrails-generation-units",
                  "guardrails-ci-planning", "guardrails-ci-static", "guardrails-ci-candidate",
                  "guardrails-system4d")
        modes = ("pinned", "pinned-9.11.1", "pinned-9.11.1", "pinned-9.11.1", "pinned-9.11.1", "pinned")
        commands = [self.lines[number - 1] for number in COHORT_LINES]
        commands[3:3] = ADDED_COHORTS
        for command, label, mode in zip(commands, labels, modes):
            # Outer shell is absolute: substitute only the dispatch command.
            body = (f'repo_root="{self.repo}"\n' + source("helpers").decode()
                    + command.decode() + "printf UNREACHABLE\n")
            result = subprocess.run(["/bin/sh", "-eu", "-c", body], cwd=self.elsewhere,
                                    env=self.env, capture_output=True, text=True, timeout=10)
            self.assertEqual(1, result.returncode)
            self.assertIn("error:", result.stderr)
            if label == "guardrails-ci-static":
                self.assertEqual("error: static guardrail seam contracts failed\n", result.stderr)
            if label == "guardrails-ci-candidate":
                self.assertEqual("error: candidate execution contracts failed\n", result.stderr)
            self.assertNotIn("UNREACHABLE", result.stdout)
        expected = []
        for command, label, mode in zip(commands, labels, modes):
            # Original selectors come from the object; the addition is pinned above.
            selectors = command.decode().split(" >/dev/null")[0]
            selectors = selectors.split('" ', 1)[1]
            expected.append(f"{self.repo}/tests/ci_unittest.sh {selectors}")
            self.assertTrue(selectors.startswith(f"{label} {mode} "))
        self.assertEqual(expected, log.read_text().splitlines())
        self.assertEqual([], list(self.tmp.iterdir()))

    def test_sh_and_bash_syntax(self):
        for shell in ("sh", "bash"):
            for path in self.files:
                result = subprocess.run([shell, "-n", str(self.repo / path)],
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
