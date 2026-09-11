#!/usr/bin/env python3
"""Fixed, fail-closed retirement of the five original-base L1 answer templates.

Not a general deletion/migration engine. Fingerprints are from L0
84d6c81e0b1146940ded9bf1bf6ede222acf67f8, never learned from a destination.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import sys
from pathlib import Path

from l1_template_receipts import (
    ADOPTION_PATH, MAP_PATH, STATE_PATH, STATE_SCHEMA, ensure_clean_git_target,
    ensure_safe_destinations, git_run, validate_established_provenance,
)

COMMON = "b900dec6d3a387588b29433dc78d5c01224e680ac8ab2bb123fc9a930b5e2050"
APPROVED = {
    "tpl-agent-repo": COMMON,
    "tpl-org-repo": COMMON,
    "tpl-project-repo": COMMON,
    "tpl-monorepo": "781390e4ec6052dd8a2360d32b7a637c47dedde81f3841249b6a297da165f450",
    "tpl-package": "27dba22ed419dc971cdc8f8ccc714336476108f3b951a5e3c15f87a370bd6d76",
}
OLD = ".copier-answers.yml.j2"
NEW = "{{ '.' ~ _copier_conf.sep ~ _copier_conf.answers_file }}.j2"
SOURCE = "{% raw %}" + NEW[:-3] + "{% endraw %}.j2"


def exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def record(root: Path, relative: str, digest: str) -> dict:
    ensure_safe_destinations(root, [relative])
    path = root / relative
    for ancestor in path.relative_to(root).parents:
        if str(ancestor) != "." and exists(root / ancestor / ".git"):
            raise ValueError(f"nested repository at {ancestor}")
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) not in (0o600, 0o640, 0o644) or info.st_nlink != 1:
        raise ValueError(f"unsafe answer-template type/mode/links: {relative}")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != digest:
        raise ValueError(f"modified or unapproved answer template: {relative}")
    return {"sha256": actual, "mode": stat.S_IMODE(info.st_mode), "device": info.st_dev, "inode": info.st_ino}


def tracked_original(repo: Path, path: str, digest: str) -> None:
    entry = git_run(repo, "ls-files", "--stage", "--", path)
    lines = entry.stdout.splitlines()
    if entry.returncode or len(lines) != 1 or not lines[0].startswith("100644 ") or " 0\t" not in lines[0]:
        raise ValueError(f"untracked or ambiguous obsolete answer template: {path}")
    committed = git_run(repo, "show", f"HEAD:{path}")
    if committed.returncode or hashlib.sha256(committed.stdout.encode()).hexdigest() != digest:
        raise ValueError(f"unattested obsolete answer template: {path}")


def plan(repo: Path, incoming: Path, current_map: dict, next_map: dict,
         classify, adoption: dict | None = None, source: bool = False) -> dict:
    if repo.is_symlink() or incoming.is_symlink():
        raise ValueError("symlinked retirement root")
    entries = {}
    for name, digest in APPROVED.items():
        old, new = f"copier/{name}/{OLD}", f"copier/{name}/{NEW}"
        if not exists(repo / old):
            continue
        # Check every candidate before any caller is allowed to mutate anything.
        for path in (old, new):
            if classify(path, current_map) != "template" or classify(path, next_map) != "template":
                raise ValueError(f"retirement requires prior and incoming template ownership: {path}")
        previous = record(repo, old, digest)
        if not os.access((repo / old).parent, os.W_OK | os.X_OK):
            raise ValueError(f"unwritable obsolete-template parent: {old}")
        tracked_original(repo, old, digest)
        if adoption is not None:
            attested = adoption["existing_template_paths"].get(old)
            if attested != {"sha256": digest, "mode": previous["mode"]}:
                raise ValueError(f"unattested obsolete answer template: {old}")
        successor = f"copier/{name}/{SOURCE}" if source else new
        record(incoming, successor, digest)
        if exists(repo / new):
            record(repo, new, digest)
        entries[old] = {"new": new, "record": previous}
    return entries


def revalidate(repo: Path, entries: dict, successors: bool = False) -> None:
    present = {f"copier/{name}/{OLD}" for name in APPROVED if exists(repo / f"copier/{name}/{OLD}")}
    if present != set(entries):
        raise ValueError("stale answer-template retirement inventory")
    approved = {f"copier/{name}/{OLD}": (f"copier/{name}/{NEW}", digest)
                for name, digest in APPROVED.items()}
    for old, entry in entries.items():
        new, digest = approved[old]
        if entry["new"] != new or entry["record"]["sha256"] != digest:
            raise ValueError("retirement plan differs from fixed approved transition")
        if record(repo, old, digest) != entry["record"]:
            raise ValueError(f"stale answer-template preflight: {old}")
        tracked_original(repo, old, digest)
        if not os.access((repo / old).parent, os.W_OK | os.X_OK):
            raise ValueError(f"unwritable obsolete-template parent: {old}")
        if successors:
            record(repo, entry["new"], digest)


def retire(repo: Path, entries: dict) -> None:
    revalidate(repo, entries, successors=True)
    for old in entries:
        (repo / old).unlink()


def prepare_wrapper(repo: Path, source: Path) -> dict:
    from l1_template_ownership import load_map, owner

    if not repo.exists():
        return {}
    ensure_safe_destinations(repo, [MAP_PATH.as_posix(), STATE_PATH.as_posix(), ADOPTION_PATH.as_posix()])
    old_present = any(exists(repo / f"copier/{name}/{OLD}") for name in APPROVED)
    if not (repo / STATE_PATH).is_file():
        if old_present:
            raise ValueError("obsolete templates require ownership adoption; use owner refresh")
        return {}
    state = json.loads((repo / STATE_PATH).read_text())
    if (state.get("schema"), state.get("kind"), state.get("state"), state.get("origin")) != (
        STATE_SCHEMA, "l1_contract_refresh_state", "established", "copier-birth"
    ) or exists(repo / ADOPTION_PATH):
        raise ValueError("copy wrapper requires copier-birth v1 state; use owner refresh/transition (v2 unsupported)")
    validate_established_provenance(repo, state, allow_uncommitted_birth_plan=not old_present)
    entries = plan(repo, source, load_map(repo), load_map(source), owner, source=True)
    if entries:
        ensure_clean_git_target(repo)
    return entries


def company_answer(path: Path) -> str:
    # Use the same pinned runtime as rendering if the host lacks YAML support.
    try:
        import yaml
    except ImportError:
        version = os.environ.get("COPIER_VERSION", "9.11.1")
        for command in (["uvx", "--from", f"copier=={version}", "python"],
                        ["uv", "tool", "run", "--from", f"copier=={version}", "python"]):
            if shutil.which(command[0]):
                os.execvp(command[0], [*command, "-B", __file__, "answer", str(path)])
        raise ValueError("company answer parsing requires pinned Copier runtime or PyYAML")
    if not path.exists():
        return ""
    if path.is_symlink() or not path.is_file():
        raise ValueError("unsafe L1 answers file")
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid L1 answers YAML: {exc}") from exc
    if data is None:
        return ""
    if not isinstance(data, dict):
        raise ValueError("L1 answers must be a mapping")
    value = data.get("company_ontology_ref")
    if value is None:
        return ""
    if not isinstance(value, str) or '"' in value or "\\" in value or (value and not value.isprintable()):
        raise ValueError("company_ontology_ref must be a printable string without double quotes or backslashes")
    return value


def copy_pretend(arguments: list[str]) -> bool:
    """Accept separate switches/attached values; reject boolean short clusters.

    Copier/Plumbum consumes option values even when they resemble switches.
    Do not inspect those values for `n`, and do not rewrite forwarded argv.
    """
    valued_long = {"--answers-file", "--data", "--data-file", "--vcs-ref",
                   "--skip", "--exclude", "--completions"}
    options = iter(arguments)
    pretend = False
    for arg in options:
        if arg == "--":
            break
        if arg.startswith("--"):
            name, equal, value = arg.partition("=")
            if name in valued_long:
                if not equal:
                    value = next(options, "")
                    if value == "=":
                        next(options, None)
                elif not value:
                    next(options, None)  # Plumbum: --name= VALUE
                continue
            if arg == "--pretend":
                pretend = True
        elif arg.startswith("-") and len(arg) >= 2:
            if arg[1] in "adrsx":
                if len(arg) == 2:
                    next(options, None)
                continue
            if len(arg) > 2:
                raise ValueError("grouped short options are unsupported; use separate switches (for example -f -n)")
            if arg == "-n":
                pretend = True
    return pretend


def run_copy_cli(completion: Path, arguments: list[str]) -> None:
    """Copier 9.11.1 adapter: observe execution, never infer it from CLI exit 0.

    Keep Plumbum's parser, informational exits, warnings and error handling intact.
    Its copy main calls _cli.Worker.run_copy within a context manager. Observe that
    return, then require the entire CLI (including worker cleanup/output flush) to
    exit successfully. A pretend worker never earns the invocation-local signal.
    Private API use is deliberately version-locked; review before changing the pin.
    """
    from importlib.metadata import version

    completion.write_text("")
    if version("copier") != "9.11.1":
        raise ValueError("copy completion adapter requires Copier 9.11.1")
    from copier import _cli

    original = _cli.Worker
    completed = False

    class ObservedWorker(original):
        def run_copy(self) -> None:
            nonlocal completed
            super().run_copy()
            completed = not self.pretend

    _cli.Worker = ObservedWorker
    try:
        try:
            _cli.CopierApp.run(["copier", *arguments])
        except SystemExit as exc:
            if exc.code == 0 and completed:
                completion.write_text("non-pretend-copy-completed\n")
            raise
    finally:
        _cli.Worker = original


def main() -> int:
    try:
        action, *args = sys.argv[1:]
        if action == "answer":
            sys.stdout.write(company_answer(Path(args[0])))
        elif action == "count":
            print(len(json.loads(Path(args[0]).read_text())["entries"]))
        elif action == "copy":
            run_copy_cli(Path(args[0]), args[1:])
        elif action == "prepare":
            repo, source, output = map(Path, args[:3])
            copy_pretend(args[3:])  # Syntax guard only; not proof that rendering ran.
            entries = prepare_wrapper(repo, source)
            if entries:
                # The incoming source map/filenames must be the selected revision.
                head = git_run(source.parent, "rev-parse", "HEAD").stdout.strip()
                options = iter(args[3:])
                for arg in options:
                    ref = None
                    if arg in ("-r", "--vcs-ref"):
                        ref = next(options, "")
                    elif arg.startswith("--vcs-ref="):
                        ref = arg.split("=", 1)[1]
                    elif arg.startswith("-r"):
                        ref = arg[2:]
                    elif arg in ("-a", "--answers-file", "-d", "--data", "--data-file", "-s", "--skip", "-x", "--exclude"):
                        next(options, "")
                    if ref is not None and ref not in ("HEAD", head):
                        raise ValueError("obsolete-template copy upgrade requires current L0 HEAD")
            control = {}
            if entries:
                control = {str(p): hashlib.sha256((repo / p).read_bytes()).hexdigest()
                           for p in (MAP_PATH, STATE_PATH)}
            payload = {"entries": entries, "control": control,
                       "incoming_map": hashlib.sha256((source / MAP_PATH).read_bytes()).hexdigest()}
            output.write_text(json.dumps(payload, sort_keys=True))
        elif action in ("check", "retire"):
            repo, saved = map(Path, args)
            payload = json.loads(saved.read_text())
            entries = payload["entries"]
            if entries:
                if action == "check":
                    ensure_clean_git_target(repo)
                    for path, digest in payload["control"].items():
                        if hashlib.sha256((repo / path).read_bytes()).hexdigest() != digest:
                            raise ValueError("stale retirement ownership controls")
                    revalidate(repo, entries)
                else:
                    if hashlib.sha256((repo / MAP_PATH).read_bytes()).hexdigest() != payload["incoming_map"]:
                        raise ValueError("rendered ownership map differs from preflight")
                    retire(repo, entries)
        else:
            raise ValueError("unknown answer-template upgrade action")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
