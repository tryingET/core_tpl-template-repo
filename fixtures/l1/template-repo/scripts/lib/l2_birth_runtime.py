"""Explicit pinned runner inputs shared by owner rendering and child execution."""
import os
import shutil
from pathlib import Path
from typing import NamedTuple

SYSTEM_PATH = "/usr/local/bin:/usr/bin:/bin"
RUNTIME = "/run/l2-pinned-runner"
# Only system interpreters with dependencies in the existing read-only runtime.
INTERPRETERS = {b"#!" + path.encode() for path in
                ("/bin/sh", "/bin/bash", "/usr/bin/sh", "/usr/bin/bash",
                 "/usr/bin/python3", "/usr/bin/python",
                 "/usr/bin/env sh", "/usr/bin/env bash",
                 "/usr/bin/env python3", "/usr/bin/env python")}


class Runner(NamedTuple):
    program: str
    path: str
    bindings: list[str]


def executable(path: Path) -> tuple[Path, bool]:
    try:
        path = path.resolve(strict=True)
        if not path.is_file() or not os.access(path, os.X_OK):
            raise ValueError("pinned Copier runner is not an executable regular file")
        with path.open("rb") as file:
            header = file.read(256)
        native = header.startswith(b"\x7fELF")
        if not native and (not header or header.splitlines()[0].strip() not in INTERPRETERS):
            raise ValueError("pinned Copier runner requires an unsupported interpreter/runtime")
        return path, native
    except OSError as error:
        raise ValueError(f"pinned Copier runner unavailable: {path}") from error


def runner(scratch: Path, name: str | None = None) -> Runner:
    # Discover only the explicitly named caller-PATH runner, never an unrelated
    # system binary for preflight followed by a different executable for copy.
    names = (name,) if name is not None else ("uvx", "uv")
    if any(item not in ("uvx", "uv") for item in names):
        raise ValueError("pinned Copier runner must be uvx/uv")
    found = next(((item, path) for item in names if (path := shutil.which(item))), None)
    if found is None:
        raise ValueError("pinned Copier runner unavailable on caller PATH")
    name, located = found
    program, native = executable(Path(located))
    # Preserve read-only access at the original pathname too if it overlaps a
    # writable scratch/child mount; the private alias must not hide that hole.
    bindings = ["--dir", RUNTIME, "--ro-bind", str(program), str(program),
                "--ro-bind", str(program), f"{RUNTIME}/{name}"]
    if name == "uvx" and native:
        # Native uvx delegates to its adjacent uv, not any uv elsewhere on PATH.
        sibling, sibling_native = executable(program.with_name("uv"))
        if not sibling_native:
            raise ValueError("native uvx requires an adjacent native uv executable")
        bindings += ["--ro-bind", str(sibling), str(sibling),
                     "--ro-bind", str(sibling), f"{RUNTIME}/uv"]
    elif name == "uv":
        # Pinned historical L0 wrappers prefer uvx. Translate that interface to
        # this very uv binary, so a system uvx cannot silently take precedence.
        shim = scratch / "uvx-dispatch.sh"
        shim.write_text(f'#!/bin/sh\nexec {RUNTIME}/uv tool run "$@"\n')
        shim.chmod(0o755)
        bindings += ["--ro-bind", str(shim), str(shim),
                     "--ro-bind", str(shim), f"{RUNTIME}/uvx"]
    return Runner(f"{RUNTIME}/{name}", f"{RUNTIME}:{SYSTEM_PATH}", bindings)


def system_bindings() -> list[str]:
    bindings = []
    for path in ("/usr", "/bin", "/sbin", "/lib", "/lib64", "/etc"):
        if Path(path).exists():
            bindings += ["--ro-bind", path, path]
    resolver = Path("/etc/resolv.conf").resolve(strict=True)
    if not resolver.is_relative_to("/etc"):
        bindings += ["--ro-bind", str(resolver), str(resolver)]
    return bindings
