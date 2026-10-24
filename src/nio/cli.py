import argparse
import sys

from nio import index, query, records


def report(errors, warnings, count):
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"{count} records, {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


def main():
    p = argparse.ArgumentParser(prog="nio", description="NIO memory CLI")
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="create a record from its template and print its path")
    n.add_argument("type", choices=sorted(set(records.REQUIRED)))
    n.add_argument("--area", required=True)
    n.add_argument("--title", required=True)
    n.add_argument("--by", default="human", help="role / host / model, or human")
    n.add_argument("--run", default="", help="run ID, e.g. R-261024-a1b2; empty when written by hand")
    c = sub.add_parser("check", help="lint every record under .nio/memory")
    c.add_argument("--base", default="HEAD", help="ref committed records are compared with; only `paths` may change (CI: origin/main)")
    i = sub.add_parser("index", help="build .nio/cache/index.db and INDEX.md from the records")
    i.add_argument("--check", action="store_true", help="also lint and run the cross-branch conflict checks")
    i.add_argument("--base", default="HEAD", help="ref committed records are compared with, as in nio check")
    q = sub.add_parser("query", help="find records by text and/or the files they touch; ≈ marks a likely duplicate")
    q.add_argument("text", nargs="?", default="", help="question or candidate text")
    q.add_argument("--path", action="append", default=[], help="a file the records should touch; repeatable")
    q.add_argument("--limit", type=int, default=10)
    q.add_argument("--all", action="store_true", help="include superseded and rejected records")
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
        report(*records.check(root, a.base))
    elif a.cmd == "query":
        if not a.text and not a.path:
            sys.exit("error: give a question, --path, or both")
        for hit in query.search(root, a.text, a.path, a.limit, a.all):
            print(query.format_hit(*hit))
    elif a.cmd == "index":
        count, embedded = index.build(root)
        print(f"indexed {count} records, embedded {embedded}")
        if a.check:
            report(*index.check(root, a.base))
