"""L1 company ontology defaults: argument safety plus real Copier convergence."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "copier-template"
SCRATCH = Path(os.environ.get("TMPDIR", str(ROOT)))
KEY = "company_ontology_ref"
ARCHETYPES = ("tpl-project-repo", "tpl-monorepo", "tpl-package")
ALL_ARCHETYPES = (*ARCHETYPES, "tpl-agent-repo", "tpl-org-repo")
# The explicit relative prefix prevents Copier 9.11.1's _adjust_rendered_part
# from reducing a directory-qualified answers path to its basename.
NESTED_ANSWERS = "{{ '.' ~ _copier_conf.sep ~ _copier_conf.answers_file }}.j2"
OUTER_ANSWERS = "{% raw %}" + NESTED_ANSWERS[:-3] + "{% endraw %}.j2"
INHERITED = "<repo:Example/ontology@v1.2.3>"
STORED = "<repo:Deliberate/ontology@v4>"
EXPLICIT = "<repo:Override/ontology@v5>"


def dump(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value), encoding="utf-8")


def run(*args: str, cwd: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)


def tree(path: Path) -> dict[str, str]:
    return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob("*") if p.is_file()}


class WrapperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH, prefix="ontology-argv-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.l1 = self.root / "l1"
        (self.l1 / "scripts").mkdir(parents=True)
        shutil.copy2(SOURCE / "scripts/new-repo-from-copier.sh", self.l1 / "scripts")
        shutil.copytree(SOURCE / "scripts/lib", self.l1 / "scripts/lib")
        dump(self.l1 / "contracts/layer-contract.yml", {"layer": "L1"})
        for name in (*ARCHETYPES, "tpl-agent-repo", "tpl-org-repo"):
            target = self.l1 / "copier" / name
            target.mkdir(parents=True)
            shutil.copy2(SOURCE / "copier" / name / "copier.yml", target)
        self.answers = self.l1 / ".copier-answers.yml"
        dump(self.answers, {KEY: INHERITED, "company_slug": "otherco"})
        self.dest = self.root / "child with spaces"
        self.record = self.root / "argv.json"
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        uvx = bin_dir / "uvx"
        uvx.write_text("#!/usr/bin/env python3\nimport json, os, sys\n"
                       "open(os.environ['ARGV_RECORD'], 'w').write(json.dumps(sys.argv[1:]))\n")
        uvx.chmod(0o755)
        ak = bin_dir / "ak"
        ak.write_text(f"#!{sys.executable}\nimport json, sys\n"
                      "if sys.argv[1:] != ['task', 'show', '1']: raise SystemExit(97)\n"
                      "print(json.dumps({'id': 1, 'status': 'claimed', 'repo': 'synthetic'}))\n")
        ak.chmod(0o755)
        self.env = dict(os.environ, PATH=f"{bin_dir}:{os.environ['PATH']}",
                        ARGV_RECORD=str(self.record), AK_CMD=str(ak),
                        PYTHONDONTWRITEBYTECODE="1", COPIER_ANSWERS_PYTHON=sys.executable, DISABLE_PROJECT_OWNER_HANDLE_INFERENCE="1")

    def invoke(self, *args: str, archetype: str = ARCHETYPES[0], ok: bool = True) -> list:
        self.record.unlink(missing_ok=True)
        result = run("sh", str(self.l1 / "scripts/new-repo-from-copier.sh"),
                     archetype, str(self.dest), *args, cwd=self.root, env=self.env)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(self.record.read_text())
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.record.exists(), "malformed inputs reached Copier")
        return []

    def defaults(self, args: list) -> list[str]:
        return [arg.split("=", 1)[1] for arg in args if arg.startswith(KEY + "=")]

    def test_precedence_and_empty_values(self) -> None:
        for archetype in ARCHETYPES:
            for stored, inherited, expected in (
                (None, INHERITED, INHERITED), (STORED, INHERITED, STORED),
                ("", INHERITED, INHERITED), (None, "", None), (None, None, None),
                (STORED, "", STORED), ("", "", "fallback"),
            ):
                with self.subTest(archetype=archetype, stored=stored, inherited=inherited):
                    dump(self.answers, {"company_slug": "otherco", KEY: inherited})
                    dump(self.dest / ".copier-answers.yml", {} if stored is None else {KEY: stored})
                    if expected == "fallback":
                        config = yaml.safe_load((SOURCE / "copier" / archetype / "copier.yml").read_text())
                        expected = config[KEY]["default"].replace("{{ company_slug }}", "otherco")
                    self.assertEqual(self.defaults(self.invoke(archetype=archetype)),
                                     [] if expected is None else [expected])

    def test_explicit_forms_even_empty_bypass_inheritance(self) -> None:
        dump(self.dest / ".copier-answers.yml", {KEY: STORED})
        for value in (EXPLICIT, ""):
            for option in (("-d", f"{KEY}={value}"), ("--data", f"{KEY}={value}"),
                           (f"-d{KEY}={value}",), (f"--data={KEY}={value}",)):
                with self.subTest(option=option):
                    args = self.invoke(*option)
                    self.assertEqual(args[-len(option)-2:-2], list(option))
                    self.assertNotIn(f"{KEY}={INHERITED}", args)
                    self.assertNotIn(f"{KEY}={STORED}", args)

    def test_custom_answers_paths_and_cli_data_files(self) -> None:
        relative = "answers dir/company choices.yml"
        dump(self.dest / ".copier-answers.yml", {KEY: "wrong-default-file"})
        dump(self.dest / relative, {KEY: STORED})
        for option in (("-a", relative), ("--answers-file", relative),
                       (f"--answers-file={relative}",), (f"-a{relative}",)):
            with self.subTest(option=option):
                self.assertEqual(self.defaults(self.invoke(*option)), [STORED])
        data = self.root / "explicit data.yml"
        for value in (EXPLICIT, ""):
            dump(data, {KEY: value})
            for option in (("--data-file", str(data)), (f"--data-file={data}",)):
                self.assertEqual(self.defaults(self.invoke(*option)), [])

    def test_shell_metacharacters_are_literal(self) -> None:
        literal = "<repo:Other/ontology@$(touch PWNED);`touch PWNED` & | > 'quoted' #>"
        for source in (self.answers, self.dest / ".copier-answers.yml"):
            dump(source, {KEY: literal})
            self.assertEqual(self.defaults(self.invoke()), [literal])
            self.assertFalse((self.root / "PWNED").exists())

    def test_unsafe_yaml_characters_rejected_at_each_input_boundary(self) -> None:
        for bad in ('<repo:Other/ontology@"quoted">', '<repo:Other/ontology@back\\slash>',
                    'line\nbreak', 'tab\tvalue', 'control\x01value'):
            for name in ARCHETYPES:
                with self.subTest(value=bad, archetype=name):
                    for option in (("-d", f"{KEY}={bad}"), ("--data", f"{KEY}={bad}"),
                                   (f"-d{KEY}={bad}",), (f"--data={KEY}={bad}",)):
                        self.invoke(*option, archetype=name, ok=False)
            data = self.root / "unsafe-data.yml"
            dump(data, {KEY: bad})
            self.invoke("--data-file", str(data), ok=False)
            for source in (self.answers, self.dest / ".copier-answers.yml"):
                dump(self.answers, {KEY: INHERITED})
                (self.dest / ".copier-answers.yml").unlink(missing_ok=True)
                dump(source, {KEY: bad})
                self.invoke(ok=False)
            dump(self.answers, {KEY: INHERITED})
            (self.dest / ".copier-answers.yml").unlink(missing_ok=True)

    def test_malformed_answers_and_options_fail_closed(self) -> None:
        for bad in ("company_ontology_ref: [broken", "- not-a-mapping\n",
                    "company_ontology_ref: {ref: wrong}\n", "company_ontology_ref: [wrong]\n",
                    "company_ontology_ref: true\n", "company_ontology_ref: 42\n",
                    'company_ontology_ref: "line\\nbreak"\n',
                    'company_ontology_ref: "nul\\0byte"\n'):
            for source in (self.answers, self.dest / ".copier-answers.yml"):
                with self.subTest(bad=bad, source=source.name):
                    dump(self.answers, {KEY: INHERITED})
                    (self.dest / ".copier-answers.yml").unlink(missing_ok=True)
                    source.parent.mkdir(parents=True, exist_ok=True)
                    source.write_text(bad)
                    self.invoke(ok=False)
        dump(self.answers, {KEY: INHERITED})
        (self.dest / ".copier-answers.yml").unlink(missing_ok=True)
        for args in (("-a",), ("--answers-file",), ("--answers-file=",),
                     ("-a", "--defaults"), ("--data-file", "missing.yml")):
            self.invoke(*args, ok=False)

    def test_unrelated_archetypes_do_not_inherit(self) -> None:
        for name in ("tpl-org-repo", "tpl-agent-repo"):
            args = ("-d", "creation_task_id=AK-1", "-d", "agent_role=test") if name == "tpl-agent-repo" else ()
            self.assertEqual(self.defaults(self.invoke(*args, archetype=name)), [])

    def test_source_fixture_copies_and_budgets(self) -> None:
        for relative in ("scripts/new-repo-from-copier.sh", "scripts/lib/company-ontology-ref.sh"):
            self.assertEqual((SOURCE / relative).read_bytes(),
                             (ROOT / "fixtures/l1/template-repo" / relative).read_bytes())
        for name in ALL_ARCHETYPES:
            expected = ROOT / "fixtures/l1/template-repo/copier" / name
            self.assertEqual((SOURCE / "copier" / name / OUTER_ANSWERS).read_bytes(),
                             (expected / NESTED_ANSWERS).read_bytes())
            self.assertFalse((expected / ".copier-answers.yml.j2").exists())
        self.assertLessEqual(len((SOURCE / "scripts/new-repo-from-copier.sh").read_text().splitlines()), 500)
        self.assertLessEqual(len((ROOT / "scripts/check-l0-guardrails.sh").read_text().splitlines()), 951)


class RendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH, prefix="ontology-render-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.l1 = self.root / "l1"
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        ak = bin_dir / "ak"
        ak.write_text(f"#!{sys.executable}\nimport json, sys\n"
                      "if sys.argv[1:] != ['task', 'show', '123']: raise SystemExit(97)\n"
                      "print(json.dumps({'id': 123, 'status': 'claimed', 'repo': 'synthetic'}))\n")
        ak.chmod(0o755)
        self.env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", COPIER_VCS_REF="HEAD",
                        COPIER_ANSWERS_PYTHON=sys.executable, AK_CMD=str(ak),
                        PATH=f"{bin_dir}:{os.environ['PATH']}", DISABLE_PROJECT_OWNER_HANDLE_INFERENCE="1")

    def checked(self, *args: str) -> None:
        result = run(*args, cwd=self.root, env=self.env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def render_l1(self, *args: str) -> None:
        self.checked("sh", str(ROOT / "scripts/new-l1-from-copier.sh"), str(self.l1),
                     "--defaults", "--overwrite", "-d", "company_slug=otherco", *args)

    def render_child(self, name: str, dest: Path, *args: str) -> None:
        identity = "package_name=inheritance-test" if name == "tpl-package" else "repo_slug=inheritance-test"
        agent = ("-d", "creation_task_id=AK-123", "-d", "agent_role=fixture-agent-role") if name == "tpl-agent-repo" else ()
        self.checked("sh", str(self.l1 / "scripts/new-repo-from-copier.sh"), name, str(dest),
                     "--defaults", "--overwrite", "-d", identity,
                     "-d", "template_source_sha=test-source", *agent, *args)

    def assert_choice(self, name: str, dest: Path, expected: str, answers: str = ".copier-answers.yml") -> None:
        self.assertEqual(yaml.safe_load((dest / answers).read_text())[KEY], expected)
        manifest = dest / "ontology/manifest.yaml"
        if name in ("tpl-project-repo", "tpl-monorepo"):
            layers = yaml.safe_load(manifest.read_text())["rocs"]["layers"]
            self.assertEqual(next(layer["ref"] for layer in layers if layer["name"] == "company"), expected)
        else:
            self.assertFalse(manifest.exists(), "metadata-only archetype gained ontology activation")

    def test_fresh_children_persist_and_reruns_preserve_choices(self) -> None:
        # Shell-active text is data, including on the real render path.
        literal = "<repo:Other/ontology@$(touch PWNED);`touch PWNED`&'tag'>"
        self.render_l1("-d", f"{KEY}={literal}")
        self.assertEqual(yaml.safe_load((self.l1 / ".copier-answers.yml").read_text())[KEY], literal)
        self.render_l1()  # No restatement: L0 rerender must retain the L1 selection.
        self.assertEqual(yaml.safe_load((self.l1 / ".copier-answers.yml").read_text())[KEY], literal)
        for name in ARCHETYPES:
            with self.subTest(archetype=name):
                dest = self.root / name
                self.render_child(name, dest)
                self.assert_choice(name, dest, literal)
                before = tree(dest)
                self.render_child(name, dest)
                self.assertEqual(tree(dest), before)
                self.render_child(name, dest, "-d", f"{KEY}={STORED}")
                self.assert_choice(name, dest, STORED)
                self.render_child(name, dest)  # L1 still differs: deliberate child choice wins.
                self.assert_choice(name, dest, STORED)
                self.render_child(name, dest, "-d", f"{KEY}={EXPLICIT}")
                self.assert_choice(name, dest, EXPLICIT)
        self.assertFalse(any(self.root.rglob("PWNED")))

    def test_empty_default_and_custom_destination_answers(self) -> None:
        self.render_l1()
        l1_answers = self.l1 / ".copier-answers.yml"
        self.assertNotIn(KEY, yaml.safe_load(l1_answers.read_text()))
        for index, name in enumerate(ARCHETYPES):
            with self.subTest(archetype=name):
                dest = self.root / name
                relative = "answers dir/child.yml"
                option = (("-a", relative), ("--answers-file", relative),
                          (f"--answers-file={relative}",))[index]
                self.render_child(name, dest, *option)
                config = yaml.safe_load((SOURCE / "copier" / name / "copier.yml").read_text())
                fallback = config[KEY]["default"].replace("{{ company_slug }}", "otherco")
                self.assert_choice(name, dest, fallback, relative)
                self.assertFalse((dest / ".copier-answers.yml").exists())
                before = tree(dest)
                self.render_child(name, dest, *option)
                self.assertEqual(tree(dest), before)
                # An empty stored value is not a deliberate choice; use archetype fallback.
                data = yaml.safe_load((dest / relative).read_text())
                data[KEY] = ""
                dump(dest / relative, data)
                self.render_child(name, dest, *option)
                self.assert_choice(name, dest, fallback, relative)
                self.render_child(name, dest, *option, "-d", f"{KEY}={STORED}")
                dump(l1_answers, {**yaml.safe_load(l1_answers.read_text()), KEY: INHERITED})
                self.render_child(name, dest, *option)
                self.assert_choice(name, dest, STORED, relative)
                self.render_child(name, dest, *option, "-d", f"{KEY}=")
                self.assert_choice(name, dest, "", relative)
                self.render_child(name, dest, *option)
                self.assert_choice(name, dest, INHERITED, relative)
                before = tree(dest)
                self.render_child(name, dest, *option)
                self.assertEqual(tree(dest), before)
                dump(l1_answers, {**yaml.safe_load(l1_answers.read_text()), KEY: ""})
        self.render_l1()
        self.assertNotIn(KEY, yaml.safe_load(l1_answers.read_text()))

    def test_all_five_filename_transport_and_outer_custom_name_isolation(self) -> None:
        for outer in (".copier-answers.yml", "parent answers.yml"):
            with self.subTest(outer=outer):
                self.l1 = self.root / ("l1-default" if outer.startswith(".") else "l1-custom")
                self.render_l1("-a", outer)
                self.assertTrue((self.l1 / outer).is_file())
                self.render_l1("-a", outer)
                for name in ALL_ARCHETYPES:
                    nested = self.l1 / "copier" / name
                    self.assertEqual([p.name for p in nested.glob("*answers*")], [NESTED_ANSWERS])
                    for answers in (".copier-answers.yml", "child answers/choice.yml"):
                        with self.subTest(archetype=name, answers=answers):
                            dest = self.root / f"{self.l1.name}-{name}-{answers.startswith('.')}"
                            args = () if answers.startswith(".") else ("--answers-file", answers)
                            self.render_child(name, dest, *args)
                            self.assertIsInstance(yaml.safe_load((dest / answers).read_text()), dict)
                            if not answers.startswith("."):
                                self.assertFalse((dest / ".copier-answers.yml").exists())
                            if outer != ".copier-answers.yml":
                                self.assertFalse((dest / outer).exists(), "outer L0 answers filename leaked")
                            before = tree(dest)
                            self.render_child(name, dest, *args)
                            self.assertEqual(tree(dest), before)

    def test_real_render_rejects_unsafe_ref_without_mutating_destination(self) -> None:
        for bad in ('<repo:other/ontology@"quote">', '<repo:other/ontology@back\\slash>', 'line\nbreak'):
            with self.subTest(value=bad):
                result = run("sh", str(ROOT / "scripts/new-l1-from-copier.sh"), str(self.l1),
                             "--defaults", "--overwrite", "-d", f"{KEY}={bad}",
                             cwd=self.root, env=self.env)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("double quotes or backslashes", result.stderr)
                self.assertFalse(self.l1.exists())
        self.render_l1("-d", f"{KEY}={INHERITED}")
        for name in ARCHETYPES:
            dest = self.root / name
            self.render_child(name, dest)
            before = tree(dest)
            result = run("sh", str(self.l1 / "scripts/new-repo-from-copier.sh"), name, str(dest),
                         "--defaults", "--overwrite", "-d", f'{KEY}=unsafe"quote',
                         cwd=self.root, env=self.env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("without double quotes or backslashes", result.stderr)
            self.assertEqual(tree(dest), before)


if __name__ == "__main__":
    unittest.main()
