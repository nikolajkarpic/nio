import argparse
import sys

from nio import records


def main():
    p = argparse.ArgumentParser(prog="nio", description="NIO memory CLI")
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="create a record from its template and print its path")
    n.add_argument("type", choices=sorted(set(records.REQUIRED)))
    n.add_argument("--area", required=True)
    n.add_argument("--title", required=True)
    n.add_argument("--by", default="human", help="role / host / model, or human")
    n.add_argument("--run", default="", help="run ID, e.g. R-261024-a1b2; empty when written by hand")
    sub.add_parser("check", help="lint every record under .nio/memory")
    sub.add_parser("run", help="start a run: create .nio/runs/<run>/promote.md and print the run ID")
    a = p.parse_args()

    root = records.repo_root()
    if a.cmd == "new":
        try:
            print(records.new(root, a.type, a.area, a.title, a.by, a.run).relative_to(root))
        except ValueError as e:
            sys.exit(f"error: {e}")
    elif a.cmd == "run":
        print(records.new_run(root))
    elif a.cmd == "check":
        errors, warnings, count = records.check(root)
        for w in warnings:
            print(f"WARN  {w}")
        for e in errors:
            print(f"ERROR {e}")
        print(f"{count} records, {len(errors)} errors, {len(warnings)} warnings")
        sys.exit(1 if errors else 0)
