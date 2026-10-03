#!/usr/bin/env python3
"""Private, source-external, no-overwrite artifact IO for observational CI profiles."""
import argparse
import os
import stat
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def checked_target(value):
    path = Path(value).absolute()
    if path.resolve().is_relative_to(ROOT):
        raise ValueError("profile output must be outside the source tree")
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ValueError("profile output may not traverse a symlink")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory = path.parent.stat()
    if directory.st_uid != os.getuid() or directory.st_mode & 0o077:
        raise ValueError("profile directory must be private and owned by this user")
    return path


def open_artifact(value, append=False):
    path = checked_target(value)
    flags = os.O_WRONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
    flags |= os.O_APPEND if append else os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    info = os.fstat(descriptor)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.getuid() or info.st_mode & 0o077:
        os.close(descriptor)
        raise ValueError("profile artifact must be private, regular, singly linked and owned")
    return os.fdopen(descriptor, "a" if append else "w", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initialize", action="store_true")
    parser.add_argument("path")
    parser.add_argument("phase")
    args = parser.parse_args()
    if not args.phase or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for character in args.phase):
        parser.error("invalid phase name")
    try:
        with open_artifact(args.path, append=not args.initialize) as output:
            output.write(f"{args.phase}\t{time.time_ns()}\t{time.monotonic_ns()}\n")
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
