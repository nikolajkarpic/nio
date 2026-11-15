"""The implement stage (2026-10-29-implement-stage): running a command with a time limit, the known test runners, a
full-suite run, and each task's status from history."""
import datetime
import os
import re
import signal
import subprocess
from pathlib import Path

from nio import flow, pack, plan, records, spec, tasks

DEFAULT_LIMIT = 600  # FR-44


def run(root, command, limit):
    """(code, output, cause) of a shell command in `root` (CT-1, FR-44): stdin closed, stderr merged into stdout, its own
    process group so the limit kills every child. `cause` is "", "time limit" or "program not found" (exit 127)."""
    p = subprocess.Popen(command, shell=True, cwd=root, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                         env={k: v for k, v in os.environ.items() if k != "NIO_PERF"}, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        out, _ = p.communicate(timeout=limit)
        code, cause = p.returncode, "program not found" if p.returncode == 127 else ""
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        out, _ = p.communicate()
        code, cause = None, "time limit"
    return code, out.decode(errors="replace"), cause


# CT-2, research RF-6. Maven and Gradle have no entry (FR-34); cargo has no "none" marker, since its doc-tests line
# "running 0 tests" appears on runs that did run tests.
RUNNERS = {
    "pytest": {"match": r"\bpytest\b", "error": ["ERROR collecting", "ImportError while importing test module",
               "error during collection", "errors during collection"], "none": ["no tests ran"]},
    "unittest": {"match": r"\bunittest\b", "error": ["Failed to import test module", "in createTests"], "none": ["Ran 0 tests", "NO TESTS RAN"]},
    "jest": {"match": r"\bjest\b", "error": ["Test suite failed to run"], "none": ["No tests found"]},
    "vitest": {"match": r"\bvitest\b", "error": ["Failed Suites"], "none": ["No test files found", "No test suite found"]},
    "mocha": {"match": r"\bmocha\b", "error": ["Exception during run"], "none": ["No test files found"]},
    "go test": {"match": r"\bgo test\b", "error": ["[build failed]", "[setup failed]"],
                "none": ["[no test files]", "[no tests to run]"]},
    "cargo test": {"match": r"\bcargo test\b", "error": ["error[E", "error: could not compile"], "none": []},
    "rspec": {"match": r"\brspec\b", "error": ["error occurred outside of examples", "errors occurred outside of examples",
              "An error occurred while loading"], "none": ["No examples found", "0 examples, 0 failures"]},
    "self-check": {"error": [], "none": ["ran 0 tests"]},  # no "match": found by its `ran N tests` summary line (CT-7)
}


def runner(command, output=""):
    """The known runner a command's own words name, else `self-check` when the output has its `ran N tests` line,
    else None: `npm test` or `bash run.sh` read as unknown (CT-2, CT-7)."""
    found = next((n for n, r in RUNNERS.items() if re.search(r.get("match", r"(?!)"), command)), None)
    return found or ("self-check" if re.search(r"^ran \d+ tests?, \d+ failed$", output, re.M) else None)


def wrong_reason(name, code, output):
    """"" when a failure may be red's right one; else why not (CT-2, FR-8): a collection, import or syntax error marker
    (pytest exit 2 or 4 too), or that no tests ran (pytest exit 5 too). An unknown runner has no wrong reason (FR-9)."""
    r = RUNNERS.get(name)
    if not r:
        crash = re.search(r"^(?:SyntaxError|IndentationError|ImportError|ModuleNotFoundError)\b", output, re.M)
        return f"collection, import or syntax error: {crash[0]}" if crash and not re.search(r"^ran \d+ tests?", output, re.M | re.I) else ""
    marker = next((m for m in r["error"] if m in output), f"exit {code}" if name == "pytest" and code in (2, 4) else "")
    if marker:
        return f"collection, import or syntax error: {marker}"
    if (name == "pytest" and code == 5) or any(m in output for m in r["none"]):
        return "no tests ran"
    return ""


# failing-test and collected-count readers, for the runners whose summary lines CT-3 names; others read as unknown
SUMMARY = {
    "pytest": (r"^(?:FAILED|ERROR) (\S+)", r"collected (\d+) items?"),
    "unittest": (r"^(?:FAIL|ERROR): (.+?)\s*$", r"^Ran (\d+) tests?"),
    "self-check": (r"^FAIL (\S+)", r"^ran (\d+) tests?"),
}


def suite(root, cfg, command=None):
    """A full-suite run read into {"command", "code", "cause", "runner", "failing", "collected", "broken",
    "output_hash", "output"} (CT-3, FR-14, FR-16, FR-35, FR-44). `failing` and `collected` are None for a runner without a reader."""
    t = cfg.get("tests") or {}
    if not t.get("suite"):
        raise ValueError("no `tests.suite` in the NIO config")
    command = command or t["suite"]
    code, out, cause = run(root, command, t.get("timeout") or DEFAULT_LIMIT)
    name = runner(command, out)
    failing = collected = None
    if name in SUMMARY:
        fail, count = SUMMARY[name]
        failing = re.findall(fail, out, re.M)
        found = re.findall(count, out, re.M)
        collected = sum(map(int, found)) if found else None
    broken = bool(cause) or wrong_reason(name, code, out).startswith("collection")
    return {"command": command, "code": code, "cause": cause, "runner": name, "failing": failing,
            "collected": collected, "broken": broken, "output_hash": flow.sha(out.encode()), "output": out}


EPIC_LIMIT = 1800  # FR-4: an epic's test run is stopped after 30 minutes; a test lowers it
TAIL = 50  # FR-4: the lines of a failed run's output that are kept


def tasks_of(root, slug):
    """Every task of tasks.md in epic order then file order, fix tasks included (CT-4): id, title, epic, heading (its
    epic's title), fix, deps, files, serves, tests, own, test (the raw `Test:`), parallel, and its epic's tier and
    effort (FR-7: an epic rated before the change takes its tasks' highest)."""
    parsed = tasks.parse("\n".join(records.parse(tasks.path(root, slug))[1]))
    out = []
    for e in parsed["epics"]:
        tier, effort = tasks.epic_rating(e, parsed["tasks"])
        for tid in e["tasks"]:
            t = parsed["tasks"][tid]
            f = t["fields"]
            out.append({"id": tid, "title": t["title"], "epic": e["id"], "heading": e["title"], "fix": t["fix"],
                        "deps": [d for d in tasks.ids(f.get("Depends on", "")) if d in parsed["tasks"]],  # a retired dependency is met
                        "files": [x for x in map(tasks.file_of, tasks.files(f.get("Files", ""))) if x],
                        "reused": [tasks.file_of(x) for x in tasks.files(f.get("Files", "")) if x.endswith("(unchanged)")],  # FR-40
                        "serves": tasks.ids(f.get("Serves", "")), "tests": tasks.ids(f.get("Test", "")),
                        "own": tasks.own(f.get("Test", "")), "test": f.get("Test", ""), "tier": tier, "effort": effort,
                        "parallel": f.get("Parallel") == "yes"})
    return out


def status(root, slug, lines):
    """{T-n: state} (CT-4): `done` after its `task_done` line, `blocked` after a task block (a spec problem) until its
    `unblock`, else `ready` when every dependency is done, `pending` when not. Ids that only the history knows (retired
    ones) keep their state. A task is done only through its epic's passing test run (FR-3)."""
    state = {}
    for line in lines:
        tid, kind = (line.get("evidence") or {}).get("task"), line.get("kind")
        if not tid:
            continue
        if kind == "task_done":
            state[tid] = "done"
        elif kind == "blocked":
            state[tid] = "blocked"
        elif kind == "unblock":
            state.pop(tid, None)
    for t in tasks_of(root, slug):
        if t["id"] not in state:
            state[t["id"]] = "ready" if all(state.get(d) == "done" for d in t["deps"]) else "pending"
    return state


def epic_list(root, slug):
    """[{"id", "title", "tasks": [task]}] in file order."""
    out = {}
    for t in tasks_of(root, slug):
        out.setdefault(t["epic"], {"id": t["epic"], "title": t["heading"], "tasks": []})["tasks"].append(t)
    return list(out.values())


def epics(root, slug, lines):
    """{E-n: (state, failed runs)} (CT-4), the spec's state table "Epic" read from the `claim`, `epic_test`, `blocked`,
    `unblock` and `task_done` lines: closed once every task is done and a passing run follows its last claim; an epic
    whose tasks are all done with no passing run since (an in-flight one, FR-44) reads `testing`. An old `epic` line (its
    implementation jury closed it) closes it too. Unblocking resets the failed runs."""
    st, out = status(root, slug, lines), {}
    for e in epic_list(root, slug):
        state, runs, passed = "waiting", 0, False
        for x in lines:
            ev = x.get("evidence") or {}
            if ev.get("epic") != e["id"] or ev.get("task"):
                continue
            kind = x["kind"]
            if kind == "claim":
                state, passed = "claimed", False
            elif kind == "epic_test":
                passed = bool(ev.get("passed"))
                runs, state = (runs, state) if passed else (runs + 1, "failed")
            elif kind == "epic":
                passed = True
            elif kind == "blocked":
                state = "blocked"
            elif kind == "unblock":
                state, runs = "waiting", 0
        done = all(st[t["id"]] == "done" for t in e["tasks"])
        if done and passed:
            state = "closed"
        elif done and state in ("waiting", "claimed"):
            state = "testing"
        out[e["id"]] = (state, runs)
    return out


def claimed(state):
    """{E-n: its claim} in state.json: `{"run", "pack", "worktree"?, "worktrees"?}`."""
    return dict(state["claims"].get("epics") or {})


def pending_epic(root, slug, lines, held=()):
    """(the first epic a claim may take, in file order: waiting, failed or testing, not claimed, its tasks' dependencies
    outside it done; why none is, else "")."""
    st, why, other = status(root, slug, lines), "", ""
    states = epics(root, slug, lines)
    of = {t["id"]: t["epic"] for t in tasks_of(root, slug)}
    for e in epic_list(root, slug):
        s = states[e["id"]][0]
        if e["id"] in held or s not in ("waiting", "failed", "testing"):
            other = other or (f"{e['id']} is claimed" if e["id"] in held else f"{e['id']} is {s}" if s != "closed" else "")
            continue
        waits = [d for t in e["tasks"] if st[t["id"]] != "done" for d in t["deps"] if of.get(d) != e["id"] and st.get(d) != "done"]
        if waits:
            why = why or f"{e['id']} waits on {of.get(waits[0], waits[0])}"
            continue
        return e, ""
    return None, why or other


def nest(lines):
    """Markdown lines with every heading one level down, so a part sits under its own `## ` heading."""
    return [f"#{x}" if x.startswith("#") else x for x in lines]


def defs(path):
    """{ID: its lines} of the `**AC-n**` and `### CT-n` / `### TC-n` items in a spec or plan file; {} when it is missing."""
    return {i: ls for i, ls in spec.items(records.parse(path)[1])} if path.exists() else {}


def finding_lines(root, slug, shown):
    """What a fix task's worker has to go on: its finding's situations (a CLI finding's hold the check's errors) and the
    fix asked, indented so an error line can't read as a heading. Nothing when `shown` has no `From:` a ledger holds."""
    from nio import jury
    m = next((m for x in shown if x.startswith("- From: ") and (m := tasks.FINDING.match(x[8:]))), None)
    f = m and next((g for g in jury.load(root, slug, m[2])["findings"] if g["id"] == m[1]), None)
    if not f:
        return []
    said = [f"- situation ({s['lens']}): " + s["situation"].replace("\n", "\n  ") for s in f["sources"]]
    return ["", "#### The finding", *said, *[f"- fix asked: {f['fix']}"] * bool(f["fix"])]


def worker_pack(root, slug, eid, heading, mine, failed=None):
    """The epic's pack (CT-1, FR-2, FR-42): exactly five `## ` parts, in order: its memory pack (no closing instructions,
    the card carries them), its undone tasks' sections of tasks.md, the ACs they serve, the CT-n blocks their TC-n entries
    cover, and those TC-n entries; a sixth, `## Last failed run`, after a failed run: its cause, failing tests and output
    tail. No handoff format: the card carries it."""
    folder = root / ".nio/specs" / slug
    files = list(dict.fromkeys(f for t in mine for f in t["files"]))
    serves = list(dict.fromkeys(a for t in mine for a in t["serves"]))
    memory, _ = pack.build(root, heading, files, serves, eid, worker=False, reader="worker", slug=slug)
    memory, sep, docs = memory.partition("## Project docs\n")
    acs, cts, tcs = defs(folder / "spec.md"), defs(folder / "contracts.md"), defs(folder / "tests.md")
    tests = list(dict.fromkeys(i for t in mine for i in t["tests"] if i in tcs))
    covers = list(dict.fromkeys(c for t in tests for c in tasks.ids(plan.field(tcs[t], "Covers")) if c in cts))
    block = lambda ids, found: [x for i in ids if i in found for x in found[i]]
    body = lambda name, lines: [f"## {name}", ""] + nest("\n".join(lines).strip().splitlines()) + [""]
    shown = []
    for t in mine:
        part = [x for x in tasks.show(root, slug, t["id"]) if not x.startswith("- Mode:")]
        shown += (part if not shown else part[2:]) + finding_lines(root, slug, part) + [""]
    out = nest(memory.rstrip().splitlines()) + [""]
    if sep:  # the docs sit in the first part: their headings are already nested
        out = nest(memory.rstrip().splitlines()) + ["", "### Project docs"] + docs.partition("\n## ")[0].rstrip().splitlines() + [""] + nest(("## " + docs.partition("\n## ")[2]).splitlines() if "\n## " in docs else [])  # the pack's `# Memory for E-n` becomes its part's heading
    last = body("Last failed run", [f"- cause: {failed['cause']}", f"- failing: {', '.join(failed.get('failing') or []) or 'not read'}",
                                    "- output tail:", *[f"    {x}" for x in failed.get("tail") or []]]) if failed else []
    return "\n".join(out + body("Tasks", shown or [heading, "", "Every task is done: the flow runs the epic's tests."])
                     + body("Acceptance criteria", block(serves, acs)) + body("Contracts", block(covers, cts))
                     + body("Tests", block(tests, tcs)) + last).rstrip() + "\n"


def branch(slug):
    return f"nio/{slug}"


def named_files(root, output):
    """The project files a command's output names, relative to the root, in order: the module behind an error."""
    out, real = [], Path(root).resolve()
    for tok in re.findall(r"[\w./-]+\.\w+", output):
        p = Path(tok)
        p = p.resolve().relative_to(real) if p.is_absolute() and p.resolve().is_relative_to(real) else p
        if not p.is_absolute() and (real / p).is_file() and str(p) not in out:
            out.append(str(p))
    return out


def start_stage(root, slug, state):
    """The first claim's start of the stage (CT-5, FR-16, FR-20, FR-35, FR-36, FR-46): onto `nio/<slug>`, then the
    baseline line; or a `pause` line naming why the stage waits, with no baseline, so the next claim starts it again.
    Returns (the line, the state it leaves, why the stage waits or "")."""
    if records.git(root, "branch", "--show-current")[0:1] != [branch(slug)]:
        exists = records.git(root, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch(slug)}")
        code, _, err = records.git(root, "checkout", *([] if exists else ["-b"]), branch(slug), full=True)
        if code:
            raise ValueError(f"can't switch to {branch(slug)}: {err.strip()}")
    cfg = records.config(root)
    why = ""
    if not (cfg.get("tests") or {}).get("suite"):
        why = "tests.suite not set"
    else:
        r = suite(root, cfg)
        if r["broken"]:
            error = r["cause"] or wrong_reason(r["runner"], r["code"], r["output"])
            where = named_files(root, r["output"])[:1]  # the module that failed to import, for the human
            why = f"the suite is broken before the first task: {error}" + "".join(f" in {f}" for f in where)
        elif r["runner"] is None and r["code"] != 0:
            why = "the baseline fails and its runner is unknown"
    if why:
        return flow.stop_line({"kind": "pause", "why": why, "waiting": {"why": why}}, "implementing", state) + (why,)
    ev = {k: r[k] for k in ("command", "code", "failing", "collected")}
    line = {"kind": "baseline", "from": "implementing", "to": "implementing",
            "evidence": {**ev, "runner": r["runner"] or "unknown", "output": r["output_hash"]}}
    return line, {**state, "waiting": None}, ""


# run folders and the index, never committed; memory records (a spec problem's change record), the human's to commit:
# so never a task's change, nor a dirty tree
SCRATCH = (".nio/runs/", ".nio/cache/", ".nio/memory/")


def porcelain(root):
    """[(git's two-letter status, path)] of every uncommitted path, untracked files included."""
    rows = records.git(root, "status", "--porcelain", "--untracked-files=all")
    return [(x[:2], x[3:].split(" -> ")[-1].strip('"')) for x in rows]


def outside(slug, paths):
    """The paths outside the effort folder and nio's scratch folders: the ones a task may change."""
    return [p for p in paths if not p.startswith(f".nio/specs/{slug}/") and not p.startswith(SCRATCH)]


def dirty(root, slug):
    """The uncommitted paths outside the effort folder (FR-22)."""
    return outside(slug, [p for _, p in porcelain(root)])


def clean(root, slug):
    """Refuse, recording nothing, while the main tree has uncommitted changes outside the effort folder (FR-22, FR-14)."""
    if left := dirty(root, slug):
        raise ValueError("uncommitted changes outside the effort folder:" + "".join(f"\n  {p}" for p in left))


def guard(root, slug, state, lines, started):
    """CT-5's refusals, in its order; each raises ValueError and nothing is recorded (FR-2, FR-3, FR-20)."""
    if not any(s == "tasks_jury" for _, _, s in flow.commits(root, slug)):
        raise ValueError('tasks not approved: no "nio: approve tasks" commit')
    stage = flow.where(root, slug, state, lines)["stage"]
    if stage != "implementing":
        raise ValueError(f"{slug} is at {stage}, not implementing")
    now = (records.git(root, "branch", "--show-current") or ["(detached)"])[0]
    if started and now != branch(slug):
        raise ValueError(f"on {now}, not {branch(slug)}")


def parallel(root):
    n = (records.config(root).get("budgets") or {}).get("parallel", 2)
    if type(n) is not int or n < 1:
        raise ValueError(f"budgets.parallel must be a whole number of at least 1, not {n!r}")
    return n


def epic_tests(root, slug, mine):
    """(the command built from the epic's TCs through the suite's runner, else None; the test files those TCs name;
    whether its tasks name any test at all, FR-10). A `Test:` that is `none` or empty names none."""
    from nio import evidence
    tcs = list(dict.fromkeys(i for t in mine for i in t["own"]))
    words = [t for t in mine if not t["own"] and t["test"].strip().lower() not in ("", "none")]
    known, suite_ = evidence.known_tests(root, slug), (records.config(root).get("tests") or {}).get("suite")
    one = [evidence.one_test(suite_, *known[c]) if known.get(c) else None for c in tcs]
    command = None
    if tcs and not words and all(one):  # one run of every named test: the runner's command, then each test
        command = one[0].rsplit(" ", 1)[0] + " " + " ".join(dict.fromkeys(c.rsplit(" ", 1)[1] for c in one))
    files = list(dict.fromkeys(f for t in mine for f in test_files(root, slug, t)))
    return command, files, bool(tcs or words)


def then_line(root, slug, eid, mine, by):
    command = epic_tests(root, slug, mine)[0]
    run = "" if command else ' --run "<the command: from the agent\'s hand-off>"'
    return f"then: nio flow finish {slug} {eid}{run} {flow.by_arg(by)}"


def claim(root, slug=None, by=None, epic=None):
    """`nio flow claim` (CT-1, CT-24, FR-1, FR-2, FR-9, FR-32, FR-43, FR-44): claim the next epic (or `epic`), starting
    the stage first when it has no baseline; print the epic, its undone tasks, the worker card for its tier, its effort,
    its pack and the command that hands it back. A second epic claimed meanwhile gets its own worktree. An old task or
    wave claim is read as its epic's. Returns (code, lines)."""
    slug = flow.pick(root, slug)
    flow.refuse(root, slug)
    w = flow.who(by)
    with flow.lock(root, slug):
        state, lines = flow.load(root, slug)
        started = any(x["kind"] == "baseline" for x in lines)
        guard(root, slug, state, lines, started)
        states, held = epics(root, slug, lines), claimed(state)
        if epic and epic not in states:
            raise ValueError(f"no {epic} in tasks.md")
        if b := next((e for e, (s, _) in states.items() if s == "blocked" and epic in (None, e)), None):
            return 1, [f'{b} is blocked: nio flow unblock {slug} {b} --human "<reason>" --by human']
        if state["abandon"] is not None or state["pause"] or started and state["waiting"]:
            return 1, flow.talk(slug, flow.where(root, slug, state, lines))  # a blocked task holds the stage (AC-23)
        old = state["claims"].get("task")
        if not held and not old and all(s != "failed" for s, _ in states.values()):
            clean(root, slug)  # a failed epic's work stays in the tree for its next agent
        base = []
        if not started:
            entry, state, why = start_stage(root, slug, state)
            if why:
                flow.write(root, slug, [entry], state, w, "implementing")
                return 1, flow.talk(slug, flow.where(root, slug))
            base = [entry]
        gate = open_gate(root, slug, lines)
        if gate:
            return 1, [f"{gate} is finished but its gate is open: run @nio:jury on implementation-{gate}, then `nio flow done implementation-{gate}`"]
        st, info = status(root, slug, lines), {}
        if old:  # FR-44: the old task or wave claim is its epic's; its worktrees are landed by `finish`
            wave = state["claims"].get("wave") or [old]
            e = next(x for x in epic_list(root, slug) if any(t["id"] == old for t in x["tasks"]))
            names = [next((x["evidence"].get("worktree") for x in reversed(lines) if x["kind"] == "claim" and
                           x["evidence"].get("task") == tid), None) for tid in wave]
            info["worktrees"] = [n for n in names if n and (root / n).is_dir()]
            held, out = {}, [f"{e['id']} is claimed already (an old claim of {', '.join(wave)}): it is now the epic's claim"]
        elif epic:
            if epic in held or states[epic][0] == "claimed":
                raise ValueError(f"{epic} is claimed")
            if states[epic][0] == "closed":
                raise ValueError(f"{epic} is closed")
            e, why = pending_epic(root, slug, lines, held | {x: 1 for x in states if x != epic})
            if not e:
                raise ValueError(f"no epic ready; {why}")
            out = []
        else:
            if len(held) >= parallel(root):
                raise ValueError(f"no epic ready; {', '.join(held)} claimed, budgets.parallel is {parallel(root)}")
            e, why = pending_epic(root, slug, lines, held)
            if not e:
                raise ValueError("no epic left: every epic is closed" if all(s == "closed" for s, _ in states.values())
                                 else f"no epic ready; {why}")
            out = []
        eid = e["id"]
        mine = [t for t in e["tasks"] if st[t["id"]] != "done"]
        head = records.git(root, "rev-parse", "HEAD")[0]
        prev = [x for x in lines if x["kind"] == "claim" and (x.get("evidence") or {}).get("epic") == eid]
        tests_ = [x["evidence"] for x in lines if x["kind"] == "epic_test" and x["evidence"].get("epic") == eid]
        failed = tests_[-1] if tests_ and not tests_[-1].get("passed") else None
        made = []
        try:
            rid = records.new_run(root, {"effort": slug, "task": eid,
                                         "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
            path = pack.save(root, rid, eid, worker_pack(root, slug, eid, e["title"], mine, failed))
            tree = prev and prev[-1]["evidence"].get("worktree")
            tree = tree if tree and (root / tree).is_dir() else None  # a failed epic's tree is reused: its work is there
            if (held or tree) and "worktrees" not in info:  # FR-43: a second epic works in its own tree
                if not tree:
                    full = root / ".nio/runs" / rid / "worktree"
                    code, _, err = records.git(root, "worktree", "add", "--detach", str(full), head, full=True)
                    if code:
                        raise ValueError(f"can't create a worktree for {eid}: {err.strip()}")
                    made.append(full)
                    tree = str(full.relative_to(root))
                info["worktree"] = tree
            info.update(run=rid, pack=str(path.relative_to(root)))
            ev = {"epic": eid, "tasks": [t["id"] for t in mine], "commit": head, "run": rid,
                  **{k: info[k] for k in ("worktree", "worktrees") if k in info}}
            claims = {"epics": {**held, eid: info}}
            flow.write(root, slug, base + [{"kind": "claim", "from": "implementing", "to": "implementing", "evidence": ev}],
                       {**state, "claims": claims}, w, "implementing")
        except BaseException:  # CT-24: a failed claim leaves no worktree it made
            for m in made:
                records.git(root, "worktree", "remove", "--force", str(m), full=True)
            raise
    tier = e["tasks"][0]["tier"] if e["tasks"] else ""
    head_line = f"epic: {eid} {e['title']}" if mine else f"epic: {eid} (every task done: run its tests)"
    out += [head_line, f"tasks: {', '.join(t['id'] for t in mine) or 'none'}", f"card: nio-worker-{tier or 'strong'}",
            f"effort: {e['tasks'][0]['effort'] if e['tasks'] else ''}", f"pack: {info['pack']}", then_line(root, slug, eid, e["tasks"], by)]
    out += [f"worktree: {x}" for x in [info.get("worktree"), *info.get("worktrees", [])] if x]
    return 0, out


def land(root, slug, tid, tree, since):
    """Apply a wave task's worktree changes since its claim commit `since`, untracked files included, to the main tree
    (CT-4). Returns (the patch, saved next to the worktree; {path: its main-tree bytes before, None when absent};
    git's error or "", the main tree untouched on an error). The effort's state and history are never applied."""
    keep = [f".nio/specs/{slug}/state.json", f".nio/specs/{slug}/history.jsonl"]
    records.git(tree, "add", "-A")
    code, diff, err = records.git(tree, "diff", "--cached", "--binary", "--no-renames", since, raw=True, full=True)
    if code:
        return "", {}, err.strip() or "git diff failed"
    path = tree.parent / f"{tid}.patch"
    path.write_bytes(diff)
    names = [p for p in records.git(tree, "-c", "core.quotepath=off", "diff", "--cached", "--name-only", "--no-renames", since) if p not in keep]
    saved = {p: (root / p).read_bytes() if (root / p).is_file() else None for p in names}
    code, _, err = records.git(root, "apply", "--binary", *[f"--exclude={p}" for p in keep], str(path), full=True) \
        if names else (0, "", "")
    return str(path.relative_to(root)), saved, err.strip() or "git apply failed" if code else ""


def restore(root, saved):
    """Put each path `land` saved back to its bytes before the apply, deleting one that didn't exist."""
    for p, b in saved.items():
        (root / p).write_bytes(b) if b is not None else (root / p).unlink(missing_ok=True)


# --- the hand-back, its test run and the epic's commit (CT-2, CT-3, CT-4) ---

PLAN_FILES = ("spec.md", "tasks.md", "plan.md", "contracts.md", "tests.md", "quickstart.md", "architecture.md")  # FR-25


def entry(kind, tid, reason=None, **ev):
    """A task history line: from and to both `implementing`, its fields under `evidence` (CT-4)."""
    line = {"kind": kind, "from": "implementing", "to": "implementing", "evidence": {"task": tid, **ev}}
    return {**line, "reason": reason} if reason is not None else line


def epic_line(kind, eid, **ev):
    """An epic's history line (CT-4): `claim`, `epic_test`, `blocked` or `unblock`."""
    return {"kind": kind, "from": "implementing", "to": "implementing", "evidence": {"epic": eid, **ev}}


def changed(root, since):
    """Every path changed between commit `since` and the working tree, untracked files included."""
    paths = records.git(root, "diff", "--name-only", since) + [p for c, p in porcelain(root) if c == "??"]
    return list(dict.fromkeys(p.strip('"') for p in paths))


def digest(root, path):
    """A file's sha256; "" when it is gone."""
    p = root / path
    return flow.sha(p.read_bytes()) if p.is_file() else ""


def test_files(root, slug, task):
    """The test files the task's TC-n entries name in their `File:` lines (FR-43)."""
    tcs = defs(root / ".nio/specs" / slug / "tests.md")
    found = [f.split(":")[0] for t in task["own"] if t in tcs for f in re.findall(r"`([^`]+)`", plan.field(tcs[t], "File"))]
    return list(dict.fromkeys(found))


def finish(root, slug, eid, command=None, by=None):
    """`nio flow finish` (CT-2, FR-3, FR-4, FR-10, FR-42, FR-44, NFR-1): the agent handed the epic back; the flow runs
    the tests its tasks name once, itself, on the main tree (a worktree epic's changes landed there first) within
    EPIC_LIMIT. A pass writes the `epic_test` line and commits the epic (CT-3); a failed, broken, empty or hung run keeps
    it open, records its cause, failing tests and output tail, and counts one failed run: the third blocks the epic for
    the human. The agent's word never counts. Returns (code, lines)."""
    flow.refuse(root, slug)
    w = flow.who(by)
    rec = flow.live_run(root / ".nio/specs" / slug / "running.json")
    if rec and rec.get("pid") != os.getpid() and re.search(rf"\bflow finish\b.*\s{eid}(\s|$)", rec.get("command", "")):
        raise ValueError(f"{eid}'s tests are running")
    with flow.lock(root, slug):
        state, lines = flow.load(root, slug)
        states, held = epics(root, slug, lines), claimed(state)
        if eid not in states:
            raise ValueError(f"no {eid} in tasks.md")
        if states[eid][0] == "closed":
            raise ValueError(f"{eid} is closed")
        if eid not in held:
            raise ValueError(f"{eid} is not claimed")
        e = next(x for x in epic_list(root, slug) if x["id"] == eid)
        st = status(root, slug, lines)
        mine = [t for t in e["tasks"] if st[t["id"]] != "done"]
        built, files, any_test = epic_tests(root, slug, e["tasks"])
        if not any_test:
            raise ValueError(f"{eid} has no test to run")
        if command:
            if missing := [f for f in files if f not in command]:
                raise ValueError(f"the command doesn't run {missing[0]}")
        elif built:
            command = built
        else:
            raise ValueError(f"{eid}'s tests can't be built from its TCs: hand the command over with --run")
        since = next(x["evidence"]["commit"] for x in reversed(lines) if x["kind"] == "claim" and x["evidence"].get("epic") == eid)
        trees = [root / x for x in [held[eid].get("worktree"), *held[eid].get("worktrees", [])] if x and (root / x).is_dir()]
        if trees:
            clean(root, slug)  # FR-14: the apply and its restore must not mix with the human's edits
        folder = f".nio/specs/{slug}/"
        saved = {}
        for tree in trees:
            patch, more, err = land(root, slug, eid, tree, since)
            saved = {**more, **saved}
            if err:
                restore(root, saved)
                raise ValueError(f"{eid}'s changes in {tree.relative_to(root)} don't apply: {err}")
        edited = [p[len(folder):] for p in [*changed(root, since), *saved] if p.startswith(folder) and p[len(folder):] in PLAN_FILES]
        if edited:
            restore(root, saved)
            raise ValueError(f"the epic edited {edited[0]}: the spec, plan and tasks are not the agent's")
        code, out, cause = run(root, command, EPIC_LIMIT)
        name = runner(command, out)
        why = cause or wrong_reason(name, code, out) or (f"the command exits {code}" if code else "")
        ev = {"command": command, "passed": not why, "runner": name or "unknown"}
        if why:
            restore(root, saved)
            failing = re.findall(SUMMARY[name][0], out, re.M) if name in SUMMARY else []
            tail, n = out.splitlines()[-TAIL:], states[eid][1] + 1
            entries = [epic_line("epic_test", eid, **ev, cause=why, failing=failing, tail=tail)]
            rest = {k: v for k, v in held.items() if k != eid}
            new = {**state, "claims": {"epics": rest} if rest else {}, "attempts": {**state["attempts"], eid: n}}
            if n >= 3:
                entries.append(epic_line("blocked", eid, cause="runs"))
                new["waiting"] = {"why": f"{eid} blocked after 3 failed test runs", "epic": eid}
            flow.write(root, slug, entries, new, w, "implementing")
            return 1, [f"{eid} failed (run {n} of 3): {why}", f"failing: {', '.join(failing) or 'not read'}", *tail] + \
                [f"blocked: {eid} after 3 failed test runs; the human unblocks it"] * (n >= 3)
        try:
            sha, report = commit(root, slug, e, mine, w, epic_line("epic_test", eid, **ev), list(saved) if trees else None)
        except Exception:
            restore(root, saved)
            raise
        for tree in trees:
            records.git(root, "worktree", "remove", "--force", str(tree), full=True) if sha else restore(root, saved)
    if sha:
        return 0, [f"closed: {eid} {sha}"] + report
    return 1, [flow.load(root, slug)[0]["waiting"]["why"], f"{eid} stays claimed; `nio flow finish {slug} {eid}` retries"]


def commit(root, slug, epic, mine, who, test, landed=None):
    """CT-3, FR-11: one `E-n: <heading>` commit on the effort branch holding the passing `epic_test` line, a `task_done`
    line per undone task, the `pass` to the pr gate once every epic is closed, the tracked changes outside the effort
    folder (or the paths `landed` from a worktree), the untracked paths the epic's tasks list (or that sit under a listed
    folder), the test files its TCs name, and history.jsonl and state.json; nothing else. Returns (the sha, the report).
    A refused commit puts history.jsonl, state.json and the index back, writes a `fail` line with git's error, sets
    `waiting` and returns (None, []). Never merges, rebases or pushes."""
    eid = epic["id"]
    if records.git(root, "branch", "--show-current") != [branch(slug)]:
        raise ValueError(f"not on {branch(slug)}: {eid} is not committed")  # FR-20
    folder = root / ".nio/specs" / slug
    sp, hp, np = folder / "state.json", folder / "history.jsonl", folder / "state.json.new"
    kept, saved = hp.read_bytes(), sp.read_bytes()
    code, tree, err = records.git(root, "write-tree", full=True)
    if code:
        raise ValueError(err.strip())
    state, lines = flow.load(root, slug)
    parent = records.git(root, "rev-parse", "HEAD")[0]
    entries = [test] + [entry("task_done", t["id"], branch=branch(slug), parent=parent) for t in mine]
    rest = {k: v for k, v in claimed(state).items() if k != eid}
    last = all(s == "closed" for s, _ in epics(root, slug, lines + entries).values())
    if last:
        entries.append({"kind": "pass", "from": "implementing", "to": "pr", "evidence": {"paths": [f".nio/specs/{slug}/tasks.md"]}})
    waiting = None if (state["waiting"] or {}).get("epic") == eid else state["waiting"]
    flow.write(root, slug, entries, {**state, "claims": {"epics": rest} if rest else {}, "waiting": waiting,
                                     "attempts": {k: v for k, v in state["attempts"].items() if k != eid}}, who, "implementing")
    listed = [f for t in epic["tasks"] for f in t["files"]] + [f for t in epic["tasks"] for f in test_files(root, slug, t)]
    mark = lambda p: any(p == f or p.startswith(f.rstrip("/") + "/") for f in listed)
    flows = [f".nio/specs/{slug}/history.jsonl", f".nio/specs/{slug}/state.json"]
    if landed is None:
        new = [p for c, p in porcelain(root) if c == "??" and outside(slug, [p]) and mark(p)]
        steps = [["add", "-u", "--", ".", f":(exclude).nio/specs/{slug}", *[f":(exclude){s}" for s in SCRATCH]]]
        steps += [["add", "--", *new]] * bool(new)
    else:
        steps = [["add", "-A", "--", *outside(slug, landed)]] * bool(outside(slug, landed))
    for args in steps + [["add", "--", *flows], ["commit", "-q", "-m", f"{eid}: {epic['title']}"]]:
        code, _, err = records.git(root, *args, full=True)
        if code:
            hp.write_bytes(kept)
            sp.write_bytes(saved)
            np.unlink(missing_ok=True)
            records.git(root, "read-tree", tree.strip(), full=True)
            err = err.strip() or f"git {args[0]} failed"
            flow.write(root, slug, [epic_line("fail", eid, output=err)], {**state, "waiting": {"why": f"commit failed: {err.splitlines()[0]}", "epic": eid}},
                       who, "implementing")
            return None, []
    sha = records.git(root, "rev-parse", "HEAD")[0]
    if not last:
        return sha, [f"next: nio flow claim {slug}"]
    # the last epic: the effort moves to the pr gate, a new unit in a fresh driver (FR-2, FR-8)
    return sha, [f"next: end this unit; the pr gate runs in a fresh driver started from `nio flow brief {slug}` alone",
                 f"notify: the human: every epic of {slug} is closed; the pr gate judges the whole effort diff next"]


def left(root, slug, lines):
    """What keeps implementing's guard from passing (CT-14): each task not done, each epic whose tasks are all done but
    whose tests haven't passed since (FR-44; not once the effort moved past implementing), then each epic still in its
    old implementation jury with no `epic` line; [] when the stage is finished."""
    st, ts = status(root, slug, lines), tasks_of(root, slug)
    out = [f"{t['id']} is {st[t['id']]}: needs " + ("the human to unblock it" if st[t["id"]] == "blocked" else f"{t['epic']} closed by `nio flow finish`")
           for t in ts if st[t["id"]] != "done"]
    if not any(x["kind"] == "pass" and x["from"] == "implementing" for x in lines):
        out += [f"{e} is testing: needs `nio flow finish`" for e, (s, _) in epics(root, slug, lines).items() if s == "testing"]
    shut = {x["evidence"].get("epic") for x in lines if x["kind"] == "epic"}
    return out + [f"{e} has no epic line" for e in dict.fromkeys(t["epic"] for t in ts) if e not in shut and in_jury(root, slug, e)]


def in_jury(root, slug, epic):
    """An epic already in its old implementation jury when per-epic gates went away: its ledger has a round. It finishes
    that jury, findings kept; any other epic closes on its own test run (2026-11-14-effort-jury FR-12)."""
    from nio import jury
    return bool(jury.load(root, slug, f"implementation-{epic}")["round"])


def open_gate(root, slug, lines):
    """The first epic whose tasks are all done, with no `epic` line, still in its old implementation jury: its gate is
    open (CT-17); None when there is none, or when an earlier epic has work left (a fix task reopened it)."""
    st, ts = status(root, slug, lines), tasks_of(root, slug)
    shut = {x["evidence"].get("epic") for x in lines if x["kind"] == "epic"}
    for e in dict.fromkeys(t["epic"] for t in ts):
        if any(st[t["id"]] != "done" for t in ts if t["epic"] == e):
            return None
        if e not in shut and in_jury(root, slug, e):
            return e
    return None


def unblock(root, slug, target, reason, by):
    """`nio flow unblock` (CT-4, CT-12): a task blocked on a spec problem goes on, or an epic blocked by its 3 failed
    runs goes back to waiting with its failed runs reset; clears `waiting` when it names it. Under auto only the human
    unblocks an epic blocked by its own runs (FR-47). Returns (code, lines)."""
    flow.refuse(root, slug)
    w = flow.who(by, root, slug)
    is_epic = bool(re.fullmatch(r"E-\d+", target))
    with flow.lock(root, slug):
        state, lines = flow.load(root, slug)
        if is_epic:
            now = epics(root, slug, lines).get(target, (None,))[0]
            if now != "blocked":
                raise ValueError(f"{target} is not blocked" if now else f"no {target} in tasks.md")
        else:
            now = status(root, slug, lines).get(target)
            if now != "blocked":
                raise ValueError(f"{target} is {now}" if now else f"no task {target} in tasks.md")
        if not (reason or "").strip():
            raise ValueError("--human needs a reason")
        if is_epic and state["auto"] and w["role"] != "human":  # FR-47: the auto run stops here for the human
            return 1, [f"{target} was blocked by its own 3 failed test runs; only the human unblocks it"]
        key = "epic" if is_epic else "task"
        waiting = None if (state["waiting"] or {}).get(key) == target else state["waiting"]
        attempts = {k: v for k, v in state["attempts"].items() if k != target}
        line = epic_line("unblock", target, reason=reason) if is_epic else entry("unblock", target, reason=reason)
        flow.write(root, slug, [line], {**state, "attempts": attempts, "waiting": waiting}, w, "implementing")
    return 0, [f"unblocked: {target}"]


PARTS = (("spec_says", "What the spec says"), ("code_shows", "What the code shows"), ("smallest_change", "Smallest change"))


def block(root, slug, tid, handoff, by):
    """`nio flow block` (CT-11, FR-23, FR-24, FR-37, AC-48): file a `status: blocked` handoff with a `change_request` as a
    pending change record against the effort's spec.md, write a `blocked` line (`cause: spec`) and set the effort
    waiting. The task's epic stays claimed and its work stays in the tree: after the unblock a fresh agent resumes it
    from `nio flow brief` (CT-4). The record holds `Handoff: <sha256>`: a pending
    one that does is reused and only the steps not yet done are written. No attempt is used. Returns (code, lines)."""
    flow.refuse(root, slug)
    w = flow.who(by)
    bad = ValueError("handoff is not blocked with a change_request")
    path = Path(handoff)
    if not path.is_file():
        raise ValueError(f"no handoff file {handoff}")
    data = path.read_bytes()
    try:
        meta = records.parse(path, data.decode(errors="replace"))[0]
    except ValueError:
        raise bad from None
    cr = meta.get("change_request")
    if meta.get("status") != "blocked" or not isinstance(cr, dict) or not all(str(cr.get(k) or "").strip() for k, _ in PARTS):
        raise bad
    for k, _ in PARTS:
        for ln in str(cr[k]).splitlines():
            if ln.startswith("## ") or ln.strip() == "---":
                raise ValueError(f'the handoff\'s {k} holds the line "{ln}"')
    hsh = flow.sha(data)
    with flow.lock(root, slug):
        state, lines = flow.load(root, slug)
        now = status(root, slug, lines).get(tid)
        mine = [x for x in lines if x["kind"] == "blocked" and x["evidence"].get("task") == tid
                and x["evidence"].get("handoff") == hsh]
        of = next((t["epic"] for t in tasks_of(root, slug) if t["id"] == tid), None)
        if not (now in ("ready", "pending") and of in claimed(state)) and not (now == "blocked" and mine):
            raise ValueError(f"{tid} is {now}" + (f", its epic {of} not claimed" if now in ("ready", "pending") else "")
                             if now else f"no task {tid} in tasks.md")
        found = next((p for p in sorted((root / ".nio/memory").rglob("C-*.md"))
                      if f"Handoff: {hsh}" in p.read_text() and records.parse(p)[0].get("outcome") == "pending"), None)
        kept = found.read_text() if found else ""
        if found is None:
            areas = records.areas(root)
            found = records.new(root, "change", "project" if "project" in areas else areas[0],
                                f"Spec problem in {tid}: " + " ".join(str(cr["spec_says"]).split()).replace("\\", "\\\\"), by=by.strip())  # one line, backslashes escaped like quotes
            head = found.read_text().partition("\n---\n")[0]
            head = re.sub(r'^against: .*$', f'against: ".nio/specs/{slug}/spec.md"', head, flags=re.M)
            body = (f"## What is wrong\nThe spec says: {str(cr['spec_says']).strip()}\n\nThe code shows: {str(cr['code_shows']).strip()}\n"
                    f"## Proposed change\n{str(cr['smallest_change']).strip()}\n\nHandoff: {hsh}\n")
            kept = f"{head}\n---\n{body}## Human decision\nPending.\n"
        found.write_text(kept)
        cid = records.parse(found)[0]["id"]
        if not mine:  # the line and the state it leaves go in one write, so a blocked line means waiting is set too
            line = {**entry("blocked", tid, cause="spec", handoff=hsh), "change": cid}
            flow.write(root, slug, [line], {**state, "waiting": {"why": f"spec problem in {tid}", "task": tid, "change": cid}},
                       w, "implementing")
    return 0, [f"blocked: {tid}", cid]
