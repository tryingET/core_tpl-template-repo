from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/l2/tpl-agent-repo"
L1_AGENT_TEMPLATE = ROOT / "fixtures/l1/template-repo/copier/tpl-agent-repo"
SCRATCH_PARENT = Path(os.environ.get("TMPDIR", str(ROOT)))
PERSONA = (
    "README.md",
    "identity.md",
    "reason.md",
    "main_task.md",
    "dream_goal.md",
    "behavior_rules.md",
)


def run(*args: str, cwd: Path, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if result.returncode != expect:
        raise AssertionError(
            f"command returned {result.returncode}, expected {expect}: {args}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AgentTemplateV2Tests(unittest.TestCase):
    def copy_fixture(self, parent: Path, name: str) -> Path:
        target = parent / name
        shutil.copytree(FIXTURE, target)
        return target

    def test_manifest_shell_and_six_canonical_persona_inputs(self) -> None:
        manifest = json.loads((FIXTURE / "agent.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], "ai-society.agent/1")
        self.assertIsInstance(manifest["role"], str)
        self.assertTrue(manifest["role"])
        self.assertEqual(manifest["system_prompt_file"], "docs/person/system-prompt.md")
        self.assertEqual(
            set(("name", "role", "system_prompt_file", "skills", "tools", "extensions", "defaults", "scope"))
            - manifest.keys(),
            set(),
        )
        self.assertIn("profile", manifest["skills"])
        self.assertIn("extra", manifest["skills"])
        self.assertIn("model", manifest["defaults"])
        self.assertIn("thinking", manifest["defaults"])

        readme = (FIXTURE / "docs/person/README.md").read_text(encoding="utf-8")
        for name in PERSONA:
            self.assertIn(f"`{name}`", readme)
        compiled = (FIXTURE / "docs/person/system-prompt.md").read_text(encoding="utf-8")
        self.assertTrue(compiled.startswith("<!-- compiled: do not edit -->"))
        for name in PERSONA:
            self.assertIn(f"## Persona source: {name}", compiled)

    def test_compiler_validates_manifest_and_detects_staleness(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT) as temp:
            agent = self.copy_fixture(Path(temp), "agent")
            compiler = agent / "scripts/compile-system-prompt.py"
            run(str(compiler), "--check", cwd=agent)
            with (agent / "docs/person/identity.md").open("a", encoding="utf-8") as stream:
                stream.write("\nchanged identity\n")
            run(str(compiler), "--check", cwd=agent, expect=1)
            run(str(compiler), cwd=agent)
            run(str(compiler), "--check", cwd=agent)

            manifest_path = agent / "agent.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["role"] = ["role-one", "role-two"]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            invalid = run(str(compiler), "--check", cwd=agent, expect=2)
            self.assertIn("role must be one non-empty string", invalid.stderr)

    def test_propagation_renders_l1_plan_first_and_preserves_agent_bytes(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT) as temp:
            parent = Path(temp)
            agent = self.copy_fixture(parent, "agent")
            template = parent / "current-l1-template"
            shutil.copytree(L1_AGENT_TEMPLATE, template)
            run("git", "init", "--quiet", cwd=agent)

            identity = agent / "docs/person/identity.md"
            with identity.open("a", encoding="utf-8") as stream:
                stream.write("\nagent-owned identity sentinel\n")
            manifest_path = agent / "agent.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["tools"] = ["read", "bash"]
            manifest["scope"]["note"] = "agent-owned scope sentinel"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            run("./scripts/compile-system-prompt.py", cwd=agent)

            protected = [agent / "docs/person" / name for name in PERSONA]
            protected.extend((manifest_path, agent / "docs/person/system-prompt.md"))
            before = {path.relative_to(agent).as_posix(): digest(path) for path in protected}

            template_readme = template / "README.md.j2"
            template_readme.write_text(
                template_readme.read_text(encoding="utf-8") + "\ntemplate refresh sentinel\n",
                encoding="utf-8",
            )
            original_readme = (agent / "README.md").read_bytes()
            propagate = agent / "scripts/propagate-template.sh"

            planned = run(str(propagate), "--source", str(template), cwd=agent)
            self.assertIn("PLAN (no files changed", planned.stdout)
            self.assertIn("update: README.md", planned.stdout)
            self.assertEqual((agent / "README.md").read_bytes(), original_readme)
            self.assertEqual(
                before,
                {path.relative_to(agent).as_posix(): digest(path) for path in protected},
            )

            applied = run(str(propagate), "--source", str(template), "--apply", cwd=agent)
            self.assertIn("APPLY", applied.stdout)
            self.assertIn("template refresh sentinel", (agent / "README.md").read_text(encoding="utf-8"))
            self.assertEqual(
                before,
                {path.relative_to(agent).as_posix(): digest(path) for path in protected},
            )
            run("./scripts/compile-system-prompt.py", "--check", cwd=agent)

    def test_propagation_refuses_unknown_top_level_file(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT) as temp:
            parent = Path(temp)
            agent = self.copy_fixture(parent, "agent")
            rendered = self.copy_fixture(parent, "rendered")
            run("git", "init", "--quiet", cwd=agent)
            (agent / "UNKNOWN.txt").write_text("must classify me\n", encoding="utf-8")
            result = run(
                "./scripts/propagate-template.sh",
                "--rendered",
                str(rendered),
                cwd=agent,
                expect=2,
            )
            self.assertIn("unclassified existing path: UNKNOWN.txt", result.stderr)

    def test_propagation_refuses_ambiguous_map_and_symlinked_parent(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT) as temp:
            parent = Path(temp)
            agent = self.copy_fixture(parent, "agent")
            rendered = self.copy_fixture(parent, "rendered")
            run("git", "init", "--quiet", cwd=agent)

            ownership = rendered / "contracts/template-ownership.yml"
            ownership.write_text(
                ownership.read_text(encoding="utf-8") + "  - README.md\n",
                encoding="utf-8",
            )
            ambiguous = run(
                "./scripts/propagate-template.sh",
                "--rendered",
                str(rendered),
                cwd=agent,
                expect=2,
            )
            self.assertIn("ambiguous ownership patterns", ambiguous.stderr)

            shutil.rmtree(rendered)
            rendered = self.copy_fixture(parent, "rendered-safe-map")
            cognitive_tools = agent / "prompts/cognitive-tools"
            shutil.rmtree(cognitive_tools)
            external = parent / "external"
            external.mkdir()
            cognitive_tools.symlink_to(external, target_is_directory=True)
            unsafe = run(
                "./scripts/propagate-template.sh",
                "--rendered",
                str(rendered),
                "--apply",
                cwd=agent,
                expect=2,
            )
            self.assertIn("symlinked destination ancestor", unsafe.stderr)
            self.assertEqual(list(external.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
