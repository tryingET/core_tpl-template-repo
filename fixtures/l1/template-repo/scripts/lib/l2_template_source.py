#!/usr/bin/env python3
"""Source-owned L2 birth staging and closed lineage; never use company copies."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import stat
import subprocess
import sys
from pathlib import Path

import yaml

TEMPLATES = {"tpl-project-repo", "tpl-agent-repo", "tpl-org-repo", "tpl-monorepo", "tpl-package"}
_active: subprocess.Popen | None = None


def checked_path(path: Path, *, missing: bool = False) -> Path:
    path = Path(os.path.abspath(path))
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            if missing:
                continue
            raise ValueError(f"missing source/provenance path: {current}")
        if stat.S_ISLNK(mode):
            raise ValueError(f"symlinked source/provenance path: {current}")
    return path


def mapping(path: Path) -> dict:
    path = checked_path(path)
    if not path.is_file():
        raise ValueError(f"provenance must be a regular file: {path}")
    value = yaml.safe_load(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"provenance must be a mapping: {path}")
    return value


def environment() -> dict[str, str]:
    env = {key: os.environ[key] for key in ("PATH", "HOME", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR", "TZ")
           if key in os.environ}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null",
               GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1", PYTHONDONTWRITEBYTECODE="1")
    return env


def stop_child(signum: int, _frame=None) -> None:
    if _active is not None:
        try:
            os.killpg(_active.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        _active.wait()
    raise SystemExit(128 + signum)


def run(argv: list[str], *, env: dict | None = None, umask: int = -1) -> str:
    global _active
    _active = subprocess.Popen(argv, env=env or environment(), stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True, umask=umask)
    try:
        try:
            out, err = _active.communicate(timeout=3600)
        except subprocess.TimeoutExpired:
            os.killpg(_active.pid, signal.SIGKILL)
            _active.communicate()
            raise ValueError("pinned template command timed out; process group killed") from None
        if _active.returncode:
            raise ValueError(f"pinned template command failed ({_active.returncode}): {err[-8192:].decode(errors='replace')}")
        return out.decode()
    finally:
        _active = None


def git(root: Path, *args: str) -> str:
    return run(["git", "-C", str(root), *args]).strip()


def verify_source(root: Path, pin: str) -> None:
    root = checked_path(root)
    meta = checked_path(root / ".git")
    if meta.is_file():
        text = meta.read_text().strip()
        if not text.startswith("gitdir: ") or "\n" in text:
            raise ValueError("invalid L0 worktree git metadata")
        meta = checked_path(root / text[8:])
    common_file = checked_path(meta / "commondir", missing=True)
    common = checked_path(meta / common_file.read_text().strip()) if common_file.exists() else meta
    if not meta.is_dir() or not common.is_dir():
        raise ValueError("L0 Git metadata must name owned directories")
    for name in ("config", "HEAD", "packed-refs", "shallow"):
        file = common / name
        if file.exists() or file.is_symlink():
            if not checked_path(file).is_file():
                raise ValueError(f"non-regular L0 Git metadata: {file}")
    for name in ("objects", "refs", "info"):
        directory = common / name
        if directory.exists():
            checked_path(directory)
            for path in directory.rglob("*"):
                checked_path(path)
                if not path.is_dir() and not path.is_file():
                    raise ValueError(f"non-regular L0 Git metadata: {path}")
    for name in ("objects/info/alternates", "info/grafts"):
        file = common / name
        if file.exists() and file.read_text().strip():
            raise ValueError(f"redirected L0 object/history authority: {name}")
    if Path(git(root, "rev-parse", "--show-toplevel")) != root:
        raise ValueError("L0 source root is not a Git worktree root")
    if Path(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")) != common:
        raise ValueError("L0 source common-dir does not match owned metadata")
    if f"worktree {root}\n" not in git(root, "worktree", "list", "--porcelain") + "\n":
        raise ValueError("unregistered L0 source worktree")
    if git(root, "cat-file", "-t", pin) != "commit":
        raise ValueError("company pin is not an available L0 commit")
    if git(root, "cat-file", "-t", f"{pin}:copier-template/copier") != "tree":
        raise ValueError("pinned L0 template catalog is missing")


def arguments(args: list[str]) -> tuple[str, dict, list[str], bool]:
    """Identify answers/data inputs without shell evaluation or swallowing values."""
    answers = ".copier-answers.yml"
    data, cli, files, no_effect = {}, {}, [], False
    i = 0
    while i < len(args):
        arg = args[i]
        value = None
        if arg in ("-a", "--answers-file", "--data-file", "-d", "--data", "-r", "--vcs-ref", "-s", "--skip", "-x", "--exclude"):
            i += 1
            if i == len(args):
                raise ValueError(f"{arg} requires a value")
            value = args[i]
        elif arg.startswith("--answers-file="):
            arg, value = "-a", arg.split("=", 1)[1]
        elif arg.startswith("-a"):
            arg, value = "-a", arg[2:]
        elif arg.startswith("--data-file="):
            arg, value = "--data-file", arg.split("=", 1)[1]
        elif arg.startswith("--data="):
            arg, value = "-d", arg.split("=", 1)[1]
        elif arg.startswith("-d"):
            arg, value = "-d", arg[2:]
        if arg in ("-a", "--answers-file"):
            answers = value or ""
        elif arg == "--data-file":
            file = checked_path(Path(value or ""))
            files.append(str(file)); data.update(mapping(file))
        elif arg in ("-d", "--data"):
            key, sep, val = (value or "").partition("=")
            if not key or not sep:
                raise ValueError("Copier data requires key=value")
            cli[key] = val
        elif arg in ("-h", "--help", "--version", "--pretend"):
            no_effect = True
        i += 1
    path = Path(answers)
    if not answers or path.is_absolute() or any(part in (".", "..") for part in answers.split("/")) or not all(answers.split("/")):
        raise ValueError("answers path must be normalized and repo-relative")
    return answers, {**data, **cli}, files, no_effect


def read_regular(path: Path) -> bytes:
    path = checked_path(path)
    if not path.is_file():
        raise ValueError(f"non-regular provenance artifact: {path}")
    return path.read_bytes()


def parent_snapshot(company: Path) -> tuple[dict, dict, str, Path]:
    seal_path = checked_path(company / "contracts/provenance-seal.yml")
    seal_bytes = read_regular(seal_path)
    seal = yaml.safe_load(seal_bytes)
    if not isinstance(seal, dict) or not isinstance(seal.get("render"), dict):
        raise ValueError("invalid company provenance seal")
    relative = seal["render"].get("answers_file", ".copier-answers.yml")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or any(p in ("", ".", "..") for p in relative.split("/")):
        raise ValueError("parent answers locator must be normalized and repo-relative")
    path = checked_path(company / relative)
    parent_bytes = read_regular(path)
    parent = yaml.safe_load(parent_bytes)
    if not isinstance(parent, dict):
        raise ValueError("parent answers must be a mapping")
    digest = hashlib.sha256()
    for value in (relative.encode(), parent_bytes, seal_bytes):
        digest.update(len(value).to_bytes(8, "little")); digest.update(value)
    if (company / ".git").exists():
        digest.update(git(company, "ls-files", "--stage", "--", "ontology").encode())
    return parent, seal, digest.hexdigest(), path


def inputs(company: Path) -> str:
    return parent_snapshot(company)[2]


def destination_guard(destination: Path, company: Path, source: Path) -> Path:
    destination = checked_path(destination, missing=True)
    if destination.is_relative_to(source) or source.is_relative_to(destination) or company.is_relative_to(destination):
        raise ValueError("destination intersects canonical company/L0 authority")
    reserved = {"contracts", "copier", "copier-overlay", "scripts", "docs", "diary", "governance", "policy", "ontology", "src", "tests", "tips", "metrics", "examples", "external"}
    if destination.is_relative_to(company):
        first = destination.relative_to(company).parts[0]
        if first in reserved or first.startswith("."):
            raise ValueError("destination is a protected company control surface")
    if destination.exists() and not destination.is_dir():
        raise ValueError("child destination must be a directory")
    return destination


def child_snapshot(destination: Path, answers: str) -> dict:
    destination = checked_path(destination, missing=True)
    identity = [destination.stat().st_dev, destination.stat().st_ino] if destination.exists() else None
    path = checked_path(destination / answers, missing=True)
    raw = read_regular(path) if path.exists() else None
    child = yaml.safe_load(raw) if raw is not None else {}
    if not isinstance(child, dict):
        raise ValueError("existing child answers must be a mapping")
    return {"identity": identity, "answers_sha256": hashlib.sha256(raw).hexdigest() if raw is not None else None, "child": child}


def check_before_copy(meta: dict, destination: Path) -> None:
    destination_guard(destination, Path(meta["company_root"]), Path(meta["source_root"]))
    if inputs(Path(meta["company_root"])) != meta["inputs_sha256"]:
        raise ValueError("company inputs changed before child rendering")
    if child_snapshot(destination, meta["answers"]) != meta["destination_snapshot"]:
        raise ValueError("destination/lineage changed before child rendering")


def prepare(company: Path, template: str, destination: Path, scratch: Path, args: list[str]) -> None:
    company, scratch = checked_path(company), checked_path(scratch)
    if template not in TEMPLATES or scratch.stat().st_uid != os.getuid() or stat.S_IMODE(scratch.stat().st_mode) != 0o700 or list(scratch.iterdir()):
        raise ValueError("invalid template or non-private/nonempty birth scratch")
    parent, seal, before, _ = parent_snapshot(company)
    slug, repo_slug, pin = parent.get("company_slug"), parent.get("repo_slug"), parent.get("l0_source_sha")
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", slug) or not isinstance(repo_slug, str):
        raise ValueError("company identity is missing or invalid")
    if not isinstance(pin, str) or not re.fullmatch(r"[0-9a-f]{40}", pin):
        raise ValueError("company L0 pin must be a full lowercase commit")
    if seal.get("schema") != "ai-society.template-provenance.v1" or seal.get("template", {}).get("source_repository") != "core/tpl-template-repo" or seal.get("template", {}).get("source_sha") != pin or seal.get("render", {}).get("layer") != "L1" or seal.get("render", {}).get("repo_slug") != repo_slug:
        raise ValueError("company answer/seal identity or pins disagree")
    answers, data, data_files, no_effect = arguments(args)
    if data.get("company_slug", slug) != slug:
        raise ValueError("child company override contradicts source lineage")
    source = checked_path(Path(os.environ.get("L0_TEMPLATE_ROOT", str(company.parent / "core/tpl-template-repo"))))
    if scratch.is_relative_to(company) or scratch.is_relative_to(source):
        raise ValueError("birth scratch must not be inside canonical company/L0")
    verify_source(source, pin)
    destination = destination_guard(destination, company, source)
    destination_snapshot = child_snapshot(destination, answers)
    # A rerun is not a new birth: preserve an already recorded immutable pin.
    child = destination_snapshot["child"]
    if "_template_lineage" in child:
        stored = child["_template_lineage"]
        if not isinstance(stored, dict) or set(stored) != {"company", "template", "l0_commit"} or stored.get("company") != slug or stored.get("template") != template or not isinstance(stored.get("l0_commit"), str) or not re.fullmatch(r"[0-9a-f]{40}", stored["l0_commit"]):
            raise ValueError("existing child lineage is malformed or contradicts this company/template")
        git(source, "merge-base", "--is-ancestor", stored["l0_commit"], pin)
        pin = stored["l0_commit"]
    if inputs(company) != before:
        raise ValueError("company inputs changed during source interpretation")
    frozen_parent = scratch / "parent-answers.yml"
    frozen_parent.write_text(yaml.safe_dump(parent))
    # Older pinned renderers read the default locator. Give them the same sealed
    # snapshot in a private input view, never a misleading live default file.
    render_input = scratch / "company-input"
    render_input.mkdir()
    (render_input / ".copier-answers.yml").write_bytes(frozen_parent.read_bytes())
    clone, render = scratch / "l0", scratch / "render"
    # Git stores executable bits, not caller umask. Materialize its canonical
    # 0644/0755 template modes even under a private runner's 077 umask. The outer
    # scratch remains 0700; only these isolated Git subprocesses get 022.
    run(["git", "clone", "--quiet", "--no-local", "--no-checkout", str(source), str(clone)], umask=0o022)
    run(["git", "-C", str(clone), "-c", "core.hooksPath=/dev/null", "checkout", "--quiet", "--detach", pin], umask=0o022)
    if git(clone, "rev-parse", "HEAD") != pin or git(clone, "status", "--porcelain"):
        raise ValueError("birth render clone is not clean at the exact pin")
    renderer = checked_path(clone / "scripts/render-l1.sh")
    for name in ("tmp", "home", "uv-cache"):
        (scratch / name).mkdir()
    env = environment()
    env.update(HOME=str(scratch / "home"), PATH="/usr/local/bin:/usr/bin:/bin",
               TMPDIR=str(scratch / "tmp"), TMP=str(scratch / "tmp"), TEMP=str(scratch / "tmp"),
               UV_CACHE_DIR=str(scratch / "uv-cache"), XDG_CACHE_HOME=str(scratch / "home/.cache"),
               COPIER_VERSION="9.11.1", COPIER_VCS_REF="HEAD")
    # No unpinned fallback inside the owner render.
    if not any(subprocess.run([name, "--version"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
               for name in ("uvx", "uv") if __import__("shutil").which(name, path=env["PATH"])):
        raise ValueError("pinned L0 rendering requires system uvx/uv")
    cmd = ["bwrap", "--die-with-parent", "--unshare-pid", "--unshare-ipc", "--unshare-uts"]
    for path in ("/usr", "/bin", "/sbin", "/lib", "/lib64", "/etc"):
        if Path(path).exists():
            cmd += ["--ro-bind", path, path]
    resolver = Path("/etc/resolv.conf").resolve(strict=True)
    if not resolver.is_relative_to("/etc"):
        cmd += ["--ro-bind", str(resolver), str(resolver)]
    cmd += ["--ro-bind", str(company), str(company), "--bind", str(scratch), str(scratch),
            "--ro-bind", str(render_input), str(render_input)]
    # Preserve source-owned ontology index topology without copying company
    # templates. The pinned render-only contract consumes answers and Git index.
    if (company / ".git").exists():
        metadata = checked_path(company / ".git")
        if metadata.is_dir():
            (render_input / ".git").mkdir()
        else:
            (render_input / ".git").touch()
        cmd += ["--ro-bind", str(metadata), str(render_input / ".git")]
    cmd += ["--dev", "/dev", "--proc", "/proc", "--chdir", str(clone),
            "sh", str(renderer), str(render_input), str(render), repo_slug]
    # The renderer also makes its own Git clone through Copier. Keep source
    # template modes canonical inside the same 0700 private sandbox.
    run(cmd, env=env, umask=0o022)
    if inputs(company) != before:
        raise ValueError("company inputs changed during pinned render")
    rendered_seal = mapping(render / "contracts/provenance-seal.yml")
    if rendered_seal["template"]["source_sha"] != pin or rendered_seal["render"]["repo_slug"] != repo_slug:
        raise ValueError("rendered provenance does not bind the requested company pin")
    template_path = checked_path(render / "copier" / template)
    for file in template_path.rglob("*"):
        checked_path(file)
        if not file.is_dir() and not file.is_file():
            raise ValueError("non-regular rendered template entry")
    if not (template_path / "copier.yml").is_file():
        raise ValueError("pinned template is unavailable after company render")
    (scratch / "lineage.json").write_text(json.dumps({"company": slug, "template": template,
        "l0_commit": pin, "template_path": str(template_path), "answers": answers,
        "company_root": str(company), "inputs_sha256": before, "source_root": str(source),
        "destination_snapshot": destination_snapshot, "data_files": data_files,
        "no_effect_requested": no_effect, "scratch": str(scratch)}, sort_keys=True) + "\n")


def record(scratch: Path, destination: Path) -> None:
    meta = json.loads((scratch / "lineage.json").read_text())
    if inputs(Path(meta["company_root"])) != meta["inputs_sha256"]:
        raise ValueError("company inputs changed during child rendering")
    if meta["no_effect_requested"]:
        return
    destination_guard(destination, Path(meta["company_root"]), Path(meta["source_root"]))
    if meta.get("execution_root_identity") is not None and [destination.stat().st_dev, destination.stat().st_ino] != meta["execution_root_identity"]:
        raise ValueError("child root identity changed before lineage recording")
    if not meta.get("copy_completed"):
        raise ValueError("Copier did not positively complete from the pinned private source")
    answers = checked_path(destination / meta["answers"])
    child = mapping(answers)
    # Monorepo/package answers intentionally omit Copier's special fields.
    if "_src_path" in child and child["_src_path"] != meta["template_path"]:
        raise ValueError("Copier output source contradicts the private pinned template")
    expected = {key: meta[key] for key in ("company", "template", "l0_commit")}
    if "_template_lineage" in child and child["_template_lineage"] != expected:
        raise ValueError("child lineage changed during rendering")
    if child.get("company_slug") != meta["company"]:
        raise ValueError("child company contradicts pinned source lineage")
    child["_template_lineage"] = {key: meta[key] for key in ("company", "template", "l0_commit")}
    # Stable legacy locator remains interpretable after scratch and copies vanish.
    child["_src_path"] = f"~/ai-society/{meta['company']}/copier/{meta['template']}"
    output = answers.with_name(answers.name + ".lineage-new")
    with output.open("x") as handle:
        yaml.safe_dump(child, handle, sort_keys=True)
    output.chmod(stat.S_IMODE(answers.stat().st_mode))
    output.replace(answers)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("prepare", "template", "record", "parent", "execute"))
    parser.add_argument("scratch", type=Path)
    parser.add_argument("values", nargs=argparse.REMAINDER)
    opt = parser.parse_args()
    if opt.operation == "prepare":
        company, template, destination, *args = opt.values
        prepare(Path(company), template, Path(destination), opt.scratch, args)
    elif opt.operation == "template":
        print(json.loads((opt.scratch / "lineage.json").read_text())["template_path"])
    elif opt.operation == "parent":
        print(parent_snapshot(opt.scratch)[3])
    elif opt.operation == "execute":
        from l2_birth_execution import execute
        meta = json.loads((opt.scratch / "lineage.json").read_text())
        destination, *argv = opt.values
        execute(meta, Path(destination), argv, run, environment, check_before_copy, destination_guard)
    else:
        record(opt.scratch, Path(opt.values[0]))


if __name__ == "__main__":
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, stop_child)
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, yaml.YAMLError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
