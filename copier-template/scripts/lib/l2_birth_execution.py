"""Bound final Copier execution to private scratch and the explicit child root."""
import os
import re
from pathlib import Path
from l2_birth_safety import directory, identity
from l2_birth_runtime import runner, system_bindings


def execute(meta: dict, destination: Path, argv: list[str], run, base_environment, check, guard) -> None:
    check(meta, destination)
    destination = guard(destination, Path(meta["company_root"]), Path(meta["source_root"]))
    if not argv or argv[0] not in ("uvx", "uv"):
        raise ValueError("pinned L2 birth requires uvx/uv; unpinned copier fallback is forbidden")
    prefix = ["uvx", "--from"] if argv[0] == "uvx" else ["uv", "tool", "run", "--from"]
    if len(argv) < len(prefix) + 2 or argv[:len(prefix)] != prefix or not re.fullmatch(r"copier==[0-9]+\.[0-9]+\.[0-9]+", argv[len(prefix)]) or argv[len(prefix)+1] != "copier":
        raise ValueError("invalid pinned Copier command prefix")
    # Copier runs from the child, but data files belong to the original caller.
    # Consume all value-taking options; option-like values are not new options.
    argv = list(argv)
    argv[-1] = str(destination)
    i = len(prefix) + 2
    while i < len(argv) - 2:
        arg = argv[i]
        if arg in ("-a", "--answers-file", "--data-file", "-d", "--data",
                   "-r", "--vcs-ref", "-s", "--skip", "-x", "--exclude"):
            i += 1
            if arg == "--data-file":
                argv[i] = os.path.abspath(argv[i])
        elif arg.startswith("--data-file="):
            argv[i] = "--data-file=" + os.path.abspath(arg.split("=", 1)[1])
        i += 1
    scratch = Path(meta["scratch"])
    runtime = runner(scratch, argv[0])
    readonly = bool(meta["no_effect_requested"])
    if readonly and not destination.exists():
        target = scratch / "no-effect-target"
        target.mkdir()
    else:
        destination = guard(destination, Path(meta["company_root"]), Path(meta["source_root"]))
        target = destination
    env = base_environment()
    env.update(HOME=str(scratch / "home"), PATH=runtime.path, TMPDIR=str(scratch / "tmp"),
               TMP=str(scratch / "tmp"), TEMP=str(scratch / "tmp"),
               UV_CACHE_DIR=str(scratch / "uv-cache"), XDG_CACHE_HOME=str(scratch / "home/.cache"))
    if "PYTHONWARNINGS" in os.environ:
        env["PYTHONWARNINGS"] = os.environ["PYTHONWARNINGS"]
    # Explicit runtime inputs, never ambient inheritance or a test-only escape.
    for key in filter(None, os.environ.get("L2_BIRTH_ENV_INHERIT", "").split(",")):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key) or key.startswith(("GIT_", "LD_", "PYTHON")) or key in env:
            raise ValueError(f"unsafe L2 birth environment input: {key}")
        if key not in os.environ:
            raise ValueError(f"missing L2 birth environment input: {key}")
        env[key] = os.environ[key]
    cmd = ["bwrap", "--die-with-parent", "--unshare-pid", "--unshare-ipc", "--unshare-uts"]
    cmd += system_bindings()
    cmd += ["--ro-bind", meta["company_root"], meta["company_root"]]
    cmd += ["--bind", str(scratch), str(scratch)]
    adapter = Path(__file__).with_name("l2_birth_completion.py").resolve(strict=True)
    completion = scratch / "copy-completed.txt"
    # These inputs stay read-only even when located inside scratch or the child.
    cmd += runtime.bindings
    for path in [adapter, *map(Path, meta["data_files"])]:
        cmd += ["--ro-bind", str(path), str(path)]
    cmd += ["--dev", "/dev", "--proc", "/proc", "--chdir", str(destination),
            runtime.program, *argv[1:len(prefix)+1], "python", "-B", str(adapter), str(completion), *argv[len(prefix)+2:]]
    expected = meta["destination_snapshot"]["identity"] if target == destination else None
    with directory(target, create=not readonly, expected=expected) as root_fd:
        meta["execution_root_identity"] = identity(root_fd)
        # Append the destination bind after scratch, before launching. bwrap
        # consumes this inherited descriptor, never reopens the host pathname.
        bind_at = cmd.index("--bind") + 3
        cmd[bind_at:bind_at] = ["--ro-bind-fd" if readonly else "--bind-fd", str(root_fd), str(destination)]
        run(cmd, env=env, pass_fds=(root_fd,))
        meta["copy_completed"] = completion.is_file() and completion.read_text() == "non-pretend-copy-completed\n"
        if not readonly and not meta["copy_completed"]:
            raise ValueError("Copier returned without positive non-pretend copy completion")
        if not readonly:
            with directory(destination, expected=meta["execution_root_identity"]):
                pass
    (scratch / "lineage.json").write_text(__import__("json").dumps(meta, sort_keys=True) + "\n")
