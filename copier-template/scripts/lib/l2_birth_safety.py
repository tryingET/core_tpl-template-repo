"""Descriptor-pinned child directory and no-follow, atomic lineage access."""
import os
import stat
from contextlib import contextmanager
from pathlib import Path

import yaml


def identity(fd: int) -> list[int]:
    observed = os.fstat(fd)
    if not stat.S_ISDIR(observed.st_mode):
        raise ValueError("child root must be a directory")
    return [observed.st_dev, observed.st_ino]


@contextmanager
def directory(path: Path, *, create: bool = False, expected=None):
    """Walk every component relative to a pinned parent; never follow links."""
    path = Path(os.path.abspath(path))
    fd = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[1:]:
            if create:
                try:
                    os.mkdir(part, dir_fd=fd)
                except FileExistsError:
                    pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        observed = identity(fd)
        if expected is not None and observed != expected:
            raise ValueError("child root identity changed")
        yield fd
    finally:
        os.close(fd)


def record_answers(root_fd: int, relative: str, update) -> None:
    """Read and replace only within descriptor-pinned, no-follow parents."""
    parts = relative.split("/")
    if not parts or any(p in ("", ".", "..") for p in parts) or Path(relative).is_absolute():
        raise ValueError("answers path must be normalized and repo-relative")
    parent = os.dup(root_fd)
    output = parts[-1] + ".lineage-new"
    created = False
    try:
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            os.close(parent)
            parent = child
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(fd, "rb") as handle:
            observed = os.fstat(handle.fileno())
            if not stat.S_ISREG(observed.st_mode):
                raise ValueError("child answers must be a regular file")
            child = yaml.safe_load(handle.read())
        if not isinstance(child, dict):
            raise ValueError("child answers must be a mapping")
        update(child)
        fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=parent)
        created = True
        with os.fdopen(fd, "w") as handle:
            yaml.safe_dump(child, handle, sort_keys=True)
            os.fchmod(handle.fileno(), stat.S_IMODE(observed.st_mode))
        os.replace(output, parts[-1], src_dir_fd=parent, dst_dir_fd=parent)
        created = False
    finally:
        if created:
            os.unlink(output, dir_fd=parent)
        os.close(parent)
