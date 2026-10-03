"""Given/When/Then source-cache regression using the real gate subprocess boundary."""
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests import test_l1_template_company_ownership as company


class SourceCacheScenarioTests(unittest.TestCase):
    def test_given_clean_source_when_focused_child_imports_then_no_bytecode(self):
        """GIVEN clean template bytes; WHEN a focused child imports; THEN no cache."""
        with tempfile.TemporaryDirectory(dir=company.SCRATCH) as tmp:
            h = company.CompanyHarness(Path(tmp))
            source = h.parent / "clean-template-source/l1_ontology_ownership.py"
            source.parent.mkdir()
            shutil.copy2(company.ROOT / "copier-template/scripts/lib/l1_ontology_ownership.py", source)
            before = source.read_bytes()
            # SourceFileLoader is the real import mechanism that produced the
            # observed cache. Use an owned copy, never dirty the active source.
            probe = h.repo / "scripts/ci/bytecode-probe.sh"
            probe.write_text("#!/bin/sh\nset -eu\npython3 - <<'PY'\n"
                             "import importlib.util\n"
                             f"spec = importlib.util.spec_from_file_location('cache_probe', {str(source)!r})\n"
                             "spec.loader.exec_module(importlib.util.module_from_spec(spec))\n"
                             "PY\n")
            self.assertEqual(list(source.parent.glob("__pycache__")), [])
            with mock.patch.dict(os.environ):
                # Do not let the aggregate runner's global setting mask a
                # missing focused-subprocess binding (the original cause).
                os.environ.pop("PYTHONDONTWRITEBYTECODE", None)
                h.run_gate({"id": "ci-full", "command": "bash scripts/ci/bytecode-probe.sh"})
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(list(source.parent.glob("__pycache__")), [],
                             "focused gate subprocess contaminated clean template source")


if __name__ == "__main__":
    unittest.main()
