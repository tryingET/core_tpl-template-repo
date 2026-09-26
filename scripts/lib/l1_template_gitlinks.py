#!/usr/bin/env python3
"""Opaque gitlink handling for L1 contract refresh.

A target's gitlinks (mode 160000) are never read, written or deleted by a refresh.
The only gitlink the L0 map knows by name is the company-owned ontology: an L1 may
keep ``ontology/`` in-tree (template-owned ``ontology/**``) or, after a receipted
ownership transition, as a company-owned submodule rendered with
``l1_ontology_layout=gitlink`` (agent-owned exact ``ontology`` and ``.gitmodules``).
The gitlink layout is admitted only when the active, provenance-validated map
already carries that company claim; the ordinary refresh never grants it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from l1_template_receipts import git_run

OWNER_GITLINKS = ("ontology",)
GITLINK_COMPANION = ".gitmodules"


def is_repository(repo: Path) -> bool:
    probe = git_run(repo, "rev-parse", "--show-toplevel")
    return probe.returncode == 0 and Path(probe.stdout.strip()).resolve() == repo.resolve()


def index_entries(repo: Path) -> dict[str, tuple[str, str]]:
    """Return ``{path: (mode, oid)}`` for stage-0 index entries; conflicts refuse."""
    probe = git_run(repo, "ls-files", "--stage", "-z")
    if probe.returncode != 0:
        raise ValueError("refresh target must be a Git repository")
    entries: dict[str, tuple[str, str]] = {}
    for record in probe.stdout.split("\0"):
        if not record:
            continue
        meta, _, path = record.partition("\t")
        fields = meta.split()
        if len(fields) != 3 or not path:
            raise ValueError("unsupported Git index record")
        mode, oid, stage = fields
        if stage != "0" or path in entries:
            raise ValueError(f"conflicted Git index entry: {path}")
        entries[path] = (mode, oid)
    return entries


def gitlinks(entries: dict[str, tuple[str, str]]) -> set[str]:
    return {path for path, (mode, _) in entries.items() if mode == "160000"}


def inside(path: str, root: str) -> bool:
    return path == root or path.startswith(root + "/")


def check(
    repo: Path,
    entries: dict[str, tuple[str, str]],
    current_map: dict[str, list[str]],
    next_map: dict[str, list[str]],
    rendered_template_paths: list[str],
    classify: Callable[[str, dict[str, list[str]]], str | None],
) -> list[str]:
    """Fail closed on any gitlink/template overlap; return preserved owner gitlinks."""
    links = gitlinks(entries)
    for link in sorted(links):
        if classify(link, next_map) == "template":
            raise ValueError(f"target gitlink {link} is template-owned by the incoming map; gitlinks are opaque")
    for path in rendered_template_paths:
        for link in links:
            if inside(path, link):
                raise ValueError(f"rendered template path {path} lies inside target gitlink {link}")
    preserved = []
    for name in OWNER_GITLINKS:
        claimed = name in next_map["agent"]
        if name in links and not claimed:
            raise ValueError(
                f"target keeps {name} as an owner gitlink but the render is not l1_ontology_layout=gitlink"
            )
        if not claimed:
            continue
        if name not in links:
            raise ValueError(f"l1_ontology_layout=gitlink requires a committed gitlink at {name}")
        for pattern in (name, GITLINK_COMPANION):
            if pattern not in current_map["agent"] or pattern not in next_map["agent"]:
                raise ValueError(
                    f"owner gitlink {name} requires a receipted ownership transition "
                    f"that makes {pattern} company-owned"
                )
        if entries.get(GITLINK_COMPANION, ("",))[0] not in {"100644", "100755"}:
            raise ValueError(f"owner gitlink {name} requires a tracked {GITLINK_COMPANION}")
        declared = git_run(
            repo, "config", "--blob", f":{GITLINK_COMPANION}", "--get-regexp", r"^submodule\..*\.path$"
        )
        paths = [line.split(" ", 1)[1] for line in declared.stdout.splitlines() if " " in line]
        if declared.returncode != 0 or paths.count(name) != 1:
            raise ValueError(f"{GITLINK_COMPANION} must declare exactly one submodule at {name}")
        preserved.append(name)
    return preserved
