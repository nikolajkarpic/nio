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
                         stderr=subprocess.STDOUT, start_new_session=True)
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
}


def runner(command):
    """The known runner a command's own words name, else None: `npm test` or `bash run.sh` read as unknown (CT-2)."""
    return next((n for n, r in RUNNERS.items() if re.search(r["match"], command)), None)


def wrong_reason(name, code, output):
    """"" when a failure may be red's right one; else why not (CT-2, FR-8): a collection, import or syntax error marker
    (pytest exit 2 or 4 too), or that no tests ran (pytest exit 5 too). An unknown runner has no wrong reason (FR-9)."""
    r = RUNNERS.get(name)
    if not r:
        return ""
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
}


def suite(root, cfg, command=None):
    """A full-suite run read into {"command", "code", "cause", "runner", "failing", "collected", "broken",
    "output_hash", "output"} (CT-3, FR-14, FR-16, FR-35, FR-44). `failing` and `collected` are None for a runner without a reader."""
    t = cfg.get("tests") or {}
    if not t.get("suite"):
        raise ValueError("no `tests.suite` in the NIO config")
    command = command or t["suite"]
    code, out, cause = run(root, command, t.get("timeout") or DEFAULT_LIMIT)
    name = runner(command)
    failing = collected = None
    if name in SUMMARY:
        fail, count = SUMMARY[name]
        failing = re.findall(fail, out, re.M)
        m = re.search(count, out, re.M)
        collected = int(m[1]) if m else None
    broken = bool(cause) or wrong_reason(name, code, out).startswith("collection")
    return {"command": command, "code": code, "cause": cause, "runner": name, "failing": failing,
            "collected": collected, "broken": broken, "output_hash": flow.sha(out.encode()), "output": out}


MODES = ("split", "single", "direct")


def tasks_of(root, slug):
    """Every task of tasks.md in epic order then file order, fix tasks included (CT-4): id, title, epic, fix, deps, files,
    serves, tests, tier, effort and mode. The mode is `implement.mode` from the config, else the task's `Mode:`, else
    split (FR-40, C-261029-nbrg)."""
    parsed = tasks.parse("\n".join(records.parse(tasks.path(root, slug))[1]))
    forced = (records.config(root).get("implement") or {}).get("mode")
    out = []
    for e in parsed["epics"]:
        for tid in e["tasks"]:
            t = parsed["tasks"][tid]
            f = t["fields"]
            word = tasks.TIER.match(f.get("Mode", "")).group(1) if f.get("Mode") else ""
            out.append({"id": tid, "title": t["title"], "epic": e["id"], "fix": t["fix"], "deps": tasks.ids(f.get("Depends on", "")),
                        "files": tasks.files(f.get("Files", "")), "serves": tasks.ids(f.get("Serves", "")),
                        "tests": tasks.ids(f.get("Test", "")), "tier": tasks.TIER.match(f["Tier"]).group(1) if f.get("Tier") else "",
                        "effort": f.get("Effort", ""), "parallel": f.get("Parallel") == "yes", "mode": forced or (word if word in MODES else "split")})
    return out


def status(root, slug, lines):
    """{T-n: state} (CT-4, FR-18): the task lines replayed through the spec's Task state table. A task with no line is
    ready when every dependency is done, else pending. Ids that only the history knows (retired ones) keep their state
    (FR-39). A passed review leaves the task green: only its `task_done` line makes it done, so a failed commit stays green."""
    ts = tasks_of(root, slug)
    mode = {t["id"]: t["mode"] for t in ts}
    state = {}
    for line in lines:
        ev, tid = line.get("evidence") or {}, (line.get("evidence") or {}).get("task")
        kind = line.get("kind")
        if not tid:
            continue
        if kind == "review":
            if not ev.get("passed"):
                state[tid] = "claimed" if mode.get(tid) == "direct" else "red"  # FR-45
        elif kind in ("claim", "red", "green", "blocked"):
            state[tid] = {"claim": "claimed", "blocked": "blocked"}.get(kind, kind)
        elif kind == "task_done":
            state[tid] = "done"
        elif kind == "unblock":
            state[tid] = "ready"
    for t in ts:
        if t["id"] not in state:
            state[t["id"]] = "ready" if all(state.get(d) == "done" for d in t["deps"]) else "pending"
    return state


def next_ready(root, slug, lines):
    """The first ready task of the first epic that has a task not done, fix tasks included (CT-4, FR-31); None when it
    has none ready."""
    st = status(root, slug, lines)
    ts = tasks_of(root, slug)
    for epic in dict.fromkeys(t["epic"] for t in ts):
        mine = [t for t in ts if t["epic"] == epic]
        if any(st[t["id"]] != "done" for t in mine):
            return next((t for t in mine if st[t["id"]] == "ready"), None)
    return None


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


def worker_pack(root, slug, task):
    """The task's worker pack (CT-6, FR-4): exactly five `## ` parts, in order: its memory pack (no closing
    instructions, CT-15 replaces them), its section of tasks.md, the ACs it serves, the CT-n blocks its TC-n entries
    cover, and those TC-n entries. No mode and no handoff format: `claim` prints the mode, the card carries the rest."""
    folder = root / ".nio/specs" / slug
    memory, _ = pack.build(root, task["title"], task["files"], task["serves"], task["id"], worker=False)
    acs, cts, tcs = defs(folder / "spec.md"), defs(folder / "contracts.md"), defs(folder / "tests.md")
    tests = [t for t in task["tests"] if t in tcs]
    covers = list(dict.fromkeys(c for t in tests for c in tasks.ids(plan.field(tcs[t], "Covers")) if c in cts))
    block = lambda ids, found: [x for i in ids if i in found for x in found[i]]
    body = lambda name, lines: [f"## {name}", ""] + nest("\n".join(lines).strip().splitlines()) + [""]
    shown = [x for x in tasks.show(root, slug, task["id"]) if not x.startswith("- Mode:")]  # claim prints the mode
    out = nest(memory.rstrip().splitlines()) + [""]  # the pack's `# Memory for T-n` becomes its part's heading
    return "\n".join(out + body("Task", shown + finding_lines(root, slug, shown)) + body("Acceptance criteria", block(task["serves"], acs))
                     + body("Contracts", block(covers, cts)) + body("Tests", block(tests, tcs))).rstrip() + "\n"


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
    """CT-5's refusals, in its order; each raises ValueError and nothing is recorded (FR-2, FR-3, FR-20, FR-22)."""
    if not any(s == "tasks_jury" for _, _, s in flow.commits(root, slug)):
        raise ValueError('tasks not approved: no "nio: approve tasks" commit')
    stage = flow.where(root, slug, state, lines)["stage"]
    if stage != "implementing":
        raise ValueError(f"{slug} is at {stage}, not implementing")
    now = (records.git(root, "branch", "--show-current") or ["(detached)"])[0]
    if started and now != branch(slug):
        raise ValueError(f"on {now}, not {branch(slug)}")
    clean(root, slug)
    if state["claims"].get("task"):
        raise ValueError(f"{state['claims']['task']} is claimed")
    if next_ready(root, slug, lines) is None:
        st = status(root, slug, lines)
        ts = [t for t in tasks_of(root, slug) if st[t["id"]] != "done"]
        if not ts:
            raise ValueError("no task left: every task is done")
        why = next((f"{t['id']} waits on {d}" for t in ts if st[t["id"]] == "pending" for d in t["deps"]
                    if st.get(d) != "done"), f"{ts[0]['id']} is {st[ts[0]['id']]}")
        raise ValueError(f"no ready task; {why}")


def claim(root, slug=None, by=None):
    """`nio flow claim` (CT-5, FR-1 to FR-4, FR-6, FR-7, FR-16, FR-20, FR-22, FR-35, FR-36, FR-40, FR-46): claim the next
    ready task, starting the stage first when it has no baseline; print the task, its mode, the worker card for its
    tier, its effort and its pack. Returns (code, lines)."""
    slug = flow.pick(root, slug)
    flow.refuse(root, slug)
    w = flow.who(by)
    with flow.lock(root, slug):
        state, lines = flow.load(root, slug)
        started = any(x["kind"] == "baseline" for x in lines)
        guard(root, slug, state, lines, started)
        if state["abandon"] is not None or state["pause"] or started and state["waiting"]:
            return 1, flow.talk(slug, flow.where(root, slug, state, lines))  # a blocked task holds the stage (AC-23)
        if t := next((t for t, v in status(root, slug, lines).items() if v == "blocked"), None):
            return 1, [f'{t} is blocked: nio flow unblock {slug} {t} --human "<reason>" --by human']
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
        task = next_ready(root, slug, lines)
        group = wave(root, slug, lines, task)
        head = records.git(root, "rev-parse", "HEAD")[0]
        made, out, claims = [], [], []
        for t in group:
            rid = records.new_run(root, {"effort": slug, "task": t["id"],
                                         "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
            path = pack.save(root, rid, t["id"], worker_pack(root, slug, t))
            ev = {"task": t["id"], "commit": head}
            out += [f"task: {t['id']} {t['title']}", f"mode: {t['mode']}", f"card: nio-worker-{t['tier']}",
                    f"effort: {t['effort']}", f"pack: {path.relative_to(root)}"]
            if len(group) > 1:
                tree = root / ".nio/runs" / rid / "worktree"
                code, _, err = records.git(root, "worktree", "add", "--detach", str(tree), head, full=True)
                if code:
                    for m in made:
                        records.git(root, "worktree", "remove", "--force", str(m), full=True)
                    raise ValueError(f"can't create a worktree for {t['id']}: {err.strip()}")
                made.append(tree)
                ev["worktree"] = str(tree.relative_to(root))
                out.append(f"worktree: {ev['worktree']}")
            claims.append({"kind": "claim", "from": "implementing", "to": "implementing", "evidence": ev})
        mark = {"task": group[0]["id"], **({"wave": [t["id"] for t in group]} if len(group) > 1 else {})}
        flow.write(root, slug, base + claims, {**state, "claims": mark}, w, "implementing")
    return 0, out


def wave(root, slug, lines, first):
    """The tasks one claim takes (CT-1, FR-1 to FR-3, FR-15): `first`, then the epic's following ready `Parallel: yes`
    tasks in file order, at most `budgets.parallel` (2 when unset) in all; just `first` when it isn't parallel."""
    n = (records.config(root).get("budgets") or {}).get("parallel", 2)
    if type(n) is not int or n < 1:
        raise ValueError(f"budgets.parallel must be a whole number of at least 1, not {n!r}")
    if n == 1 or not first["parallel"]:
        return [first]
    st, ts = status(root, slug, lines), tasks_of(root, slug)
    after = ts[[t["id"] for t in ts].index(first["id"]) + 1:]
    return [first] + [t for t in after if t["epic"] == first["epic"] and t["parallel"] and st[t["id"]] == "ready"][:n - 1]


def release(claims, tid):
    """`claims` without `tid` (CT-1): a wave keeps its other tasks, the first left leading; {} once none is left."""
    left = [t for t in claims.get("wave", []) if t != tid]
    return {"task": left[0], "wave": left} if left else {}


def land(root, slug, tid, tree, since):
    """Apply a wave task's worktree changes since its claim commit `since`, untracked files included, to the main tree
    (CT-4). Returns (the patch, saved next to the worktree; {path: its main-tree bytes before, None when absent};
    git's error or "", the main tree untouched on an error). The effort's state and history are never applied."""
    keep = [f".nio/specs/{slug}/state.json", f".nio/specs/{slug}/history.jsonl"]
    records.git(tree, "add", "-A")
    diff = records.git(tree, "diff", "--cached", "--binary", "--no-renames", since, full=True)[1]
    path = tree.parent / f"{tid}.patch"
    path.write_text(diff)
    names = [p for p in records.git(tree, "-c", "core.quotepath=off", "diff", "--cached", "--name-only", "--no-renames", since) if p not in keep]
    saved = {p: (root / p).read_bytes() if (root / p).is_file() else None for p in names}
    code, _, err = records.git(root, "apply", "--binary", *[f"--exclude={p}" for p in keep], str(path), full=True) \
        if names else (0, "", "")
    return str(path.relative_to(root)), saved, err.strip() or "git apply failed" if code else ""


def restore(root, saved):
    """Put each path `land` saved back to its bytes before the apply, deleting one that didn't exist."""
    for p, b in saved.items():
        (root / p).write_bytes(b) if b is not None else (root / p).unlink(missing_ok=True)


def worktree(root, lines, tid):
    """The absolute worktree the task's latest claim line names, None when it names none or the folder is gone (CT-2)."""
    name = next((x["evidence"].get("worktree") for x in reversed(lines) if x["kind"] == "claim" and x["evidence"].get("task") == tid), None)
    return root / name if name and (root / name).is_dir() else None


# --- red, green, review, attempts and unblock (CT-7, CT-8, CT-10, CT-12) ---

PLAN_FILES = ("spec.md", "tasks.md", "plan.md", "contracts.md", "tests.md", "quickstart.md", "architecture.md")  # FR-25


def entry(kind, tid, reason=None, **ev):
    """A task history line: from and to both `implementing`, its fields under `evidence` (CT-4)."""
    line = {"kind": kind, "from": "implementing", "to": "implementing", "evidence": {"task": tid, **ev}}
    return {**line, "reason": reason} if reason is not None else line


def since_claim(lines, tid):
    """The task's own lines from its latest claim on: a claim after an unblock starts afresh (FR-38)."""
    mine = [x for x in lines if (x.get("evidence") or {}).get("task") == tid]
    at = max((i for i, x in enumerate(mine) if x["kind"] == "claim"), default=0)
    return mine[at:]


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
    found = [f.split(":")[0] for t in task["tests"] if t in tcs for f in re.findall(r"`([^`]+)`", plan.field(tcs[t], "File"))]
    return list(dict.fromkeys(found))


def limit(root):
    return (records.config(root).get("tests") or {}).get("timeout") or DEFAULT_LIMIT


def shelve(root, slug, run, tid, tree=None):
    """Save the task's uncommitted changes outside the effort folder (`git diff HEAD` plus untracked files) as
    `.nio/runs/<run>/T-n.patch` of the main tree, then restore those paths to HEAD (CT-10). `tree` is the task's
    worktree, when it has one. Returns the patch's path."""
    main, root = root, tree or root
    keep = (lambda p: not p.startswith(SCRATCH) and not p.startswith(f".nio/specs/{slug}/") or  # a worktree is removed: keep
            p.startswith(f".nio/specs/{slug}/") and p.rsplit("/", 1)[-1] not in ("state.json", "history.jsonl")) \
        if tree else (lambda p: bool(outside(slug, [p])))  # its effort-folder edits too
    rows = [(c, p) for c, p in porcelain(root) if keep(p)]
    paths = [p for _, p in rows]
    diff = ""
    if paths:
        if new := [p for c, p in rows if c == "??"]:
            records.git(root, "add", "-N", "--", *new)  # so `git diff` shows untracked files too
        diff = records.git(root, "diff", "HEAD", "--binary", "--", *paths, full=True)[1]
    path = main / ".nio/runs" / run / f"{tid}.patch"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(diff)  # written before anything is restored: the work is never only in the tree
    for p in paths:
        if records.git(root, "cat-file", "-e", f"HEAD:{p}", full=True)[0] == 0:
            records.git(root, "checkout", "-q", "HEAD", "--", p)
        else:
            records.git(root, "rm", "-q", "--cached", "--ignore-unmatch", "--", p)
            (root / p).unlink(missing_ok=True)
    if tree:
        records.git(main, "worktree", "remove", "--force", str(tree), full=True)
    return str(path.relative_to(main))


def run_of(root, slug, lines, tid):
    """The run of the task's latest claim, else a new one: where its patch goes."""
    return next((x.get("run") for x in reversed(since_claim(lines, tid)) if x["kind"] == "claim"), "") \
        or records.new_run(root, {"effort": slug, "task": tid})


def attempt(root, slug, state, lines, tid, line):
    """(lines, state) for a refusal or failed review `line` (CT-10, FR-26, FR-37): one attempt more; the third shelves
    the task's changes as a patch, blocks it, clears the claim and sets the effort waiting, auto flag on or off."""
    n = state["attempts"].get(tid, 0) + 1
    state = {**state, "attempts": {**state["attempts"], tid: n}}
    if n < 3:
        return [line], state
    patch = shelve(root, slug, run_of(root, slug, lines, tid), tid, worktree(root, lines, tid))
    why = f"{tid} blocked after 3 attempts"
    return [line, entry("blocked", tid, cause="attempts", patch=patch)], \
        {**state, "claims": release(state["claims"], tid), "waiting": {"why": why, "task": tid}}


def refused(root, slug, state, lines, tid, step, command, why, w):
    """Write a guard refusal and its attempt (FR-37); (1, what to print)."""
    entries, state = attempt(root, slug, state, lines, tid, entry("refused", tid, step=step, command=command, cause=why))
    flow.write(root, slug, entries, state, w, "implementing")
    return 1, [f"refused: {why}"] + said(entries)


def said(entries):
    """The block an attempt caused, for the human."""
    ev = entries[-1]["evidence"]
    return [f"blocked: {ev['task']} after 3 attempts; its changes are in {ev['patch']}"] if entries[-1]["kind"] == "blocked" else []


def task_for(root, slug, lines, tid, allowed):
    """(task, state) for red or green; refuses, recording nothing, when the state table forbids it (FR-32)."""
    now = status(root, slug, lines).get(tid)
    if now is None:
        raise ValueError(f"no task {tid} in tasks.md")
    task = next((t for t in tasks_of(root, slug) if t["id"] == tid), None)
    if now not in allowed or task is None:
        raise ValueError(f"{tid} is {now}")
    return task, now


def by_worker(task, w, step):
    """Only single mode takes red and green from its worker; the orchestrator reports them otherwise (CT-15, FR-42)."""
    if w["role"] == "worker" and task["mode"] != "single":
        raise ValueError(f"{task['id']} is in {task['mode']} mode: only single mode takes {step} from its worker")


def red(root, slug, tid, command, by):
    """`nio flow red` (CT-7, FR-8 to FR-11, FR-32, FR-37, FR-41 to FR-44): run the command; accept red only on a failure
    for the right reason, freezing the files changed since the claim (the first red picks them; a later one re-hashes
    the same ones). A guard refusal writes a `refused` line and costs an attempt. Returns (code, lines)."""
    flow.refuse(root, slug)
    w = flow.who(by)
    with flow.lock(root, slug):
        state, lines = flow.load(root, slug)
        task, _ = task_for(root, slug, lines, tid, ("claimed", "red"))
        if task["mode"] == "direct":
            raise ValueError(f"{tid} is in direct mode: no red")
        by_worker(task, w, "red")
        named, name, out = test_files(root, slug, task), runner(command), ""
        if named and not any(f in command for f in named):
            why = f"the command doesn't name {' or '.join(named)}"
        else:
            code, out, cause = run(worktree(root, lines, tid) or root, command, limit(root))
            # a cause first: a killed run's partial output proves nothing either way
            why = cause or ("the test passes before the code exists" if code == 0 else wrong_reason(name, code, out))
        if why:
            return refused(root, slug, state, lines, tid, "red", command, why, w)
        mine, tree = since_claim(lines, tid), worktree(root, lines, tid) or root
        reds = [x for x in mine if x["kind"] == "red"]
        paths = list(reds[0]["evidence"]["frozen"]) if reds else \
            outside(slug, changed(tree, mine[0]["evidence"].get("commit") or "HEAD"))  # FR-10, FR-11: never grown
        frozen = {p: digest(tree, p) for p in paths}
        line = entry("red", tid, command=command, output=flow.sha(out.encode()), runner=name or "unknown", frozen=frozen)
        flow.write(root, slug, [line], state, w, "implementing")
    return 0, [f"red: {tid} accepted", "frozen:"] + [f"  {p}" for p in frozen]


def closes(root, slug, task, lines):
    """(whether this task closes its epic, whether it closes the last one): every other task there is done."""
    st, ts = status(root, slug, lines), [t for t in tasks_of(root, slug) if t["id"] != task["id"]]
    return all(st[t["id"]] == "done" for t in ts if t["epic"] == task["epic"]), all(st[t["id"]] == "done" for t in ts)


def review(root, slug, task, lines):
    """The review line of a green task, checks only and no model call (CT-8, FR-14, FR-15, FR-17, FR-25, FR-36), in the
    order of the decision table Review; the first failing row decides. Files outside the task's list are recorded:
    changed, and in neither `Files:` nor the red line's `frozen`. Tests beyond the task's own run only for the task
    closing an epic, so that task answers for a failure any of the epic's tasks caused: `tests.epic` when set, and the
    full suite for the last epic or when it isn't."""
    tid = task["id"]
    mine = since_claim(lines, tid)
    # a wave task's changes are applied on HEAD, which may hold a sibling's commit since its claim (CT-5)
    paths = changed(root, "HEAD" if worktree(root, lines, tid) else mine[0]["evidence"].get("commit") or "HEAD")
    reds = [x for x in mine if x["kind"] == "red"]
    frozen = reds[-1]["evidence"]["frozen"] if reds else {}
    folder = f".nio/specs/{slug}/"
    reasons = [f"the task edited {p[len(folder):]}: the spec, plan and tasks are not the worker's" for p in paths
               if p.startswith(folder) and p[len(folder):] in PLAN_FILES]
    reasons = reasons or [f"{p} changed since red" for p, h in frozen.items() if digest(root, p) != h]
    new, still = [], []
    # #66: the full suite took about half the worker time on every task; the task's own test already ran at green
    epic_closes, all_close = closes(root, slug, task, lines)
    if not reasons and epic_closes:
        base = next((x["evidence"] for x in reversed(lines) if x["kind"] == "baseline"), {})
        cfg = records.config(root)
        quick = None if all_close else (cfg.get("tests") or {}).get("epic")  # a slow suite runs in full only at the end
        r = suite(root, cfg, quick)
        if r["broken"]:
            reasons.append(f"the suite is broken: {r['cause'] or wrong_reason(r['runner'], r['code'], r['output'])}")
        elif r["runner"] is None or r["failing"] is None:
            if r["code"] != 0:
                reasons.append(f"new failure: the suite exits {r['code']} and its runner is unknown")
        new = [f for f in r["failing"] or [] if f not in (base.get("failing") or [])]
        still = [f for f in r["failing"] or [] if f in (base.get("failing") or [])]
        if new:
            reasons.append("new failures: " + ", ".join(new))
        if not quick and r["collected"] is not None and base.get("collected") is not None and r["collected"] < base["collected"]:
            reasons.append(f"{r['collected']} tests collected against the baseline's {base['collected']}")
    out = [p for p in outside(slug, paths) if p not in task["files"] and p not in frozen]
    return entry("review", tid, passed=not reasons, reasons=reasons, failing=new, still=still, outside=out)


def commit(root, slug, task, who, review=None):
    """CT-9, FR-19 to FR-21: commit a task whose review passed as `T-n: <title>` on the effort branch, the `task_done`
    line (with its branch and parent commit), the lines `epic_end` owes and the task's changes together; returns (the
    sha, the epic report with the sha filled in). A refused commit puts
    history.jsonl, state.json and the index back as `flow.commit_gate` does, writes a `fail` line with git's error, sets
    `waiting` and returns (None, []): the task stays green. Never merges, rebases or pushes."""
    tid = task["id"]
    if records.git(root, "branch", "--show-current") != [branch(slug)]:
        raise ValueError(f"not on {branch(slug)}: {tid} is not committed")  # FR-20
    folder = root / ".nio/specs" / slug
    sp, hp, np = folder / "state.json", folder / "history.jsonl", folder / "state.json.new"
    kept, saved = hp.read_bytes(), sp.read_bytes()
    code, tree, err = records.git(root, "write-tree", full=True)
    if code:
        raise ValueError(err.strip())
    state, _ = flow.load(root, slug)
    parent = records.git(root, "rev-parse", "HEAD")[0]
    waiting = None if (state["waiting"] or {}).get("task") == tid else state["waiting"]
    flow.write(root, slug, [entry("task_done", tid, branch=branch(slug), parent=parent)],
               {**state, "claims": release(state["claims"], tid), "waiting": waiting}, who, "implementing")
    ends, report = epic_end(root, slug, task, review or {})
    if ends:
        flow.write(root, slug, ends, flow.load(root, slug)[0], who, "implementing")
    rel = outside(slug, [p for _, p in porcelain(root)]) + [f".nio/specs/{slug}/history.jsonl", f".nio/specs/{slug}/state.json"]
    for args in (["add", "-A", "--", *rel], ["commit", "-q", "-m", f"{tid}: {task['title']}", "--", *rel]):
        code, _, err = records.git(root, *args, full=True)
        if code:
            hp.write_bytes(kept)
            sp.write_bytes(saved)
            np.unlink(missing_ok=True)
            records.git(root, "read-tree", tree.strip(), full=True)
            err = err.strip() or f"git {args[0]} failed"
            flow.write(root, slug, [entry("fail", tid, err.splitlines()[0], output=err)],
                       {**state, "waiting": {"why": f"commit failed: {err.splitlines()[0]}", "task": tid}}, who, "implementing")
            return None, []
    sha = records.git(root, "rev-parse", "HEAD")[0]
    return sha, [x.replace(THIS, sha) for x in report]


THIS = "<this commit>"  # the report's commit for the task being committed, filled in once git made it


def commits_of(root, slug):
    """{T-n: sha} of the `T-n: <title>` commits on the effort branch, the newest of each."""
    out = {}
    for x in records.git(root, "log", "--format=%H %s", branch(slug)):
        sha, _, subject = x.partition(" ")
        out.setdefault(subject.split(":")[0], sha)
    return out


def epic_end(root, slug, task, review):
    """CT-13 (FR-27 to FR-31): after the task's `task_done` line, when every task of its epic (fix tasks included) is
    done and its review found no new failure: no line is written (`nio flow done implementation-E-n` writes `epic`
    and `pass`, CT-17). Returns ([], the report: each done task with its commit, the files outside
    each task's list, the baseline failures still failing, a `notify:` line ); ([], [])
    otherwise. The task being committed has no commit yet: its line names THIS."""
    ev = review.get("evidence") or {}
    lines = flow.load(root, slug)[1]
    st, ts = status(root, slug, lines), tasks_of(root, slug)
    eid = task["epic"]
    mine = [t for t in ts if t["epic"] == eid]
    if ev.get("failing") or any(st[t["id"]] != "done" for t in mine):
        return [], []
    shas = commits_of(root, slug)
    reviews = {x["evidence"]["task"]: x["evidence"] for x in lines if x["kind"] == "review" and x["evidence"].get("passed")}
    reviews[task["id"]] = ev
    report = [f"epic: {eid} finished"]
    for t in mine:
        report.append(f"  {t['id']} {THIS if t['id'] == task['id'] else shas.get(t['id'], '(no commit found)')} {t['title']}")
        report += [f"  outside {t['id']}'s files: {p}" for p in (reviews.get(t["id"]) or {}).get("outside", [])]
    report += [f"  baseline failure still failing: {f}" for f in ev.get("still") or []]
    report += [f"next: run @nio:jury on implementation-{eid}", f"notify: the human: {eid} is finished; its epic gate is open"]
    return [], report


NEEDS = {"split": "red, green and review", "single": "red, green and review", "direct": "green and review"}


def left(root, slug, lines):
    """What keeps implementing's guard from passing (CT-14): each task not done with what it still needs, then each
    epic with no `epic` line; [] when the stage is finished."""
    st, ts = status(root, slug, lines), tasks_of(root, slug)
    needs = {"red": "green and review", "green": "its review", "blocked": "the human to unblock it"}
    out = [f"{t['id']} is {st[t['id']]}: needs {needs.get(st[t['id']], NEEDS[t['mode']])}" for t in ts if st[t["id"]] != "done"]
    shut = {x["evidence"].get("epic") for x in lines if x["kind"] == "epic"}
    return out + [f"{e} has no epic line" for e in dict.fromkeys(t["epic"] for t in ts) if e not in shut]


def open_gate(root, slug, lines):
    """The first epic whose tasks are all done and that has no `epic` line (an old skipped one counts as closed): its gate
    is open (CT-17); None when there is none, or when an earlier epic has work left (a fix task reopened it)."""
    st, ts = status(root, slug, lines), tasks_of(root, slug)
    shut = {x["evidence"].get("epic") for x in lines if x["kind"] == "epic"}
    for e in dict.fromkeys(t["epic"] for t in ts):
        if any(st[t["id"]] != "done" for t in ts if t["epic"] == e):
            return None
        if e not in shut:
            return e
    return None


def green(root, slug, tid, command, by):
    """`nio flow green` (CT-8, FR-12 to FR-15, FR-32, FR-33, FR-37, FR-41, FR-45): on a red task run the red line's
    command (another `--run` is refused) with its frozen files unchanged; on a direct claimed task run `--run`. An
    exit 0 writes `green` and the review runs at once; a passed review commits. A `green` task (its commit failed) runs
    no guard: only the review and the commit again. Returns (code, lines): 0 only when the task is done."""
    flow.refuse(root, slug)
    w = flow.who(by)
    with flow.lock(root, slug):
        state, lines = flow.load(root, slug)
        task, now = task_for(root, slug, lines, tid, ("claimed", "red", "green"))
        direct, tree = task["mode"] == "direct", worktree(root, lines, tid) or root
        if tree != root:
            clean(root, slug)  # FR-14: the apply and its restore must not mix with the human's edits
        if now == "claimed" and not direct:
            raise ValueError(f"{tid} has no failing test first")
        by_worker(task, w, "green")
        printed = []
        if now != "green":
            why = ""
            if direct:
                if not command:
                    raise ValueError(f"{tid} is in direct mode: green needs --run")
            else:
                ev = [x for x in since_claim(lines, tid) if x["kind"] == "red"][-1]["evidence"]
                if command and command != ev["command"]:
                    why = f"the command recorded at red is {ev['command']}"
                command = ev["command"]
                why = why or next((f"{p} changed since red; prove red again" for p, h in ev["frozen"].items()
                                   if digest(tree, p) != h), "")
            if not why:
                code, out, cause = run(tree, command, limit(root))
                why = cause or (f"the command exits {code}" if code else "")
            if why:
                return refused(root, slug, state, lines, tid, "green", command, why, w)
            line = entry("green", tid, command=command, output=flow.sha(out.encode()))
            flow.write(root, slug, [line], state, w, "implementing")
            lines, printed = lines + [line], [f"green: {tid} accepted"]
        saved = {}
        if tree != root:
            patch, saved, err = land(root, slug, tid, tree, since_claim(lines, tid)[0]["evidence"]["commit"])
            if err:
                records.git(root, "worktree", "remove", "--force", str(tree), full=True)
                why = f"{tid} blocked: its changes don't apply"
                flow.write(root, slug, [entry("blocked", tid, cause="apply", patch=patch)],
                           {**state, "claims": release(state["claims"], tid), "waiting": {"why": why, "task": tid}}, w, "implementing")
                return 1, printed + [why, f"  {err}", f"its changes are in {patch}"]
        line = review(root, slug, task, lines)
        ev = line["evidence"]
        if not ev["passed"]:
            restore(root, saved)
            entries, state = attempt(root, slug, state, lines, tid, line)
            flow.write(root, slug, entries, state, w, "implementing")
            return 1, printed + ["review: failed"] + [f"  {r}" for r in ev["reasons"]] + said(entries)
        flow.write(root, slug, [line], state, w, "implementing")
        printed += ["review: passed"] + [f"  outside the task's files: {p}" for p in ev["outside"]]
        try:
            sha, report = commit(root, slug, task, w, line)
        except Exception:
            restore(root, saved)
            raise
        if tree != root:
            records.git(root, "worktree", "remove", "--force", str(tree), full=True) if sha else restore(root, saved)
    if sha:
        return 0, printed + [f"done: {tid} {sha}"] + report
    return 1, printed + [flow.load(root, slug)[0]["waiting"]["why"], f"{tid} stays green; `nio flow green {slug} {tid}` retries"]


def unblock(root, slug, tid, reason, by):
    """`nio flow unblock` (CT-12, FR-38): the human sets a blocked task ready, its attempts reset and its frozen files
    dropped (its next claim freezes afresh); clears `waiting` when it names this task. Returns (code, lines)."""
    flow.refuse(root, slug)
    w = flow.who(by)
    with flow.lock(root, slug):
        state, lines = flow.load(root, slug)
        now = status(root, slug, lines).get(tid)
        if now != "blocked":
            raise ValueError(f"{tid} is {now}" if now else f"no task {tid} in tasks.md")
        if not (reason or "").strip():
            raise ValueError("--human needs a reason")
        waiting = None if (state["waiting"] or {}).get("task") == tid else state["waiting"]
        attempts = {k: v for k, v in state["attempts"].items() if k != tid}
        flow.write(root, slug, [entry("unblock", tid, reason=reason)], {**state, "attempts": attempts, "waiting": waiting},
                   w, "implementing")
    return 0, [f"unblocked: {tid}"]


PARTS = (("spec_says", "What the spec says"), ("code_shows", "What the code shows"), ("smallest_change", "Smallest change"))


def block(root, slug, tid, handoff, by):
    """`nio flow block` (CT-11, FR-23, FR-24, FR-37, AC-48): file a `status: blocked` handoff with a `change_request` as a
    pending change record against the effort's spec.md, shelve the task's changes like the cap does, write a `blocked`
    line (`cause: spec`), clear the claim and set the effort waiting. The record holds `Handoff: <sha256>`: a pending
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
    hsh = flow.sha(data)
    with flow.lock(root, slug):
        state, lines = flow.load(root, slug)
        now = status(root, slug, lines).get(tid)
        mine = [x for x in lines if x["kind"] == "blocked" and x["evidence"].get("task") == tid
                and x["evidence"].get("handoff") == hsh]
        if now not in ("claimed", "red", "green") and not (now == "blocked" and mine):
            raise ValueError(f"{tid} is {now}" if now else f"no task {tid} in tasks.md")
        found = next((p for p in sorted((root / ".nio/memory").rglob("C-*.md"))
                      if f"Handoff: {hsh}" in p.read_text() and records.parse(p)[0].get("outcome") == "pending"), None)
        kept = found.read_text() if found else ""
        patch = "" if mine else shelve(root, slug, run_of(root, slug, lines, tid), tid, worktree(root, lines, tid))  # first: it cleans every untracked file
        if found is None:
            areas = records.areas(root)
            found = records.new(root, "change", "project" if "project" in areas else areas[0],
                                f"Spec problem in {tid}: {str(cr['spec_says']).strip()}", by=by.strip())
            head = found.read_text().partition("\n---\n")[0]
            head = re.sub(r'^against: .*$', f'against: ".nio/specs/{slug}/spec.md"', head, flags=re.M)
            body = "".join(f"## {name}\n{str(cr[k]).strip()}\n" for k, name in PARTS)
            kept = f"{head}\n---\n{body}## Human decision\nPending.\n\nHandoff: {hsh}\n"
        found.write_text(kept)  # a reused record, untracked, was cleaned with the task's files
        cid = records.parse(found)[0]["id"]
        if not mine:  # the line and the state it leaves go in one write, so a blocked line means waiting is set too
            line = {**entry("blocked", tid, cause="spec", handoff=hsh, patch=patch), "change": cid}
            flow.write(root, slug, [line], {**state, "claims": release(state["claims"], tid), "waiting": {"why": f"spec problem in {tid}", "task": tid, "change": cid}},
                       w, "implementing")
    return 0, [f"blocked: {tid}", cid]
