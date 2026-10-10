"""Complete Git tree reconstruction and strict layout byte substitution."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from tests.test_l1_template_transitions import SCRATCH, TRANSITIONS, git, init
import l1_ontology_convergence as CONVERGENCE


class RetainedTreeTests(unittest.TestCase):
    def test_tree_identity_includes_nested_paths_modes_and_git_sort_order(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            repo = Path(raw)
            files = []
            for path, data, mode in (
                ("a.txt", b"file\n", "100644"),
                ("a/z", b"nested\n", "100755"),
                ("a-/x", b"other directory\n", "100644"),
                ("vocabulary/é.txt", b"\xff\x00\n", "100644"),
            ):
                dest = repo / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
                dest.chmod(0o755 if mode == "100755" else 0o644)
                files.append(dict(path="ontology/" + path, mode=mode,
                    oid=CONVERGENCE.object_oid("blob", data), content_sha256=CONVERGENCE.sha(data)))
            init(repo)
            files.sort(key=lambda entry: entry["path"])
            self.assertEqual(CONVERGENCE.retained_tree(files), git(repo, "rev-parse", "HEAD^{tree}"))
            changed = copy.deepcopy(files); changed[0]["mode"] = "100755"
            self.assertNotEqual(CONVERGENCE.retained_tree(changed), git(repo, "rev-parse", "HEAD^{tree}"))

    def test_paths_modes_oid_hash_order_and_unknown_keys_refuse(self):
        entry = dict(path="ontology/a", mode="100644", oid="a" * 40, content_sha256="b" * 64)
        invalid = [[], [entry, entry], [entry, dict(entry, path="ontology/a/b")],
                   [dict(entry, path="ontology/b"), entry]]
        for path in ("../outside", "ontology/../outside", "ontology/.git/object", "ontology//x", "ontology/x\ny", "ontology/x\\y", "ontology/./x"):
            invalid.append([dict(entry, path=path)])
        for key, value in (("mode", "120000"), ("mode", "160000"), ("oid", "A" * 40), ("oid", "a" * 39), ("content_sha256", "g" * 64), ("extra", True)):
            invalid.append([dict(entry, **{key: value})])
        for files in invalid:
            with self.subTest(files=files), self.assertRaises(ValueError):
                CONVERGENCE.retained_tree(files)

    def test_layout_update_is_exact_and_refuses_ambiguous_or_implicit_answers(self):
        old = b"_src_path: pinned\nl1_ontology_layout: gitlink\nflag: false\n"
        self.assertEqual(CONVERGENCE.answers_successor(old), old.replace(b": gitlink", b": tree"))
        for value in (
            b"flag: false\n", old + b"l1_ontology_layout: tree\n",
            old + b"'l1_ontology_layout': tree\n", old + b'"l1_ontology_layout": tree\n',
            old.replace(b": gitlink", b": tree"), old.replace(b": gitlink", b": 'gitlink'"),
            old.replace(b"l1_ontology_layout:", b"  l1_ontology_layout:"),
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                CONVERGENCE.answers_successor(value)


if __name__ == "__main__":
    unittest.main()
