import argparse
import datetime
import re
import shlex
import sys
from pathlib import Path
from importlib import resources

from nio import agents, evidence, explain, flow, hooks, implement, index, jury, onboard, pack, plan, query, records, spec, tasks, usage


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
    n = sub.add_parser("new", help="create a record (or `new spec <name>`, a spec; `new plan <slug>`, a spec's plan files) from its template and print its path")
    n.add_argument("type", choices=sorted(set(records.REQUIRED) | {"spec", "plan", "tasks"}))
    n.add_argument("slug", nargs="?", help="spec: a short name; the folder is .nio/specs/<YYYY-MM-DD>-<name>/. plan: the spec's slug")
    n.add_argument("--area", help="records: the area folder")
    n.add_argument("--title", help="records: the title")
    n.add_argument("--route", choices=sorted(spec.ROUTES), default="full", help="spec only: full, lite (bugfix) or epic")
    n.add_argument("--epic", default="", help="spec only: the epic slice it belongs to, e.g. checkout/R-2")
    n.add_argument("--by", default="human", help="role / host / model, or human")
    n.add_argument("--run", default="", help="run ID, e.g. R-261024-a1b2; empty when written by hand")
    c = sub.add_parser("check", help="lint every record under .nio/memory, or `check spec|plan <slug>`: a spec's or its plan's mechanical checks")
    c.add_argument("what", nargs="?", choices=["spec", "plan", "tasks", "explainer"])
    c.add_argument("slug", nargs="?")
    c.add_argument("--gate", action="store_true", help="spec: also require no [default] and no open points. plan: no open points")
    c.add_argument("--approved", action="store_true", help="plan: exit 0 when the tasks stage may start. tasks: exit 0 when the implement stage may")
    c.add_argument("--rated-from", default="", help="tasks: a copy of tasks.md from before rating; only Tier and Effort lines may differ")
    e = sub.add_parser("explain", help="explainer commands: `explain finish <path>` and `explain topic <text>`")
    e.add_argument("action", choices=["finish", "topic"])
    e.add_argument("target", nargs="?")
    ob = sub.add_parser("onboard", help="`onboard scan`: list the project's docs, manifests, IaC and CI files with a content hash")
    ob.add_argument("action", choices=["scan", "start", "confirm", "pause", "skip", "backup", "changed", "reconciled"])
    ob.add_argument("arg", nargs="*", help="skip: the reason; confirm: the doc")
    ob.add_argument("--empty", action="store_true", help="start: write blank docs")
    ob.add_argument("--app", action="append", default=[], help="start: <slug>=<path>[,<path>...], repeatable; confirm: the app's slug")
    t = sub.add_parser("task", help="`task show <slug> T-n`: one task's section and its epic's title, for a worker's pack")
    t.add_argument("action", choices=["show", "retire"])
    t.add_argument("slug")
    t.add_argument("id")
    t.add_argument("--reason", default="", help="retire: why the fix task is dropped; its finding closes as accepted risk with it")
    t.add_argument("--by", choices=sorted(jury.BY), help="retire (required): who retires the fix task")
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
    k.add_argument("--reader", choices=list(onboard.READERS), help="add the project docs this reader gets")
    k.add_argument("--slug", default="", help="effort slug; picks the apps its spec names")
    sub.add_parser("hooks", help="install git hooks: refresh the index and agent files after pulls, checkouts and rebases; check memory before commits and pushes")
    md = sub.add_parser("mods", help="install NIO's Claude Code mods for this clone")
    md.add_argument("mods_cmd", choices=["install"])
    md.add_argument("--skip", action="store_true", help="install nothing; report what is already installed")
    al = sub.add_parser("allow", help="let agents run stage commands without a prompt on Claude Code; the human's decisions still prompt")
    scope = al.add_mutually_exclusive_group(required=True)
    scope.add_argument("--personal", action="store_true", help="this clone only: .claude/settings.local.json, gitignored")
    scope.add_argument("--shared", action="store_true", help="everyone on the repo: .claude/settings.json, to commit")
    sub.add_parser("status", help="index freshness: indexed commit against HEAD, model, store")
    r = sub.add_parser("run", help="start a run: create .nio/runs/<run>/promote.md and print the run ID")
    r.add_argument("slug", nargs="?", help="the effort the run serves (.nio/specs/<slug>/)")
    r.add_argument("target", nargs="?", help="the stage or task (T-n) it serves; written to the run's flow.json")
    us = sub.add_parser("usage", help="record what a run spends: install the agent hooks, or write an effort's summary")
    ussub = us.add_subparsers(dest="usage_cmd", required=True)
    ui = ussub.add_parser("install", help="install the hooks that timestamp each agent and shell call")
    ui.add_argument("--host", default="claude", choices=sorted(usage.HOSTS))
    uscope = ui.add_mutually_exclusive_group(required=True)
    uscope.add_argument("--personal", action="store_true", help="this clone only: .claude/settings.local.json, gitignored")
    uscope.add_argument("--shared", action="store_true", help="everyone on the repo: .claude/settings.json, to commit")
    ussub.add_parser("event", help="record one hook payload from stdin; the hooks call this").add_argument("host", choices=sorted(usage.HOSTS))
    ussub.add_parser("report", help="write .nio/specs/<slug>/usage.json without committing it").add_argument("slug")
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
    jp.add_argument("--pick", help="lens,lens: the lenses to run when the plan is over the cap; the core lenses must be in it")
    jg = jsub.add_parser("changed", help="IDs and sections changed since the version the last round judged, their neighbours, and the lenses to re-run")
    jf = jsub.add_parser("fixcheck", help="print one lens's fix-check pack for a re-review or the final fix check")
    jf.add_argument("--lens", required=True)
    jf.add_argument("--blocker", metavar="J-N", help="the pack for an escalation juror, who judges only this new blocker")
    jn = jsub.add_parser("next", help="run one gate step: collect, check and write the next packs; prints the next action")
    jn.add_argument("--run", default="")
    jn.add_argument("--add", action="append", default=[], help="lens:reason; repeatable")
    jn.add_argument("--pick", help="lens,lens")
    jc = jsub.add_parser("collect", help="merge the run's lens outputs (and the refuter's, if present) into .nio/specs/<slug>/jury/<gate>")
    jc.add_argument("--run", required=True)
    jc.add_argument("--expect", action="append", default=[], help="a lens that must report; repeatable")
    jc.add_argument("--tier", choices=["low", "medium", "high"], help="the ladder rung triage picked")
    jd = jsub.add_parser("dispose", help="set a finding's disposition; accepted-risk, out-of-scope and overruled need --by human")
    jd.add_argument("slug")
    jd.add_argument("gate", type=jury.gate_arg, metavar="GATE")
    jd.add_argument("id")
    jd.add_argument("disposition", choices=sorted(jury.DISPOSITIONS | {"reopen"}))
    jd.add_argument("--by", required=True, choices=sorted(jury.BY))
    jd.add_argument("--note", required=True, action="append")
    jd.add_argument("--change", default="", metavar="C-ID", help="spec-change only: the change record the finding waits on")
    jr = jsub.add_parser("rule", help="the human's ruling on findings of a capped batch: accept (as risk), fix (no re-check) or again (one more round)")
    jr.add_argument("slug")
    jr.add_argument("gate", type=jury.gate_arg, metavar="GATE")
    jr.add_argument("id")
    jr.add_argument("ruling", choices=jury.RULINGS)
    jr.add_argument("--note", required=True, help="the human's words")
    jr.add_argument("--by", default="human", metavar="BY", help='human (the default), or the driver "<role> / <host> / <model>" under auto')
    je = jsub.add_parser("evidence", help="run an epic's tests, checks, attacks and journeys in a throwaway copy and write the run's results.json")
    je.add_argument("slug")
    je.add_argument("epic", metavar="E-n|pr", help="an epic, or pr: the whole effort diff")
    je.add_argument("--run", required=True)
    jl = jsub.add_parser("files", help="the files a juror at this gate reads, and the only files its quotes may come from")
    jpk = jsub.add_parser("pack", help="print one lens's pack at an implementation gate: the epic's diff, its ACs and the run's results")
    jpk.add_argument("--lens", required=True)
    jpk.add_argument("--run", required=True)
    jk = jsub.add_parser("check", help="compose the gate outcome; exit 0 approved, 1 rejected, 2 rerun or pending, 3 human")
    jk.add_argument("--record", action="store_true", help="write the verdict record to memory (once per round and outcome)")
    jk.add_argument("--human", default="", metavar="REASON", help="the human closes the gate themselves: outcome human, with their reason")
    for s in (jp, jg, jf, jc, jk, jl, jpk, jn):  # dispose takes them first, before the finding
        s.add_argument("slug")
        s.add_argument("gate", type=jury.gate_arg, metavar="GATE")
    f = sub.add_parser("flow", help="where an effort is, what to do next, and moving it on only when its guards pass")
    fsub = f.add_subparsers(dest="flow_cmd", required=True)
    by = {"metavar": "BY", "help": '"<role> / <host> / <model>", or human'}
    fn = fsub.add_parser("next", help="the effort's state, the skill to run, its inputs, exit criteria and done command")
    fn.add_argument("slug", nargs="?", help="default: the effort with the newest history line")
    fn.add_argument("--by", metavar="BY", help="record what the call finds owed (a resume, a move back, a pause) as this caller")
    fs = fsub.add_parser("start", help="start an effort, or resume a parked, suspended or abandoned one")
    fs.add_argument("slug")
    fd = fsub.add_parser("done", help="report a stage done: its guard decides; at a gate, --commit approves it")
    fd.add_argument("stage", type=flow.stage_arg, metavar="STAGE", help="a stage, or an epic's gate as implementation-E-n")
    fd.add_argument("slug", nargs="?", help="default: the effort with the newest history line")
    fd.add_argument("--commit", action="store_true", help="at a gate: make the `nio: approve <gate>` commit")
    fd.add_argument("--human", metavar="REASON", help="the human passes a failing check, with their reason")
    fbr = fsub.add_parser("brief", help="what a fresh driver starts from: the state, the next command, a running long command, open tasks and findings")
    fbr.add_argument("slug")
    fbr.add_argument("--all", action="store_true", help="list every open task and finding, past the 80-line cap")
    for s in (fs, fd):
        s.add_argument("--auto", action="store_true", help="the human's auto-mode grant")
    fsh = fsub.add_parser("show", help="an effort's drill-down data as one JSON line")
    fsh.add_argument("slug")
    fsh.add_argument("--json", action="store_true", required=True)
    fsub.add_parser("status", help="one line per effort, newest activity first")
    fap = fsub.add_parser("approve", help="the human approves the pr gate at a terminal, typing the effort's slug back")
    fap.add_argument("slug", nargs="?", help="default: the effort with the newest history line")
    fp = fsub.add_parser("park", help="park an effort, with the reason")
    fa = fsub.add_parser("abandon", help="abandon an effort until `nio flow start` resumes it, with the reason")
    for s in (fp, fa):
        s.add_argument("slug")
        s.add_argument("why")
    fe = fsub.add_parser("seen", help="the human saw the effort's overrides")
    fe.add_argument("slug")
    fc = fsub.add_parser("claim", help="implementing: claim the next ready epic; prints its tasks, worker card, effort, pack and hand-back")
    fc.add_argument("slug", nargs="?", help="default: the effort with the newest history line")
    fc.add_argument("epic", nargs="?", metavar="E-n", help="claim this epic, not the next ready one")
    ff = fsub.add_parser("finish", help="implementing: the agent handed an epic back; run its tests and close it if they pass")
    ff.add_argument("slug")
    ff.add_argument("epic", metavar="E-n")
    fu = fsub.add_parser("unblock", help="implementing: the human sets a blocked task or epic going again, with the reason")
    fb = fsub.add_parser("block", help="implementing: file an agent's blocked handoff as a pending change request")
    fu.add_argument("slug")
    fu.add_argument("task", metavar="T-n|E-n")
    fb.add_argument("slug")
    fb.add_argument("task", metavar="T-n")
    fu.add_argument("--human", required=True, metavar="REASON", help="why the task or epic can go on")
    fb.add_argument("--handoff", required=True, metavar="FILE", help="the handoff: status blocked with a change_request")
    fm = fsub.add_parser("manual", help="the human switches an effort's auto flag off")
    fm.add_argument("slug")
    fv = fsub.add_parser("drive", help="take, refresh (--token) or release (--release --token) an effort's driver claim")
    fv.add_argument("slug")
    fv.add_argument("--token", help="the token the first call printed")
    fv.add_argument("--release", action="store_true", help="remove the claim when --token matches")
    for s in (fs, fd, fp, fa, fe, fc, ff, fu, fb, fv, fm):
        s.add_argument("--by", required=True, **by)
    a = p.parse_args()

    if a.cmd == "usage" and a.usage_cmd == "event":  # before repo_root: a hook must never fail the agent's call
        usage.record(a.host)
        return
    if a.cmd == "onboard":  # before repo_root: outside a git repo it says so instead of a traceback
        if records.git(".", "rev-parse", "--is-inside-work-tree", full=True)[0]:
            sys.exit(f"nio onboard {a.action} needs a git repository")
        if a.action == "backup":
            try:
                print(onboard.backup(a.arg[0] if a.arg else "", records.repo_root()))
            except (ValueError, OSError) as e:
                sys.exit(f"error: {e}")
            return
        if a.action in ("changed", "reconciled"):
            try:
                r = records.repo_root()
                if a.action == "reconciled":
                    onboard.reconciled(r, a.arg)
                    print("reconciled")
                elif a.arg:
                    print("\n".join(f"{p}: {', '.join(d)}" for p, d in onboard.changed(r, a.arg[0])) or "no project doc source changed")
                else:
                    print("\n".join(onboard.to_reconcile(r)) or "nothing to reconcile")
            except ValueError as e:
                sys.exit(f"error: {e}")
            return
        if a.action != "scan":
            try:
                st_apps = dict((k, v.split(",")) for k, _, v in (x.partition("=") for x in a.app)) if a.action == "start" else None
                print(onboard.act(a.action, " ".join(a.arg), a.arg[0] if a.arg else "", a.empty, root=records.repo_root(),
                                  apps=st_apps, app=a.app[0] if a.action == "confirm" and a.app else ""))
            except ValueError as e:
                sys.exit(f"error: {e}")
            return
        found = onboard.scan(records.repo_root())
        for c, f, h in found:
            print(c, f, h) if h else print(c, f)
        print(f"{len(found)} candidate files" if found else "no candidate files found")
        return
    if a.cmd == "mods":  # local scope is keyed to the clone's root, so resolve it; no repo: use cwd
        try:
            top = records.repo_root()
        except (IndexError, OSError):  # OSError: no git on PATH either
            top = Path.cwd()
        print("\n".join(hooks.mods_install(top, a.skip)))
        return
    root = records.repo_root()

    def long(call):  # a long command is recorded as running while it runs (#128 FR-17)
        with flow.running(root, a.slug, shlex.join(["nio", *sys.argv[1:]])):
            return call()
    if a.cmd == "new":
        try:
            if a.type == "spec":
                if not a.slug:
                    sys.exit("error: give the spec a short name: nio new spec <name>")
                print(spec.new(root, a.slug, a.route, a.epic).relative_to(root))
            elif a.type == "plan":
                if not a.slug:
                    sys.exit("error: give the spec's slug: nio new plan <slug>")
                print("\n".join(str(p.relative_to(root)) for p in plan.new(root, a.slug)))
            elif a.type == "tasks":
                if not a.slug:
                    sys.exit("error: give the spec's slug: nio new tasks <slug>")
                print(tasks.new(root, a.slug).relative_to(root))
            elif not (a.area and a.title):
                sys.exit("error: a record needs --area and --title")
            else:
                print(records.new(root, a.type, a.area, a.title, a.by, a.run).relative_to(root))
        except ValueError as e:
            sys.exit(f"error: {e}")
    elif a.cmd == "run":
        link = None
        if a.slug:
            if not a.target:
                sys.exit("error: give the stage or task too: nio run <slug> <stage|T-n>")
            if not (root / ".nio/specs" / a.slug).is_dir():
                sys.exit(f"error: no effort {a.slug} under .nio/specs/")
            if a.target not in flow.STAGES and not re.fullmatch(r"T-\d+", a.target):
                sys.exit(f"error: {a.target} is neither a stage ({', '.join(flow.STAGES)}) nor a task T-n")
            link = {"effort": a.slug, "task" if a.target.startswith("T-") else "stage": a.target,
                    "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        print(records.new_run(root, link))
    elif a.cmd == "check" and a.what:
        if not a.slug:
            sys.exit(f"error: give the spec's slug: nio check {a.what} <slug>")
        if a.approved:
            if a.what not in ("plan", "tasks"):
                sys.exit("error: --approved is for `nio check plan` and `nio check tasks`")
            try:
                ok, why = {"plan": plan, "tasks": tasks}[a.what].approved(root, a.slug)
            except ValueError as e:
                sys.exit(f"error: {e}")
            print(why)
            sys.exit(0 if ok else 1)
        try:
            errors, notes = {"spec": spec, "plan": plan, "tasks": tasks, "explainer": explain}[a.what].check(root, a.slug, a.gate, a.base)
            if a.rated_from and a.what == "tasks":
                errors += tasks.rated_from(root, a.slug, a.rated_from)
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
            text, ids = pack.build(root, a.text, a.path, a.ac, a.task, a.diff, reader=a.reader or "", slug=a.slug)
            name = a.task or records.slug(a.text)
            if a.run:
                print(f"saved {pack.save(root, a.run, name, text).relative_to(root)}", file=sys.stderr)
            query.log(root, "pack", name, ids, text)
            print(text, end="")
        except ValueError as e:
            sys.exit(f"error: {e}")
    elif a.cmd == "allow":
        try:
            print(f"wrote {hooks.allow(root, a.shared).relative_to(root)}; other hosts keep their own prompts")
        except ValueError as e:
            sys.exit(f"error: {e}")
    elif a.cmd == "hooks":
        try:
            for path in hooks.install(root):
                print(path)
        except ValueError as e:
            sys.exit(f"error: {e}")
    elif a.cmd == "usage":
        try:
            if a.usage_cmd == "install":
                print(f"wrote {usage.HOSTS[a.host]['install'](root, a.shared).relative_to(root)}")
            else:
                path = usage.write(root, a.slug)
                print(path.relative_to(root) if path else f"nothing recorded for {a.slug}")
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
            if jury.impl_gate(getattr(a, "gate", "")):  # a ruling needn't wait for the fix tasks; a round does
                jury.epic_gate(root, a.slug, a.gate, finished=a.jury_cmd in ("plan", "collect", "next"))
            if a.jury_cmd == "evidence":
                print("\n".join(long(lambda: evidence.collect(root, a.slug, a.epic, a.run))))
            elif a.jury_cmd == "answers":
                print("\n".join(jury.answers(root, a.slug)))
            elif a.jury_cmd == "template":
                print(resources.files("nio").joinpath("templates/lens-output.md").read_text(), end="")
            elif a.jury_cmd == "plan":
                lines, ok = jury.plan(root, a.slug, a.gate, a.add, a.pick)
                print("\n".join(lines))
                sys.exit(0 if ok else 1)
            elif a.jury_cmd == "changed":
                ids, rerun, near, secs = jury.changed(root, a.slug, a.gate)
                print(f"changed: {', '.join(ids) or 'nothing'}\nsections: {', '.join(secs) or 'nothing'}\n"
                      f"neighbours: {', '.join(near) or 'nothing'}\nre-run: {', '.join(rerun) or 'nothing'}")
                if added := jury.fixes_added(root, a.slug, a.gate):
                    print(f"added under Fixes: {', '.join(added)}")
            elif a.jury_cmd == "pack":
                print(evidence.pack(root, a.slug, a.gate, a.lens, a.run), end="")
            elif a.jury_cmd == "files":
                print("\n".join(str(f.relative_to(root)) for f in jury.sources(root, a.slug, a.gate)))
            elif a.jury_cmd == "fixcheck":
                print("\n".join(jury.fixcheck(root, a.slug, a.gate, a.lens, a.blocker)))
            elif a.jury_cmd == "next":
                print("\n".join(jury.step(root, a.slug, a.gate, a.run, a.add, a.pick)))
            elif a.jury_cmd == "collect":
                print("\n".join(jury.collect(root, a.slug, a.gate, a.run, a.expect, a.tier)))
            elif a.jury_cmd == "rule":
                for i in jury.rule(root, a.slug, a.gate, a.id, a.ruling, a.note, a.by):
                    print(f"{i}: {a.ruling} by human")
            elif a.jury_cmd == "dispose":
                for i in jury.dispose(root, a.slug, a.gate, a.id, a.disposition, a.by, a.note, a.change):
                    print(f"{i}: {a.disposition} by {a.by}")
            else:
                outcome, lines = jury.check(root, a.slug, a.gate, a.record, a.human)
                print("\n".join(lines))
                sys.exit({"approved": 0, "rejected": 1, "human": 3}.get(outcome, 2))
        except (ValueError, flow.Busy) as e:
            sys.exit(f"error: {e}")
    elif a.cmd == "flow":
        try:
            code, lines = {
                "next": lambda: flow.next_step(root, a.slug, by=a.by),
                "start": lambda: flow.start(root, a.slug, by=a.by, auto=a.auto),
                "done": lambda: flow.done(root, a.stage, a.slug, commit=a.commit, human=a.human, by=a.by, **({"auto": True} if a.auto else {})),
                "status": lambda: flow.status(root),
                "approve": lambda: flow.approve(root, a.slug),
                "park": lambda: flow.park(root, a.slug, a.why, by=a.by),
                "abandon": lambda: flow.abandon(root, a.slug, a.why, by=a.by),
                "seen": lambda: flow.seen(root, a.slug, by=a.by),
                "manual": lambda: flow.manual(root, a.slug, by=a.by),
                "drive": lambda: flow.drive(root, a.slug, a.by, token=a.token, release=a.release),
                "claim": lambda: implement.claim(root, a.slug, by=a.by, epic=a.epic),
                "brief": lambda: flow.brief(root, a.slug, a.all),
                "finish": lambda: long(lambda: implement.finish(root, a.slug, a.epic, by=a.by)),
                "show": lambda: flow.show(root, a.slug),
                "block": lambda: implement.block(root, a.slug, a.task, a.handoff, by=a.by),
                "unblock": lambda: implement.unblock(root, a.slug, a.task, a.human, by=a.by),
            }[a.flow_cmd]()
        except (ValueError, flow.Broken, flow.Busy) as e:
            sys.exit(f"error: {e}")
        print("\n".join(lines))
        sys.exit(code)
    elif a.cmd == "explain":
        try:
            print(explain.topic(root, a.target or "") if a.action == "topic" else "\n".join(explain.finish(root, a.target)))
        except ValueError as e:
            sys.exit(f"error: {e}")
    elif a.cmd == "task":
        try:
            print(tasks.retire(root, a.slug, a.id, a.reason, a.by) if a.action == "retire" else "\n".join(tasks.show(root, a.slug, a.id)))
        except ValueError as e:
            sys.exit(f"error: {e}")
    elif a.cmd == "status":
        try:
            ob = onboard.status_lines(root)
        except ValueError as e:
            ob = [f"onboarding: error: {e}"]
        print("\n".join(query.status(root) + ob + explain.stale(root)))
    elif a.cmd == "index":
        count, embedded = index.build(root)
        print(f"indexed {count} records, embedded {embedded}")
        if a.check:
            report(*index.check(root, a.base))
