"""The tasks stage (#42): create tasks.md next to an approved spec and plan, run its free checks, print the estimate,
show one task, and answer whether the implement stage may start."""
from pathlib import PurePosixPath
import collections
import os
import re
from importlib import resources

from nio import records, spec

FIELDS = ["Files", "Serves", "Test", "Depends on", "Parallel", "Tier", "Effort", "Mode"]
MODES = ["split", "single", "direct"]
MODE_SINCE = "2026-10-30"  # a list approved before this date may omit `Mode:` and runs in split (C-261029-nbrg)
TIER = re.compile(r"^(\S+?)(?::\s*(.*))?$")
TIERS = ["cheap", "strong", "max", "frontier"]
EFFORTS = ["low", "med", "high"]
EPIC = re.compile(r"^## (E-\d+)\b\s*(.*)$")
TASK = re.compile(r"^### (T-\d+)\b\s*(.*)$")
LINE = re.compile(r"^- ([A-Z][A-Za-z ]*?):\s*(.*?)\s*$")
ID = re.compile(r"(?<![\w-])([A-Z]+-\d+)(?![\w-])")
CHANGE = re.compile(r"\bC-\d{6}-[a-z2-7]{4}\b")
FINDING = re.compile(r"^(J-\d+) \(([\w-]+), round \d+\)$")


def path(root, slug):
    return spec.path(root, slug).parent / "tasks.md"


def route(root, slug):
    if not spec.path(root, slug).exists():
        raise ValueError(f"no spec at {spec.path(root, slug).relative_to(root)}")
    return records.parse(spec.path(root, slug))[0].get("route")


def may_start(root, slug):
    """(ok, why): may the tasks stage start (#42 FR-2, FR-39)? The spec gate approved or closed by the human, and on a
    full spec the plan approved too."""
    from nio import jury, plan
    kind = route(root, slug)
    if kind == "epic":
        return False, f"`{slug}` is an epic: run the tasks stage on each slice's spec"
    if kind == "lite":
        from nio import spec
        if spec.check(root, slug, gate=True)[0]:
            return False, "the bug-fix spec must pass nio check spec --gate first (the grill)"
        return True, "the tasks stage may start"
    if jury.standing(root, slug, "spec") not in ("approved", "closed"):
        return False, "the spec must be approved first"
    if kind == "full":
        ok, why = plan.approved(root, slug)
        if not ok:
            return False, why
    return True, "the tasks stage may start"


def new(root, slug):
    """Write tasks.md from its template, never overwriting it; refuse until the tasks stage may start."""
    ok, why = may_start(root, slug)
    if not ok:
        raise ValueError(why)
    if path(root, slug).exists():
        raise ValueError(f"{path(root, slug).relative_to(root)} already exists")
    text = resources.files("nio").joinpath("templates/tasks.md").read_text().replace("<slug>", slug)
    path(root, slug).write_text(text)
    return path(root, slug)


def parse(text):
    """{"epics": [{"id", "title", "story", "head", "tasks": [ids]}], "tasks": {id: task}, "dupes": [ids]}. A task holds its
    epic, whether it sits under `#### Fixes`, its block of lines and its `- Name: value` fields."""
    epics, tasks, dupes, epic, fix, cur = [], {}, [], None, False, None
    for line in re.sub(r"<!--.*?-->", "", text, flags=re.S).splitlines():
        if m := EPIC.match(line):
            story = re.search(r"\((US-\d+|Foundation)\)\s*$", m[2])
            epic, fix, cur = {"id": m[1], "title": m[2], "story": story[1] if story else "", "head": line, "tasks": []}, False, None
            epics.append(epic)
        elif line.strip() == "#### Fixes":
            fix, cur = True, None
        elif (m := TASK.match(line)) and epic:
            if m[1] in tasks:
                dupes.append(m[1])
            cur = {"id": m[1], "title": m[2], "epic": epic["id"], "fix": fix, "block": [line], "fields": {}}
            tasks[m[1]] = cur
            epic["tasks"].append(m[1])
        elif line.startswith("## ") or line.startswith("# "):
            epic, cur = None, None
        elif cur is not None and line.strip():
            cur["block"].append(line)
            if m := LINE.match(line):
                cur["fields"].setdefault(m[1], m[2])
    return {"epics": epics, "tasks": tasks, "dupes": dupes}


def files(value):
    return [f.strip().strip("`") for f in value.split(",") if f.strip().strip("`")]


def file_of(entry):
    """The path a `Files:` entry names, past a `:line` or trailing words; None when it names no file-like path."""
    m = re.search(r"[\w./-]*\w\.\w+", entry)
    return m[0] if m else None


def ids(value):
    return ID.findall(value)


def own(test_line):
    """TC IDs of a Test: line, minus those only in a `;` part saying "proved later"."""
    parts = test_line.split(";")
    later = {i for p in parts if "proved later" in p for i in ids(p) if i.startswith("TC-")}
    keep = {i for p in parts if "proved later" not in p for i in ids(p)}
    return [i for i in dict.fromkeys(ids(test_line)) if i.startswith("TC-") and (i in keep or i not in later)]


def reach(tasks):
    """{task: every task it depends on, directly or through others}."""
    deps = {t: set(ids(tasks[t]["fields"].get("Depends on", ""))) & tasks.keys() for t in tasks}
    out = {}
    for t in tasks:
        seen, todo = set(), list(deps[t])
        while todo:
            d = todo.pop()
            if d not in seen:
                seen.add(d)
                todo += deps.get(d, [])
        out[t] = seen
    return out


def cycles(tasks):
    """Each dependency cycle once, as its tasks in order."""
    deps = {t: [d for d in ids(tasks[t]["fields"].get("Depends on", "")) if d in tasks] for t in tasks}
    found, state = [], {}

    def walk(t, stack):
        state[t] = "open"
        for d in deps[t]:
            if state.get(d) == "open":
                found.append(stack[stack.index(d):] + [d])
            elif d not in state:
                walk(d, stack + [d])
        state[t] = "done"
    for t in tasks:
        if t not in state:
            walk(t, [t])
    return found


def plan_parts(root, slug):
    """(build order {entry: (files, TCs)}, TC IDs) of a full spec's plan."""
    folder = spec.path(root, slug).parent
    _, cbody = records.parse(folder / "contracts.md")
    bound = {}
    for iid, block in spec.items(spec.sections(cbody).get("Contracts", [])):
        m = re.search(r"^- Binding:\s*`([^`:]+)", "\n".join(block), re.M)
        if m:
            bound[iid] = m[1]
    _, tbody = records.parse(folder / "tests.md")
    tcs = set(re.findall(r"^### (TC-\d+)\b", "\n".join(tbody), re.M))
    _, pbody = records.parse(folder / "plan.md")
    entries = {}
    for name, lines in spec.subsections(spec.sections(pbody).get("Build order", [])):
        key = re.match(r"(US-\d+|Foundation)", name)
        text = "\n".join(lines)
        get = lambda f: ids((re.search(rf"^- {f}:\s*(.*)$", text, re.M) or [None, ""])[1])
        if key:
            entries[key[1]] = ({bound[c] for c in get("Delivers") if c in bound}, get("Tests"))
    return entries, tcs


def approved_before(root, slug, since, base="HEAD"):
    """Was `nio: approve tasks` committed (committer date) before `since`? False when it never was."""
    rel = str(path(root, slug).relative_to(root))
    day = (records.git(root, "log", "-1", "--format=%cs", "--grep=^nio: approve tasks$", base, "--", rel) or [""])[0]
    return bool(day) and day < since


def check(root, slug, gate=False, base="HEAD"):
    """(errors, notes): the free checks of tasks.md (#42 FR-6 to FR-16, FR-24, FR-28 to FR-30, FR-34 to FR-38, FR-40,
    FR-45, FR-48 to FR-50, FR-53, FR-55; NFR-1), and the estimate as notes. `gate` is accepted for the CLI's sake."""
    kind = route(root, slug)
    p = path(root, slug)
    if not p.exists():
        return [f"{p.relative_to(root)} is missing; create it with `nio new tasks {slug}`"], []
    meta, body = records.parse(p)
    retired = meta.get("retired") or []
    parsed = parse("\n".join(body))
    tasks, epics = parsed["tasks"], parsed["epics"]
    _, sbody = records.parse(spec.path(root, slug))
    acs = {i for _, lines in spec.sections(sbody).items() for i, _ in spec.items(lines) if i.startswith("AC-")}
    errs = [f"`slug` must be `{slug}`"] * (meta.get("slug") != slug)
    errs += [f"{t} is defined {1 + parsed['dupes'].count(t)} times" for t in dict.fromkeys(parsed["dupes"])]
    errs += [f"{e} is defined {n} times" for e, n in collections.Counter(e["id"] for e in epics).items() if n > 1]
    full = kind == "full"
    old = approved_before(root, slug, MODE_SINCE, base)
    entries, tcs = plan_parts(root, slug) if full else ({}, set())
    for t, task in tasks.items():
        f = task["fields"]
        errs += [f"{t}: needs `- {name}:`" for name in FIELDS if name not in f and not (name == "Mode" and old)]
        if any(re.match(r"^- \[[ xX]\]", line) or re.match(r"^- Status:", line) for line in task["block"]):
            errs.append(f"{t} holds a status or a checkbox; status lives in the CLI's state, not tasks.md")
        if t in retired:
            errs.append(f"{t} is retired and can't be used again")
        for name in ("Serves", "Depends on", "Test"):
            for i in ids(f.get(name, "")):
                if i in retired:
                    errs.append(f"{t} cites {i}, which is retired")
                elif i.startswith("AC-") and i not in acs:
                    errs.append(f"{t} cites {i}, which the spec doesn't define")
                elif i.startswith("T-") and i not in tasks:
                    errs.append(f"{t} cites {i}, which tasks.md doesn't define")
                elif i.startswith("TC-") and full and i not in tcs:
                    errs.append(f"{t} cites {i}, which the plan doesn't define")
                elif i.startswith("J-") and not (task["fix"] and FINDING.match(f.get("From", "")) and FINDING.match(f["From"])[1] == i):
                    errs.append(f"{t} cites {i}; a finding is served only by a fix task whose `From:` names it")
        if f.get("Test", "").startswith("new:") and not (task["fix"] and f.get("From")):
            errs.append(f"{t}: `Test: new:` belongs to a fix task with a `From:` line")
        if "Depends on" in f and f["Depends on"] != "none" and not ids(f["Depends on"]):
            errs.append(f"{t}: `Depends on:` lists task IDs or says `none`")
        if "Parallel" in f and f["Parallel"] not in ("yes", "no"):
            errs.append(f"{t}: `Parallel:` must be yes or no, not `{f['Parallel']}`")
        if "Tier" in f and f["Tier"] != "to be rated":
            m = TIER.match(f["Tier"])
            if m[1] not in TIERS:
                errs.append(f"{t}: `{m[1]}` is not cheap, strong, max or frontier")
            elif not (m[2] or "").strip():
                errs.append(f"{t}: `Tier: {m[1]}` needs a reason, as `Tier: {m[1]}: <why>`")
        if "Mode" in f and f["Mode"] != "to be rated":
            m = TIER.match(f["Mode"])
            if m[1] not in MODES:
                errs.append(f"{t}: `{m[1]}` is not split, single or direct")
            elif not (m[2] or "").strip():
                errs.append(f"{t}: `Mode: {m[1]}` needs a reason, as `Mode: {m[1]}: <why>`")
        if "Effort" in f and f["Effort"] not in EFFORTS:
            errs.append(f"{t}: `Effort:` must be low, med or high, not `{f['Effort']}`")
        if full and "Test" in f and not ids(f["Test"]):
            errs.append(f"{t}: on a full spec `Test:` cites the plan's `TC-n`")
        if "Serves" in f and not [i for i in ids(f["Serves"]) if i.startswith("AC-")] and not (
                task["fix"] and [i for i in ids(f["Serves"]) if i.startswith("J-")]):
            errs.append(f"{t} serves no AC")
    served = {i for task in tasks.values() for i in ids(task["fields"].get("Serves", ""))}
    errs += [f"{ac} is served by no task" for ac in sorted(acs, key=lambda a: int(a[3:])) if ac not in served]
    errs += [f"dependency cycle: {' → '.join(c)}" for c in cycles(tasks)]
    # parallel clashes across the whole spec, unless one task depends on the other (#42 FR-13, FR-48)
    below = reach(tasks)
    par = [t for t in tasks if tasks[t]["fields"].get("Parallel") == "yes"]
    for i, a in enumerate(par):
        for b in par[i + 1:]:
            if a in below[b] or b in below[a]:
                continue
            for f in sorted(set(files(tasks[a]["fields"].get("Files", ""))) & set(files(tasks[b]["fields"].get("Files", "")))):
                errs.append(f"parallel clash: {a} and {b} both name `{f}`")
    # a foundational task serves only ACs its dependents serve (#42 FR-45)
    above = {t: {u for u in tasks if t in below[u]} for t in tasks}
    for e in epics:
        if e["story"] == "Foundation" or not e["story"] and kind != "lite":
            for t in (x for x in e["tasks"] if not tasks[x]["fix"]):  # a fix task is appended with no dependents
                theirs = {i for u in above[t] for i in ids(tasks[u]["fields"].get("Serves", ""))}
                errs += [f"{t} serves {ac}, which no task depending on it serves" for ac in ids(tasks[t]["fields"].get("Serves", ""))
                         if ac.startswith("AC-") and ac not in theirs]
    # each build-order entry's files and planned tests land in its epic (#42 FR-53)
    for e in epics:
        if e["story"] in entries:
            want_files, want_tcs = entries[e["story"]]
            named = {f for t in e["tasks"] for f in files(tasks[t]["fields"].get("Files", ""))}
            cited = {i for t in e["tasks"] for i in ids(tasks[t]["fields"].get("Test", ""))}
            errs += [f"{e['id']} names `{f}` in no `Files:` line, though its build-order entry delivers it" for f in sorted(want_files - named)]
            errs += [f"{e['id']} has no task citing {tc}, which its build-order entry lists" for tc in want_tcs if tc not in cited]
    errs += check_fixes(root, slug, parsed, retired, base)
    notes = estimate(parsed)
    if kind == "lite":
        paths = [PurePosixPath(f) for t in tasks.values() for f in files(t["fields"].get("Files", ""))]
        dirs = {str(q.parent) for q in paths if not ({"tests", "test"} & set(q.parts[:-1]) or q.name.startswith("test_"))}
        if len(dirs) > 1:
            notes.append(f"escalate: the fix changes files in {len(dirs)} folders ({', '.join(sorted(dirs))}): offer the full flow (@nio:spec, \"Escalating a bug fix\")")
    return errs, notes


def check_fixes(root, slug, parsed, retired, base="HEAD"):
    """Fix tasks (#42 FR-27 to FR-30, FR-49, FR-50): a `From:` naming a finding or a change record, the next free ID,
    and planned tasks frozen once `nio: approve tasks` is committed."""
    from nio import jury
    tasks, errs = parsed["tasks"], []
    planned = [t for t in tasks if not tasks[t]["fix"]]
    top = max([int(t[2:]) for t in planned] + [int(r[2:]) for r in retired if r.startswith("T-")] + [0])
    for t, task in sorted(tasks.items(), key=lambda x: int(x[0][2:])):  # IDs in the order they were taken: epics reopen out of file order
        if not task["fix"]:
            continue
        src = task["fields"].get("From", "")
        if not src:
            errs.append(f"{t}: a fix task needs `- From:` naming its finding or change request")
        elif not FINDING.match(src) and not (CHANGE.fullmatch(src) and jury.change_record(root, src)[0]):
            errs.append(f"{t}: `From: {src}` names no finding (`J-n (<gate>, round n)`) or change record")
        if int(t[2:]) <= top:
            errs.append(f"{t}: a fix task takes the next free ID, T-{top + 1}")
        top = max(top, int(t[2:]))
    rel = str(path(root, slug).relative_to(root))
    sha = (records.git(root, "log", "-1", "--format=%H", "--grep=^nio: approve tasks$", base, "--", rel) or [""])[0]
    if sha:
        old = parse("\n".join(records.git(root, "show", f"{sha}:{rel}")))["tasks"]
        flat = lambda b: " ".join(" ".join(b).split())
        for t, task in old.items():
            if task["fix"]:
                continue
            if t not in tasks and t not in retired:
                errs.append(f"{t} was removed after `nio: approve tasks` without being retired")
            elif t in tasks and flat(tasks[t]["block"]) != flat(task["block"]):
                errs.append(f"{t} changed after `nio: approve tasks`; planned tasks are frozen after approval")
    return errs


def rated_from(root, slug, copy):
    """Errors when tasks.md differs from `copy` outside Tier/Effort/Mode lines, or a rating still reads `to be rated`."""
    p = path(root, slug)
    rel, new, old = p.relative_to(root), p.read_text().splitlines(), open(copy).read().splitlines()
    rating = lambda l: re.match(r"- (Tier|Effort|Mode):", l)
    if len(new) != len(old):
        return [f'{rel}:1: not a rating line: "line count {len(old)} became {len(new)}"']
    errors = []
    for n, (a, b) in enumerate(zip(old, new), 1):
        if a != b and not (rating(a) and rating(b)):
            errors.append(f'{rel}:{n}: not a rating line: "{b}"')
        elif rating(b) and "to be rated" in b:
            errors.append(f"{rel}:{n}: not rated")
    return errors


def estimate(parsed):
    """One row per epic: task count, tier and effort counts, and the parallel tasks; no token or money figure (#42
    FR-14). Parallel comes only from `Parallel:` (FR-47)."""
    out = []
    for e in parsed["epics"]:
        ts = [parsed["tasks"][t]["fields"] for t in e["tasks"]]
        tier = lambda f: TIER.match(f.get("Tier", "")).group(1) if TIER.match(f.get("Tier", "")) else ""
        par = [t for t in e["tasks"] if parsed["tasks"][t]["fields"].get("Parallel") == "yes"]
        out.append(f"{e['id']}: {len(ts)} tasks; tier " + ", ".join(f"{x} {sum(tier(f) == x for f in ts)}" for x in TIERS)
                   + "; effort " + ", ".join(f"{x} {sum(f.get('Effort') == x for f in ts)}" for x in EFFORTS)
                   + f"; parallel: {', '.join(par) or 'none'}")
    return out


def show(root, slug, tid):
    """The epic's heading and one task's section, nothing else (#42 FR-35)."""
    p = path(root, slug)
    if not p.exists():
        raise ValueError(f"no tasks.md for {slug}")
    parsed = parse("\n".join(records.parse(p)[1]))
    if tid not in parsed["tasks"]:
        raise ValueError(f"no {tid} in tasks.md")
    task = parsed["tasks"][tid]
    head = next(e["head"] for e in parsed["epics"] if e["id"] == task["epic"])
    return [head, ""] + (["#### Fixes", ""] if task["fix"] else []) + [globbed(root, x) for x in task["block"]]


def globbed(root, line):
    """A `- Files:` line with each glob pattern as the paths it matches, or marked as matching none (#126 FR-17)."""
    if not line.startswith("- Files:") or not any(c in line for c in "*?"):
        return line
    out = []
    for f in files(line[len("- Files:"):]):
        if not any(c in f for c in "*?"):  # `[` is literal, as in `app/[id]/page.tsx`
            out.append(f"`{f}`")
            continue
        try:
            hits = sorted(str(p.relative_to(root)) for p in root.glob(f.replace("[", "[[]")) if p.is_file() and p.resolve().is_relative_to(root.resolve()))
        except (ValueError, NotImplementedError):  # an absolute or empty pattern matches nothing here
            hits = []
        out += [f"`{h}`" for h in hits] or [f"`{f}` (pattern: matches no file)"]
    return "- Files: " + ", ".join(out)


def approved(root, slug):
    """(ok, why): may the implement stage start (#42 FR-33, FR-44, FR-56)? The tasks gate approved, or closed by the
    human, on the current planned tasks, plan and spec; a fix task appended since doesn't withdraw it."""
    from nio import jury
    if not path(root, slug).exists():
        return False, "the tasks must be approved first (there is no tasks.md)"
    now = jury.standing(root, slug, "tasks")
    if now == "approved":
        return True, "the tasks jury approved the tasks"
    if now == "closed":
        return True, "the human closed the tasks gate"
    return False, f"the tasks must be approved first (the tasks jury's outcome is {now})"


def finished(states, epic):
    """(finished, not done): an epic is finished, and ready for the implementation jury, only when every task in it, fix
    tasks included, is `done` in the CLI's state (#42 FR-25, FR-26; the state machine itself is #45's)."""
    left = [t for t in epic["tasks"] if states.get(t) != "done"]
    return not left, left


def fixes_of(root, slug, gate, fid):
    """The tasks whose `From:` names this finding of this gate; another epic's ledger counts from J-1 too."""
    tasks = parse("\n".join(records.parse(path(root, slug))[1]))["tasks"]
    return [t for t, x in tasks.items() if (m := FINDING.match(x["fields"].get("From", ""))) and (m[1], m[2]) == (fid, gate)]


def retire(root, slug, tid, reason, by):
    """Retire a fix task (#126 FR-9, FR-11): its block leaves tasks.md, its ID joins `retired:`, and the finding it served
    closes as `accepted-risk` credited to `by`, the reason its note, so no later round makes it a task again. The tasks
    gate stays approved. Refused, changing nothing, without a reason."""
    from nio import jury
    if not reason.strip():
        raise ValueError(f"retiring {tid} needs a reason (--reason)")
    if by not in jury.BY:
        raise ValueError(f"retiring {tid} needs --by, one of {', '.join(sorted(jury.BY))}: who retires it")
    p = path(root, slug)
    task = parse("\n".join(records.parse(p)[1]))["tasks"].get(tid)
    if not task or not task["fix"]:
        raise ValueError(f"{tid} is not a fix task in tasks.md; retire a planned task by hand (it reopens the tasks gate)")
    text = re.sub(rf"^### {tid}\b.*?(?=^#{{1,4}} |\Z)", "", p.read_text(), count=1, flags=re.M | re.S)
    text, n = re.subn(r"^(retired:\s*\[)([^\]\n]*)\]", lambda m: f"{m[1]}{m[2].strip() + ', ' if m[2].strip() else ''}{tid}]",
                      text, count=1, flags=re.M)
    if not n:
        raise ValueError("tasks.md has no `retired: [...]` line")
    p.write_text(text)
    m = FINDING.match(task["fields"].get("From", ""))
    led = jury.load(root, slug, m[2]) if m else None
    f = next((g for g in led["findings"] if g["id"] == m[1] and g["status"] in ("open", "disposed")), None) if m else None
    if f:
        f.update(status="disposed", disposition="accepted-risk", by=by, note=reason)
        jury.save(root, led)
    return f"retired {tid}" + (f"; {f['id']} closed as accepted-risk by {by}" if f else "")


def fix_test(root, slug, finding, cites):
    """A fix task's `Test:` (CT-14): the finding's `run` when tests.md holds it, else a TC covering its cite, else `new:`."""
    from nio import evidence
    known = evidence.known_tests(root, slug)
    run = next((s["run"] for s in finding["sources"] if s.get("run")), "")
    if ids(run) and set(ids(run)) <= known.keys():
        return run
    tests = path(root, slug).with_name("tests.md")
    covers = {}
    for m in re.finditer(r"^### (TC-\d+)\b.*?(?=^#{2,3} |\Z)", tests.read_text() if tests.exists() else "", re.M | re.S):
        head = re.search(r"\(([^()]*;[^()]*)\)", m[0].splitlines()[0])  # `(AC-1; unit)`
        line = re.search(r"^- Covers:(.*)$", m[0], re.M)
        covers[m[1]] = set(ids((head[1] if head else "") + " " + (line[1] if line else "")))
    tc = next((tc for c in cites for tc, cov in covers.items() if c in cov), None)
    return tc or f"new: {cites[0] if cites else finding['id']}"


def append_fix(root, slug, epic, finding):
    """`one_fix` under the effort's lock: two calls at once would pick one ID and lose a task (AC-50)."""
    from nio import flow
    try:
        with flow.lock(root, slug):
            return one_fix(root, slug, epic, finding)
    except flow.Busy as e:
        raise ValueError(f"another nio call holds the lock of {slug}, try again: {e}") from None


def one_fix(root, slug, epic, finding):
    """Append one fix task for a finding the decision table routes to a task, under the epic's `#### Fixes`, and dispose of
    the finding as `fix-task` (CT-14, FR-26, FR-27, FR-29). The new ID, or None when the finding already has a task. Every
    byte already in the file stays; the decision table's routing is the caller's (`jury.to_task`)."""
    from nio import jury
    gate, fid = f"implementation-{epic}", finding["id"]
    led = jury.load(root, slug, gate)
    src = f"{fid} ({gate}, round {led['round']})"
    now = next((f for f in led["findings"] if f["id"] == fid), None)
    if not now:
        raise ValueError(f"no finding {fid} in the {gate} ledger of {slug}")
    p = path(root, slug)
    meta, body = records.parse(p)
    parsed = parse("\n".join(body))
    had = fixes_of(root, slug, gate, fid)
    tid = None
    if not had:
        taken = [int(t[2:]) for t in parsed["tasks"]] + [int(r[2:]) for r in meta.get("retired") or [] if r.startswith("T-")]
        tid = f"T-{max(taken + [0]) + 1}"
        text = p.read_bytes().decode()  # read_text would turn a hand-saved CRLF file into LF
        nl = "\r\n" if "\r\n" in text else "\n"
        cites = [c for c in finding["cites"] if re.fullmatch(r"(AC|FR|CT)-\d+", c)]
        serves = cites + [fid] * (not any(c.startswith("AC-") for c in cites))  # `tasks.check`: an AC, or the finding itself
        tracked = set(records.git(root, "ls-files"))
        named = list(dict.fromkeys(f for f in map(file_of, files(finding["where"])) if f in tracked))
        if not named:  # as `evidence.check_finding`: the epic's changed files
            from nio import evidence
            commits = evidence.commits_of(root, slug, epic)
            named = evidence.code_diff(root, evidence.parent_of(root, commits[-1]), commits[0], "--name-only", "--diff-filter=d") if commits else []
        where = ", ".join(f"`{f}`" for f in named)
        ask = "Justify or remove" if finding.get("gap") == "unrequested" else "Fix"
        block = [f"### {tid} {ask}: {finding['title']}", f"- From: {src}", f"- Files: {where}", f"- Serves: {', '.join(serves)}",
                 f"- Test: {fix_test(root, slug, finding, cites)}", "- Depends on: none", "- Parallel: no",
                 "- Tier: strong: a fix from a jury finding", "- Effort: med", "- Mode: single: a fix from a jury finding", ""]
        # headings inside a comment aren't headings, as in `parse`; an opening mark in a title would hide the tasks after it
        mask = re.sub(r"<!--.*?-->", lambda m: re.sub(r"[^\r\n]", " ", m[0]), text, flags=re.S)
        start = re.search(rf"^## {epic}\b", mask, re.M)
        if not start:
            raise ValueError(f"no {epic} in tasks.md")
        end = re.compile(r"^#{1,2} ", re.M).search(mask, start.end())
        cut = end.start() if end else len(text)
        head, tail = text[:cut], text[cut:]
        fixes = re.search(r"^\s*#### Fixes\s*$", mask[start.start():cut], re.M)
        new = head + ("" if head.endswith(nl * 2) else nl if head.endswith(nl) else nl * 2) + (f"#### Fixes{nl}{nl}" if not fixes else "") \
            + nl.join(block).replace("<!--", "< !--") + (nl if tail else "") + tail
        tmp = p.with_name(p.name + ".tmp")
        with open(tmp, "wb") as f:
            f.write(new.encode())
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, p)
    # the ledger follows the file; a crash between the two is mended by the next call in the same round. A finding reopened
    # in a later round keeps its one task and stays open.
    if now["status"] == "open" and (tid or parsed["tasks"][had[0]]["fields"]["From"] == src):
        jury.dispose(root, slug, gate, fid, "fix-task", "agent", f"fix task {tid or had[0]}", routed=True)
    return tid
