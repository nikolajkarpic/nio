import argparse
import sys
from importlib import resources

from nio import agents, hooks, index, jury, pack, query, records, spec


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
    n = sub.add_parser("new", help="create a record (or `new spec <slug>`, a spec) from its template and print its path")
    n.add_argument("type", choices=sorted(set(records.REQUIRED) | {"spec"}))
    n.add_argument("slug", nargs="?", help="spec only: a short name; the folder is .nio/specs/<YYYY-MM-DD>-<name>/")
    n.add_argument("--area", help="records: the area folder")
    n.add_argument("--title", help="records: the title")
    n.add_argument("--route", choices=sorted(spec.ROUTES), default="full", help="spec only: full, lite (bugfix) or epic")
    n.add_argument("--epic", default="", help="spec only: the epic slice it belongs to, e.g. checkout/R-2")
    n.add_argument("--by", default="human", help="role / host / model, or human")
    n.add_argument("--run", default="", help="run ID, e.g. R-261024-a1b2; empty when written by hand")
    c = sub.add_parser("check", help="lint every record under .nio/memory, or `check spec <slug>`: a spec's mechanical checks")
    c.add_argument("what", nargs="?", choices=["spec"])
    c.add_argument("slug", nargs="?")
    c.add_argument("--gate", action="store_true", help="spec only: also require no [default] and no open points")
    c.add_argument("--base", default="HEAD", help="ref committed records are compared with; only `paths` may change (CI: origin/main)")
    i = sub.add_parser("index", help="build .nio/cache/index.db and INDEX.md from the records")
    i.add_argument("--check", action="store_true", help="also lint and run the cross-branch conflict checks")
    i.add_argument("--base", default="HEAD", help="ref committed records are compared with, as in nio check")
    q = sub.add_parser("query", help="find records by text, by the files they touch, or walk the graph from one; ≈ marks a likely duplicate")
    q.add_argument("text", nargs="?", default="", help="question or candidate text")
    q.add_argument("--path", action="append", default=[], help="a file the records should touch; repeatable")
    q.add_argument("--graph", metavar="ID", help="walk links both ways from this record: → it points there, ← that points here")
    q.add_argument("--depth", type=int, default=2)
    q.add_argument("--limit", type=int, default=10)
    q.add_argument("--all", action="store_true", help="include superseded and rejected records")
    g = sub.add_parser("get", help=f"print up to {query.MAX_GET} records by ID")
    g.add_argument("ids", nargs="+")
    k = sub.add_parser("pack", help="print the memory that applies to a piece of work, for an agent to read before it starts")
    k.add_argument("text", help="what the work is, in a sentence or two")
    k.add_argument("--path", action="append", default=[], help="a file in the work's scope, existing or not; repeatable")
    k.add_argument("--ac", action="append", default=[], help="an acceptance criterion the work serves; repeatable")
    k.add_argument("--task", default="", help="task ID; names the pack")
    k.add_argument("--diff", metavar="REF", help="juror pack: add the files changed since REF and judge against the records")
    k.add_argument("--run", help="also save the pack to .nio/runs/<run>/packs/")
    sub.add_parser("hooks", help="install git hooks: refresh the index and agent files after pulls, checkouts and rebases; check memory before commits and pushes")
    sub.add_parser("status", help="index freshness: indexed commit against HEAD, model, store")
    sub.add_parser("run", help="start a run: create .nio/runs/<run>/promote.md and print the run ID")
    ag = sub.add_parser("agents", help="agent cards: render them for each host, or check which model they ran on")
    agsub = ag.add_subparsers(dest="agents_cmd", required=True)
    agsub.add_parser("sync", help="render the shipped, personal and team cards as .claude/agents and .codex/agents files")
    v = agsub.add_parser("verify", help="compare the model each recent Claude run of a nio-* agent used with its tier's model")
    v.add_argument("--limit", type=int, default=20)
    j = sub.add_parser("jury", help="jury gates: collect lens outputs into the findings ledger, dispose of findings, compose the outcome")
    jsub = j.add_subparsers(dest="jury_cmd", required=True)
    jsub.add_parser("template", help="print the lens output format, for a juror's context pack")
    ja = jsub.add_parser("answers", help="the human's grill answers (question and answer chosen), for the scope lens's pack")
    ja.add_argument("slug")
    jp = jsub.add_parser("plan", help="the lens runs a gate needs, why each runs, the tier and the run budget; fails on a missing card")
    jp.add_argument("--add", action="append", default=[], help="lens:reason, a lens the skill's own triggers add; repeatable")
    jg = jsub.add_parser("changed", help="IDs changed since the version the last round judged, and the lenses to re-run")
    jc = jsub.add_parser("collect", help="merge the run's lens outputs (and the refuter's, if present) into .nio/specs/<slug>/jury/<gate>")
    jc.add_argument("--run", required=True)
    jc.add_argument("--expect", action="append", default=[], help="a lens that must report; repeatable")
    jc.add_argument("--tier", choices=["low", "medium", "high"], help="the ladder rung triage picked")
    jd = jsub.add_parser("dispose", help="set a finding's disposition; accepted-risk and out-of-scope need --by human")
    jd.add_argument("slug")
    jd.add_argument("gate", choices=sorted(jury.GATES))
    jd.add_argument("id")
    jd.add_argument("disposition", choices=sorted(jury.DISPOSITIONS))
    jd.add_argument("--by", required=True, choices=sorted(jury.BY))
    jd.add_argument("--note", required=True)
    jk = jsub.add_parser("check", help="compose the gate outcome; exit 0 approved, 1 rejected, 2 rerun or pending, 3 human")
    jk.add_argument("--record", action="store_true", help="write the verdict record to memory (once per round and outcome)")
    jk.add_argument("--human", default="", metavar="REASON", help="the human closes the gate themselves: outcome human, with their reason")
    for s in (jp, jg, jc, jk):  # dispose takes them first, before the finding
        s.add_argument("slug")
        s.add_argument("gate", choices=sorted(jury.GATES))
    a = p.parse_args()

    root = records.repo_root()
    if a.cmd == "new":
        try:
            if a.type == "spec":
                if not a.slug:
                    sys.exit("error: give the spec a short name: nio new spec <name>")
                print(spec.new(root, a.slug, a.route, a.epic).relative_to(root))
            elif not (a.area and a.title):
                sys.exit("error: a record needs --area and --title")
            else:
                print(records.new(root, a.type, a.area, a.title, a.by, a.run).relative_to(root))
        except ValueError as e:
            sys.exit(f"error: {e}")
    elif a.cmd == "run":
        print(records.new_run(root))
    elif a.cmd == "check" and a.what == "spec":
        if not a.slug:
            sys.exit("error: give the spec's slug: nio check spec <slug>")
        try:
            errors, notes = spec.check(root, a.slug, a.gate, a.base)
        except ValueError as e:
            sys.exit(f"error: {e}")
        print("\n".join([f"ERROR {e}" for e in errors] + notes + [f"{len(errors)} errors"]))
        sys.exit(1 if errors else 0)
    elif a.cmd == "check":
        report(*records.check(root, a.base))
    elif a.cmd == "query":
        try:
            if a.graph:
                steps = query.graph(root, a.graph, a.depth)
                out, ids = [query.format_step(*s) for s in steps], [s[3] for s in steps if s[4] == "record"]
                kind, asked = "graph", a.graph
            elif a.text or a.path:
                hits = query.search(root, a.text, a.path, a.limit, a.all)
                out, ids = [query.format_hit(*h) for h in hits], [h[0] for h in hits]
                kind, asked = "query", " ".join([a.text, *a.path])
            else:
                sys.exit("error: give a question, --path, or --graph")
        except ValueError as e:
            sys.exit(f"error: {e}")
        text = "".join(f"{line}\n" for line in out)
        query.log(root, kind, asked, ids, text)
        print(text, end="")
    elif a.cmd == "get":
        try:
            text = "".join(f"==> {path} <==\n{body}\n" for path, body in query.get(root, a.ids))
        except ValueError as e:
            sys.exit(f"error: {e}")
        query.log(root, "get", " ".join(a.ids), a.ids, text)
        print(text, end="")
    elif a.cmd == "pack":
        try:
            text, ids = pack.build(root, a.text, a.path, a.ac, a.task, a.diff)
            name = a.task or records.slug(a.text)
            if a.run:
                print(f"saved {pack.save(root, a.run, name, text).relative_to(root)}", file=sys.stderr)
            query.log(root, "pack", name, ids, text)
            print(text, end="")
        except ValueError as e:
            sys.exit(f"error: {e}")
    elif a.cmd == "hooks":
        try:
            for path in hooks.install(root):
                print(path)
        except ValueError as e:
            sys.exit(f"error: {e}")
    elif a.cmd == "agents":
        try:
            if a.agents_cmd == "sync":
                out, errors = agents.sync(root)
                print("\n".join(out + [f"ERROR {e}" for e in errors]))
                sys.exit(1 if errors else 0)
            out, bad = agents.verify(root, a.limit)
            print("\n".join(out))
            sys.exit(1 if bad else 0)
        except ValueError as e:
            sys.exit(f"error: {e}")
    elif a.cmd == "jury":
        try:
            if a.jury_cmd == "answers":
                print("\n".join(jury.answers(root, a.slug)))
            elif a.jury_cmd == "template":
                print(resources.files("nio").joinpath("templates/lens-output.md").read_text(), end="")
            elif a.jury_cmd == "plan":
                lines, ok = jury.plan(root, a.slug, a.gate, a.add)
                print("\n".join(lines))
                sys.exit(0 if ok else 1)
            elif a.jury_cmd == "changed":
                ids, rerun = jury.changed(root, a.slug, a.gate)
                print(f"changed: {', '.join(ids) or 'nothing'}\nre-run: {', '.join(rerun) or 'nothing'}")
            elif a.jury_cmd == "collect":
                print("\n".join(jury.collect(root, a.slug, a.gate, a.run, a.expect, a.tier)))
            elif a.jury_cmd == "dispose":
                jury.dispose(root, a.slug, a.gate, a.id, a.disposition, a.by, a.note)
                print(f"{a.id}: {a.disposition} by {a.by}")
            else:
                outcome, lines = jury.check(root, a.slug, a.gate, a.record, a.human)
                print("\n".join(lines))
                sys.exit({"approved": 0, "rejected": 1, "human": 3}.get(outcome, 2))
        except ValueError as e:
            sys.exit(f"error: {e}")
    elif a.cmd == "status":
        print("\n".join(query.status(root)))
    elif a.cmd == "index":
        count, embedded = index.build(root)
        print(f"indexed {count} records, embedded {embedded}")
        if a.check:
            report(*index.check(root, a.base))
