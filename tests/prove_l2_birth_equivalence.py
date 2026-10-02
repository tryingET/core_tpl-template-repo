"""Read-only company-copy comparison: preserve every non-provenance birth delta."""
import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ("tpl-project-repo", "tpl-agent-repo", "tpl-org-repo", "tpl-monorepo", "tpl-package")
PROVENANCE = {"_src_path", "_commit", "_template_lineage", "template_source_sha"}


def tree(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def run(argv, env):
    result = subprocess.run(argv, env=env, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"{argv}: {result.returncode}\n{result.stdout}\n{result.stderr}")


def compare(old, new):
    left, right = tree(old), tree(new)
    deltas = []
    for path in sorted(left.keys() | right.keys()):
        a, b = left.get(path), right.get(path)
        if path == ".copier-answers.yml" and a is not None and b is not None:
            a = yaml.safe_dump({k: v for k, v in yaml.safe_load(a).items() if k not in PROVENANCE}).encode()
            b = yaml.safe_dump({k: v for k, v in yaml.safe_load(b).items() if k not in PROVENANCE}).encode()
        if a != b:
            deltas.append({"path": path, "company_copy_base64": base64.b64encode(a).decode() if a is not None else None,
                           "pinned_birth_base64": base64.b64encode(b).decode() if b is not None else None})
    return deltas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    opts = parser.parse_args()
    parent_bytes = (opts.company / ".copier-answers.yml").read_bytes()
    parent = yaml.safe_load(parent_bytes)
    report = {"scope": "all five archetypes, copied holdingco configuration and actual on-disk catalog including ignored residue",
              "company": str(opts.company), "l0_commit": parent["l0_source_sha"],
              "company_answers_sha256": hashlib.sha256(parent_bytes).hexdigest(),
              "provenance_only_answer_keys": sorted(PROVENANCE),
              "limit": "isolated company copies have no original Git index; no other companies or existing-child migration proved",
              "archetypes": {}, "catalog_observations": {}}
    residue = opts.company / "copier/tpl-project-repo/ontology/manifest.yaml"
    report["catalog_observations"]["ignored_plain_ontology_manifest"] = {
        "present": residue.is_file(),
        "sha256": hashlib.sha256(residue.read_bytes()).hexdigest() if residue.is_file() else None,
        "base64": base64.b64encode(residue.read_bytes()).decode() if residue.is_file() else None,
        "interpretation": "copied without exclusion; Copier's templated manifest wins in the observed final birth"}
    report["catalog_observations"]["tracked_obsolete_project_files"] = subprocess.check_output(
        ["git", "-C", str(opts.company), "ls-files", "--", "copier/tpl-project-repo/.gitlab-ci.yml",
         "copier/tpl-project-repo/gitlab/ci/rocs.yml", "copier/tpl-project-repo/governance/work-items.cue",
         "copier/tpl-project-repo/governance/work-items.json"], text=True).splitlines()
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"), prefix="ak6351-equivalence-") as tmp:
        root = Path(tmp)
        old, new = root / "legacy-company", root / "pinned-company"
        for company in (old, new):
            (company / "contracts").mkdir(parents=True)
            (company / ".copier-answers.yml").write_bytes(parent_bytes)
            for name in ("provenance-seal.yml", "layer-contract.yml"):
                shutil.copy2(opts.company / "contracts" / name, company / "contracts" / name)
        shutil.copytree(opts.company / "scripts", old / "scripts")
        # Deliberately no ignore function: obsolete tracked and ignored files remain.
        shutil.copytree(opts.company / "copier", old / "copier")
        shutil.copytree(ROOT / "copier-template/scripts", new / "scripts")
        env = dict(os.environ, L0_TEMPLATE_ROOT=str(ROOT), PYTHONDONTWRITEBYTECODE="1",
                   DISABLE_PROJECT_OWNER_HANDLE_INFERENCE="1", COPIER_VCS_REF="HEAD")
        for template in TEMPLATES:
            destinations = [root / ("copy-" + template), root / ("pin-" + template)]
            identity = "package_name=equivalence-core" if template == "tpl-package" else "repo_slug=equivalence-test"
            args = ["--defaults", "--overwrite", "-d", identity, "-d", "template_source_sha=equivalence-source"]
            if template == "tpl-agent-repo":
                args += ["-d", "creation_task_id=AK-5105", "-d", "agent_role=fixture-agent-role"]
            for company, destination in zip((old, new), destinations):
                run(["sh", str(company / "scripts/new-repo-from-copier.sh"), template, str(destination), *args], env)
            deltas = compare(*destinations)
            report["archetypes"][template] = {"equivalent_except_provenance": not deltas, "deltas": deltas}
    report["acceptance_satisfied"] = all(v["equivalent_except_provenance"] for v in report["archetypes"].values())
    opts.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    for template, result in report["archetypes"].items():
        print(template, "equal" if result["equivalent_except_provenance"] else "NOT EQUAL", [v["path"] for v in result["deltas"]])
    print("acceptance_satisfied=", report["acceptance_satisfied"])


if __name__ == "__main__":
    main()
