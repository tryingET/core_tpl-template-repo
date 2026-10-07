"""P07 rendered instruction conformance, not actor/birth/runtime authorization proof.

Use the real two-stage wrapper and pinned Copier. The exact-task lookup shim is
fixture construction only; none of these agents is deployed or appointed.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRATCH_PARENT = Path(os.environ.get("TMPDIR", str(ROOT)))


def run(*args: str, cwd: Path, env: dict[str, str]) -> str:
    result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True)
    if result.returncode:
        raise AssertionError(f"{args}: exit {result.returncode}\n{result.stdout}\n{result.stderr}")
    return result.stdout


class AgentInstructionConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = tempfile.TemporaryDirectory(dir=SCRATCH_PARENT)
        cls.addClassCleanup(cls.scratch.cleanup)
        parent = Path(cls.scratch.name)
        lookup = parent / "fixture-ak"
        lookup.write_text(
            '#!/bin/sh\n[ "$#" = 3 ] && [ "$1 $2 $3" = "task show 5105" ]\n',
            encoding="utf-8",
        )
        lookup.chmod(0o755)
        # Child births stage this exact L0 source, not a guessed sibling core/ path.
        env = dict(os.environ, AK_CMD=str(lookup), L0_TEMPLATE_ROOT=str(ROOT),
                   PYTHONDONTWRITEBYTECODE="1", COPIER_VERSION="9.11.1")
        if not (shutil.which("uvx", path=env.get("PATH")) or shutil.which("uv", path=env.get("PATH"))):
            raise AssertionError("native conformance requires the wrapper's pinned uvx/uv runtime; no unpinned fallback")
        # Test one committed exact source: dirty edits cannot become implicit proof.
        revision = run("git", "rev-parse", "HEAD", cwd=ROOT, env=env).strip()
        env["COPIER_VCS_REF"] = revision
        cls.rendered = {}
        for company in ("holdingco", "softwareco"):
            l1, l2 = parent / company, parent / f"{company}-agent"
            run(
                "sh", str(ROOT / "scripts/new-l1-from-copier.sh"), str(l1),
                "-d", f"company_slug={company}", "-d", f"repo_slug={company}",
                "--defaults", "--overwrite", cwd=ROOT, env=env,
            )
            # Rendered L1 is not a Git source; use Copier's local-directory path.
            run(
                "sh", "./scripts/new-repo-from-copier.sh", "tpl-agent-repo", str(l2),
                "-d", "repo_slug=fixture-agent", "-d", "agent_role=Fixture Role",
                "-d", "creation_task_id=AK-5105", "--defaults", "--overwrite",
                cwd=l1, env=env,
            )
            cls.rendered[company] = (l2 / "AGENTS.md").read_text(encoding="utf-8")

    def test_native_render_does_not_prescribe_unadmitted_home_or_mr_only_work(self) -> None:
        for company, text in self.rendered.items():
            with self.subTest(company=company):
                self.assertNotIn("Never push to `main`; open branches + MRs.", text)
                self.assertNotIn("Keep one role in one `ai-society/agents/agent-<name>` repository", text)
                self.assertIn("owner-admitted placement", text)
                self.assertIn("main-first", text)
                self.assertIn("Publication/push", text)

    def test_native_render_preserves_owner_authority_and_unappointed_ceiling(self) -> None:
        for company, text in self.rendered.items():
            with self.subTest(company=company):
                self.assertIn("Unappointed agents are advisory", text)
                self.assertIn("current owner-issued", text)
                self.assertIn("persona may narrow", text)
                self.assertIn("never issue or broaden a grant", text)
                self.assertIn("exact active AK task owned by that target repository", text)
                self.assertIn("role-card exclusions", text)
                self.assertIn("Appointment, repository creation and runtime activation are separate", text)

    def test_no_rendered_grant_or_loader_override_is_introduced(self) -> None:
        for company, text in self.rendered.items():
            with self.subTest(company=company):
                self.assertNotIn("AGENTS.override.md", text)
                self.assertNotIn("automatically authorized", text)
                self.assertIn("Missing, expired, revoked or conflicting admission", text)
                self.assertIn("affected act", text)
                self.assertIn("unaffected admitted work", text)
                self.assertIn("D68", text)


if __name__ == "__main__":
    unittest.main()
