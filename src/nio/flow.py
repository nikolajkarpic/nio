"""`nio flow`: where an effort is, and moving it on only when deterministic guards pass (2026-10-28-flow-state)."""
import contextlib
import datetime
import hashlib
import json
import os
import re
import secrets
import socket
import time

from nio import records

DATED = re.compile(r"^\d{4}-\d{2}-\d{2}-")
STAGES = {  # the state table "Flow": stage -> (where a passing guard goes, where a jury rejection sends it)
    "intake": ("drafting", None), "drafting": ("researching", None), "researching": ("advocate_walking", None),
    "advocate_walking": ("grilling", None), "grilling": ("spec_jury", None), "spec_jury": ("arch_grilling", "grilling"),
    "arch_grilling": ("planning", None), "planning": ("plan_jury", None), "plan_jury": ("tasking", "planning"),
    "tasking": ("tasks_jury", None), "tasks_jury": ("implementing", "tasking"), "implementing": ("done", None),
    "done": (None, None)}
EPIC_GATE = re.compile(r"implementation-E-\d+")
NOT_BUILT = {"researching", "advocate_walking", "arch_grilling"}  # skipped on the record (FR-21)
ROUTE_SKIPS = {"lite": {"spec_jury", "planning", "plan_jury"}}  # stages a route skips on the record (FR-2)
# each gate stage's jury gate and approval commit message: CT-6's search, CT-7's judged versions and CT-11's commit
GATES = {"spec_jury": ("spec", "nio: approve spec"), "plan_jury": ("plan", "nio: approve plan"),
         "tasks_jury": ("tasks", "nio: approve tasks")}
STATE_KEYS = ("auto", "pause", "abandon", "waiting", "claims", "attempts", "run")  # FR-3, and nothing else


def defaults():
    return {"auto": False, "pause": None, "abandon": None, "waiting": None, "claims": {}, "attempts": {}, "run": ""}


class Broken(Exception):
    """An effort's flow files can't be trusted (CT-1, FR-6): printed as `error: <slug>: <file>, <where>`."""
    def __init__(self, file, where, slug=""):
        super().__init__(f"{slug}: {file}, {where}")
        self.file, self.where, self.slug = file, where, slug


class Busy(Exception):
    """Another `nio flow` call holds the effort's lock (CT-3, FR-45)."""


HELD = {}  # (effort folder, pid) -> the lock this process holds there, re-read before each write (CT-3)


def who(by):
    """`--by "<role> / <host> / <model>"` as a history line's `who`; `human` alone is the human (CT-2, CT-16)."""
    if by.strip() == "human":
        return {"role": "human", "host": "", "model": ""}
    parts = [p.strip() for p in by.split("/")]
    if len(parts) != 3 or not all(parts):
        raise ValueError(f'--by must be "<role> / <host> / <model>" or human, not "{by}"')
    return dict(zip(("role", "host", "model"), parts))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(root, slug):
    """(state, lines, tail) for `load` and `record` (CT-1). `tail` says what the next write must repair: `keep`, the
    bytes of history.jsonl that stay; `cut`, the torn bytes after them and `line`, the first cut line's number;
    `newline`, the kept last line lacks its `\\n`; `temp`, whether state.json.new is the state the last line names."""
    folder = root / ".nio/specs" / slug
    sp, hp, np = folder / "state.json", folder / "history.jsonl", folder / "state.json.new"
    if not hp.exists():
        if sp.exists():
            raise Broken("history.jsonl", "missing", slug)
        return defaults(), [], {"keep": 0, "cut": b"", "line": 0, "newline": False, "temp": False}
    raw, hashes = hp.read_bytes(), {sha(p.read_bytes()) for p in (sp, np) if p.exists()}
    rows, pos = [], 0  # (line number, parsed or None, end offset, has its \n)
    for n, chunk in enumerate(re.findall(rb"[^\n]*\n|[^\n]+$", raw), 1):
        pos += len(chunk)
        try:
            line = json.loads(chunk)
        except ValueError:
            line = None
        whole = chunk.endswith(b"\n")
        if whole and not isinstance(line, dict):
            raise Broken("history.jsonl", f"line {n}", slug)
        if not whole and not (isinstance(line, dict) and line.get("state") in hashes):
            line = None  # a torn last line (FR-59)
        rows.append((n, line, pos, whole))
    ends = [i for i, r in enumerate(rows) if r[1] is not None and r[1].get("end")]
    kept = rows[:ends[-1] + 1] if ends else []  # lines after the last `end` line are a batch cut off mid-write
    keep = kept[-1][2] if kept else 0
    lines = [r[1] for r in kept]
    tail = {"keep": keep, "cut": raw[keep:], "line": rows[len(kept)][0] if len(rows) > len(kept) else 0,
            "newline": bool(kept) and not kept[-1][3], "temp": False}
    want = lines[-1].get("state") if lines else None
    path = sp
    if want and np.exists() and sha(np.read_bytes()) == want and not (sp.exists() and sha(sp.read_bytes()) == want):
        path, tail["temp"] = np, True  # a write that crashed after its lines: the temp state is the one they name
    if not path.exists():
        if want:
            raise Broken("state.json", "missing", slug)
        return defaults(), lines, tail
    data = path.read_bytes()
    try:
        state = json.loads(data)
    except ValueError:
        state = None
    if not isinstance(state, dict):
        raise Broken("state.json", "not valid JSON", slug)
    for key in sorted(state):
        if key not in STATE_KEYS:
            raise Broken("state.json", f"key {key}", slug)
    if sha(data) != want:
        raise Broken("state.json", "hash mismatch", slug)
    return {**defaults(), **state}, lines, tail


def load(root, slug):
    """(state, lines): the effort's state.json (the defaults when it has none) and its complete history lines, oldest
    first (CT-1, FR-3, FR-6, FR-58, FR-59). Raises Broken when either file can't be trusted."""
    return read(root, slug)[:2]


def record(root, slug, entries, state, who, run, at=None):
    """Append `entries` as history lines and write the state they leave (CT-2, FR-4, FR-5, FR-25, FR-58, FR-59), only
    while holding the effort's lock. A torn tail is cut first and noted on a `repair` line. Write order: the state to
    state.json.new, the lines in one write, then the rename; CT-1 reads a crash at any point as the last `end` line."""
    folder = root / ".nio/specs" / slug
    mine = HELD.get((folder.resolve(), os.getpid()))
    if mine and holder(folder / "flow.lock")[:2] != mine[:2]:  # taken over meanwhile: never double a line
        raise busy(slug, folder / "flow.lock")
    sp, hp, np = folder / "state.json", folder / "history.jsonl", folder / "state.json.new"
    _, lines, tail = read(root, slug)
    if not entries and not tail["cut"]:  # a cut alone still writes its `repair` line
        raise ValueError("a state.json write needs at least one history line")
    if tail["temp"]:
        os.replace(np, sp)  # roll the crashed write forward
    elif np.exists():
        np.unlink()  # a temp state no line names
    entries = list(entries)
    if not lines and entries and (route := header_route(root, slug)):  # the route the effort starts on (AC-2)
        entries[0] = {**entries[0], "evidence": {**(entries[0].get("evidence") or {}), "route": route}}
    if tail["cut"]:
        cut = tail["cut"]
        last = lines[-1]["to"] if lines else None
        entries.insert(0, {"kind": "repair", "from": last, "to": last,
                           "reason": f"cut torn history from line {tail['line']}: {len(cut)} bytes: {cut.hex()}"})
        with open(hp, "r+b") as f:
            f.truncate(tail["keep"])
    data = (json.dumps(state, indent=2, sort_keys=True) + "\n").encode()
    stamp = (at or datetime.datetime.now(datetime.timezone.utc)).astimezone(datetime.timezone.utc)
    out = []
    for i, e in enumerate(entries):
        line = {"kind": e["kind"], "at": stamp.strftime("%Y-%m-%dT%H:%M:%SZ"), "who": who, "from": e.get("from"),
                "to": e.get("to"), "evidence": {"paths": [], "verdict": "", "output": "", **(e.get("evidence") or {})},
                "run": run, "state": sha(data)}
        if e.get("reason") is not None:
            line["reason"] = e["reason"]
        if e.get("change") is not None:
            line["change"] = e["change"]
        if i == len(entries) - 1:
            line["end"] = True
        out.append(json.dumps(line, ensure_ascii=False) + "\n")
    with open(np, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    with open(hp, "ab") as f:
        f.write(("\n" if tail["newline"] else "").encode() + "".join(out).encode())
        f.flush()
        os.fsync(f.fileno())
    os.replace(np, sp)


def holder(path):
    """(pid, host, at) a lock file names; (None, None, None) when it is gone or unreadable."""
    try:
        data = json.loads(path.read_text())
        return data.get("pid"), data.get("host"), data.get("at")
    except (OSError, ValueError, AttributeError):
        return None, None, None


def busy(slug, path):
    pid, host, _ = holder(path)
    return Busy(f"{slug} is being written by another nio flow call (pid {pid} on {host}); try again")


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except (PermissionError, TypeError, ValueError, OverflowError):
        return isinstance(pid, int)  # another user's process is still a process; a bad pid is none
    return True


@contextlib.contextmanager
def lock(root, slug):
    """Hold `.nio/specs/<slug>/flow.lock` for the body (CT-3, FR-45, FR-54): created atomically, naming this process
    and host; a lock older than a minute whose process on this host is gone, or whose host is another one, is taken
    over. Raises Busy otherwise. Removed on exit only while it is still this caller's."""
    folder = root / ".nio/specs" / slug
    ignore = folder / ".gitignore"
    have = ignore.read_text().splitlines() if ignore.exists() else []
    if missing := [x for x in ("flow.lock*", "state.json.new") if x not in have]:
        ignore.write_text("".join(f"{x}\n" for x in have + missing))
    path, host = folder / "flow.lock", socket.gethostname()
    mine = (os.getpid(), host, datetime.datetime.now(datetime.timezone.utc).isoformat())

    def create():
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w") as f:
            json.dump(dict(zip(("pid", "host", "at"), mine)), f)

    try:
        create()
    except FileExistsError:
        judged = holder(path)
        pid, other, _ = judged
        try:
            age = time.time() - path.stat().st_mtime
        except FileNotFoundError:
            age = 0  # released meanwhile: a new try is a new call
        if not (age > 60 and (other != host or not alive(pid))):
            raise busy(slug, path) from None
        stale = folder / f"flow.lock.{os.getpid()}.{secrets.token_hex(4)}"
        try:
            os.rename(path, stale)  # of two callers taking it over, only one renames it
        except FileNotFoundError:
            raise busy(slug, path) from None
        if holder(stale) != judged:  # not the lock judged stale but a new holder's: put it back and step aside
            try:
                os.link(stale, path)
            except FileExistsError:
                pass
            stale.unlink()
            raise busy(slug, path)
        try:
            create()
        except FileExistsError:
            raise busy(slug, path) from None
        finally:
            stale.unlink()
    HELD[(folder.resolve(), os.getpid())] = mine
    try:
        yield
    finally:
        HELD.pop((folder.resolve(), os.getpid()), None)
        if holder(path) == mine:
            path.unlink()


def verdict(root, slug, gate, rnd, outcome):
    """The ID of the verdict record the jury wrote for this gate, round and outcome, or ''."""
    found = ""
    for path in sorted((root / ".nio/memory").rglob("V-*.md")):
        try:
            if f"{gate}:{slug}" not in path.read_text():  # only parse the few that can match (NFR-3)
                continue
            meta = records.parse(path)[0]
        except ValueError:
            continue
        if (meta.get("subject"), meta.get("outcome")) == (f"{gate}:{slug}", outcome) and \
                str(meta.get("title", "")).endswith(f"(round {rnd})"):
            found = meta["id"]
    return found


def header_route(root, slug):
    """The route spec.md's header names, or None when it names none or can't be read."""
    try:
        return records.parse(root / ".nio/specs" / slug / "spec.md")[0].get("route")
    except (OSError, ValueError):
        return None


def ran_full(root, slug):
    """The effort ran on the full route: its first history line recorded `full`, or its spec jury has a round. With
    neither, the header decides (an effort from before routes were recorded)."""
    from nio import jury
    try:
        with open(root / ".nio/specs" / slug / "history.jsonl", encoding="utf-8") as f:
            if (json.loads(f.readline()).get("evidence") or {}).get("route") == "full":
                return True
    except (OSError, ValueError, AttributeError):
        pass
    try:
        return bool(jury.load(root, slug, "spec")["round"])
    except (OSError, ValueError, KeyError):
        return False


def skips(root, slug):
    """Stages skipped on the record: NOT_BUILT plus the spec's route's own (CT-1); none of lite's once the effort ran
    full."""
    route = header_route(root, slug)
    if route == "lite" and ran_full(root, slug):
        route = "full"
    return NOT_BUILT | ROUTE_SKIPS.get(route, set())


def guard(root, slug, stage, evidence=True):
    """(result, output, evidence) of the stage's guard, per the decision table "Guards" (CT-5, FR-12 to FR-15, FR-27):
    `pass`, `fail` or `closed` (a jury gate the human closed, `output` holding their reason). Decided only from files
    and the stage checks' results, never from an agent's word. `evidence` is CT-2's: paths read, verdict ID, output hash;
    `where`, which records nothing, skips the verdict lookup (NFR-3)."""
    from nio import jury, plan, spec, tasks
    if stage not in STAGES or stage == "done" or stage in skips(root, slug):
        raise ValueError(f"{stage} has no guard to run")
    folder = root / ".nio/specs" / slug
    rel = lambda *names: [str((folder / n).relative_to(root)) for n in names]
    paths, vid, result = rel("spec.md"), "", "fail"
    try:
        if stage == "intake":
            paths = rel("intake.md")
            output = [] if (folder / "intake.md").exists() else [f"ERROR {paths[0]} does not exist"]
        elif stage in ("drafting", "grilling"):
            output = [f"ERROR {e}" for e in spec.check(root, slug, gate=stage == "grilling")[0]]
            if any("`## Open points` must be empty" in x for x in output):  # name each one left (AC-14)
                body = records.parse(folder / "spec.md")[1]
                output += [f"ERROR open point {x.strip()[2:]}" for x in spec.sections(body).get("Open points", [])
                           if x.strip().startswith("- **OP-")]
        elif stage == "planning":
            paths = rel("spec.md", *plan.FILES)
            output = [f"ERROR {e}" for e in plan.check(root, slug, gate=True)[0]]
        elif stage == "tasking":
            paths = rel("spec.md", *plan.FILES, "tasks.md")
            output = [f"ERROR {e}" for e in tasks.check(root, slug)[0]]
        elif stage == "implementing":  # implement CT-14
            from nio import implement
            paths = rel("tasks.md")
            output = implement.left(root, slug, load(root, slug)[1])
        else:
            gate = GATES[stage][0]
            paths = rel(*jury.GATES[gate], f"jury/{gate}.json")
            led = jury.load(root, slug, gate)
            now = jury.standing(root, slug, gate)  # a closure is read the same way at every gate (CT-5)
            if now == "closed":
                pass
            elif stage == "spec_jury":
                left = sum(f["status"] == "open" for f in led["findings"])
                output = [] if now == "approved" and not left else \
                    [f"the spec jury's outcome is {now}" + (f", {left} findings open" if left else "")]
            else:
                ok, why = (plan if stage == "plan_jury" else tasks).approved(root, slug)
                output = [] if ok else [why]
            if now == "closed":
                result, output = "closed", [led["closed"][2]]
                vid = verdict(root, slug, gate, led["round"], "human") if evidence else ""
            if result != "closed" and not output and evidence:
                vid = verdict(root, slug, gate, led["round"], "approved")
    except ValueError as e:  # a missing spec, plan or tasks file is a failing guard, said as such
        output = [f"ERROR {e}"]
    if result != "closed":
        result = "fail" if output else "pass"
    text = "\n".join(output)
    return result, output, {"paths": paths, "verdict": vid, "output": sha(text.encode()) if text else ""}


def kind(root, slug):
    """`legacy`, `unsupported: <route>`, `route changed: ...` or `effort` (CT-4, FR-29, FR-50): an undated folder is
    legacy; a dated one is unsupported when its spec.md names a route other than `full` or `lite`, and route changed
    when the header says lite on an effort that ran full."""
    if not DATED.match(slug):
        return "legacy"
    path = root / ".nio/specs" / slug / "spec.md"
    if path.exists():
        try:
            route = records.parse(path)[0].get("route")
        except ValueError:  # a header that can't be read names no route yet
            route = None
        if route and route not in ("full", "lite"):
            return f"unsupported: {route}"
        if route == "lite" and ran_full(root, slug):  # read only when the header says lite: kind runs per folder
            return "route changed: recorded full, spec.md says lite"
    return "effort"


def efforts(root):
    """The dated, full-route folders under .nio/specs/: the efforts a command can act on (CT-4)."""
    specs = root / ".nio/specs"
    return sorted(p.name for p in specs.iterdir() if p.is_dir() and kind(root, p.name) == "effort") if specs.is_dir() else []


def pick(root, slug=None):
    """The effort a command acts on (CT-4, FR-9, FR-11): the slug given, or the one whose last complete history line is
    the newest. Keeps no pointer of its own. Raises ValueError, listing the efforts it can act on."""
    listing = "".join(f"\n  {s}" for s in efforts(root))
    if slug is not None:
        if not (root / ".nio/specs" / slug).is_dir():
            raise ValueError(f"no effort {slug} under .nio/specs/{listing}")
        return slug
    newest, broken = None, []
    for s in efforts(root):
        if not (root / ".nio/specs" / s / "history.jsonl").exists():
            continue
        try:
            lines = load(root, s)[1]
        except Broken as e:  # one broken effort doesn't stop the others (FR-6 refuses only that one)
            broken.append(f"\n  broken: {e}")
            continue
        if lines and (newest is None or lines[-1]["at"] > newest[0]):
            newest = (lines[-1]["at"], s)
    if not newest:
        raise ValueError('no current effort; start one with: nio flow start <slug> --by "<role> / <host> / <model>"'
                         + listing + "".join(broken))
    return newest[1]


# --- where an effort is (CT-6) and the commands (CT-9, CT-10, CT-13) ---

SKILL = {"intake": "@nio:spec", "drafting": "@nio:spec", "grilling": "@nio:grill", "spec_jury": "@nio:jury",
         "planning": "@nio:plan", "plan_jury": "@nio:jury", "tasking": "@nio:tasks", "tasks_jury": "@nio:jury",
         "implementing": "@nio:implement"}
INPUTS = {"intake": [], "drafting": ["intake.md"], "grilling": ["spec.md", "research.md", "grill.md"],
          "planning": ["spec.md", "architecture.md", "research.md", "grill.md"],
          "tasking": ["spec.md", "architecture.md", "plan.md", "contracts.md", "tests.md", "quickstart.md"],
          "implementing": ["tasks.md"]}
EXIT = {  # the decision table "Guards", word for word
    "intake": "`intake.md` exists",
    "drafting": "`spec.md` exists and every template section is filled or has an open point",
    "grilling": "`nio check spec --gate` passes: no open point, no unconfirmed `[default]`",
    "spec_jury": "the spec ledger says approved with `unresolved: 0`, or the human closed it with a reason",
    "planning": "`nio check plan --gate` passes",
    "plan_jury": "`nio check plan --approved` exits 0",
    "tasking": "`nio check tasks` passes: every AC has a task and every task an AC",
    "tasks_jury": "`nio check tasks --approved` exits 0 (the tasks ledger approved, or the human closed it with a reason)",
    "implementing": "every task is done and every epic has its `epic` line"}
ASKED = re.compile(r"^## Asked · (Q\d+)\b", re.M)
ANSWERED = re.compile(r"^## (Q\d+)\b", re.M)


def commits(root, slug):
    """The `nio: approve <gate>` commits touching the effort folder, newest first: (hash, commit time, gate stage)."""
    stage_of = {message: s for s, (_, message) in GATES.items()}
    out = []
    for x in records.git(root, "log", "--format=%H %cI %s", "--grep", "^nio: approve ", "--", f".nio/specs/{slug}"):
        h, when, message = x.split(" ", 2)
        if message in stage_of:
            out.append((h, when, stage_of[message]))
    return out


def approvals(root, slug, found=None):
    """{gate stage: the ledger rounds its `nio: approve <gate>` commits of the effort folder hold} (FR-55), read with
    one `git log` and one `git show`."""
    folder = f".nio/specs/{slug}"
    found = [(h, s) for h, _, s in (commits(root, slug) if found is None else found)]
    specs = [f"{h}:{folder}/jury/{GATES[s][0]}.json" for h, s in found]
    out = {s: set() for s in GATES}
    code, text, _ = records.git(root, "show", *specs, full=True) if specs else (1, "", "")
    docs = []
    if code == 0:
        pos, decoder = 0, json.JSONDecoder()
        while pos < len(text.rstrip()):
            try:
                doc, pos = decoder.raw_decode(text, pos)
            except ValueError:
                docs = []
                break
            docs.append(doc)
            pos = len(text) - len(text[pos:].lstrip())
    if len(docs) != len(specs):  # a commit without the ledger, or one that isn't JSON: one at a time
        docs = []
        for spec_ in specs:
            code, text, _ = records.git(root, "show", spec_, full=True)
            try:
                docs.append(json.loads(text) if code == 0 else None)
            except ValueError:
                docs.append(None)
    for (_, s), doc in zip(found, docs):
        if isinstance(doc, dict):
            out[s].add(doc.get("round"))
    return out


def gate_passed(stage, led, lines, approved):
    """A gate counts as passed only with a `nio: approve <gate>` commit of the effort folder holding the ledger's
    current round, or an override line from it at that round; an earlier round's approval no longer counts (FR-55)."""
    return led["round"] in approved[stage] or any(
        x["kind"] == "override" and x["from"] == stage and x["evidence"].get("round") == led["round"] for x in lines)


def question(root, slug):
    """The grill's last asked question with no answer entry after it (FR-8), or None."""
    path = root / ".nio/specs" / slug / "grill.md"
    text = path.read_text() if path.exists() else ""
    open_ = [m.group(1) for m in ASKED.finditer(text)
             if not any(a.group(1) == m.group(1) and a.start() > m.start() for a in ANSWERED.finditer(text))]
    return open_[-1] if open_ else None


def unseen(lines):
    """(stage, reason) of each override no `seen` line follows (CT-15, FR-57)."""
    out = []
    for x in lines:
        out = [] if x["kind"] == "seen" else out + [(x["from"], x.get("reason", ""))] * (x["kind"] == "override")
    return out


def plan_files():
    from nio import plan
    return list(plan.FILES)


# the decision table "Owning stage": file -> (where a pending change request sends the effort, where an edit after its
# gate approved it does); and the gate whose approval judged each file
OWNING = {"intake.md": ("drafting", None), "research.md": ("grilling", None), "spec.md": ("grilling", "spec_jury"),
          "architecture.md": ("arch_grilling", None), **{f: ("planning", "plan_jury") for f in plan_files()},
          "tasks.md": ("tasking", "tasks_jury")}
JUDGED_BY = {"spec.md": "spec_jury", **{f: "plan_jury" for f in plan_files()},
             "tasks.md": "tasks_jury"}


def planned(name, text):
    """A file as its gate judges it (RF-9): jury.planned, which jury.artefact uses too."""
    from nio import jury
    return jury.planned(name, text)


def judged_blob(root, slug, name):
    """The blob CT-7 compares a file by: git's hash of the raw file, or for tasks.md of its planned part as the jury
    reads it. The same on every side (approval commit, override line, now), so line endings never read as an edit."""
    from nio import jury
    if name == "tasks.md":
        return jury.blob(root, planned(name, (root / ".nio/specs" / slug / name).read_text()))
    return records.git(root, "hash-object", f".nio/specs/{slug}/{name}")[0]


def when_of(at):
    return datetime.datetime.fromisoformat(at.replace("Z", "+00:00")).timestamp()


def named(entry, lines, kinds=("back", "resume")):
    """Whether a `back` (or `resume`) line already names this change (FR-37, FR-42)."""
    for x in lines:
        if x["kind"] in kinds and x.get("change") is not None:
            c = x["change"]
            if entry["pending"] and c == entry["change"]:
                return True
            if not entry["pending"] and isinstance(c, dict) and (c.get("file"), c.get("judged")) == (
                    entry["change"], entry["judged"]):
                return True
    return False


def scan(root, slug, lines, found=None):
    """(entries, unreadable change records): CT-7's changes, and the change records that couldn't be read."""
    from nio import jury
    folder, rel = root / ".nio/specs" / slug, f".nio/specs/{slug}"
    out, unreadable = [], []
    for path in sorted((root / ".nio/memory").rglob("C-*.md")) if (root / ".nio/memory").is_dir() else []:
        if slug not in path.read_text():
            continue
        try:
            meta = records.parse(path)[0]
        except ValueError:
            unreadable.append(str(path.relative_to(root)))  # a record lint is `nio check`'s job, never fatal here
            continue
        against = str(meta.get("against") or "").removeprefix(".nio/specs/")
        name = against.removeprefix(f"{slug}/")
        if meta.get("outcome") == "pending" and against == f"{slug}/{name}" and name in OWNING:  # FR-35
            out.append({"change": meta.get("id", path.name[:13]), "target": OWNING[name][0], "judged": "",
                        "current": "", "pending": True, "file": name, "record": str(path.relative_to(root))})
    newest = {}
    for h, at_, s in commits(root, slug) if found is None else found:
        newest.setdefault(s, (h, at_))
    trees, raw = {}, None
    for name, gate in JUDGED_BY.items():  # FR-36: an approved file edited since its gate judged it
        if not (folder / name).exists():
            continue
        judged, h, since = None, None, None
        if gate in newest:
            h, since = newest[gate]
            if h not in trees:
                trees[h] = {path: blob for _, _, blob, path in (
                    x.replace("\t", " ").split(" ", 3) for x in records.git(root, "ls-tree", "-r", h, "--", rel))}
            judged = trees[h].get(f"{rel}/{name}")
        over = [x for x in lines if x["kind"] == "override" and x["from"] == gate and
                (since is None or when_of(x["at"]) > when_of(since)) and name in x["evidence"].get("blobs", {})]
        if over:
            judged, h = over[-1]["evidence"]["blobs"][name], None
        if not judged:
            continue
        if raw is None:
            names = [n for n in JUDGED_BY if (folder / n).exists()]
            raw = dict(zip(names, records.git(root, "hash-object", *[f"{rel}/{n}" for n in names])))
        current = raw.get(name)
        if name == "tasks.md" and current != judged:  # compare the planned part only: a fix task doesn't count
            if h:
                code, text, _ = records.git(root, "show", f"{h}:{rel}/{name}", full=True)
                judged = jury.blob(root, planned(name, text)) if code == 0 else judged
            current = jury.blob(root, planned(name, (folder / name).read_text()))
        if current != judged:
            out.append({"change": name, "target": OWNING[name][1], "judged": judged, "current": current,
                        "pending": False, "file": name})

    def settled(e):  # a pass or override leaving its target after the `back` line that named it (CT-7)
        marks = [i for i, x in enumerate(lines) if x["kind"] == "back" and named(e, [x], ("back",))]
        return bool(marks) and any(x["kind"] in ("pass", "override") and x["from"] == e["target"]
                                   for x in lines[marks[-1] + 1:])
    return [e for e in out if e["pending"] or not settled(e)], unreadable


def changes(root, slug, lines):
    """CT-7 (FR-35 to FR-38): the pending change records against the effort's files and the approved files edited
    since their gate judged them, each with the stage the decision table "Owning stage" sends the effort to."""
    return scan(root, slug, lines)[0]


def backs(here, lines, slug, auto=False):
    """The `back` lines a writing call owes: one per change no `back` line names yet, recorded once (FR-37); with the
    auto flag on, only once a `resume` line names it, since the effort first pauses for the human (FR-42)."""
    out, prev = [], last_to(lines)
    for e in here["changes"]:
        if named(e, lines, ("back",)) or auto and not named(e, lines, ("resume",)):
            continue
        change = e["change"] if e["pending"] else {"file": e["file"], "judged": e["judged"], "current": e["current"]}
        out.append({"kind": "back", "from": prev, "to": e["target"], "change": change,
                    "evidence": {"paths": [f".nio/specs/{slug}/{e['file']}"]}})
        prev = e["target"]
    return out


def where(root, slug, state=None, lines=None):
    """Where the effort is (CT-6, FR-2, FR-8, FR-22, FR-23, FR-47, FR-49, FR-55, FR-56): the first stage of the state
    table "Flow" that has not passed, read from the files, the ledgers, git and history; never writes."""
    from nio import jury
    if state is None:
        state, lines = load(root, slug)
    skill = ""
    stage, why, ready, results, ledgers, approved, sent_by, task = "done", "", None, {}, {}, [], None, ""
    passes = lambda s: results[s] if s in results else results.setdefault(s, guard(root, slug, s, evidence=False)[0])
    ledger = lambda s: ledgers[s] if s in ledgers else ledgers.setdefault(s, jury.load(root, slug, GATES[s][0]))

    found = commits(root, slug)

    def cleared(s):  # the gate's guard passes and its approval commit or override counts (FR-55)
        approved[:] = approved or [approvals(root, slug, found)]
        return passes(s) in ("pass", "closed") and gate_passed(s, ledger(s), lines, approved[0])

    order, off = list(STAGES), skips(root, slug)
    for s in STAGES:
        if s == "done" or s in off:
            continue
        if s in GATES:
            gate, led = GATES[s][0], ledger(s)
            judged = jury.version(led, led["round"])
            if led.get("outcome") == "rejected" and judged and jury.blob(root, jury.artefact(root, slug, gate)) == judged:
                stage, why, sent_by = STAGES[s][1], f"the {gate} jury rejected round {led['round']}", s
                break
            if cleared(s):
                continue
            stage, ready = s, passes(s)
            break
        # a stage before a gate that has passed needs no check of its own: the gate's approval covers its files (NFR-3)
        gate = next((g for g in order[order.index(s):] if g in GATES and g not in off), None)
        if gate and cleared(gate):
            continue
        if s == "drafting" and passes("grilling") == "pass":  # the gate's spec check is a superset of drafting's
            continue
        if passes(s) == "pass" or any(x["kind"] == "override" and x["from"] == s for x in lines):
            continue
        stage = s
        break
    entries, unreadable = scan(root, slug, lines, found)
    if state["abandon"] is not None:  # frozen where it was abandoned until `nio flow start` resumes it (FR-52)
        stage, entries = next((x["from"] for x in reversed(lines) if x["kind"] == "abandon"), stage), []
    at = list(STAGES).index
    for e in entries:  # a change sends the effort back to the stage that owns the file (FR-35, FR-36)
        if state["auto"] and not named(e, lines):
            continue  # FR-42: an auto effort waits for the human before a change moves it (CT-8)
        if at(e["target"]) < at(stage) or e["target"] == stage and ready:
            stage, ready, why = e["target"], None, f"{e['change']} moved it back"
    skipped = []
    for s in reversed(order[:order.index(stage)]):
        if s not in off:
            break
        skipped.insert(0, s)
    folder = root / ".nio/specs" / slug
    rel = lambda name: str((folder / name).relative_to(root))
    names = jury_files(stage) if stage in GATES else INPUTS.get(stage, [])
    command = f"nio flow done {stage} {slug}"
    asked = question(root, slug)
    pending = [e for e in entries if e["pending"] and (not state["auto"] or named(e, lines))]  # FR-38
    if state["abandon"] is not None:
        status, command = f"abandoned: {state['abandon']}", f"nio flow start {slug} --by human"
    elif state["pause"]:
        status, command = f"{state['pause']['kind']}: {state['pause']['why']}", f"nio flow start {slug} --by human"
    elif state["waiting"]:
        status, command = f"waiting_for_human: {state['waiting']['why']}", f"nio flow start {slug} --by human"
        if state["waiting"]["why"].startswith("commit failed"):  # CT-9: the retry re-runs the review and the commit
            command = f"nio flow green {slug} {state['waiting']['task']} {by_arg(None)}"
        elif state["waiting"].get("task"):  # CT-10, CT-11: a blocked task goes on when the human unblocks it
            command = f'nio flow unblock {slug} {state["waiting"]["task"]} --human "<reason>" --by human'
    elif pending:
        status, command = f"waiting_for_human: {pending[0]['change']} pending", ""
    elif asked:
        status, command = f"waiting_for_human: {asked}", ""
    elif ready == "pass":
        status, command = f"waiting_for_human: approve {GATES[stage][0]}", f"nio flow done {stage} --commit {slug} --by human"
    elif stage == "implementing":  # implement CT-14: the claimed task, else the next ready one
        from nio import implement
        tid = state["claims"].get("task")
        t = next((t for t in implement.tasks_of(root, slug) if t["id"] == tid), None) if tid else \
            implement.next_ready(root, slug, lines)
        status, command = "working", "" if tid or not t else f"nio flow claim {slug}"
        task = f"{t['id']} {t['title']}" + " (claimed)" * bool(tid) if t else ""
        gate = None if tid else implement.open_gate(root, slug, lines)
        if gate:  # CT-17: the epic waits on its gate
            gate = f"implementation-{gate}"
            held = [p for p in jury.gate_changes(root, slug, gate) if re.search(r"^outcome: pending", (root / p).read_text(), re.M)]
            task = f"{gate} is open" + (f" (held on a change request: {held[0]})" if held else "")
            skill, command = "@nio:jury", f"nio flow done {gate} {slug}"
    elif stage == "done":
        status, command = "done", ""
    else:
        status = "working"
    return {"stage": stage, "status": status, "why": why, "skill": skill or SKILL.get(stage, ""),
            "inputs": [rel(n) for n in names if (folder / n).exists()], "exit": EXIT.get(stage, ""),
            "command": command, "skipped": skipped, "changes": entries, "overrides": unseen(lines),
            "unreadable": unreadable, "refs": pending[0]["record"] if pending else "",
            "gate": sent_by or (stage if stage in GATES else None), "ready": ready, "task": task}


def jury_files(stage):
    from nio import jury
    return jury.GATES[GATES[stage][0]]


def refuse(root, slug):
    """Legacy and unsupported folders are never written (FR-29, FR-50)."""
    k = kind(root, slug)
    if k != "effort":
        raise ValueError(f"{slug} is {k}; nio flow writes nothing in it")


def run_for(root, slug, stage, state):
    """A history line's run (CT-17, FR-5): the newest run whose flow.json names this effort and the stage being left
    (or a task), else state.json's `run`, else ''."""
    best = ("", "")
    for path in (root / ".nio/runs").glob("R-*/flow.json"):
        try:
            link = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if isinstance(link, dict) and link.get("effort") == slug and (link.get("stage") == stage or "task" in link):
            best = max(best, (str(link.get("at", "")), path.parent.name))
    return best[1] or state.get("run") or ""


def write(root, slug, entries, state, w, stage):
    """`record` with the run CT-17 looks up, stored as state.json's `run` too."""
    run = run_for(root, slug, stage, state)
    record(root, slug, entries, {**state, "run": run}, w, run)


def last_to(lines):
    return lines[-1]["to"] if lines else None


def resumed(state, lines, stage, stop=None):
    """The `resume` line and the state clearing what held the effort (FR-31, FR-44, FR-53), or (None, state). A
    stop-list pause, stored or found live (`stop`), is named on the line: its change (FR-42) or its gate and round
    (FR-39), so it doesn't pause the effort again."""
    waiting = state["waiting"] or (stop or {}).get("waiting")
    held = [f"abandoned: {state['abandon']}"] if state["abandon"] is not None else []
    held += [f"{state['pause']['kind']}: {state['pause']['why']}"] if state["pause"] else []
    held += [f"waiting_for_human: {waiting['why']}"] if waiting else []
    if not held:
        return None, state
    line = {"kind": "resume", "from": last_to(lines), "to": stage, "reason": "; ".join(held)}
    if waiting:
        line["evidence"] = {"waiting": waiting}
        if waiting.get("change") is not None:
            line["change"] = waiting["change"]
    return line, {**state, "pause": None, "abandon": None, "waiting": None}


def held(state):
    return state["abandon"] is not None or bool(state["pause"]) or bool(state["waiting"])


def typed(skill):
    """What the human types to run a skill on this host; a host we can't identify gets the plain name."""
    # ponytail: only Claude Code is detected; add a host's form here once it is verified on that host
    return f"/{skill[1:]}" if os.environ.get("CLAUDECODE") else f"the {skill[1:]} skill"


def by_arg(by):
    return '--by "<role> / <host> / <model>"' if by is None else "--by human" if by == "human" else f'--by "{by}"'


def talk(slug, here):
    """An effort that waits, in the "Talking to the human" shape, naming no skill (CT-9, FR-43)."""
    status = here["status"]
    first, refs = next(((f, r) for key, f, r in [
        ("waiting_for_human: C-", "Settle the change request {q}", ""),
        ("waiting_for_human: Q", "Answer the grill's question {q}", "grill.md"),
        ("waiting_for_human: approve", "Approve or push back: run the command below", "jury/"),
        ("waiting_for_human: commit failed", "Fix what git refused, then run the command below", "history.jsonl"),
        ("waiting_for_human: spec problem", "Settle the change request, then run the command below", "spec.md"),
        ("waiting_for_human: T-", "Look at the task's saved changes, then run the command below", "history.jsonl"),
        ("done", "Nothing needed: the effort is done", "history.jsonl")] if status.startswith(key)),
        ("Run this command to resume", "state.json"))
    out = [first.format(q=status.split(": ", 1)[-1].split()[0]), f"effort: {slug}", f"state: {here['stage']} ({status})"]
    out += [here["command"]] * bool(here["command"]) + overridden(here)
    return out + [f"Refs: {here.get('refs') or f'.nio/specs/{slug}/{refs}'}"]


def overridden(here):
    """One line listing every override the human hasn't seen yet (FR-57), or none."""
    return ["override not seen: " + "; ".join(f"{s}: {r}" for s, r in here["overrides"])] if here["overrides"] else []


def next_step(root, slug=None, by=None):
    """`nio flow next` (CT-9, FR-7, FR-31, FR-43, NFR-1): the state, the skill, its inputs, exit criteria and done
    command; in the "Talking to the human" shape when the effort waits. Writes only with `by`, and only what it owes:
    a parked effort's resume, the `back` lines of a change, a stop-list pause, a torn line's cut. Returns (code, lines)."""
    slug = pick(root, slug)
    k = kind(root, slug)
    if k == "legacy":
        return 0, [f"legacy: {slug} has no flow layout; nothing to do"]
    if k.startswith("route changed:"):
        return 0, [k, "a full effort can't go lite: restore `route: full` in spec.md's header"]
    if k != "effort":
        return 0, [f"{k}: nio flow drives full and lite specs only"]

    def owes(state, lines):  # (what the call owes, as line kinds; the lines; the state they leave; where it is shown)
        parked = bool(state["pause"]) and state["pause"]["kind"] == "parked"
        shown = {**state, "pause": None} if parked else state  # what `next --by` shows once it resumed the effort
        here = where(root, slug, shown, lines)
        entry, new = resumed(state, lines, here["stage"]) if parked else (None, state)
        entries = [entry] * bool(entry)
        stop = None if held(shown) else stops(root, slug, here, shown, lines)
        if stop:  # one stop-list pause, recorded before anything else (CT-8)
            line, new = stop_line(stop, here["stage"], new)
            entries.append(line)
            here = stopped(here, stop, slug)
        else:
            entries += backs(here, lines + entries, slug, state["auto"])
        return entries, new, here

    state, lines, tail = read(root, slug)
    has = (root / ".nio/specs" / slug / "history.jsonl").exists()
    entries, new, here = owes(state, lines)
    owed = [x["kind"] for x in entries] + ["repair"] * bool(tail["cut"]) if has else []
    if owed and by is not None:
        w = who(by)
        with lock(root, slug):
            state, lines = load(root, slug)
            entries, new, _ = owes(state, lines)
            write(root, slug, entries, new, w, last_to(lines))
        state, lines = load(root, slug)
        here = where(root, slug, state, lines)
    if here["status"] == "working":
        out = [f"effort: {slug}", f"state: {here['stage']} (working{': ' + here['why'] if here['why'] else ''})",
               f"skill: {here['skill']}", f"next: run {typed(here['skill'])}", f"inputs: {', '.join(here['inputs']) or 'none'}", f"exit: {here['exit']}"]
        out += [f"task: {here['task']}"] * bool(here["task"])
        label = "claim" if here["command"].startswith("nio flow claim") else "done"
        out += [f"never reviewed: {e}" for e in never_reviewed(root, slug, lines)]
        out += [f"{label}: {here['command']} {by_arg(by)}"] * bool(here["command"])
        out += [f"skipped: {', '.join(x)} ({why})" for x, why in (
            ([x for x in here["skipped"] if x in NOT_BUILT], "not built"),
            ([x for x in here["skipped"] if x not in NOT_BUILT], "lite route")) if x] + overridden(here)
    else:
        out = talk(slug, here)
        if here["status"] == "suspended: cap":  # FR-40: report what it used
            juries, runs = used(root, slug)
            out[-1:-1] = [f"juries used: {juries}", f"subagent runs used: {runs}"]
    if owed and by is None:
        out.append(f"would record: {', '.join(dict.fromkeys(owed))} (run with --by to record)")
    return 0, out


def never_reviewed(root, slug, lines):
    """Epics closed by an old `skipped: not built` line (CT-17)."""
    return [x["evidence"]["epic"] for x in lines if x["kind"] == "epic" and x.get("reason") == "skipped: not built"]


def start(root, slug, by):
    """`nio flow start` (CT-10, FR-10, FR-44, FR-53): create the flow files with a `start` line, resume a held effort
    (also one the stop list pauses), then record the `back` lines a change owes; or record a `start` line on a working
    one, which makes it the effort with the newest line. Returns (code, lines)."""
    slug = pick(root, slug)
    refuse(root, slug)
    w = who(by)
    load(root, slug)  # a broken effort is refused before the lock or .gitignore is touched
    with lock(root, slug):
        state, lines = load(root, slug)
        fresh = not (root / ".nio/specs" / slug / "history.jsonl").exists()
        stop = None if held(state) else stops(root, slug, where(root, slug, state, lines), state, lines)
        entry, new = resumed(state, lines, None, stop if stop and stop["kind"] == "pause" else None)
        if fresh:
            entry, new = {"kind": "start", "from": None, "to": None}, defaults()
        elif not entry:
            entry = {"kind": "start", "from": last_to(lines), "to": None}
        entry["to"] = where(root, slug, new, lines)["stage"]
        here = where(root, slug, new, lines + [entry])  # the resume names the change it cleared: now it moves
        write(root, slug, [entry] + backs(here, lines + [entry], slug, new["auto"]), new, w, entry["from"] or entry["to"])
    return 0, [f"{'resumed' if entry['kind'] == 'resume' else 'started'} {slug} at {here['stage']}"]


def park(root, slug, why, by):
    """`nio flow park` (CT-13, FR-30, FR-32): mark the effort parked with the reason and record it; creates the flow
    files first when missing, writing only the `park` line. Returns (code, lines)."""
    slug = pick(root, slug)
    refuse(root, slug)
    if not (why or "").strip():
        raise ValueError("park needs a reason")
    w = who(by)
    if where(root, slug)["stage"] == "done":
        raise ValueError(f"{slug} is done; nothing to park")
    with lock(root, slug):
        state, lines = load(root, slug)
        here = where(root, slug, state, lines)
        stage = here["stage"]
        new = {**state, "pause": {"kind": "parked", "why": why}}
        write(root, slug, backs(here, lines, slug, state["auto"]) + [{"kind": "park", "from": stage, "to": stage, "reason": why}],
              new, w, stage)
    return 0, [f"parked {slug}: {why}"]


# --- nio flow done (CT-11, CT-19) ---

RISKY = {"money", "data-deletion", "migration", "auth"}  # FR-51: with these the human always gives --commit


def moves(stage, off=NOT_BUILT):
    """The `skip` lines after `stage` up to the next built stage (FR-21), and that stage."""
    out, s = [], STAGES[stage][0]
    while s in off:
        out.append({"kind": "skip", "from": s, "to": STAGES[s][0],
                    "reason": "skipped: not built" if s in NOT_BUILT else "skipped: lite route"})
        s = STAGES[s][0]
    return out, s


def risky(root, slug):
    try:
        flags = records.parse(root / ".nio/specs" / slug / "spec.md")[0].get("risk") or []
    except (OSError, ValueError):
        return False
    return bool(RISKY & set(flags))


def pending_pass(lines, stage, verdict_id):
    """A crash between the append and the commit left this gate's `pass` line, for the round the guard approves now,
    as the newest line but for its skips: the next `--commit` only commits (CT-11)."""
    for x in reversed(lines):
        if x["kind"] == "skip":
            continue
        return x["kind"] == "pass" and x["from"] == stage and x["evidence"].get("verdict") == verdict_id
    return False


def stage_arg(name):
    """argparse type: a stage, or an epic's gate as `implementation-E-n`."""
    import argparse
    if name in STAGES or EPIC_GATE.fullmatch(name):
        return name
    raise argparse.ArgumentTypeError(f"invalid choice: {name!r} (choose from {', '.join(STAGES)}, implementation-E-n)")


def done(root, stage, slug=None, commit=False, human=None, by=None):
    """`nio flow done` (CT-11, FR-12 to FR-27, FR-48, FR-62): run the stage's guard and, when it passes (or the human
    overrides a failing one), record the move and the skips after it; at a gate, `--commit` (or the auto flag on a
    spec without a risky flag) also makes the approval commit, rolled back when git fails. Returns (code, lines)."""
    from nio import jury
    if EPIC_GATE.fullmatch(stage):
        return epic_done(root, stage, slug, by)
    if stage not in STAGES:
        raise ValueError(f"unknown stage {stage}")
    slug = pick(root, slug)
    refuse(root, slug)
    if human is not None and stage in GATES:  # FR-62: the jury closes its own gates
        gate = GATES[stage][0]
        return 1, [f"--human can't pass a jury gate; the human closes it through the jury:",
                   f'nio jury check {slug} {gate} --human "{human}" --record']
    if human is not None and not human.strip():
        raise ValueError("--human needs a reason")
    w = who(by)
    state, lines = load(root, slug)
    if commit and w["role"] != "human" and (not state["auto"] or risky(root, slug)):  # FR-18, FR-48, FR-51
        raise ValueError("--commit approves a gate: only the human gives it, with --by human")
    here = where(root, slug, state, lines)
    if held(state):
        return 1, talk(slug, here)
    if stops(root, slug, here, state, lines):  # CT-8: a writing call records the stop-list pause before anything else
        with lock(root, slug):
            state, lines = load(root, slug)  # what another writer recorded meanwhile stands
            here = where(root, slug, state, lines)
            stop = None if held(state) else stops(root, slug, here, state, lines)
            if stop:
                line, new = stop_line(stop, here["stage"], state)
                write(root, slug, [line], new, w, here["stage"])
        return 1, talk(slug, stopped(here, stop, slug) if stop else here)
    at, rec = list(STAGES).index, last_to(lines)
    for e in here["changes"]:  # FR-38: settle the change request first
        if e["pending"] and at(stage) >= at(e["target"]):
            raise ValueError(f"{e['change']} is outcome: pending against {e['file']}; settle it first")
    if at(stage) > at(here["stage"]):
        raise ValueError(f"{slug} is at {here['stage']}, not {stage}")
    # FR-47: the files may be past stages history hasn't recorded yet; `done` records those from where history stands.
    # A stage before both is already passed (FR-17).
    if at(stage) < at(here["stage"]) and (rec is None or at(stage) < at(rec)):
        return 0, [f"{slug} is past {stage}; nothing to do"]
    if stage == "done":
        return 0, [f"{slug} is done; nothing to do"]
    result, output, ev = guard(root, slug, stage)
    skipl, to = moves(stage, skips(root, slug))
    if result == "fail" and human is None:  # FR-13: nothing written, but FR-41's `fail` line in auto mode
        if state["auto"]:
            with lock(root, slug):
                state, lines = load(root, slug)
                fail = {"kind": "fail", "from": stage, "to": stage,
                        "evidence": {**ev, "output": fail_hash(root, output), "output_text": "\n".join(output)}}
                entries, last = [fail], (lines + [fail])[-3:]
                if len(last) == 3 and all(x["kind"] == "fail" and (x["from"], x["evidence"]["output"]) == (
                        stage, fail["evidence"]["output"]) for x in last):  # FR-41: stuck
                    entries.append({"kind": "suspend", "from": stage, "to": stage, "reason": "stuck"})
                    state = {**state, "pause": {"kind": "suspended", "why": "stuck"}}
                write(root, slug, entries, state, w, stage)
        return 1, output
    line = {"kind": "pass", "from": stage, "to": STAGES[stage][0], "evidence": ev}
    if human is not None:
        line["reason"] = human  # AC-30: a passing guard with --human is a plain pass, with the reason
        if result == "fail":  # FR-24
            line.update(kind="override", evidence={**ev, "output_text": "\n".join(output)})
    if result == "closed":  # FR-27: the human closed the jury gate; the ledger's reason is the override's
        gate = GATES[stage][0]
        led = jury.load(root, slug, gate)
        files = [n for n in jury.GATES[gate] if (root / ".nio/specs" / slug / n).exists()]
        line.update(kind="override", reason=output[0], evidence={
            **ev, "blobs": {n: judged_blob(root, slug, n) for n in files},
            "round": led["round"]})
    gated = stage in GATES and result == "pass"
    if gated and jury.load(root, slug, GATES[stage][0])["round"] in approvals(root, slug)[stage]:
        gated = False  # its approval commit for this round exists already: record the pass, commit nothing (FR-17, FR-47)
    if gated and not (commit or state["auto"] and not risky(root, slug)):
        command = f"nio flow done {stage} --commit {slug} --by human"
        return 0, [f"{slug}: the {GATES[stage][0]} gate passes; nothing is recorded until the human approves it:",
                   command]  # FR-48
    out = [f"moved {slug}: {stage} → {to}"] + [f"skipped {s['from']} ({s['reason'][9:]})" for s in skipl]
    if to in SKILL:
        out.append(f"next: run {typed(SKILL[to])}")
    with lock(root, slug):
        state, now = load(root, slug)
        if now != lines:
            raise ValueError(f"{slug} changed while its guard ran; try again")
        owed = backs(here, lines, slug, state["auto"])
        entries = owed + ([] if gated and pending_pass(lines, stage, ev["verdict"]) else [line] + skipl)
        if not gated:
            write(root, slug, entries, state, w, stage)
            if to == "done":
                from nio import usage
                out += usage.finish(root, slug)
            return 0, out
        return commit_gate(root, slug, stage, entries, state, w, out)


def epic_done(root, gate, slug=None, by=None):
    """`nio flow done implementation-E-n` (CT-17): when the gate is approved or the human closed it, and that is recorded,
    write the epic's `epic` line with the outcome as its reason and, after the last epic, the `pass` line implementing ->
    done, and make the approval commit. Any other standing refuses, naming the gate. An `epic` line already there, an
    old `skipped: not built` too, is closed: a second call writes nothing, and only commits what a crash left uncommitted."""
    from nio import implement, jury
    slug = pick(root, slug)  # no `refuse`: an epic with a recorded gate is what lets this write, whatever the folder's name
    w, epic = who(by), gate.removeprefix("implementation-")
    if not any(t["epic"] == epic for t in implement.tasks_of(root, slug)):
        raise ValueError(f"the subject of the implementation gate must be an epic from tasks.md, not {gate}")
    state, lines = load(root, slug)
    if held(state):
        return 1, talk(slug, where(root, slug, state, lines))
    line = next((x for x in lines if x["kind"] == "epic" and x["evidence"].get("epic") == epic), None)
    reason = line and line.get("reason")
    if not line:
        led, now = jury.load(root, slug, gate), jury.standing(root, slug, gate)
        if now not in ("approved", "closed"):
            return 1, [f"{gate} is {now}, not approved or closed; `nio flow done {gate}` needs its jury to approve it or the human to close it"]
        if [led["round"], now] not in led["recorded"]:
            return 1, [f"{gate} is {now} but not recorded: run `nio jury check {slug} {gate} --record` first"]
        reason = "human" if now == "closed" else now
    message = f"nio: approve {gate}"
    with lock(root, slug):
        state, now_lines = load(root, slug)
        if now_lines != lines:
            raise ValueError(f"{slug} changed while its gate was read; try again")
        entries = [] if line else [{"kind": "epic", "from": "implementing", "to": "implementing", "reason": reason, "evidence": {"epic": epic}}]
        last = not implement.left(root, slug, lines + entries) and not any(x["kind"] == "pass" and x["from"] == "implementing" for x in lines)
        if last:
            entries.append({"kind": "pass", "from": "implementing", "to": STAGES["implementing"][0],
                            "evidence": {"paths": [f".nio/specs/{slug}/tasks.md"]}})
        crashed = line and reason != "skipped: not built" and uncommitted(root, slug, gate) and \
            not records.git(root, "log", "-1", "--format=%H", f"--grep=^{message}$", "--", f".nio/specs/{slug}")
        if not entries and not crashed:
            return 0, [f"{gate} is closed already ({reason}); nothing to do"]
        out = [f"closed {gate}: {reason}"] + [f"merge: {implement.branch(slug)}"] * last
        if last:
            out += docs_close_lines(root, slug)
            out += [f"never reviewed: {e}" for e in never_reviewed(root, slug, lines + entries)]
        return commit_gate(root, slug, "implementing", entries, state, w, out, gate, message)


def docs_close_lines(root, slug):
    """CT-20: the project-doc sources the effort changed since it left main; nothing when there is no base or no docs."""
    from nio import onboard, implement
    base = (records.git(root, "merge-base", "main", implement.branch(slug)) or [""])[0]
    if not base:
        return []
    try:
        return onboard.close_lines(root, base)
    except ValueError:  # git failed: the close must not depend on the docs
        return []


def gate_paths(root, slug, gate):
    """What a gate's commit holds, as paths from the root: the effort folder, the gate's verdict records and, at an epic's
    gate, the change requests its findings raised."""
    from nio import jury
    return [f".nio/specs/{slug}", *verdicts(root, slug, gate), *jury.gate_changes(root, slug, gate)]


def uncommitted(root, slug, gate):
    return bool(records.git(root, "status", "--porcelain", "--", *gate_paths(root, slug, gate)))


def verdicts(root, slug, gate):
    """The verdict records `nio jury check --record` wrote for this gate, as paths from the root."""
    line = f'subject: "{gate}:{slug}"'
    return sorted(str(p.relative_to(root)) for p in (root / ".nio/memory").rglob("V-*.md")
                  if line in p.read_text(encoding="utf-8").splitlines())


def commit_gate(root, slug, stage, entries, state, w, out, gate=None, message=None):
    """Record the gate's pass and make its `nio: approve <gate>` commit (or `message`, for `gate`) of the effort folder and
    the gate's verdict records (FR-18, the jury skill's Approval step); when git
    fails, put history.jsonl, state.json and the index back as they were, byte for byte, and print git's error (FR-20,
    CT-19)."""
    folder = root / ".nio/specs" / slug
    sp, hp, np = folder / "state.json", folder / "history.jsonl", folder / "state.json.new"
    kept = hp.read_bytes() if hp.exists() else None  # the whole file: a cut torn tail must come back too
    saved = sp.read_bytes() if sp.exists() else None
    code, tree, err = records.git(root, "write-tree", full=True)
    if code:
        return 1, [err.strip()]
    if entries:
        write(root, slug, entries, state, w, stage)
    gate, message = gate or GATES[stage][0], message or GATES[stage][1]
    rel = gate_paths(root, slug, gate)
    for args in (["add", "-A", "--", *rel], ["commit", "-q", "-m", message, "--", *rel]):
        code, _, err = records.git(root, *args, full=True)
        if code:
            if kept is None:
                hp.unlink(missing_ok=True)
            else:
                hp.write_bytes(kept)
            if saved is None:
                sp.unlink(missing_ok=True)
            else:
                sp.write_bytes(saved)
            np.unlink(missing_ok=True)
            records.git(root, "read-tree", tree.strip(), full=True)
            return 1, [line for line in (err.strip() or f"git {args[0]} failed").splitlines()]
    return 0, out + [f"committed {message}"]


# --- nio flow status (CT-12) and abandon (CT-14) ---

def stamp(at):
    """An ISO time as `YYYY-MM-DD HH:MM` UTC, or `-`."""
    if not at:
        return "-"
    when = datetime.datetime.fromisoformat(at.replace("Z", "+00:00")).astimezone(datetime.timezone.utc)
    return when.strftime("%Y-%m-%d %H:%M")


def status_row(root, slug):
    """(abandoned, last activity, line) for one folder under .nio/specs/ (CT-12)."""
    commit = lambda: (records.git(root, "log", "-1", "--format=%cI", "--", f".nio/specs/{slug}") or [""])[0]
    k = kind(root, slug)
    if k != "effort":
        act = commit()
        return False, act, f"{slug} · {k} · {stamp(act)}"
    try:
        state, lines = load(root, slug)
    except Broken as e:
        return False, commit(), f"{slug} · broken: {e.file}, {e.where}"
    try:
        here = where(root, slug, state, lines)
        stop = None if held(state) else stops(root, slug, here, state, lines)
    except ValueError as e:  # a damaged ledger or a failing git: this effort is broken, the others are listed (FR-60)
        return False, commit(), f"{slug} · broken: {(str(e).splitlines() or [type(e).__name__])[0]}"
    here = stopped(here, stop, slug) if stop else here
    act = lines[-1]["at"] if lines else commit()
    return state["abandon"] is not None, act, " · ".join(
        [slug, here["stage"], "auto" if state["auto"] else "manual", here["status"], stamp(act)]
        + [f"override not seen: {s}: {r}" for s, r in here["overrides"]])


def status(root):
    """`nio flow status` (CT-12, FR-28, FR-46, FR-57, FR-60): one line per folder under .nio/specs/, newest activity
    first, abandoned efforts last; never locks, never writes. Returns (0, lines)."""
    specs = root / ".nio/specs"
    rows = [status_row(root, p.name) for p in sorted(specs.iterdir()) if p.is_dir()] if specs.is_dir() else []
    norm = lambda at: datetime.datetime.fromisoformat(at.replace("Z", "+00:00")).timestamp() if at else None
    rows.sort(key=lambda r: (r[0], norm(r[1]) is None, -(norm(r[1]) or 0)))
    return 0, [r[2] for r in rows]


def abandon(root, slug, why, by):
    """`nio flow abandon` (CT-14, FR-52, FR-53, FR-61): mark the effort abandoned with the reason and record it; it
    stays at that stage, unmoved by changes, until `nio flow start` resumes it. Returns (code, lines)."""
    slug = pick(root, slug)
    refuse(root, slug)
    if not (why or "").strip():
        raise ValueError("abandon needs a reason")
    w = who(by)
    if where(root, slug)["stage"] == "done":
        raise ValueError(f"{slug} is done; nothing to abandon")
    with lock(root, slug):
        state, lines = load(root, slug)
        here = where(root, slug, state, lines)
        stage = here["stage"]
        write(root, slug, backs(here, lines, slug, state["auto"]) + [{"kind": "abandon", "from": stage, "to": stage, "reason": why}],
              {**state, "abandon": why}, w, stage)
    return 0, [f"abandoned {slug}: {why}"]


def seen(root, slug, by):
    """`nio flow seen` (CT-15, FR-57): the human saw the effort's overrides; one `seen` line, or none when there is
    nothing to see. Returns (code, lines)."""
    slug = pick(root, slug)
    refuse(root, slug)
    w = who(by)
    state, lines = load(root, slug)
    if not unseen(lines):
        return 0, [f"nothing to see on {slug}"]
    with lock(root, slug):
        state, lines = load(root, slug)
        here = where(root, slug, state, lines)
        n, stage = len(unseen(lines)), here["stage"]
        write(root, slug, backs(here, lines, slug, state["auto"]) + [{"kind": "seen", "from": stage, "to": stage}], state, w, stage)
    return 0, [f"seen {n} overrides on {slug}"]


# --- the stop list (CT-8, FR-39 to FR-42, FR-51) ---

STAMP = re.compile(r"\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?)?")


def fail_hash(root, output):
    """FR-41: the hash of a guard's output with every ISO date or time and every path removed, so a repeat of the same
    failure hashes the same."""
    text = STAMP.sub("", "\n".join(output)).replace(f"{root}/", "").replace(str(root), "")
    return sha(re.sub(r"\S*/\S*", "", text).encode())


def used(root, slug):
    """(juries used, subagent runs used): the rounds summed over the effort's ledgers, and their `collected` keys."""
    from nio import jury
    leds = [jury.load(root, slug, gate) for gate, _ in GATES.values()]
    return sum(x["round"] for x in leds), sum(len(x.get("collected") or {}) for x in leds)


def stops(root, slug, here, state, lines):
    """The pause or suspension a writing call must record before anything else, or None (CT-8); only with the auto
    flag on. In order: the round cap and the no-progress pause (FR-39), the count caps (FR-40), the change pause
    (FR-42). FR-41's stuck rule is `done`'s, when it records a `fail` line."""
    from nio import jury
    if not state["auto"]:
        return None
    if here["gate"]:
        gate = GATES[here["gate"]][0]
        led = jury.load(root, slug, gate)
        n, found = led["round"], led["findings"]
        left = [f["id"] for f in found if f.get("status") == "open"]
        seen_ = any(x["kind"] == "resume" and (x["evidence"].get("waiting") or {}).get("gate") == gate and
                    (x["evidence"].get("waiting") or {}).get("round") == n for x in lines)
        why = None
        if not seen_ and n >= 3 and jury.standing(root, slug, gate) not in ("approved", "closed"):
            why = f"{gate} jury ran {n} rounds without approval"
        elif not seen_ and n >= 2 and not any(f.get("fixed_in") == n for f in found) and any(
                f.get("status") == "open" and f.get("first_round", n) < n for f in found):
            why = f"{gate} jury round {n} closed none of round {n - 1}'s findings"
        if why:
            why += f"; open: {', '.join(left)}" if left else ""
            return {"kind": "pause", "why": why, "waiting": {"why": why, "gate": gate, "round": n}}
    if here["stage"] in GATES and here["ready"] == "fail":  # its jury must run a round
        caps = records.config(root).get("budgets") or {}
        juries, runs = used(root, slug)
        if caps.get("juries") and caps["juries"] <= juries or caps.get("subagents") and caps["subagents"] <= runs:
            return {"kind": "suspend", "why": "cap", "pause": {"kind": "suspended", "why": "cap"}}
    for e in here["changes"]:
        if not named(e, lines):
            why = f"{e['change']} would move it back to {e['target']}"
            change = e["change"] if e["pending"] else {"file": e["file"], "judged": e["judged"], "current": e["current"]}
            return {"kind": "pause", "why": why, "waiting": {"why": why, "change": change, "target": e["target"]}}
    return None


def stopped(here, stop, slug):
    """`where`'s answer with a stop-list pause shown as the effort's status (CT-12's order: after the stored marks)."""
    status = f"suspended: {stop['why']}" if stop["kind"] == "suspend" else f"waiting_for_human: {stop['why']}"
    return {**here, "status": status, "command": f"nio flow start {slug} --by human", "refs": ""}


def stop_line(stop, stage, state):
    """The history line and the state that record a stop-list pause."""
    line = {"kind": stop["kind"], "from": stage, "to": stage, "reason": stop["why"]}
    held = {"pause": stop["pause"]} if stop["kind"] == "suspend" else {"waiting": stop["waiting"]}
    return line, {**state, **held}
