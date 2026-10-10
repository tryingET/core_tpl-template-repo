"""CLI dispatch for ownership transitions; shared library retains the verification API."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    import l1_template_transitions as transition
    import l1_template_company as company
    import l1_template_fold as fold
    parser = argparse.ArgumentParser(description=transition.__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    for action in ("plan", "reverse-plan"):
        p = sub.add_parser(action); p.add_argument("--spec", type=Path, required=True); p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("apply"); p.add_argument("--plan", type=Path, required=True)
    p = sub.add_parser("finalize"); p.add_argument("--plan", type=Path, required=True); p.add_argument("--finalize-task", required=True)
    p = sub.add_parser("commit-message"); p.add_argument("--plan", type=Path, required=True); p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(); repo = args.repo_root.resolve()
    try:
        if args.command == "plan": return transition.create_plan(repo, args.spec.resolve(), args.output.resolve(), None)
        if args.command == "reverse-plan": return company.reverse_plan(repo, args.spec.resolve(), args.output.resolve(), None)
        if args.command == "commit-message": return fold.commit_message(repo, args.plan.resolve(), args.output.resolve())
        if args.command == "apply": return transition.apply(repo, args.plan.resolve(), None)
        return transition.finalize(repo, args.plan.resolve(), args.finalize_task, None)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 2
