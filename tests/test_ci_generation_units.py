"""Fast synthetic seam contracts, never generation/hosted/performance proof.

ci_generation_source_map.json maps every original line (not just assertion labels)
from the observed pre-extraction script to its exact retained bytes. Reconstruction
must match the pinned digest. Runtime spies operate only in private fake repos.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = "scripts/check-l0-generation.sh"
PRIVATE = "tests/ci_generation_unit.sh"
BASELINE_SHA256 = "ab516ad1e3d80b2670f28a6e07a36a6375257ae679afa361dc59727b935f930c"
SOURCE_MAP = json.loads((ROOT / "tests/ci_generation_source_map.json").read_text())
PATHS = sorted({block["target"] for block in SOURCE_MAP["blocks"]} | {
    PRIVATE, "tests/ci_generation_schedule.sh",
})
PROFILES = (
    ("l1-template-sample", "false", "false", "false", "rich"),
    ("l1-template-community", "true", "false", "false", "rich"),
    ("l1-template-release", "false", "true", "false", "rich"),
    ("l1-template-vouch", "false", "false", "true", "rich"),
    ("l1-template-compact-org", "false", "false", "false", "compact"),
)
UNITS = ("profile-community", "profile-release", "profile-vouch", "profile-compact",
         "sample-shell", "generation-python")
DOCS = ("purpose.md", "mission.md", "vision.md", "strategic_objectives.md",
        "values_ethics.md", "governance.md", "glossary.md")
SHELL = ["shell:transport", "shell:matrix", "shell:launchers", "shell:metadata"]
COHORT = ("generation-main", "python3", "tests/test_agent_template_v2.py",
          "tests/test_l1_template_ownership.py", "tests/test_render_l1.py",
          "tests/test_l0_check_timeouts.py", "tests/test_l1_template_company_ownership.py")


def executable_lines(text):
    return [line.strip() for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


# Close the previously unpinned complement of the original source map. Comparing
# all executable bytes outside mapped bodies catches *any* shadow definition,
# including alternate syntax, nested/eval definitions, and extra sourced files.
GLUE = {
    PUBLIC: ['. "$repo_root/tests/ci_generation_schedule.sh"', 'generation_context',
             'generation_preprofile_probes', 'generation_profile_fixtures',
             'generation_rich_org_doc', 'generation_compact_org_doc',
             'generation_compact_operating_model', 'generation_other_shell',
             'generation_python_cohort'],
    "tests/ci_generation_common.sh": ["generation_context() {", "}"],
    "tests/ci_generation_profiles.sh": executable_lines('''
        generation_preprofile_probes() {
        }
        generation_profile_fixtures() {
        }
        generation_rich_org_doc() {
        }
        generation_compact_org_doc() {
        }
        generation_compact_operating_model() {
        }
        generation_rich_docs() {
            rich_l1="$tmp_root/l1-template-sample"
            for org_doc in purpose.md mission.md vision.md strategic_objectives.md values_ethics.md governance.md glossary.md; do
                generation_rich_org_doc
            done
        }
        generation_compact_docs() {
            compact_l1="$tmp_root/l1-template-compact-org"
            for org_doc in purpose.md mission.md vision.md strategic_objectives.md values_ethics.md governance.md glossary.md; do
                generation_compact_org_doc
            done
            generation_compact_operating_model
        }
    '''),
}
for name in ("shell_transport", "shell_matrix", "shell_launchers", "shell_metadata", "python"):
    function = "generation_python_cohort" if name == "python" else "generation_" + name
    GLUE[f"tests/ci_generation_{name}.sh"] = [function + "() {", "}"]
GLUE["tests/ci_generation_schedule.sh"] = [
    f'. "$repo_root/tests/ci_generation_{name}.sh"'
    for name in ("common", "profiles", "shell_transport", "shell_matrix",
                 "shell_launchers", "shell_metadata", "python")
] + ["generation_other_shell() {", "generation_shell_transport", "generation_shell_matrix",
     "generation_shell_launchers", "generation_shell_metadata", "}"]
PRIVATE_SHA256 = "83f4091fe2ec7d1b99e5ce109f26aed7a7ec86f0a92a259a09b998f8c91076fa"


def assert_closed_graph(case, root):
    mapped = {}
    for block in SOURCE_MAP["blocks"]:
        path = block["target"]
        first, last = block["extracted"]
        lines = (root / path).read_bytes().splitlines(keepends=True)
        case.assertEqual(hashlib.sha256(b"".join(lines[first - 1:last])).hexdigest(),
                         block["sha256"], f"mapped body changed: {path}")
        mapped.setdefault(path, set()).update(range(first, last + 1))
    for path, expected in GLUE.items():
        lines = (root / path).read_text().splitlines(keepends=True)
        glue = "".join(line for number, line in enumerate(lines, 1)
                       if number not in mapped.get(path, set()))
        case.assertEqual(executable_lines(glue), expected, f"unowned/shadow code: {path}")
    case.assertEqual(hashlib.sha256((root / PRIVATE).read_bytes()).hexdigest(), PRIVATE_SHA256,
                     "private entrypoint changed outside its closed routing contract")


def snapshot(root):
    return {str(path.relative_to(root)): (path.read_bytes(), path.stat().st_mode)
            for path in root.rglob("*") if path.is_file()}


def environment(**overrides):
    # Ambient instrumentation/Git/AK must not affect synthetic tests.
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("L0_", "GIT_", "AK_", "CI_GENERATION"))}
    env.update(PYTHONDONTWRITEBYTECODE="1", **overrides)
    return env


def copy_seam(root):
    for relative in PATHS:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)


def executable(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\nset -eu\n" + body)
    path.chmod(0o755)


SPIES = r'''
emit() { printf '%s\n' "$*" >>"$SPY_LOG"; }
generation_context() {
    cd "$repo_root"
    export L0_TEMPLATE_ROOT="$repo_root"
    tmp_root="$SPY_TMP"
    python_exec=python3
    emit context
}
generation_preprofile_probes() { emit preprofile; }
generation_profile_fixtures() { emit fixtures; }
profile_phase() { emit "phase:$1"; }
render_l1_case() {
    case_name="$1"
    enable_community_pack="$2"
    enable_release_pack="$3"
    enable_vouch_gate="$4"
    l1_org_docs_profile="$5"
    l1_dir="$tmp_root/$case_name"
    emit "render:$case_name:$enable_community_pack:$enable_release_pack:$enable_vouch_gate:$l1_org_docs_profile:$l1_dir"
    [ "${SPY_FAIL:-}" != "$case_name" ] || exit 19
}
generation_rich_org_doc() { emit "rich:$rich_l1:$org_doc"; }
generation_compact_org_doc() { emit "compact:$compact_l1:$org_doc"; }
generation_compact_operating_model() { emit "operating:$compact_l1"; }
generation_shell_transport() { emit shell:transport; }
generation_shell_matrix() {
    emit shell:matrix
    [ "${SPY_FAIL:-}" != matrix ] || exit 19
}
generation_shell_launchers() { emit shell:launchers; }
generation_shell_metadata() { emit shell:metadata; }
'''


class GenerationSourceContracts(unittest.TestCase):
    def test_every_original_line_and_assertion_is_retained_exactly_once(self):
        reconstructed = []
        coverage = []
        target_coverage = set()
        for block in SOURCE_MAP["blocks"]:
            with self.subTest(block=block["label"]):
                first, last = block["original"]
                start, end = block["extracted"]
                self.assertEqual(last - first, end - start)
                content = (ROOT / block["target"]).read_bytes().splitlines(keepends=True)
                retained = b"".join(content[start - 1:end])
                self.assertEqual(hashlib.sha256(retained).hexdigest(), block["sha256"])
                reconstructed.append(retained)
                coverage.extend(range(first, last + 1))
                for line in range(start, end + 1):
                    coordinate = (block["target"], line)
                    self.assertNotIn(coordinate, target_coverage)
                    target_coverage.add(coordinate)
        self.assertEqual(coverage, list(range(1, 1151)))
        self.assertEqual(SOURCE_MAP["original_lines"], 1150)
        self.assertEqual(SOURCE_MAP["original_sha256"], BASELINE_SHA256)
        self.assertEqual(hashlib.sha256(b"".join(reconstructed)).hexdigest(), BASELINE_SHA256)

    def test_explicit_assertion_inventory_maps_retained_bodies_to_closed_routes(self):
        # Diagnostic/invocation anchors are an explicit inspection index. The full
        # source hash above protects multiline predicates and bodies as well.
        pattern = re.compile(r'^\s*(?:assert_(?:file_contains|path_absent|command_fails|command_fails_with_stderr|trees_equal_without_answers)\s|fail\s|echo "error:)|\|\| fail\s')
        count = 0
        shell_targets = set()
        for block in SOURCE_MAP["blocks"]:
            start, end = block["extracted"]
            lines = (ROOT / block["target"]).read_text().splitlines()[start - 1:end]
            anchors = [block["original"][0] + index for index, line in enumerate(lines)
                       if pattern.search(line)]
            self.assertEqual(anchors, block["assertion_lines"], block["label"])
            count += len(anchors)
            if "shell_" in block["target"]:
                shell_targets.add(block["target"])
        self.assertEqual(count, 158)
        self.assertEqual(shell_targets, {f"tests/ci_generation_shell_{name}.sh"
                                        for name in ("transport", "matrix", "launchers", "metadata")})
        # Those four bodies are reached once by sample-shell and by the full
        # schedule; the dynamic closed-membership test rejects extra cases.
        schedule = (ROOT / "tests/ci_generation_schedule.sh").read_text()
        self.assertEqual(schedule.split("generation_other_shell() {\n", 1)[1],
                         "\tgeneration_shell_transport\n\tgeneration_shell_matrix\n"
                         "\tgeneration_shell_launchers\n\tgeneration_shell_metadata\n}\n")

    def test_source_graph_and_syntax_are_bounded(self):
        schedule = (ROOT / "tests/ci_generation_schedule.sh").read_text()
        sources = [line for line in schedule.splitlines() if line.startswith('. "')]
        self.assertEqual(sources, [f'. "$repo_root/tests/ci_generation_{name}.sh"'
                                  for name in ("common", "profiles", "shell_transport",
                                               "shell_matrix", "shell_launchers",
                                               "shell_metadata", "python")])
        for path in PATHS:
            with self.subTest(path=path):
                self.assertLessEqual(len((ROOT / path).read_text().splitlines()), 500)
                result = subprocess.run(["sh", "-n", str(ROOT / path)], capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                result = subprocess.run(["bash", "-n", str(ROOT / path)], capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
        public = (ROOT / PUBLIC).read_text()
        self.assertNotIn('case "$1"', public)
        self.assertNotIn("getopts", public)
        # Existing guardrails inspect these strings; the source map above verifies
        # their real relocated implementation, not these explanatory references.
        for text in ("tests/test_agent_template_v2.py", "tests/test_l1_template_ownership.py",
                     "preview-l1-diff.sh", "ok: no diff between rendered L1 and target"):
            self.assertIn(text, public)


class GenerationScheduleContracts(unittest.TestCase):
    def invoke(self, entry, args=(), fail="", ambient=None):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as temporary:
            base = Path(temporary)
            root = base / "source"
            scratch = base / "generated"
            scratch.mkdir()
            copy_seam(root)
            schedule = root / "tests/ci_generation_schedule.sh"
            with schedule.open("a") as stream:
                stream.write(SPIES)
            executable(root / "tests/ci_unittest.sh",
                       'printf "python:%s\\n" "$*" >>"$SPY_LOG"\n')
            log = base / "spy.log"
            before = snapshot(root)
            env = environment(SPY_LOG=str(log), SPY_TMP=str(scratch), SPY_FAIL=fail)
            env.update(ambient or {})
            result = subprocess.run(["sh", str(root / entry), *args], cwd=base,
                                    env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(snapshot(root), before, "synthetic source tree was written")
            events = log.read_text().replace(str(scratch), "$tmp_root").splitlines() if log.exists() else []
            return result, events

    @staticmethod
    def render(profile):
        return "render:" + ":".join(profile) + ":$tmp_root/" + profile[0]

    @staticmethod
    def rich_docs():
        return ["rich:$tmp_root/l1-template-sample:" + doc for doc in DOCS]

    @staticmethod
    def compact_docs():
        return ["compact:$tmp_root/l1-template-compact-org:" + doc for doc in DOCS]

    def expected_default(self):
        result = ["context", "preprofile", "fixtures", "phase:profiles"]
        result += [self.render(profile) for profile in PROFILES]
        for rich, compact in zip(self.rich_docs(), self.compact_docs()):
            result.extend((rich, compact))
        return result + ["operating:$tmp_root/l1-template-compact-org", *SHELL,
                         "phase:python-cohort", "python:" + " ".join(COHORT), "phase:complete"]

    def test_default_exact_serial_schedule_variables_cohort_and_output(self):
        result, events = self.invoke(PUBLIC)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(events, self.expected_default())
        self.assertEqual(result.stdout,
                         "ok: l0 generation smoke + idempotency + ownership-aware template propagation\n")

    def test_public_arguments_and_unit_like_environment_do_not_select_or_skip(self):
        result, events = self.invoke(PUBLIC, ("--unit", "profile-community", "--skip-all"),
                                     ambient={"CI_GENERATION_UNIT": "profile-vouch"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(events, self.expected_default())

    def test_private_closed_membership_and_union_without_extra_profile_proofs(self):
        expected = {}
        for unit, profile in zip(UNITS[:4], PROFILES[1:]):
            expected[unit] = ["context", "fixtures", "phase:profiles", self.render(profile)]
        expected["profile-compact"] += self.compact_docs() + ["operating:$tmp_root/l1-template-compact-org"]
        expected["sample-shell"] = ["context", "preprofile", "fixtures", "phase:profiles",
                                    self.render(PROFILES[0]), *self.rich_docs(), *SHELL]
        expected["generation-python"] = ["context", "phase:python-cohort", "python:" + " ".join(COHORT)]
        all_events = []
        for unit in UNITS:
            with self.subTest(unit=unit):
                result, events = self.invoke(PRIVATE, (unit,))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(events, expected[unit] + ["phase:complete"])
                self.assertEqual(result.stdout, "")
                all_events.extend(events)
        proofs = [event for event in all_events if event.startswith(("render:", "shell:", "python:"))]
        default_proofs = [event for event in self.expected_default()
                          if event.startswith(("render:", "shell:", "python:"))]
        self.assertCountEqual(proofs, default_proofs)

    def test_unknown_units_and_wrong_arity_refuse_before_any_setup_or_cases(self):
        for args in ((), ("all",), ("profiles",), ("--help",), ("--skip",), ("generation-python", "extra"),
                     ("",), ("sample-shell; touch source",), ("../sample-shell",)):
            with self.subTest(args=args):
                result, events = self.invoke(PRIVATE, args)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(events, [])
                self.assertEqual(result.stdout, "")
                if len(args) == 1:
                    self.assertIn("valid: " + " ".join(UNITS), result.stderr)

    def test_first_failure_aborts_subsequent_cases(self):
        expected = self.expected_default()
        for failure, final in (("l1-template-release", self.render(PROFILES[2])), ("matrix", "shell:matrix")):
            result, events = self.invoke(PUBLIC, fail=failure)
            self.assertEqual(result.returncode, 19)
            self.assertEqual(events, expected[:expected.index(final) + 1])
            self.assertEqual(result.stdout, "")

    def test_real_context_scratch_cleanup_and_exact_source_binding(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as temporary:
            base = Path(temporary)
            root = base / "source"
            root.mkdir()
            scratch = base / "scratch"
            scratch.mkdir()
            copy_seam(root)
            (root / "scripts/lib").mkdir()
            (root / "scripts/lib/copier-answers.sh").write_text("# synthetic answer library\n")
            before = snapshot(root)
            script = '. "$repo_root/tests/ci_generation_schedule.sh"; generation_context; printf "%s\\n%s\\n" "$tmp_root" "$L0_TEMPLATE_ROOT"'
            env = environment(repo_root=str(root), TMPDIR=str(scratch))
            result = subprocess.run(["sh", "-eu", "-c", script], cwd=base, env=env,
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            generated, bound = result.stdout.splitlines()
            self.assertEqual(bound, str(root))
            self.assertEqual(Path(generated).parent, scratch)
            self.assertFalse(Path(generated).exists(), "original EXIT cleanup was lost")
            self.assertEqual(snapshot(root), before)


class RenderProofCommandContracts(unittest.TestCase):
    """Execute the actual extracted renderer with isolated command spies only."""
    def invoke(self, profile, fail_command=""):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as temporary:
            base = Path(temporary)
            root = base / "source"
            generated = base / "generated"
            generated.mkdir()
            copy_seam(root)
            log = base / "commands.log"
            bin_dir = base / "bin"
            executable(bin_dir / "git", '''printf 'git:%s:%s\n' "${PWD##*/}" "$*" >>"$SPY_LOG"
''')
            executable(root / "scripts/new-l1-from-copier.sh", '''printf 'render:%s\n' "$*" >>"$SPY_LOG"
destination="$1"
mkdir -p "$destination/scripts/ci" "$destination/scripts/release"
for entry in scripts/install-hooks.sh scripts/ci/smoke.sh scripts/check-template-ci.sh scripts/release/check.sh; do
    cat >"$destination/$entry" <<'STUB'
#!/bin/sh
printf 'gate:%s:%s\n' "${PWD##*/}" "$0" >>"$SPY_LOG"
[ "${SPY_FAIL_COMMAND:-}" != "$0" ] || exit 23
STUB
    chmod +x "$destination/$entry"
done
printf '{".": "0.1.0"}\n' >"$destination/.release-please-manifest.json"
printf '## [0.1.0]\n' >"$destination/CHANGELOG.md"
''')
            executable(root / "scripts/preview-l1-diff.sh", '''printf 'preview:%s\n' "$*" >>"$SPY_LOG"
echo "ok: no diff between rendered L1 and target"
''')
            before = snapshot(root)
            env = environment(repo_root=str(root), tmp_root=str(generated),
                              SPY_LOG=str(log), SPY_FAIL_COMMAND=fail_command,
                              PATH=str(bin_dir) + os.pathsep + os.environ["PATH"])
            script = ('. "$repo_root/tests/ci_generation_schedule.sh"; '
                      'generation_profile_fixtures; render_l1_case "$@"')
            result = subprocess.run(["sh", "-eu", "-c", script, "synthetic", *profile],
                                    cwd=base, env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(snapshot(root), before, "renderer wrote to synthetic source")
            events = log.read_text().replace(str(generated), "$tmp_root").splitlines()
            keep = generated / profile[0] / "governance/task-scopes/KEEP.txt"
            manifest = (generated / profile[0] / ".release-please-manifest.json").read_text()
            return result, events, keep.exists(), manifest

    def test_all_profiles_retain_exact_birth_gate_history_rerender_and_preview_commands(self):
        for profile in PROFILES:
            with self.subTest(profile=profile[0]):
                result, events, keep, manifest = self.invoke(profile)
                name, community, release, vouch, docs = profile
                self.assertEqual(result.returncode, 0, result.stderr)
                render = (f"render:$tmp_root/{name} -d repo_slug={name} -d maintainer_handle=@template-owner "
                          f"-d l1_org_docs_profile={docs} -d enable_community_pack={community} "
                          f"-d enable_release_pack={release} -d enable_vouch_gate={vouch} --defaults --overwrite")
                expected = [render, f"git:{name}:init -b main",
                            f"git:{name}:config user.name tpl-template-repo ci",
                            f"git:{name}:config user.email ci@tpl-template-repo.local",
                            f"gate:{name}:./scripts/install-hooks.sh", f"gate:{name}:./scripts/ci/smoke.sh",
                            f"gate:{name}:./scripts/check-template-ci.sh", f"git:{name}:add .",
                            f"git:{name}:commit -m initial render ({name})", render,
                            f"git:{name}:status --porcelain"]
                if name == "l1-template-sample":
                    expected += [f"render:$tmp_root/l1-preview-target -d repo_slug={name} --defaults --overwrite",
                                 "preview:$tmp_root/l1-preview-alias"]
                    self.assertFalse(keep)
                if name == "l1-template-release":
                    expected += [f"preview:$tmp_root/{name}", f"gate:{name}:./scripts/release/check.sh"]
                    self.assertIn('"0.1.1"', manifest)
                self.assertEqual(events, expected)

    def test_gate_failure_is_not_reused_or_hidden(self):
        result, events, _, _ = self.invoke(PROFILES[1], "./scripts/ci/smoke.sh")
        self.assertEqual(result.returncode, 23)
        self.assertEqual(events[-1], "gate:l1-template-community:./scripts/ci/smoke.sh")
        self.assertFalse(any(":commit " in event or event.startswith("preview:") for event in events))


class ClosedDefinitionContracts(unittest.TestCase):
    def test_all_retained_bodies_and_new_definition_frames_are_closed(self):
        assert_closed_graph(self, ROOT)

    def test_duplicate_shadow_counterexample_rejected_at_every_source_surface(self):
        # Preserve every mapped assertion byte: only append the reviewer's
        # counterexample. The old source map alone would accept all these edits.
        for path in PATHS:
            with self.subTest(path=path), tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
                root = Path(tmp)
                copy_seam(root)
                with (root / path).open("a") as stream:
                    stream.write("\ngeneration_shell_transport() { :; }\n")
                with self.assertRaises(AssertionError):
                    assert_closed_graph(self, root)

    def test_empty_original_body_rejected(self):
        for name in ("transport", "matrix", "launchers", "metadata"):
            with self.subTest(name=name), tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
                root = Path(tmp)
                copy_seam(root)
                (root / f"tests/ci_generation_shell_{name}.sh").write_text(
                    f"generation_shell_{name}() {{ :; }}\n")
                with self.assertRaises(AssertionError):
                    assert_closed_graph(self, root)


class ActualWrapperCommandContracts(unittest.TestCase):
    """Fail-stop command witnesses execute loaded wrappers, never replace them.

    These deliberately probe only each wrapper's command prefix. Complete body
    retention + the closed glue contract protect the rest; this is not a claim
    of executing every scenario synthetically or verifying product behavior.
    """
    EXPECTED = {
        "transport": (83, ["birth:$tmp_root/l1-template-colon -d repo_slug=l1-template-colon -d maintainer_handle=@template-owner -d company_name=Foo: Labs --defaults --overwrite"]),
        "matrix": (83, ["birth:$tmp_root/l1-template-matrix -d repo_slug=l1-template-matrix -d maintainer_handle=@template-owner --defaults --overwrite"]),
        # Success of this synthetic invalid-bin command must be refused by the
        # ACTUAL assert_command_fails helper before the wrapper advances.
        "launchers": (1, ["rocs:/definitely/missing:--doctor"]),
        "metadata": (83, ["git:-C $tmp_root/rocs-workspace/core/ontology-kernel init -q -b main"]),
        "python": (0, ["cohort:" + " ".join(COHORT)]),
    }

    def invoke(self, name, mutation=""):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            base = Path(tmp)
            root = base / "source"
            scratch = base / "scratch"
            scratch.mkdir()
            copy_seam(root)
            function = "generation_python_cohort" if name == "python" else "generation_shell_" + name
            if mutation == "shadow":
                with (root / "tests/ci_generation_schedule.sh").open("a") as stream:
                    stream.write(f"\n{function}() {{ :; }}\n")
            elif mutation == "empty":
                path = f"tests/ci_generation_{'python' if name == 'python' else 'shell_' + name}.sh"
                (root / path).write_text(f"{function}() {{ :; }}\n")
            log = base / "commands.log"
            bin_dir = base / "bin"
            executable(root / "scripts/new-l1-from-copier.sh",
                       'printf "birth:%s\\n" "$*" >>"$SPY_LOG"\nexit 83\n')
            executable(root / "scripts/rocs.sh",
                       'printf "rocs:%s:%s\\n" "$ROCS_BIN" "$*" >>"$SPY_LOG"\nexit 0\n')
            executable(bin_dir / "git", 'printf "git:%s\\n" "$*" >>"$SPY_LOG"\nexit 83\n')
            executable(root / "tests/ci_unittest.sh", 'printf "cohort:%s\\n" "$*" >>"$SPY_LOG"\n')
            before = snapshot(root)
            env = environment(repo_root=str(root), tmp_root=str(scratch), python_exec="python3",
                              SPY_LOG=str(log), PATH=str(bin_dir) + os.pathsep + os.environ["PATH"])
            script = '. "$repo_root/tests/ci_generation_schedule.sh"; ' + function
            result = subprocess.run(["sh", "-eu", "-c", script], cwd=base, env=env,
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(snapshot(root), before)
            events = log.read_text().replace(str(scratch), "$tmp_root").splitlines() if log.exists() else []
            return result, events

    def assert_witness(self, name, result, events):
        status, expected = self.EXPECTED[name]
        self.assertEqual(result.returncode, status, result.stderr)
        self.assertEqual(events, expected)
        if name == "launchers":
            self.assertIn("root ROCS doctor must fail closed when ROCS_BIN is invalid", result.stderr)

    def test_actual_loaded_wrappers_reach_exact_command_and_refusal_witnesses(self):
        for name in self.EXPECTED:
            with self.subTest(name=name):
                result, events = self.invoke(name)
                self.assert_witness(name, result, events)

    def test_empty_and_shadow_bodies_lose_runtime_witnesses_and_are_rejected(self):
        for name in self.EXPECTED:
            for mutation in ("shadow", "empty"):
                with self.subTest(name=name, mutation=mutation):
                    result, events = self.invoke(name, mutation)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(events, [])
                    with self.assertRaises(AssertionError):
                        self.assert_witness(name, result, events)


class OwnerSelectionAndBytecodeContracts(unittest.TestCase):
    def test_owner_selects_separate_fast_cohort_without_editing_existing_cohorts(self):
        source = (ROOT / "scripts/check-l0-guardrails.sh").read_text()
        calls = [line for line in source.splitlines() if line.startswith('sh "$repo_root/tests/ci_unittest.sh"')]
        self.assertEqual(calls, [
            'sh "$repo_root/tests/ci_unittest.sh" guardrails-main pinned tests.test_ci_profile tests.test_hosted_ci tests.test_ci_red_green tests.test_l1_template_transitions tests.test_l1_template_company_ownership.CompanyOntologyTests.test_legacy_plans_stay_nonempty_and_map_v2_refuses_unknown_or_overlapping_classes tests.test_company_ontology_ref_inheritance tests.test_l2_template_source tests.test_l1_answer_template_upgrade.UpgradeSafetyTests tests.test_l1_answer_template_legacy tests.test_l1_template_gitlink_retirements >/dev/null || fail "L1 transition / company ontology upgrade / gitlink and retirement behavior tests failed"',
            'sh "$repo_root/tests/ci_unittest.sh" guardrails-generation-units pinned-9.11.1 tests.test_ci_generation_units >/dev/null || fail "generation unit seam contracts failed"',
            'sh "$repo_root/tests/ci_unittest.sh" guardrails-ci-planning pinned-9.11.1 tests.test_ci_coverage tests.test_ci_schedule >/dev/null || fail "independent coverage and routing contracts failed"',
            'sh "$repo_root/tests/ci_unittest.sh" guardrails-ci-static pinned-9.11.1 tests.test_ci_guardrails >/dev/null || fail "static guardrail seam contracts failed"',
            'sh "$repo_root/tests/ci_unittest.sh" guardrails-ci-candidate pinned-9.11.1 tests.test_ci_worker tests.test_ci_aggregate tests.test_ci_candidate_workflow >/dev/null || fail "candidate execution contracts failed"',
            'sh "$repo_root/tests/ci_unittest.sh" guardrails-system4d pinned tests.test_l2_system4d_context >/dev/null || fail "L2 system4d.yaml context tests failed"',
        ])
        # Execute the actual selected line against a command spy, not its comments.
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            root = Path(tmp)
            log = root / "selection.log"
            executable(root / "tests/ci_unittest.sh", 'printf "%s\\n" "$*" >"$SPY_LOG"\n')
            env = environment(repo_root=str(root), SPY_LOG=str(log))
            for index, expected in ((1, "guardrails-generation-units pinned-9.11.1 tests.test_ci_generation_units\n"),
                                    (2, "guardrails-ci-planning pinned-9.11.1 tests.test_ci_coverage tests.test_ci_schedule\n"),
                                    (3, "guardrails-ci-static pinned-9.11.1 tests.test_ci_guardrails\n"),
                                    (4, "guardrails-ci-candidate pinned-9.11.1 tests.test_ci_worker tests.test_ci_aggregate tests.test_ci_candidate_workflow\n")):
                result = subprocess.run(["sh", "-eu", "-c", calls[index]], env=env,
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(log.read_text(), expected)

    def invoke_bare_python_unit(self, remove_guard=False, ambient=None):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            base = Path(tmp)
            root = base / "source"
            scratch = base / "scratch"
            scratch.mkdir()
            copy_seam(root)
            (root / "scripts/lib").mkdir()
            (root / "scripts/lib/copier-answers.sh").write_text("# synthetic answer library\n")
            # Plain Python import would write bytecode without the runner guard.
            (root / "bytecode_probe.py").write_text("VALUE = 1\n")
            executable(root / "tests/ci_unittest.sh", '''
python3 -c 'import bytecode_probe; print(bytecode_probe.VALUE)'
printf 'guard:%s\n' "${PYTHONDONTWRITEBYTECODE:-missing}"
''')
            if remove_guard:
                runner = root / PRIVATE
                runner.write_text(runner.read_text().replace("export PYTHONDONTWRITEBYTECODE=1\n", ""))
            before = snapshot(root)
            env = environment(TMPDIR=str(scratch))
            env.pop("PYTHONDONTWRITEBYTECODE", None)
            env.pop("PYTHONPYCACHEPREFIX", None)
            env.pop("PYTHONPATH", None)
            if ambient is not None:
                env["PYTHONDONTWRITEBYTECODE"] = ambient
            result = subprocess.run(["sh", str(root / PRIVATE), "generation-python"], cwd=base,
                                    env=env, capture_output=True, text=True, timeout=10)
            return result, before, snapshot(root), list(scratch.iterdir())

    def test_private_runner_suppresses_bytecode_without_ambient_help(self):
        for ambient in (None, "0", ""):
            with self.subTest(ambient=ambient):
                result, before, after, scratch = self.invoke_bare_python_unit(ambient=ambient)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "1\nguard:1\n")
                self.assertEqual(after, before)
                self.assertEqual(scratch, [])

    def test_removing_bytecode_guard_is_detected_by_real_import_source_writes(self):
        result, before, after, _ = self.invoke_bare_python_unit(remove_guard=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("guard:missing", result.stdout)
        self.assertNotEqual(after, before)
        self.assertTrue(any(name.startswith("__pycache__/") for name in after.keys() - before.keys()))


if __name__ == "__main__":
    unittest.main()
