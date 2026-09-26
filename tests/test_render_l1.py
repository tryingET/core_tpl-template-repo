from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/l1/template-repo"
SCRIPT = ROOT / "scripts/render-l1.sh"
SCRATCH_PARENT = Path(os.environ.get("TMPDIR", str(ROOT)))


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True)


def snapshot(repo: Path) -> tuple[str, str]:
    status = run("git", "status", "--porcelain", "--ignored", cwd=repo).stdout
    files = sorted(str(p.relative_to(repo)) for p in repo.rglob("*") if ".git" not in p.relative_to(repo).parts)
    return status, "\n".join(files)


class RenderL1Tests(unittest.TestCase):
    def test_render_only_writes_output_and_leaves_target_untouched(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT) as temp:
            parent = Path(temp)
            target = parent / "target"
            shutil.copytree(FIXTURE, target)
            for args in (("init", "--quiet"), ("config", "user.name", "render test"),
                         ("config", "user.email", "test@example.invalid"), ("config", "gc.auto", "0"),
                         ("config", "maintenance.auto", "false"), ("add", "."), ("commit", "--quiet", "-m", "fixture")):
                self.assertEqual(run("git", *args, cwd=target).returncode, 0)
            before = snapshot(target)
            out = parent / "render"
            result = run("sh", str(SCRIPT), str(target), str(out), cwd=parent)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(f"==> rendered: {out}", result.stdout)
            self.assertTrue((out / "contracts/template-ownership.yml").is_file())
            self.assertTrue((out / "copier/tpl-project-repo/scripts/rocs.sh.j2").is_file())
            self.assertEqual(snapshot(target), before)
            again = run("sh", str(SCRIPT), str(target), str(out), cwd=parent)
            self.assertEqual(again.returncode, 2)
            self.assertIn("output path already exists", again.stderr)

    def test_usage_errors_exit_2(self) -> None:
        self.assertEqual(run("sh", str(SCRIPT), cwd=ROOT).returncode, 2)


if __name__ == "__main__":
    unittest.main()
