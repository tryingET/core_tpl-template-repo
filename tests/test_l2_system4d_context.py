"""Generated repos get a System4D context that names the repo and marks what is still open (AK 6133).

Agents read ontology/src/system4d.yaml before they work in a repo. The templates render what the
copier answers know and leave every other value as explicit FILL IN guidance, never a literal
<...> placeholder token.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

import yaml
from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/lib"))
import l1_template_retirements as retirements  # noqa: E402

TEMPLATES = ("tpl-project-repo", "tpl-monorepo")
SOURCE = "ontology/src/system4d.yaml"
PLACEHOLDER = re.compile(r"<[^<>\n]+>")
FILL_IN = "FILL IN"


def source(template: str) -> Path:
    return ROOT / "copier-template/copier" / template / f"{SOURCE}.j2"


def render(template: str, **answers: object) -> dict:
    context = {"company_slug": "holdingco", "company_name": "Holding Company", **answers}
    env = SandboxedEnvironment(keep_trailing_newline=True, undefined=StrictUndefined)
    text = env.from_string(source(template).read_text(encoding="utf-8")).render(**context)
    return yaml.safe_load(text)["ontology"]["system4d"]


def strings(node: object):
    if isinstance(node, dict):
        for value in node.values():
            yield from strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from strings(value)
    elif isinstance(node, str):
        yield node


def dependency_names(system4d: dict) -> list[str]:
    return [item["name"] for item in system4d["container"]["dependencies"]]


class System4dContextTests(unittest.TestCase):
    def test_templates_render_the_file_and_carry_no_placeholder_tokens(self) -> None:
        for template in TEMPLATES:
            with self.subTest(template=template):
                self.assertFalse((ROOT / "copier-template/copier" / template / SOURCE).exists())
                text = source(template).read_text(encoding="utf-8")
                self.assertEqual(PLACEHOLDER.findall(text), [])
                self.assertIn('name: "{{ repo_slug }}"', text)

    def test_rendered_fixtures_name_the_repo_and_mark_every_open_value(self) -> None:
        rendered = sorted((ROOT / "fixtures").glob(f"**/{SOURCE}"))
        self.assertEqual(len(rendered), 8, "expected the l2 and matrix renders of both templates")
        for path in rendered:
            repo = path.parents[2]
            with self.subTest(fixture=str(repo.relative_to(ROOT))):
                answers = yaml.safe_load((repo / ".copier-answers.yml").read_text(encoding="utf-8"))
                text = path.read_text(encoding="utf-8")
                self.assertEqual(PLACEHOLDER.findall(text), [])
                system4d = yaml.safe_load(text)["ontology"]["system4d"]
                self.assertEqual(system4d["name"], answers["repo_slug"])
                values = list(strings(system4d))
                self.assertTrue(any(value.startswith(FILL_IN) for value in values))
                self.assertEqual([v for v in values if FILL_IN in v and not v.startswith(FILL_IN)], [])
                lane = (repo / "policy/engineering-lane.json").exists()
                self.assertEqual("engineering-core" in dependency_names(system4d), lane)

    def test_ids_and_engineering_lane_follow_the_answers(self) -> None:
        cases = (
            ("replay-fabric", "go", True, "RF", "The go engineering lane"),
            ("agent_kernel", "typescript", True, "AK", "The ts engineering lane"),
            ("dspx", "bash", True, "DSPX", None),
            ("proj.foo", "python", False, "PF", None),
        )
        for slug, language, pack, prefix, lane_note in cases:
            with self.subTest(slug=slug, language=language, pack=pack):
                system4d = render(
                    "tpl-project-repo", repo_slug=slug, language=language, enable_software_pack=pack, location="owned"
                )
                self.assertEqual(system4d["name"], slug)
                self.assertEqual(system4d["engine"]["invariants"][0]["id"], f"{prefix}-INV-001")
                self.assertEqual(system4d["fog"]["debt"][0]["id"], f"{prefix}-D-001")
                notes = [item["note"] for item in system4d["container"]["dependencies"] if item["name"] == "engineering-core"]
                self.assertEqual([note.split(":")[0] for note in notes], [lane_note] if lane_note else [])
        monorepo = render("tpl-monorepo", repo_slug="platform-mono", package_manager="pnpm")
        self.assertEqual(monorepo["engine"]["invariants"][0]["id"], "PM-INV-001")
        self.assertIn("Workspace package manager: pnpm; each package and app declares its own language",
                      monorepo["container"]["constraints"])
        self.assertIn("engineering-core", dependency_names(monorepo))

    def test_l1_refresh_retires_the_plain_copies_l1s_still_carry(self) -> None:
        # Without this, an L1 refresh keeps the old file beside the .j2 and both render one L2 path.
        entries = retirements.load_manifest()
        for template in TEMPLATES:
            path = f"copier/{template}/{SOURCE}"
            with self.subTest(path=path):
                self.assertEqual(len([item for item in entries if item["regex"].match(path)]), 1)
                self.assertEqual([item for item in entries if item["regex"].match(f"{path}.j2")], [])


if __name__ == "__main__":
    unittest.main()
