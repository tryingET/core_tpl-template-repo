"""Copier 9.11.1 positive-completion adapter, not inference from exit zero."""
import sys
from importlib.metadata import version
from pathlib import Path


def main() -> None:
    completion = Path(sys.argv[1])
    completion.write_text("")
    if version("copier") != "9.11.1":
        raise ValueError("L2 birth completion adapter requires Copier 9.11.1")
    from copier import _cli
    original = _cli.Worker
    completed = False

    class ObservedWorker(original):
        def run_copy(self):
            nonlocal completed
            super().run_copy()
            completed = not self.pretend

    _cli.Worker = ObservedWorker
    try:
        try:
            _cli.CopierApp.run(["copier", *sys.argv[2:]])
        except SystemExit as error:
            if error.code == 0 and completed:
                completion.write_text("non-pretend-copy-completed\n")
            raise
    finally:
        _cli.Worker = original


if __name__ == "__main__":
    main()
