"""Self-check for nio flow (2026-10-28-flow-state), and the task state machine's refusals (#42 AC-36, AC-56, AC-57),
which wait for #43, which builds the task machine (change request C-261028-xcg6), as the tasks-stage spec's non-goal
says. Until then each of those says so and passes.
Run: uv run python tests/test_flow.py"""
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from test_records import repo

from nio import flow, jury, records

S = "2026-10-20-refunds"
BY = "orchestrator / test / test"
FIXTURES = Path(__file__).parent / "fixtures"
ORDER = ["intake", "drafting", "researching", "advocate_walking", "grilling", "spec_jury", "arch_grilling", "planning",
         "plan_jury", "tasking", "tasks_jury", "implementing", "done"]
LENS = {"spec": "logic", "plan": "test-proof", "tasks": "executability"}


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout


def approve(root, slug, gate, commit=True, run=None):
    """A real jury round that approves `gate` (as tests/test_jury.py:approve_spec), then its `nio: approve` commit;
    another `run` makes a later round."""
    run = run or f"R-{gate}-{slug}"
    path = root / ".nio/runs" / run / "jury" / f"{gate}-{LENS[gate]}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nlens: {LENS[gate]}\ngate: {gate}\nsubject: {slug}\nby: \"juror / claude-code / opus\"\n"
                    "context: sufficient\n---\n## Reasoning\nChecked every item.\n\n## Findings\nnone\n")
    jury.collect(root, slug, gate, run)
    assert jury.check(root, slug, gate, record=True)[0] == "approved"
    if commit:
        git(root, "add", "-A")
        git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", f"nio: approve {gate}")


def effort(stage, slug=S, risk="[]", route="full", root=None):
    """A temporary git repo (or `root`, for a second effort) with the refunds fixtures in `.nio/specs/<slug>/`, brought
    to `stage` with real files: every stage before it passes (gates by real jury rounds and their approval commits);
    the stage's own guard doesn't. No history.jsonl."""
    if root is None:
        root = repo()
        git(root, "config", "user.name", "t")
        git(root, "config", "user.email", "t@t")
        (root / ".nio/config.json").write_text('{"memory": {"areas": ["auth", "project"]}}')
    folder = root / ".nio/specs" / slug
    folder.mkdir(parents=True)
    at = ORDER.index(stage)
    put = lambda name, text: (folder / name).write_text(text.replace("slug: checkout-refunds", f"slug: {slug}"))
    if at > ORDER.index("intake"):
        put("intake.md", "# Intake\nRefund paid orders.\n")
    if at > ORDER.index("drafting"):
        text = re.sub(r"^risk: .*$", f"risk: {risk}", (FIXTURES / "spec/spec.md").read_text(), count=1, flags=re.M)
        text = re.sub(r"^route: \w+", f"route: {route}", text, count=1, flags=re.M)
        if at > ORDER.index("grilling"):  # the grill settled OP-1 and confirmed the default
            text = re.sub(r"^- \*\*OP-1\*\*.*\n", "", text, flags=re.M).replace("[default]", "[human]")
        put("spec.md", text)
        put("research.md", '- **RF-5** The payments client retries without a key. Source: app.py:1: "retry()"\n')
    if at > ORDER.index("spec_jury"):
        approve(root, slug, "spec")
    if at > ORDER.index("planning"):
        for name in ("plan.md", "contracts.md", "tests.md", "quickstart.md"):
            put(name, (FIXTURES / "plan" / name).read_text())
    if at > ORDER.index("plan_jury"):
        approve(root, slug, "plan")
    if at > ORDER.index("tasking"):
        put("tasks.md", (FIXTURES / "tasks/tasks.md").read_text())
    if at > ORDER.index("tasks_jury"):
        approve(root, slug, "tasks")
    return root


def history(root, slug, *lines):
    """Write history.jsonl and state.json through `flow.record`, one call per line. A line is a dict of an entry's
    fields plus `at` (a datetime) and, optionally, `state` (keys to set in the state it leaves)."""
    for line in lines:
        line = dict(line)
        at, changes = line.pop("at", None), line.pop("state", {})
        state = {**flow.load(root, slug)[0], **changes}
        flow.record(root, slug, [line], state, flow.who(BY), "", at=at)


def cli(root, *args, by=True):
    """`nio flow <args>` in `root` as a subprocess, `--by` added to the writing subcommands unless `by=False`.
    Returns (exit code, stdout + stderr)."""
    extra = ["--by", BY] if by and args and args[0] in ("start", "done", "park", "abandon", "seen") else []
    r = subprocess.run([sys.executable, "-c", "from nio.cli import main; main()", "flow", *args, *extra], cwd=root,
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def snap(root, slug):
    """The bytes of every file in the effort folder."""
    folder = root / ".nio/specs" / slug
    return {p.relative_to(folder): p.read_bytes() for p in sorted(folder.rglob("*")) if p.is_file()}


def flow_files(root):
    return [p for p in (root / ".nio/specs").rglob("*") if p.name in ("state.json", "history.jsonl")]


# --- which effort (CT-4) ---

def test_ac4_no_current_effort():
    """TC-4: no slug and no effort with history: refused, listing the dated efforts, never the legacy folder."""
    root = effort("planning")
    shutil.copytree(root / ".nio/specs" / S, root / ".nio/specs/2026-10-21-refunds")
    (root / ".nio/specs/grilling").mkdir()
    try:
        flow.pick(root)
        raise AssertionError("pick chose an effort with no history")
    except ValueError as e:
        msg = str(e)
    assert S in msg and "2026-10-21-refunds" in msg and "nio flow start" in msg and "grilling" not in msg, msg
    assert not flow_files(root)
    assert flow.pick(root, S) == S
    try:
        flow.pick(root, "2026-10-29-nothing")
        raise AssertionError("pick took a slug with no folder")
    except ValueError as e:
        assert "no effort 2026-10-29-nothing under .nio/specs/" in str(e) and "  2026-10-21-refunds" in str(e), e
    assert flow.kind(root, "grilling") == "legacy" and flow.kind(root, S) == "effort"
    spec = root / ".nio/specs" / S / "spec.md"
    spec.write_text(spec.read_text().replace("route: full", "route: lite", 1))
    assert flow.kind(root, S) == "unsupported: lite" and S not in flow.efforts(root)
    print("ok")


# --- the flow files (CT-1, CT-2) ---

def at(hour):
    import datetime
    return datetime.datetime(2026, 10, 20, hour, tzinfo=datetime.timezone.utc)


def lines_of(root, slug=S):
    return [json.loads(x) for x in (root / ".nio/specs" / slug / "history.jsonl").read_text().splitlines()]


def lines_of_bytes(data):
    return [json.loads(x) for x in data.decode().splitlines()]


def broken(root, file, where, slug=S):
    try:
        flow.load(root, slug)
        raise AssertionError(f"load took a broken effort ({file}, {where})")
    except flow.Broken as e:
        assert (e.file, e.where) == (file, where) and str(e) == f"{slug}: {file}, {where}", e


def test_load_and_record():
    """CT-1, CT-2: defaults with no files; each line carries who, when, run and the hash of the state it left, the last
    of a call's batch `end`; a `--by` that isn't role / host / model is refused."""
    root = effort("drafting")
    folder = root / ".nio/specs" / S
    assert flow.load(root, S) == (dict(zip(flow.STATE_KEYS, [False, None, None, None, {}, {}, ""])), [])
    assert flow.who("human") == {"role": "human", "host": "", "model": ""}
    assert flow.who("orchestrator / claude-code / opus") == {"role": "orchestrator", "host": "claude-code", "model": "opus"}
    for bad in ("orchestrator", "a / b", "a /  / c"):
        try:
            flow.who(bad)
            raise AssertionError(bad)
        except ValueError:
            pass
    state = {**flow.load(root, S)[0], "run": "R-1"}
    flow.record(root, S, [{"kind": "start", "from": None, "to": "drafting"},
                          {"kind": "skip", "from": "drafting", "to": "grilling", "reason": "skipped: not built",
                           "evidence": {"paths": ["spec.md"]}}], state, flow.who(BY), "R-1", at=at(10))
    got = lines_of(root)
    digest = hashlib.sha256((folder / "state.json").read_bytes()).hexdigest()
    assert [x["kind"] for x in got] == ["start", "skip"] and "end" not in got[0] and got[1]["end"] is True, got
    assert all(x["state"] == digest and x["at"] == "2026-10-20T10:00:00Z" and x["run"] == "R-1" for x in got), got
    assert got[0]["who"] == {"role": "orchestrator", "host": "test", "model": "test"} and "reason" not in got[0]
    assert got[1]["evidence"] == {"paths": ["spec.md"], "verdict": "", "output": ""} and got[1]["reason"] == "skipped: not built"
    assert (folder / "state.json").read_text() == json.dumps(state, indent=2, sort_keys=True) + "\n"
    assert not (folder / "state.json.new").exists()
    assert flow.load(root, S) == (state, got)
    print("ok")


def test_load_refuses_what_it_cant_trust():
    """CT-1 (FR-6, FR-58): a bad state.json, an unknown key, a bad middle line, a hash mismatch, one file without the other."""
    root = effort("drafting")
    folder = root / ".nio/specs" / S
    history(root, S, {"kind": "start", "from": None, "to": "drafting", "at": at(10)},
            {"kind": "park", "from": "drafting", "to": "drafting", "reason": "x", "at": at(11)})
    sp, hp = folder / "state.json", folder / "history.jsonl"
    good_state, good_history = sp.read_bytes(), hp.read_bytes()

    def fixed(text):  # a test-only write that fixes the hash, so only the content is wrong
        sp.write_text(text)
        line = lines_of(root)[-1]
        line["state"] = hashlib.sha256(text.encode()).hexdigest()
        hp.write_bytes(good_history + (json.dumps(line) + "\n").encode())

    fixed('{"auto": false, "stage": "done"}\n')
    broken(root, "state.json", "key stage")
    fixed("[1, 2]\n")
    broken(root, "state.json", "not valid JSON")
    sp.write_bytes(good_state.replace(b'"auto": false', b'"auto": true'))
    hp.write_bytes(good_history)
    broken(root, "state.json", "hash mismatch")
    sp.write_bytes(good_state)
    hp.write_bytes(good_history.replace(b"\n", b"\n{not json\n", 1))
    broken(root, "history.jsonl", "line 2")
    hp.write_bytes(good_history)
    assert len(flow.load(root, S)[1]) == 2
    sp.unlink()
    broken(root, "state.json", "missing")
    sp.write_bytes(good_state)
    hp.unlink()
    broken(root, "history.jsonl", "missing")
    print("ok")


def test_torn_tail_is_cut_and_noted():
    """CT-1, CT-2 (FR-59): a torn last line, or a batch with no `end` line, is ignored, then cut on the next write and
    noted on a `repair` line holding the cut bytes in hex; a whole last line missing only its newline is kept."""
    root = effort("drafting")
    folder = root / ".nio/specs" / S
    hp = folder / "history.jsonl"
    history(root, S, {"kind": "start", "from": None, "to": "drafting", "at": at(10)})
    before = hp.read_bytes()
    state = flow.load(root, S)[0]
    hp.write_bytes(before + b'{"kind": "pass", "fr')
    assert flow.load(root, S) == (state, lines_of_bytes(before))
    history(root, S, {"kind": "park", "from": "drafting", "to": "drafting", "reason": "x", "at": at(11)})
    got = lines_of(root)
    assert hp.read_bytes().startswith(before) and [x["kind"] for x in got] == ["start", "repair", "park"], got
    assert '{"kind": "pass", "fr'.encode().hex() in got[1]["reason"] and "line 2" in got[1]["reason"], got[1]
    assert b'{"kind": "pass", "fr' not in hp.read_bytes() and "end" not in got[1] and got[2]["end"]
    # a batch cut off after a complete line but before its `end` line
    whole = hp.read_bytes()
    stray = dict(got[-1], kind="pass")
    stray.pop("end")
    hp.write_bytes(whole + (json.dumps(stray) + "\n").encode())
    assert flow.load(root, S)[1] == got
    history(root, S, {"kind": "seen", "from": "drafting", "to": "drafting", "at": at(12)})
    assert [x["kind"] for x in lines_of(root)] == ["start", "repair", "park", "repair", "seen"]
    # a whole last line missing only its newline is complete: kept byte for byte, its newline added, nothing cut
    whole = hp.read_bytes()
    hp.write_bytes(whole[:-1])
    assert flow.load(root, S)[1] == lines_of_bytes(whole)
    history(root, S, {"kind": "seen", "from": "drafting", "to": "drafting", "at": at(13)})
    assert hp.read_bytes().startswith(whole) and [x["kind"] for x in lines_of(root)][-2:] == ["seen", "seen"]
    print("ok")


def test_temp_state_rolled_forward_or_dropped():
    """CT-1, CT-2 (FR-58): a state.json.new the last `end` line names is read and renamed into place on the next write;
    one no line names is ignored and deleted."""
    root = effort("drafting")
    folder = root / ".nio/specs" / S
    sp, hp, np = folder / "state.json", folder / "history.jsonl", folder / "state.json.new"
    history(root, S, {"kind": "start", "from": None, "to": "drafting", "at": at(10)})
    state = flow.load(root, S)[0]
    # a crash before the lines: the temp state matches no line
    np.write_text(json.dumps({**state, "auto": True}, indent=2, sort_keys=True) + "\n")
    assert flow.load(root, S)[0] == state
    history(root, S, {"kind": "seen", "from": "drafting", "to": "drafting", "at": at(11)})
    assert not np.exists() and flow.load(root, S)[0] == state
    # a crash after the lines: the temp state is the one the last line names
    parked = {**state, "pause": {"kind": "parked", "why": "x"}}
    data = json.dumps(parked, indent=2, sort_keys=True) + "\n"
    np.write_text(data)
    line = dict(lines_of(root)[-1], kind="park", state=hashlib.sha256(data.encode()).hexdigest())
    hp.write_bytes(hp.read_bytes() + (json.dumps(line) + "\n").encode())
    assert flow.load(root, S)[0] == parked
    history(root, S, {"kind": "seen", "from": "drafting", "to": "drafting", "at": at(12)})
    assert not np.exists() and json.loads(sp.read_text())["pause"] == {"kind": "parked", "why": "x"}
    assert hashlib.sha256(sp.read_bytes()).hexdigest() == lines_of(root)[-1]["state"]
    print("ok")


# --- the lock (CT-3) ---

def old_lock(root, pid, host, seconds=120, slug=S):
    path = root / ".nio/specs" / slug / "flow.lock"
    path.write_text(json.dumps({"pid": pid, "host": host, "at": "2026-10-20T10:00:00+00:00"}))
    os.utime(path, (time.time() - seconds,) * 2)
    return path


def refused(root, slug=S):
    try:
        with flow.lock(root, slug):
            raise AssertionError("the lock was taken")
    except flow.Busy as e:
        return str(e)


def test_lock():
    """CT-3 (FR-45, FR-54): a held lock refuses; a stale one (old, its process gone or its host another) is taken over;
    a live or young one is not; the lock is gone after the body, also after an exception; git ignores it."""
    root = effort("drafting")
    folder = root / ".nio/specs" / S
    path, host = folder / "flow.lock", socket.gethostname()
    with flow.lock(root, S):
        held = json.loads(path.read_text())
        assert held["pid"] == os.getpid() and held["host"] == host and held["at"], held
        assert subprocess.run(["git", "check-ignore", "-q", f".nio/specs/{S}/flow.lock"], cwd=root).returncode == 0
        msg = refused(root)
        assert msg == f"{S} is being written by another nio flow call (pid {os.getpid()} on {host}); try again", msg
    assert not path.exists()
    assert (folder / ".gitignore").read_text() == "flow.lock*\nstate.json.new\n"
    try:
        with flow.lock(root, S):
            raise KeyError("boom")
    except KeyError:
        pass
    assert not path.exists()
    gone = subprocess.Popen(["true"])
    gone.wait()
    for pid, other, seconds, taken in [(gone.pid, host, 120, True), (os.getpid(), host, 120, False),
                                       (gone.pid, host, 30, False), (12345, "elsewhere", 120, True),
                                       (12345, "elsewhere", 30, False)]:
        before = old_lock(root, pid, other, seconds).read_bytes()
        if taken:
            with flow.lock(root, S):
                assert json.loads(path.read_text())["pid"] == os.getpid()
            assert not path.exists()
        else:
            assert f"(pid {pid} on {other})" in refused(root) and path.read_bytes() == before
            path.unlink()
        assert sorted(p.name for p in folder.iterdir() if p.name.startswith("flow.lock")) == []
    assert (folder / ".gitignore").read_text() == "flow.lock*\nstate.json.new\n"  # written once
    print("ok")


def test_lock_taken_over_meanwhile():
    """CT-3: a holder whose lock was taken over writes nothing and never deletes the new holder's lock."""
    root = effort("drafting")
    folder = root / ".nio/specs" / S
    history(root, S, {"kind": "start", "from": None, "to": "drafting", "at": at(10)})
    before = (folder / "history.jsonl").read_bytes()
    with flow.lock(root, S):
        (folder / "flow.lock").write_text(json.dumps({"pid": 12345, "host": "elsewhere", "at": "x"}))
        try:
            history(root, S, {"kind": "seen", "from": "drafting", "to": "drafting"})
            raise AssertionError("wrote under a lock taken over")
        except flow.Busy as e:
            assert "(pid 12345 on elsewhere)" in str(e), e
    assert (folder / "history.jsonl").read_bytes() == before and json.loads((folder / "flow.lock").read_text())["pid"] == 12345
    print("ok")


# --- git's exit code (CT-19) ---

def test_git_full():
    """CT-19: `full=True` returns (exit code, stdout, stderr); without it, stdout lines as before."""
    root = repo()
    code, out, err = records.git(root, "rev-parse", "--verify", "no-such-ref", full=True)
    assert code == 128 and out == "" and err.startswith("fatal: "), (code, out, err)
    code, out, err = records.git(root, "log", "--format=%s", full=True)
    assert (code, out, err) == (0, "init\n", ""), (code, out, err)
    assert records.git(root, "log", "--format=%s") == ["init"]
    print("ok")


# --- the guards (CT-5) ---

def test_stages():
    """The state table "Flow": its stages in order, where a pass goes and where a jury rejection sends the effort."""
    assert list(flow.STAGES) == ORDER
    assert all(flow.STAGES[a][0] == b for a, b in zip(ORDER, ORDER[1:])) and flow.STAGES["done"] == (None, None)
    assert {s: r for s, (_, r) in flow.STAGES.items() if r} == {"spec_jury": "grilling", "plan_jury": "planning",
                                                                "tasks_jury": "tasking"}
    for stage in ("researching", "advocate_walking", "arch_grilling", "done", "nowhere"):
        try:
            flow.guard(effort("intake"), S, stage)
            raise AssertionError(stage)
        except ValueError:
            pass
    print("ok")


GUARDED = ["intake", "drafting", "grilling", "spec_jury", "planning", "plan_jury", "tasking", "tasks_jury"]
FAILS = {"intake": "ERROR .nio/specs/2026-10-20-refunds/intake.md does not exist",
         "drafting": "ERROR no spec at .nio/specs/2026-10-20-refunds/spec.md",
         "grilling": "`## Open points` must be empty at the gate",
         "spec_jury": "the spec jury's outcome is ",
         "planning": "ERROR ",
         "plan_jury": "the plan must be approved first",
         "tasking": "ERROR ",
         "tasks_jury": "the tasks must be approved first"}


def test_guards_fail_at_their_stage():
    """The decision table "Guards": at each stage its own guard fails, saying what is missing, with its output's hash."""
    for stage in GUARDED:
        root = effort(stage)
        result, output, ev = flow.guard(root, S, stage)
        assert result == "fail" and any(FAILS[stage] in line for line in output), (stage, output)
        assert ev["output"] == hashlib.sha256("\n".join(output).encode()).hexdigest() and ev["verdict"] == "", ev
        assert ev["paths"] and all(p.startswith(f".nio/specs/{S}/") for p in ev["paths"]), ev
    print("ok")


def task_line(kind, task, **ev):
    """A task history line (implement CT-4): from and to `implementing`, its fields under `evidence`."""
    return {"kind": kind, "from": "implementing", "to": "implementing", "evidence": {"task": task, **ev}}


def test_guards_pass_and_implementing_waits_for_its_tasks():
    """Every guard before implementing passes on an effort past them, a gate naming its approval verdict; implementing
    passes only once every task is done and every epic has its `epic` line (implement CT-14)."""
    root = effort("implementing")
    for stage in GUARDED:
        result, output, ev = flow.guard(root, S, stage)
        assert (result, output, ev["output"]) == ("pass", [], ""), (stage, output)
        assert bool(ev["verdict"]) == (stage in flow.GATES) and ev["verdict"][:2] in ("", "V-"), (stage, ev)
    result, output, ev = flow.guard(root, S, "implementing")
    assert result == "fail" and any(x.startswith("T-1 is ready") for x in output) and "isn't built" not in str(output), output
    history(root, S, *[task_line("task_done", t) for t in ("T-1", "T-2", "T-3")])
    result, output, ev = flow.guard(root, S, "implementing")
    assert result == "fail" and output == ["E-1 has no epic line"], output
    history(root, S, {"kind": "epic", "from": "implementing", "to": "implementing", "reason": "skipped: not built",
                      "evidence": {"epic": "E-1"}})
    assert flow.guard(root, S, "implementing")[:2] == ("pass", [])
    print("ok")


def test_closed_gate_is_an_override():
    """CT-5 (FR-27): a jury gate the human closed with a reason is `closed`, carrying the reason, at every gate."""
    for stage, (gate, _) in flow.GATES.items():
        root = effort(stage)
        assert jury.check(root, S, gate, record=True, human="ship it, I accept the risk")[0] == "human"
        result, output, ev = flow.guard(root, S, stage)
        assert (result, output) == ("closed", ["ship it, I accept the risk"]), (stage, result, output)
        assert ev["verdict"].startswith("V-"), ev
    print("ok")


# --- the command line (CT-16) ---

def test_ac6_by_required():
    """TC-77: a writing subcommand without --by refuses and writes nothing."""
    root = effort("planning")
    before = snap(root, S)
    for args in (["start", S], ["done", "planning", S], ["park", S, "x"], ["abandon", S, "x"], ["seen", S]):
        code, out = cli(root, *args, by=False)
        assert code != 0 and "--by" in out, (args, code, out)
    assert snap(root, S) == before
    print("ok")


def test_cli_errors():
    """CT-16: a ValueError, flow.Broken or flow.Busy from a flow function prints `error: <message>` and exits 1;
    otherwise the function's lines are printed and its exit code kept. The flow functions are stubbed here."""
    root = repo()
    stub = ("import sys\nfrom nio import cli, flow\n"
            "def fake(*args, **kw):\n    {body}\n"
            "for name in ('next_step', 'start', 'done', 'status', 'park', 'abandon', 'seen'):\n"
            "    setattr(flow, name, fake)\n"
            "sys.argv = ['nio', 'flow', *sys.argv[1:]]\ncli.main()\n")
    run = lambda body, *args: subprocess.run([sys.executable, "-c", stub.format(body=body), *args], cwd=root,
                                             capture_output=True, text=True)
    for body, message in [("raise ValueError('no effort x under .nio/specs/')", "error: no effort x under .nio/specs/"),
                          ("raise flow.Broken('state.json', 'key stage', 'x')", "error: x: state.json, key stage"),
                          ("raise flow.Busy('x is being written by another nio flow call (pid 1 on h); try again')",
                           "error: x is being written by another nio flow call (pid 1 on h); try again")]:
        for args in (["next"], ["start", "x", "--by", BY], ["done", "planning", "--by", "human"], ["status"],
                     ["park", "x", "why", "--by", BY], ["abandon", "x", "why", "--by", BY], ["seen", "x", "--by", BY]):
            r = run(body, *args)
            assert r.returncode == 1 and r.stderr.strip() == message and not r.stdout, (args, r)
    r = run("print(kw, args[1:]); return 3, ['line one', 'line two']", "done", "spec_jury", "x", "--commit", "--human",
            "why not", "--by", "human")
    assert r.returncode == 3 and r.stdout.splitlines()[-2:] == ["line one", "line two"], r
    assert "{'commit': True, 'human': 'why not', 'by': 'human'} ('spec_jury', 'x')" in r.stdout, r.stdout
    print("ok")


# --- where an effort is and what to do next (CT-6, CT-9) ---

os.environ.pop("CLAUDECODE", None)  # expected output below is the plain form, wherever the tests run


def nxt(root, slug=S, by=None):
    code, out = flow.next_step(root, slug, by=by)
    assert code == 0, out
    return "\n".join(out)


def test_ac1_next_names_planning():
    """TC-1: after the spec gate's approval commit, next names planning, the plan skill, spec.md and the done command."""
    root = effort("planning")
    out = nxt(root)
    assert "state: planning" in out and "skill: @nio:plan" in out, out
    assert "spec.md" in next(x for x in out.splitlines() if x.startswith("inputs: ")), out
    assert any(x.startswith(f"done: nio flow done planning {S} --by") for x in out.splitlines()), out
    assert "skipped: arch_grilling (not built)" in out and len(out.splitlines()) <= 12, out
    os.environ["CLAUDECODE"] = "1"  # #56: the next command as this host types it, else the plain name
    try:
        assert "next: run /nio:plan\n" in nxt(root) + "\n", out
        del os.environ["CLAUDECODE"]
        assert "next: run the nio:plan skill\n" in nxt(root) + "\n", out
    finally:
        os.environ.pop("CLAUDECODE", None)
    assert not flow_files(root)  # next without history writes nothing
    print("ok")


def test_ac2_open_question_waits():
    """TC-2: an asked grill question with no answer entry waits for the human, naming no skill."""
    root = effort("grilling")
    (root / ".nio/specs" / S / "grill.md").write_text(
        "# Grill\n\n## Q3 · OP-2\nQuestion: a?\nAnswer: b\n\n## Asked · Q4 · OP-3 · 2026-10-20\nQuestion: Who pays the fee?\n")
    out = nxt(root)
    assert "waiting_for_human" in out and "Q4" in out and "@nio:" not in out, out
    assert out.splitlines()[0] == "Answer the grill's question Q4" and out.splitlines()[-1].startswith("Refs: "), out
    print("ok")


def test_ac8_ledger_read_live():
    """TC-8: a spec ledger edited to rejected, the spec unchanged since that round, sends the effort back to grilling
    with no flow write."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    folder = root / ".nio/specs" / S
    before = (folder / "state.json").read_bytes()
    ledger = folder / "jury/spec.json"
    ledger.write_text(ledger.read_text().replace('"outcome": "approved"', '"outcome": "rejected"'))
    out = nxt(root)
    assert "state: grilling" in out and "rejected round 1" in out, out
    assert (folder / "state.json").read_bytes() == before
    print("ok")


def test_gate_waits_for_its_approval_commit():
    """CT-6 (FR-49, FR-55): a gate whose guard passes waits for the human's approval until its commit exists."""
    root = effort("spec_jury")
    approve(root, S, "spec", commit=False)
    lines = nxt(root).splitlines()
    assert lines[0] == "Approve or push back: run the command below", lines
    assert "state: spec_jury (waiting_for_human: approve spec)" in lines and "@nio:" not in "\n".join(lines), lines
    assert f"nio flow done spec_jury --commit {S} --by human" in lines and lines[-1].startswith("Refs: "), lines
    git(root, "add", "-A")
    git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "nio: approve spec")
    assert "state: planning (working)" in nxt(root)
    print("ok")


def test_next_on_legacy_unsupported_and_parked():
    """CT-9: legacy and unsupported folders get one line and exit 0; a parked effort shows the work it resumes to and
    records the resume only with --by (FR-31)."""
    root = effort("planning")
    (root / ".nio/specs/grilling").mkdir()
    assert flow.next_step(root, "grilling") == (0, ["legacy: grilling has no flow layout; nothing to do"])
    flow.start(root, S, by=BY)
    flow.park(root, S, "waiting on legal", by=BY)
    before = snap(root, S)
    out = nxt(root)
    assert "state: planning (working)" in out and out.endswith("would record: resume (run with --by to record)"), out
    assert snap(root, S) == before
    out = nxt(root, by=BY)
    assert "would record" not in out and f'done: nio flow done planning {S} --by "{BY}"' in out, out
    last = lines_of(root)[-1]
    assert (last["kind"], last["reason"], last["to"]) == ("resume", "parked: waiting on legal", "planning"), last
    assert flow.load(root, S)[0]["pause"] is None and not (root / ".nio/specs" / S / "flow.lock").exists()
    spec = root / ".nio/specs" / S / "spec.md"
    spec.write_text(spec.read_text().replace("route: full", "route: lite", 1))
    assert flow.next_step(root, S) == (0, ["unsupported: lite: nio flow drives full-route specs only"])
    print("ok")


# --- nio flow start (CT-10) ---

def test_ac3_start_makes_current():
    """TC-3: the effort just started is the one `next` acts on; nothing outside the two effort folders changes."""
    root = effort("planning")
    other = "2026-10-21-refunds"
    shutil.copytree(root / ".nio/specs" / S, root / ".nio/specs" / other)
    history(root, S, {"kind": "start", "from": None, "to": "planning", "at": at(10)})
    import datetime
    history(root, other, {"kind": "start", "from": None, "to": "planning",
                          "at": datetime.datetime(2026, 10, 21, 10, tzinfo=datetime.timezone.utc)})
    files = lambda: {p: p.read_bytes() for p in root.rglob("*") if p.is_file() and ".git" not in p.relative_to(root).parts}
    before = files()
    code, out = cli(root, "start", S)
    assert code == 0 and out.strip() == f"started {S} at planning", out
    code, out = cli(root, "next")
    assert code == 0 and f"effort: {S}" in out, out
    after = files()
    changed = {p for p in set(before) | set(after) if before.get(p) != after.get(p)}
    assert changed and all(p.relative_to(root).parts[2] in (S, other) for p in changed), changed
    print("ok")


def test_ac5_unknown_slug():
    """TC-5: start on a slug with no folder refuses, naming it, and writes nothing. (TC-5 calls start without `by`;
    CT-16 makes `by` required, so it is passed here, as the helper rule says.)"""
    root = effort("planning")
    try:
        flow.start(root, "2026-10-29-nothing", by=BY)
        raise AssertionError("started an effort with no folder")
    except ValueError as e:
        assert "2026-10-29-nothing" in str(e), e
    assert not (root / ".nio/specs/2026-10-29-nothing").exists() and not flow_files(root)
    print("ok")


def test_ac6_start_creates_files():
    """TC-6: start creates state.json and history.jsonl with one start line carrying who, when, run and the state hash."""
    import datetime
    root = effort("planning")
    folder = root / ".nio/specs" / S
    assert flow.start(root, S, by="orchestrator / claude-code / opus") == (0, [f"started {S} at planning"])
    got = lines_of(root)
    assert len(got) == 1 and got[0]["kind"] == "start" and (got[0]["from"], got[0]["to"]) == (None, "planning"), got
    assert got[0]["who"] == {"role": "orchestrator", "host": "claude-code", "model": "opus"} and "run" in got[0]
    datetime.datetime.fromisoformat(got[0]["at"].replace("Z", "+00:00"))
    assert got[0]["state"] == hashlib.sha256((folder / "state.json").read_bytes()).hexdigest()
    print("ok")


def test_ac7_state_keys():
    """TC-7: state.json holds only FR-3's keys and none of the ledger's facts."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    text = (root / ".nio/specs" / S / "state.json").read_text()
    assert set(json.loads(text)) <= {"auto", "pause", "abandon", "waiting", "claims", "attempts", "run"}, text
    assert not re.search(r"outcome|round|version|\bQ\d+|\bC-\d", text), text
    print("ok")


def test_ac6_intake_only_folder():
    """TC-76: a dated folder holding only intake.md is an effort; start records one start line to drafting, and
    status shows it at drafting, not unsupported."""
    root = repo()
    folder = root / ".nio/specs/2026-10-22-new"
    folder.mkdir(parents=True)
    (folder / "intake.md").write_text("# Intake\nA new thing.\n")
    assert flow.kind(root, "2026-10-22-new") == "effort"
    assert flow.start(root, "2026-10-22-new", by=BY) == (0, ["started 2026-10-22-new at drafting"])
    got = lines_of(root, "2026-10-22-new")
    assert [(x["kind"], x["to"]) for x in got] == [("start", "drafting")] and (folder / "state.json").exists(), got
    line = next(x for x in flow.status(root)[1] if x.startswith("2026-10-22-new"))
    assert "2026-10-22-new · drafting" in line and "unsupported" not in line, line
    print("ok")


def test_start_resumes_and_refuses_legacy():
    """CT-10: start on a parked effort resumes it; on a working one it appends a start line; legacy and unsupported
    folders are refused with nothing written."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    flow.park(root, S, "lunch", by=BY)
    assert flow.start(root, S, by=BY) == (0, [f"resumed {S} at planning"])
    assert flow.start(root, S, by=BY) == (0, [f"started {S} at planning"])
    assert [x["kind"] for x in lines_of(root)] == ["start", "park", "resume", "start"]
    assert lines_of(root)[2]["reason"] == "parked: lunch" and flow.load(root, S)[0]["pause"] is None
    (root / ".nio/specs/grilling").mkdir()
    for slug, message in [("grilling", "grilling is legacy; nio flow writes nothing in it")]:
        try:
            flow.start(root, slug, by=BY)
            raise AssertionError(slug)
        except ValueError as e:
            assert str(e) == message, e
    assert not list((root / ".nio/specs/grilling").iterdir())
    print("ok")


# --- nio flow park and the write path (CT-13, CT-1 to CT-3) ---

def test_ac12_second_writer_refused():
    """TC-12: while one call holds the lock a second writer is refused; the first call's line lands, the lock goes."""
    root = effort("drafting")
    flow.start(root, S, by=BY)
    count = len(lines_of(root))
    with flow.lock(root, S):
        assert subprocess.run(["git", "check-ignore", f".nio/specs/{S}/flow.lock"], cwd=root,
                              capture_output=True).returncode == 0
        code, out = cli(root, "park", S, "x")
        assert code != 0 and "being written" in out, (code, out)
        flow.record(root, S, [{"kind": "pass", "from": "drafting", "to": "grilling"}], flow.load(root, S)[0],
                    flow.who(BY), "")
    got = lines_of(root)
    assert len(got) == count + 1 and got[-1]["kind"] == "pass", got
    assert not (root / ".nio/specs" / S / "flow.lock").exists()
    print("ok")


def test_ac56_stale_lock():
    """TC-56: a stale lock whose process is gone is taken over; git shows only the two flow files changed."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    git(root, "add", "-A")
    git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "started")
    gone = subprocess.Popen(["true"])
    gone.wait()
    old_lock(root, gone.pid, socket.gethostname())
    count = len(lines_of(root))
    code, out = cli(root, "park", S, "x")
    assert code == 0 and out.strip() == f"parked {S}: x", out
    got = lines_of(root)
    assert len(got) == count + 1 and got[-1]["kind"] == "park", got
    status = git(root, "status", "--porcelain", "--", f".nio/specs/{S}").splitlines()
    assert sorted(x[3:] for x in status) == [f".nio/specs/{S}/history.jsonl", f".nio/specs/{S}/state.json"], status
    print("ok")


def test_ac59_torn_line():
    """TC-59: park cuts a torn last line and notes it on a repair line before its own."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    hp = root / ".nio/specs" / S / "history.jsonl"
    hp.write_bytes(hp.read_bytes() + b'{"kind": "pass", "fr')
    assert flow.park(root, S, "x", by=BY)[0] == 0
    text = hp.read_text()
    assert text.endswith("\n") and [x["kind"] for x in lines_of(root)][-2:] == ["repair", "park"], text
    assert '{"kind": "pass", "fr'.encode().hex() in lines_of(root)[-2]["reason"] and '{"kind": "pass", "fr' not in text
    print("ok")


def test_ac58_temp_state_dropped():
    """TC-74: a temp state written before a crash mid-append is ignored, then dropped by the next write."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    folder = root / ".nio/specs" / S
    sp, hp, np = folder / "state.json", folder / "history.jsonl", folder / "state.json.new"
    state = flow.load(root, S)[0]
    np.write_text(json.dumps({**state, "pause": {"kind": "parked", "why": "y"}}, indent=2, sort_keys=True) + "\n")
    hp.write_bytes(hp.read_bytes() + b'{"kind": "park", "at": "2026-')
    assert flow.load(root, S)[0] == state
    assert flow.park(root, S, "x", by=BY)[0] == 0
    assert not np.exists() and [x["kind"] for x in lines_of(root)][-2:] == ["repair", "park"]
    assert hashlib.sha256(sp.read_bytes()).hexdigest() == lines_of(root)[-1]["state"]
    print("ok")


def test_ac59_whole_line_no_newline():
    """TC-75: a whole last line missing only its newline is kept byte for byte, with no repair line."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    hp = root / ".nio/specs" / S / "history.jsonl"
    start_line = hp.read_bytes()[:-1]
    hp.write_bytes(start_line)
    assert flow.park(root, S, "x", by=BY)[0] == 0
    assert hp.read_bytes().startswith(start_line + b"\n") and [x["kind"] for x in lines_of(root)] == ["start", "park"]
    print("ok")


# --- a broken effort stops the commands; a leftover temp state rolls forward (T-10) ---

def test_ac9_unknown_state_key():
    """TC-9: an unknown key in state.json, its hash fixed so only the key is wrong, stops next, start and park."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    bad_key(root)
    before = snap(root, S)
    for args in (["next"], ["start", S], ["park", S, "x"]):
        code, out = cli(root, *args)
        assert code != 0 and "state.json" in out and "stage" in out, (args, code, out)
        if args[0] != "next":  # with no slug, next names the broken effort among the ones it can't pick
            assert out.strip() == f"error: {S}: state.json, key stage", out
    assert snap(root, S) == before
    print("ok")


def test_ac58_hash_mismatch():
    """TC-58: a hand-edited state.json stops next, naming the file and the hash mismatch; nothing is written."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    sp = root / ".nio/specs" / S / "state.json"
    sp.write_text(sp.read_text().replace('"auto": false', '"auto": true'))
    before = snap(root, S)
    try:
        flow.next_step(root, S)
        raise AssertionError("next read a hand-edited state.json")
    except flow.Broken as e:
        assert "state.json" in str(e) and "hash mismatch" in str(e), e
    assert snap(root, S) == before
    print("ok")


def test_ac58_temp_state_rolled_forward():
    """TC-73: a temp state the last `end` line names is read, then rolled forward by the next write."""
    # TC-73 asserts pause still set after start; CT-10/FR-31 resume clears it. So this checks that the rolled-forward
    # `park` line stays, followed by start's `resume` line, and that state.json then matches the last line.
    root = effort("planning")
    flow.start(root, S, by=BY)
    folder = root / ".nio/specs" / S
    sp, hp, np = folder / "state.json", folder / "history.jsonl", folder / "state.json.new"
    parked = {**flow.load(root, S)[0], "pause": {"kind": "parked", "why": "x"}}
    data = json.dumps(parked, indent=2, sort_keys=True) + "\n"
    np.write_text(data)
    line = dict(lines_of(root)[-1], kind="park", reason="x", state=hashlib.sha256(data.encode()).hexdigest())
    hp.write_bytes(hp.read_bytes() + (json.dumps(line) + "\n").encode())
    assert flow.load(root, S)[0] == parked
    assert flow.start(root, S, by=BY) == (0, [f"resumed {S} at planning"])
    assert not np.exists() and [x["kind"] for x in lines_of(root)] == ["start", "park", "resume"]
    assert lines_of(root)[-1]["reason"] == "parked: x"
    assert hashlib.sha256(sp.read_bytes()).hexdigest() == lines_of(root)[-1]["state"]
    print("ok")


def test_park_refusals():
    """CT-13 (FR-32): park refuses an empty reason and a legacy folder, writing nothing."""
    root = effort("planning")
    (root / ".nio/specs/grilling").mkdir()
    for slug, why, message in [(S, "  ", "park needs a reason"),
                               ("grilling", "x", "grilling is legacy; nio flow writes nothing in it")]:
        try:
            flow.park(root, slug, why, by=BY)
            raise AssertionError(message)
        except ValueError as e:
            assert str(e) == message, e
    assert not flow_files(root) and not (root / ".nio/specs" / S / ".gitignore").exists()
    print("ok")


# --- the flow rule in every skill and card (CT-18) ---

RULE = ("Flow state: only `nio flow` writes `state.json` and `history.jsonl`; never edit them. Only the human gives "
        "`--human` to `nio flow done`, runs `nio flow seen`, or asks for `nio flow abandon`.")


def test_ac11_no_hand_edit_instruction():
    """TC-11: every skill and agent card carries the flow rule; every other line naming a flow file names a `nio flow`
    command, and none tells an agent to edit, write, append to or change one."""
    here = Path(__file__).parent.parent
    paths = sorted(here.glob("skills/*/SKILL.md")) + sorted(here.glob("src/nio/agents/*.md"))
    assert len(paths) == 26, paths
    for path in paths:
        lines = path.read_text().splitlines()
        assert lines.count(RULE) == 1, path
        for line in lines:
            if line == RULE:
                continue
            if "state.json" in line or "history.jsonl" in line:
                assert "nio flow" in line, (path, line)
            assert not re.search(r"(edit|write|append to|change) .*(state\.json|history\.jsonl)", line), (path, line)
    print("ok")


# --- nio flow done (CT-11) ---

def count(root, slug=S):
    path = root / ".nio/specs" / slug / "history.jsonl"
    return len(path.read_text().splitlines()) if path.exists() else 0


def gate_ready(root, slug=S):
    """Pass the grill: settle OP-1 and confirm the default, as the grill does."""
    spec = root / ".nio/specs" / slug / "spec.md"
    spec.write_text(re.sub(r"^- \*\*OP-1\*\*.*\n", "", spec.read_text(), flags=re.M).replace("[default]", "[human]"))


FINDING = """### F1 Refunds never say the currency
- cites: FR-1
- kind: gap
- severity: major
- evidence: observed
- quote: "refund the full order amount"
- situation: a refund for a paid order never says which currency it pays in
- fix: say the currency in FR-1
"""


def reject_spec(root, slug=S):
    """A real first spec review the jury rejects and records (as tests/test_jury.py:first_review, before the fixes)."""
    run = root / ".nio/runs/R-rej/jury"
    run.mkdir(parents=True, exist_ok=True)
    (run / "spec-logic.md").write_text(f"---\nlens: logic\ngate: spec\nsubject: {slug}\nby: \"juror / claude-code / opus\"\n"
                                       f"context: sufficient\n---\n## Reasoning\nChecked every rule.\n\n## Findings\n{FINDING}")
    jury.collect(root, slug, "spec", "R-rej")
    (run / "spec-refuter.md").write_text("### J-1\n- result: confirmed\n- reason: it holds\n")
    jury.collect(root, slug, "spec", "R-rej")
    assert jury.check(root, slug, "spec", record=True)[0] == "rejected"


def test_ac13_done_grilling_passes():
    """TC-13: a passing grill guard moves the effort to spec_jury with exactly one pass line."""
    root = effort("grilling")
    flow.start(root, S, by=BY)
    gate_ready(root)
    n = count(root)
    assert flow.done(root, "grilling", S, by=BY) == (0, [f"moved {S}: grilling → spec_jury", "next: run the nio:jury skill"])
    assert "state: spec_jury" in nxt(root)
    new = lines_of(root)[n:]
    assert len(new) == 1 and (new[0]["kind"], new[0]["from"], new[0]["to"]) == ("pass", "grilling", "spec_jury"), new
    assert any(p.endswith("spec.md") for p in new[0]["evidence"]["paths"]), new
    assert re.fullmatch(r"[0-9a-f]{64}", new[0]["evidence"]["output"]) or new[0]["evidence"]["output"] == "", new
    print("ok")


def test_ac14_done_grilling_fails():
    """TC-14: a failing grill guard names the open point and the unconfirmed default; nothing is recorded."""
    # `spec.check --gate` says only "`## Open points` must be empty"; the grill guard adds one line per open point
    # left (CT-5's "lines that say what is missing") so that OP-3 is named, as AC-14 asks.
    root = effort("grilling")
    flow.start(root, S, by=BY)
    spec = root / ".nio/specs" / S / "spec.md"
    text = spec.read_text().replace("- **OP-1**", "- **OP-3** (decision; FR-1) Which currency?\n- **OP-1**")
    spec.write_text(re.sub(r"(\*\*FR-2\*\*.*)\[human\]", r"\1[default]", text))
    n = count(root)
    code, out = flow.done(root, "grilling", S, by=BY)
    assert code == 1 and "OP-3" in "\n".join(out) and "FR-2" in "\n".join(out), out
    assert "state: grilling" in nxt(root) and count(root) == n
    print("ok")


def test_ac15_handoff_is_not_evidence():
    """TC-15: a worker's handoff never passes the spec gate: the guard reads the ledger, which says rerun."""
    root = effort("spec_jury")
    reject_spec(root)
    spec = root / ".nio/specs" / S / "spec.md"
    spec.write_text(spec.read_text().replace("refund the full order amount.", "refund the full order amount in EUR."))
    flow.start(root, S, by=BY)
    (root / ".nio/specs" / S / "handoff.md").write_text("all tests pass\n")
    code, out = flow.done(root, "spec_jury", S, by=BY)
    text = "\n".join(out)
    assert code == 1 and "the spec jury's outcome is rerun" in text, out
    assert "all tests pass" not in text and "handoff.md" not in text, out
    print("ok")


def test_ac16_done_tasking_fails():
    """TC-16: an AC with no task fails tasking, naming it as `nio check tasks` does."""
    # TC-16 names AC-4, which the refunds fixture spec doesn't have; AC-2 is left with no task instead.
    root = effort("tasking")
    flow.start(root, S, by=BY)
    text = (FIXTURES / "tasks/tasks.md").read_text().replace("slug: checkout-refunds", f"slug: {S}")
    text = text.replace("- Serves: AC-2\n", "- Serves: AC-1\n").replace("- Serves: AC-1, AC-2\n", "- Serves: AC-1\n")
    (root / ".nio/specs" / S / "tasks.md").write_text(text)
    from nio import tasks
    want = [e for e in tasks.check(root, S)[0] if "AC-2" in e]
    code, out = flow.done(root, "tasking", S, by=BY)
    assert code == 1 and want and all(f"ERROR {e}" in out for e in want), (out, want)
    print("ok")


def test_ac17_stage_not_reached():
    """TC-17: done on a stage the effort hasn't reached names the current one and records nothing."""
    root = effort("drafting")
    flow.start(root, S, by=BY)
    n = count(root)
    try:
        flow.done(root, "planning", S, by=BY)
        raise AssertionError("done on a stage not reached")
    except ValueError as e:
        assert str(e) == f"{S} is at drafting, not planning", e
    assert count(root) == n
    print("ok")


def test_ac18_stage_already_passed():
    """TC-18: done on a stage already passed changes nothing and exits 0."""
    root = effort("grilling")
    flow.start(root, S, by=BY)
    before = snap(root, S)
    assert flow.done(root, "drafting", S, by=BY)[0] == 0
    assert snap(root, S) == before
    print("ok")


def test_ac22_skips_not_built():
    """TC-22: passing drafting records the pass and a skip line per not-built stage, landing at grilling."""
    root = effort("drafting")
    flow.start(root, S, by=BY)
    folder = root / ".nio/specs" / S
    folder.joinpath("spec.md").write_text((FIXTURES / "spec/spec.md").read_text().replace("checkout-refunds", S)
                                          .replace("risk: [money, external-input]", "risk: []"))
    n = count(root)
    code, out = flow.done(root, "drafting", S, by=BY)
    assert code == 0 and out == [f"moved {S}: drafting → grilling", "skipped researching (not built)",
                                 "skipped advocate_walking (not built)", "next: run the nio:grill skill"], out
    new = [(x["kind"], x["from"], x["to"], x.get("reason")) for x in lines_of(root)[n:]]
    assert new == [("pass", "drafting", "researching", None),
                   ("skip", "researching", "advocate_walking", "skipped: not built"),
                   ("skip", "advocate_walking", "grilling", "skipped: not built")], new
    out = nxt(root)
    assert "state: grilling" in out and "skipped: researching, advocate_walking (not built)" in out, out
    assert flow.done(root, "drafting", S, by=BY)[0] == 0 and count(root) == n + 3  # now recorded: FR-17
    print("ok")


def test_uj1_no_say_so():
    """TC-68: a handoff saying the grill is done doesn't pass it; a hand-set wait in state.json breaks the effort."""
    root = effort("grilling")
    flow.start(root, S, by=BY)
    spec = root / ".nio/specs" / S / "spec.md"
    spec.write_text(spec.read_text().replace("- **OP-1**", "- **OP-3** (decision; FR-1) Which currency?\n- **OP-1**"))
    (root / ".nio/specs" / S / "handoff.md").write_text("grilling done\n")
    n = count(root)
    code, out = flow.done(root, "grilling", S, by="orchestrator / claude-code / opus")
    assert code == 1 and "OP-3" in "\n".join(out) and count(root) == n, out
    sp = root / ".nio/specs" / S / "state.json"
    sp.write_text(json.dumps({**json.loads(sp.read_text()), "waiting": {"why": "x"}}, indent=2, sort_keys=True) + "\n")
    try:
        flow.next_step(root, S)
        raise AssertionError("next read a hand-edited state.json")
    except flow.Broken as e:
        assert "state.json" in str(e) and "hash mismatch" in str(e), e
    print("ok")


def test_ac9_done_refuses():
    """TC-78: a state.json with an unknown key stops done."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    bad_key(root)
    code, out = cli(root, "done", "planning", S)
    assert code != 0 and "state.json" in out and "stage" in out, (code, out)
    print("ok")


def bad_key(root, slug=S):
    """TC-9's effort: `"stage"` added to state.json, the hash fixed by a test-only line so only the key is wrong."""
    folder = root / ".nio/specs" / slug
    text = json.dumps({**json.loads((folder / "state.json").read_text()), "stage": "done"}, indent=2, sort_keys=True) + "\n"
    (folder / "state.json").write_text(text)
    line = dict(lines_of(root, slug)[-1], kind="seen", state=hashlib.sha256(text.encode()).hexdigest())
    (folder / "history.jsonl").write_bytes((folder / "history.jsonl").read_bytes() + (json.dumps(line) + "\n").encode())


def test_done_refusals():
    """CT-11: --human at a jury gate points to the jury's own closure (FR-62); an empty --human is refused (FR-26);
    a parked effort answers with the waiting output; none records anything."""
    root = effort("spec_jury")
    flow.start(root, S, by=BY)
    before = snap(root, S)
    code, out = flow.done(root, "spec_jury", S, human="it's fine", by="human")
    assert code == 1 and out[-1] == f'nio jury check {S} spec --human "it\'s fine" --record', out
    try:
        flow.done(root, "grilling", S, human="  ", by="human")
        raise AssertionError("empty --human")
    except ValueError as e:
        assert str(e) == "--human needs a reason", e
    assert snap(root, S) == before
    flow.park(root, S, "lunch", by=BY)
    n = count(root)
    code, out = flow.done(root, "spec_jury", S, by=BY)
    assert code == 1 and out[0] == "Run this command to resume" and f"nio flow start {S} --by human" in out, out
    assert count(root) == n
    print("ok")


# --- the gate commit (CT-11, CT-19) ---

def test_ac19_commit_on_gate():
    """TC-19: --commit makes one `nio: approve spec` commit holding the effort folder and its verdict record."""
    root = effort("spec_jury")
    approve(root, S, "spec", commit=False)
    flow.start(root, S, by=BY)
    (root / "notes.txt").write_text("mine\n")
    mem = root / ".nio/memory/project"
    mem.mkdir(parents=True, exist_ok=True)
    rec = ".nio/memory/project/V-261028-aaaa-spec-gate.md"
    (root / rec).write_text(f'---\nid: V-261028-aaaa\nsubject: "spec:{S}"\n---\n')
    (mem / "V-261028-bbbb-plan-gate.md").write_text(f'---\nid: V-261028-bbbb\nsubject: "plan:{S}"\n---\n')
    code, out = cli(root, "done", "spec_jury", S, "--commit", "--by", "human", by=False)  # only the human approves
    assert code == 0 and f"moved {S}: spec_jury → planning" in out and "skipped arch_grilling (not built)" in out, out
    assert git(root, "log", "-1", "--format=%s").strip() == "nio: approve spec"
    files = git(root, "show", "--name-only", "--format=", "HEAD").split()
    assert f".nio/specs/{S}/history.jsonl" in files and f".nio/specs/{S}/jury/spec.json" in files, files
    assert rec in files, files  # the gate's verdict record goes in the same commit; another gate's does not
    assert ".nio/memory/project/V-261028-bbbb-plan-gate.md" not in files, files
    assert all(f.startswith((f".nio/specs/{S}/", ".nio/memory/project/V-")) for f in files), files
    assert "?? notes.txt" in git(root, "status", "--porcelain").splitlines()
    assert "state: planning (working)" in nxt(root)
    print("ok")


def test_ac20_no_commit_off_gate():
    """TC-20: a pass that is not a gate makes no commit; the line rides along uncommitted."""
    root = effort("grilling")
    flow.start(root, S, by=BY)
    gate_ready(root)
    git(root, "add", "-A")
    git(root, "commit", "-qm", "started")
    head = git(root, "rev-parse", "HEAD")
    code, out = cli(root, "done", "grilling", S)
    assert code == 0 and git(root, "rev-parse", "HEAD") == head, out
    assert f" M .nio/specs/{S}/history.jsonl" in git(root, "status", "--porcelain").splitlines()
    print("ok")


def test_ac21_commit_fails():
    """TC-21: a commit the hook rejects records nothing: history, state, a partly staged file and the index are as
    they were, and git's error is printed."""
    root = effort("spec_jury")
    approve(root, S, "spec", commit=False)
    flow.start(root, S, by=BY)
    notes = root / ".nio/specs" / S / "notes.md"
    notes.write_text("one\n")
    git(root, "add", str(notes))
    git(root, "commit", "-qm", "notes")
    notes.write_text("one\ntwo\n")
    git(root, "add", str(notes))
    notes.write_text("one\ntwo\nthree\n")
    hook = root / ".git/hooks/pre-commit"
    hook.write_text("#!/bin/sh\necho 'hook says no'\nexit 1\n")
    hook.chmod(0o755)
    folder = root / ".nio/specs" / S
    shot = lambda: ((folder / "history.jsonl").read_bytes(), (folder / "state.json").read_bytes(), notes.read_bytes(),
                    git(root, "ls-files", "-s"), git(root, "diff", "--cached"))
    before = shot()
    code, out = cli(root, "done", "spec_jury", S, "--commit", "--by", "human", by=False)  # only the human approves
    assert code != 0 and "hook says no" in out, (code, out)
    assert shot() == before and not (folder / "state.json.new").exists()
    assert "state: spec_jury" in nxt(root)
    print("ok")


def test_commit_fails_after_cutting_a_torn_tail():
    """CT-11 (FR-20): a failed gate commit on an effort with a torn last line puts history.jsonl back byte for byte,
    torn tail included, so nothing is lost."""
    root = effort("spec_jury")
    approve(root, S, "spec", commit=False)
    flow.start(root, S, by=BY)
    folder = root / ".nio/specs" / S
    hp = folder / "history.jsonl"
    hp.write_bytes(hp.read_bytes() + b'{"kind": "pass", "fr')
    hook = root / ".git/hooks/pre-commit"
    hook.write_text("#!/bin/sh\necho 'hook says no'\nexit 1\n")
    hook.chmod(0o755)
    before = snap(root, S)
    code, out = flow.done(root, "spec_jury", S, commit=True, by="human")
    assert code == 1 and "hook says no" in out, out
    assert snap(root, S) == before
    print("ok")


def test_ac52_needs_commit_flag():
    """TC-52: without --commit (auto off) a passing gate is neither committed nor recorded; done and next both print
    the human's approval command."""
    root = effort("spec_jury")
    approve(root, S, "spec", commit=False)
    flow.start(root, S, by=BY)
    head, n = git(root, "rev-parse", "HEAD"), count(root)
    outs = [cli(root, "done", "spec_jury", S), cli(root, "next", S)]
    assert git(root, "rev-parse", "HEAD") == head and count(root) == n
    for code, out in outs:
        assert code == 0 and "nio flow done spec_jury --commit" in out and "--by human" in out, out
    print("ok")


def test_auto_commits_unless_risky():
    """CT-11 (FR-18, FR-51): with the auto flag on, a passing gate commits without --commit, unless the spec carries a
    risky flag, when it waits for the human's --commit as with the flag off."""
    for risk, commits in (("[]", True), ("[money]", False)):
        root = effort("spec_jury", risk=risk)
        approve(root, S, "spec", commit=False)
        history(root, S, {"kind": "start", "from": None, "to": "spec_jury", "state": {"auto": True}})
        head = git(root, "rev-parse", "HEAD")
        code, out = flow.done(root, "spec_jury", S, by=BY)
        assert code == 0 and (git(root, "rev-parse", "HEAD") != head) == commits, (risk, out)
        assert ("committed nio: approve spec" in out) == commits and lines_of(root)[-1]["kind"] == (
            "skip" if commits else "start"), (risk, out)
    print("ok")


def test_crash_between_append_and_commit():
    """CT-11: a pass line recorded but never committed is not recorded again; the next --commit only commits."""
    root = effort("spec_jury")
    approve(root, S, "spec", commit=False)
    flow.start(root, S, by=BY)
    # simulate the crash: the lines land, the commit never runs
    from nio import flow as f
    _, _, ev = f.guard(root, S, "spec_jury")
    skips, _ = f.moves("spec_jury")
    with f.lock(root, S):
        f.record(root, S, [{"kind": "pass", "from": "spec_jury", "to": "arch_grilling", "evidence": ev}] + skips,
                 f.load(root, S)[0], f.who(BY), "")
    n = count(root)
    assert "waiting_for_human: approve spec" in nxt(root)
    code, out = flow.done(root, "spec_jury", S, commit=True, by="human")
    assert code == 0 and count(root) == n and git(root, "log", "-1", "--format=%s").strip() == "nio: approve spec", out
    assert not git(root, "status", "--porcelain", "--", f".nio/specs/{S}")
    print("ok")


# --- gates and rejections as where reads them (CT-6) ---

def test_ac23_implementing_names_the_skill():
    """TC-23, now built (implement CT-14): implementing is working, naming @nio:implement, tasks.md and the next task."""
    out = nxt(effort("implementing"))
    assert "state: implementing (working)" in out and "skill: @nio:implement" in out, out
    assert f".nio/specs/{S}/tasks.md" in out and "task: T-1 Refund a paid order in full" in out, out
    assert "not built" not in out, out
    print("ok")


def test_ac24_spec_rejected():
    """TC-24: a recorded rejected spec round, the spec unchanged since, sends the effort back to grilling."""
    root = effort("spec_jury")
    reject_spec(root)
    out = nxt(root)
    assert "state: grilling" in out and "round 1" in out, out
    print("ok")


def test_ac63_rereview():
    """TC-63: once the spec changes after its rejection, the effort is at the spec gate again for its re-review."""
    root = effort("spec_jury")
    reject_spec(root)
    spec = root / ".nio/specs" / S / "spec.md"
    spec.write_text(spec.read_text().replace("## Summary\n", "## Summary\nRefunds are paid in the order's currency.\n", 1))
    assert "state: spec_jury" in nxt(root)
    print("ok")


def test_ac25_tasks_rejected():
    """TC-25: a tasks ledger whose round 1 is rejected, tasks.md unchanged, sends the effort back to tasking."""
    root = effort("implementing")
    ledger = root / ".nio/specs" / S / "jury/tasks.json"
    ledger.write_text(ledger.read_text().replace('"outcome": "approved"', '"outcome": "rejected"'))
    assert "state: tasking" in nxt(root)
    print("ok")


def test_ac51_no_history_no_write():
    """TC-51: a past effort with no history reads as planning from its files and is not written."""
    root = effort("planning")
    assert "state: planning" in nxt(root) and not flow_files(root)
    print("ok")


def test_ac64_approval_commit():
    """TC-64: an approved spec ledger counts only with its approval commit; without it the gate waits for the human."""
    committed, bare = effort("spec_jury"), effort("spec_jury")
    approve(committed, S, "spec")
    approve(bare, S, "spec", commit=False)
    code, out = cli(committed, "next", S)
    assert code == 0 and "state: planning" in out, out
    code, out = cli(bare, "next", S)
    assert code == 0 and "waiting_for_human" in out and "nio flow done spec_jury --commit" in out, out
    print("ok")


def test_old_round_approval_no_longer_counts():
    """CT-6 (FR-55): an approval commit from an earlier round doesn't count once the ledger has moved on a round."""
    root = effort("planning")
    ledger = root / ".nio/specs" / S / "jury/spec.json"
    led = json.loads(ledger.read_text())
    led["round"] += 1
    led["versions"][str(led["round"])] = led["versions"][str(led["round"] - 1)]
    ledger.write_text(json.dumps(led))
    out = nxt(root)
    assert "state: spec_jury" in out and "planning" not in out.splitlines()[1], out
    print("ok")


# --- nio flow status (CT-12) ---

def when(day, hour=10):
    import datetime
    return datetime.datetime(2026, 10, day, hour, tzinfo=datetime.timezone.utc)


def line_for(root, slug):
    return next(x for x in flow.status(root)[1] if x.startswith(slug + " · "))


def test_ac10_bad_history_line():
    """TC-10: a bad middle history line stops next and shows the effort broken in status, the others listed as usual."""
    root = effort("planning")
    history(root, S, *[{"kind": "seen", "from": "planning", "to": "planning", "at": at(10 + i)} for i in range(5)])
    hp = root / ".nio/specs" / S / "history.jsonl"
    rows = hp.read_text().splitlines()
    rows[2] = "{not json"
    hp.write_text("\n".join(rows) + "\n")
    other = "2026-10-21-refunds"
    effort("planning", slug=other, root=root)
    flow.start(root, other, by=BY)
    code, out = cli(root, "next", S)
    assert code != 0 and "history.jsonl" in out and "line 3" in out, out
    code, out = cli(root, "status")
    assert code == 0 and f"{S} · broken: history.jsonl, line 3" in out.splitlines(), out
    assert any(x.startswith(other) for x in out.splitlines()), out
    print("ok")


def test_ac31_status_five_efforts():
    """TC-31: five efforts, newest activity first, each with its status word; one with no history dated by its commit."""
    a, b, c, d, e = (f"2026-10-0{i}-{n}" for i, n in enumerate("abcde", 1))
    root = effort("planning", slug=a)
    effort("grilling", slug=b, root=root)
    effort("planning", slug=c, root=root)
    effort("implementing", slug=d, root=root)
    effort("grilling", slug=e, root=root)  # after the others' approval commits, which add everything
    import os as _os
    subprocess.run(["git", "add", "-A", "--", f".nio/specs/{e}"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "e", "--", f".nio/specs/{e}"], cwd=root, check=True,
                   env={**_os.environ, "GIT_COMMITTER_DATE": "2026-10-21T10:00:00Z", "GIT_AUTHOR_DATE": "2026-10-21T10:00:00Z"})
    (root / ".nio/specs" / b / "grill.md").write_text("## Asked · Q4 · OP-1 · 2026-10-24\nQuestion: who pays?\n")
    history(root, a, {"kind": "start", "from": None, "to": "planning", "at": when(25)})
    history(root, b, {"kind": "start", "from": None, "to": "grilling", "at": when(24)})
    history(root, c, {"kind": "start", "from": None, "to": "planning", "at": when(22, 9)},
            {"kind": "park", "from": "planning", "to": "planning", "reason": "waiting on #43", "at": when(23),
             "state": {"pause": {"kind": "parked", "why": "waiting on #43"}}})
    history(root, d, {"kind": "start", "from": None, "to": "implementing", "at": when(22)})
    code, out = cli(root, "status")
    rows = out.splitlines()
    assert code == 0 and len(rows) == 5 and [x.split(" · ")[0] for x in rows] == [a, b, c, d, e], out
    for row, word in zip(rows, ["working", "waiting_for_human: Q4", "parked: waiting on #43",
                                "implementing · manual · working", "2026-10-21 10:00"]):
        assert word in row, (row, word)
    assert rows[0] == f"{a} · planning · manual · working · 2026-10-25 10:00", rows[0]
    print("ok")


def test_ac32_legacy_folder():
    """TC-32: an undated folder shows as legacy and is never written."""
    root = effort("planning")
    legacy = root / ".nio/specs/grilling"
    legacy.mkdir()
    (legacy / "spec.md").write_text("# old\n")
    before = snap(root, "grilling")
    assert any(x.startswith("grilling · legacy · ") for x in flow.status(root)[1]), flow.status(root)
    try:
        flow.start(root, "grilling", by=BY)
        raise AssertionError("started a legacy folder")
    except ValueError:
        pass
    assert snap(root, "grilling") == before
    print("ok")


def test_ac53_lite_unsupported():
    """TC-53: a lite spec is unsupported in status and next, which name no skill and write nothing."""
    root = effort("drafting", route="lite")
    (root / ".nio/specs" / S / "spec.md").write_text(
        re.sub(r"^slug: .*$", f"slug: {S}", (FIXTURES / "spec/spec-bugfix.md").read_text(), count=1, flags=re.M))
    assert "unsupported: lite" in line_for(root, S)
    out = nxt(root)
    assert "unsupported: lite" in out and "@nio:" not in out and not flow_files(root), out
    print("ok")


def test_uj2_idle_visible():
    """TC-69: an idle effort shows when it was last active, below the newer one."""
    root = effort("planning")
    other = "2026-10-21-refunds"
    effort("planning", slug=other, root=root)
    history(root, S, {"kind": "start", "from": None, "to": "planning", "at": when(28, 9)})
    history(root, other, {"kind": "start", "from": None, "to": "planning", "at": when(21, 9)})
    rows = flow.status(root)[1]
    assert rows[0].startswith(S) and rows[1].startswith(other) and "2026-10-21 09:00" in rows[1], rows
    print("ok")


def test_nfr3_status_speed():
    """TC-67: status over 20 efforts at tasks_jury, 50 history lines each, takes under 2 seconds."""
    slugs = [f"2026-10-{i:02d}-e" for i in range(1, 21)]
    root = effort("tasks_jury", slug=slugs[0])
    for slug in slugs[1:]:
        effort("tasks_jury", slug=slug, root=root)
    for i, slug in enumerate(slugs):
        line = {"kind": "seen", "from": "tasks_jury", "to": "tasks_jury"}
        state = flow.defaults()
        lines = [{**line, "at": when(1 + i % 27)} for _ in range(50)]
        for x in lines:  # one record call per line, as `history` does, but with the state in hand
            at_ = x.pop("at")
            flow.record(root, slug, [x], state, flow.who(BY), "", at=at_)
    start = time.perf_counter()
    code, out = cli(root, "status")
    took = time.perf_counter() - start
    assert code == 0 and len(out.splitlines()) == 20 and took < 2.0, (took, out)
    print(f"ok ({took:.2f}s)")


# --- park and resume as the human sees them (CT-13, CT-9) ---

def test_ac33_park():
    """TC-33: park records the reason, and status shows it."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    n = count(root)
    assert flow.park(root, S, "waiting on #43", by=BY) == (0, [f"parked {S}: waiting on #43"])
    assert "parked: waiting on #43" in line_for(root, S)
    new = lines_of(root)[n:]
    assert [(x["kind"], x["reason"]) for x in new] == [("park", "waiting on #43")], new
    print("ok")


def test_ac34_next_resumes():
    """TC-34: next with --by resumes a parked effort with one resume line."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    flow.park(root, S, "lunch", by=BY)
    n = count(root)
    flow.next_step(root, S, by=BY)
    assert "working" in line_for(root, S)
    assert [x["kind"] for x in lines_of(root)[n:]] == ["resume"] and flow.load(root, S)[0]["pause"] is None
    print("ok")


def test_ac35_park_refusals():
    """TC-35: park refuses an empty reason and a done effort, recording nothing."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    other = "2026-10-21-refunds"
    effort("implementing", slug=other, root=root)
    flow.start(root, other, by=BY)
    assert flow.done(root, "implementing", other, human="shipped by hand", by="human")[0] == 0
    assert " · done · " in line_for(root, other)
    counts = count(root), count(root, other)
    for slug, why in ((S, ""), (other, "x")):
        try:
            flow.park(root, slug, why, by=BY)
            raise AssertionError(slug)
        except ValueError:
            pass
    assert (count(root), count(root, other)) == counts
    print("ok")


def test_ac61_live_lock():
    """TC-61: a live lock on this host, however old, is not taken over; nothing is written and the lock is kept."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    path = old_lock(root, os.getpid(), socket.gethostname())
    before, n = path.read_bytes(), count(root)
    code, out = cli(root, "park", S, "x")
    assert code != 0 and "being written" in out and count(root) == n and path.read_bytes() == before, out
    print("ok")


def test_nfr2_offline():
    """TC-66: next, status and park make no network call, and the embedding model is never imported."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    site = Path(tempfile.mkdtemp())
    (site / "sitecustomize.py").write_text(
        "import socket\ndef no(*a, **k):\n    raise OSError('network blocked')\n"
        "socket.socket.connect = no\nsocket.create_connection = no\n")
    env = {**os.environ, "PYTHONPATH": str(site)}
    for args in (["next"], ["status"], ["park", S, "x", "--by", BY]):
        r = subprocess.run([sys.executable, "-c", "from nio.cli import main; main()", "flow", *args], cwd=root,
                           capture_output=True, text=True, env=env)
        assert r.returncode == 0 and "network blocked" not in r.stdout + r.stderr, (args, r)
    flow.next_step(root, S)
    flow.status(root)
    flow.park(root, S, "y", by=BY)
    assert "fastembed" not in sys.modules
    print("ok")


# --- nio flow abandon (CT-14) ---

def test_ac55_abandon():
    """TC-55: abandon freezes the effort at its stage, listed last, until start resumes it."""
    root = effort("tasking")
    flow.start(root, S, by=BY)
    flow.park(root, S, "lunch", by=BY)
    other = "2026-10-21-refunds"
    effort("planning", slug=other, root=root)
    flow.start(root, other, by=BY)
    assert flow.abandon(root, S, "superseded by #60", by=BY) == (0, [f"abandoned {S}: superseded by #60"])
    path = records.new(root, "change", "project", "Refund in EUR")
    path.write_text(path.read_text().replace('against: ""', f'against: ".nio/specs/{S}/plan.md"'))
    rows = flow.status(root)[1]
    assert rows[-1].startswith(S) and " · tasking · " in rows[-1] and "abandoned: superseded by #60" in rows[-1], rows
    # TC-55 expects `working` after start; but the pending change record filed against plan.md now applies (FR-35),
    # so per CT-7/FR-38 the effort moves back to planning and waits on that record.
    cid = path.name[:13]
    assert flow.start(root, S, by=BY) == (0, [f"resumed {S} at planning"])
    assert f" · planning · manual · waiting_for_human: {cid} pending" in line_for(root, S), line_for(root, S)
    got = lines_of(root)
    assert [x["kind"] for x in got][-3:] == ["abandon", "resume", "back"], got
    assert got[-2]["reason"] == "abandoned: superseded by #60; parked: lunch" and got[-1]["change"] == cid
    print("ok")


def test_ac62_abandon_refusals():
    """TC-62: abandon refuses an empty reason, a legacy, a lite and a done effort, writing nothing anywhere."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    (root / ".nio/specs/grilling").mkdir()
    (root / ".nio/specs/grilling/spec.md").write_text("# old\n")
    fix = root / ".nio/specs/2026-10-21-fix"
    fix.mkdir()
    (fix / "spec.md").write_text(
        re.sub(r"^slug: .*$", "slug: 2026-10-21-fix", (FIXTURES / "spec/spec-bugfix.md").read_text(), count=1, flags=re.M))
    finished = "2026-10-22-refunds"
    effort("implementing", slug=finished, root=root)
    flow.start(root, finished, by=BY)
    flow.done(root, "implementing", finished, human="shipped by hand", by="human")
    slugs = [S, "grilling", "2026-10-21-fix", finished]
    before = {s: snap(root, s) for s in slugs}
    for slug, why in zip(slugs, ["", "x", "x", "x"]):
        try:
            flow.abandon(root, slug, why, by=BY)
            raise AssertionError(slug)
        except ValueError:
            pass
    assert {s: snap(root, s) for s in slugs} == before
    print("ok")


def test_ac9_abandon_refuses():
    """TC-79: a state.json with an unknown key stops abandon."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    bad_key(root)
    code, out = cli(root, "abandon", S, "x")
    assert code != 0 and "state.json" in out and "stage" in out, (code, out)
    print("ok")


# --- nio run names its effort (CT-17) ---

def nio(root, *args):
    r = subprocess.run([sys.executable, "-c", "from nio.cli import main; main()", *args], cwd=root,
                       capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def test_ac36_run_names_effort():
    """TC-36: `nio run <slug> <stage>` writes flow.json; the next history line for that stage carries the run."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    for name in ("plan.md", "contracts.md", "tests.md", "quickstart.md"):  # plan files passing `nio check plan --gate`
        (root / ".nio/specs" / S / name).write_text((FIXTURES / "plan" / name).read_text().replace("checkout-refunds", S))
    code, out, err = nio(root, "run", S, "planning")
    rid = out.strip()
    assert code == 0 and re.fullmatch(r"R-\d{6}-[a-z2-7]{4}", rid), (out, err)
    link = json.loads((root / ".nio/runs" / rid / "flow.json").read_text())
    assert (link["effort"], link["stage"]) == (S, "planning"), link
    code, out = cli(root, "done", "planning", S)
    assert code == 0 and lines_of(root)[-1]["run"] == rid and flow.load(root, S)[0]["run"] == rid, (out, lines_of(root))
    print("ok")


def test_ac37_plain_run():
    """TC-37: `nio run` with no arguments works as today: one run ID, promote.md, no flow.json."""
    root = repo()
    code, out, err = nio(root, "run")
    rid = out.strip()
    assert code == 0 and re.fullmatch(r"R-\d{6}-[a-z2-7]{4}", rid) and len(out.splitlines()) == 1, (out, err)
    assert (root / ".nio/runs" / rid / "promote.md").exists() and not (root / ".nio/runs" / rid / "flow.json").exists()
    print("ok")


def test_run_refusals():
    """CT-17: one argument only, an unknown slug or an unknown stage are refused before any run folder exists; a task
    is linked as `task`."""
    root = effort("planning")
    runs = lambda: sorted((root / ".nio/runs").iterdir()) if (root / ".nio/runs").exists() else []
    before = runs()
    for args in ([S], ["2026-10-29-nothing", "planning"], [S, "nowhere"]):
        code, out, err = nio(root, "run", *args)
        assert code == 1 and err.startswith("error: "), (args, out, err)
    assert runs() == before
    code, out, err = nio(root, "run", S, "T-3")
    assert code == 0 and json.loads((root / ".nio/runs" / out.strip() / "flow.json").read_text())["task"] == "T-3"
    print("ok")


# --- overrides (CT-11, FR-24 to FR-30) ---

def op3(root, slug=S):
    """The spec still has OP-3 open (as well as the fixture's OP-1)."""
    spec = root / ".nio/specs" / slug / "spec.md"
    spec.write_text(spec.read_text().replace("- **OP-1**", "- **OP-3** (decision; FR-1) Which currency?\n- **OP-1**"))


def test_ac26_override():
    """TC-26: --human passes a failing guard on its own override line, holding the failing output and the reason."""
    root = effort("grilling")
    flow.start(root, S, by=BY)
    op3(root)
    n = count(root)
    code, out = flow.done(root, "grilling", S, human="OP-3 is settled in Q5", by="human")
    assert code == 0 and "state: spec_jury" in nxt(root), out
    new = lines_of(root)[n:]
    assert len(new) == 1 and (new[0]["kind"], new[0]["from"], new[0]["reason"]) == (
        "override", "grilling", "OP-3 is settled in Q5"), new
    assert "OP-3" in new[0]["evidence"]["output_text"] and re.fullmatch(r"[0-9a-f]{64}", new[0]["evidence"]["output"])
    print("ok")
    return root


def test_ac27_overrides_not_merged():
    """TC-27: the same override on two efforts is two lines, one in each history."""
    other = "2026-10-21-refunds"
    root = effort("grilling")
    effort("grilling", slug=other, root=root)
    for slug in (S, other):
        flow.start(root, slug, by=BY)
        op3(root, slug)
    for slug in (S, other):
        assert flow.done(root, "grilling", slug, human="same reason", by="human")[0] == 0
    for slug in (S, other):
        got = [x for x in lines_of(root, slug) if x["kind"] == "override"]
        assert len(got) == 1 and got[0]["reason"] == "same reason", got
    print("ok")


def test_ac28_empty_reason():
    """TC-28: an empty or blank --human reason is refused and records nothing."""
    root = effort("grilling")
    flow.start(root, S, by=BY)
    op3(root)
    n = count(root)
    for reason in ("", "   "):
        try:
            flow.done(root, "grilling", S, human=reason, by="human")
            raise AssertionError(repr(reason))
        except ValueError as e:
            assert "reason" in str(e), e
    assert count(root) == n
    print("ok")


def test_ac29_jury_closed_by_human():
    """TC-29: a jury gate the human closed with a reason passes as an override carrying it, with no commit."""
    root = effort("spec_jury")
    assert jury.check(root, S, "spec", record=True, human="pack bug")[0] == "human"
    flow.start(root, S, by=BY)
    head, n = git(root, "rev-parse", "HEAD"), count(root)
    code, out = flow.done(root, "spec_jury", S, by=BY)
    first = lines_of(root)[n]
    assert code == 0 and (first["kind"], first["from"], first["reason"]) == ("override", "spec_jury", "pack bug"), out
    assert first["evidence"]["round"] == jury.load(root, S, "spec")["round"] and "spec.md" in first["evidence"]["blobs"]
    assert git(root, "rev-parse", "HEAD") == head and "state: planning" in nxt(root)
    print("ok")


def test_ac30_human_on_passing_guard():
    """TC-30: --human on a guard that passes records a plain pass with the reason, no override."""
    root = effort("grilling")
    flow.start(root, S, by=BY)
    gate_ready(root)
    n = count(root)
    assert flow.done(root, "grilling", S, human="just in case", by="human")[0] == 0
    new = lines_of(root)[n:]
    assert [(x["kind"], x.get("reason")) for x in new] == [("pass", "just in case")], new
    print("ok")


def test_ac65_human_at_gate_refused():
    """TC-72: --human at a jury gate is refused, records nothing and points to the jury's own closure."""
    root = effort("spec_jury")
    reject_spec(root)
    spec = root / ".nio/specs" / S / "spec.md"
    spec.write_text(spec.read_text().replace("refund the full order amount.", "refund the full order amount in EUR."))
    flow.start(root, S, by=BY)
    n = count(root)
    code, out = cli(root, "done", "spec_jury", S, "--human", "pack bug")
    assert code != 0 and count(root) == n, out
    assert f'nio jury check {S} spec --human "pack bug" --record' in out, out
    print("ok")


# --- seen and unseen overrides (CT-15) ---

def test_ac57_seen():
    """TC-57: an override shows in status until `seen` records that the human saw it."""
    root = test_ac26_override()
    assert "override not seen: grilling: OP-3 is settled in Q5" in line_for(root, S)
    n = count(root)
    assert flow.seen(root, S, by="human") == (0, [f"seen 1 overrides on {S}"])
    assert "override not seen" not in line_for(root, S)
    assert [x["kind"] for x in lines_of(root)[n:]] == ["seen"]
    assert flow.seen(root, S, by="human") == (0, [f"nothing to see on {S}"]) and count(root) == n + 1
    print("ok")


def test_nfr1_next_twelve_lines():
    """TC-65: next stays within 12 lines at drafting, grilling just after skips, planning with 5 unseen overrides,
    plan_jury and tasking."""
    root = effort("planning")
    history(root, S, *[{"kind": "override", "from": "intake", "to": "drafting", "reason": f"reason {i}", "at": at(10 + i)}
                       for i in range(5)])
    outs = [nxt(root)]
    assert outs[0].count("reason ") == 5, outs[0]
    grill = effort("grilling")
    history(grill, S, {"kind": "pass", "from": "drafting", "to": "researching", "at": at(10)},
            {"kind": "skip", "from": "researching", "to": "advocate_walking", "reason": "skipped: not built", "at": at(10)},
            {"kind": "skip", "from": "advocate_walking", "to": "grilling", "reason": "skipped: not built", "at": at(10)})
    outs += [nxt(grill)] + [nxt(effort(stage)) for stage in ("drafting", "plan_jury", "tasking")]
    for out in outs:
        assert len(out.splitlines()) <= 12, out
    print("ok")


def test_uj3_override_shown():
    """TC-70: an agent's override is on the record under its role and shows in status and next until seen; every
    skill and card carries the flow rule."""
    root = effort("grilling")
    flow.start(root, S, by=BY)
    op3(root)
    flow.done(root, "grilling", S, human="settled", by="orchestrator / claude-code / opus")
    assert lines_of(root)[-1]["who"]["role"] == "orchestrator"
    assert "override not seen: grilling: settled" in line_for(root, S)
    assert "override not seen: grilling: settled" in nxt(root)
    here = Path(__file__).parent.parent
    for path in sorted(here.glob("skills/*/SKILL.md")) + sorted(here.glob("src/nio/agents/*.md")):
        assert RULE in path.read_text().splitlines(), path
    print("ok")


def test_ac9_seen_refuses():
    """TC-80: a state.json with an unknown key stops seen."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    bad_key(root)
    code, out = cli(root, "seen", S)
    assert code != 0 and "state.json" in out and "stage" in out, (code, out)
    print("ok")


# --- a change sends the effort back (CT-7) ---

def change_record(root, against, outcome="pending"):
    """A change record against a file of the effort; returns its ID."""
    path = records.new(root, "change", "project", "Refund in EUR")
    text = path.read_text().replace('against: ""', f'against: "{against}"')
    path.write_text(re.sub(r"^outcome: \w+", f"outcome: {outcome}", text, count=1, flags=re.M))
    return path.name[:13]


def test_ac38_pending_change():
    """TC-38: a pending change record against plan.md waits on the record and moves the effort back once."""
    root = effort("tasking")
    flow.start(root, S, by=BY)
    cid = change_record(root, f".nio/specs/{S}/plan.md")
    n = count(root)
    out = nxt(root, by=BY)
    assert "waiting_for_human" in out and cid in out and "planning" in out and "@nio:" not in out, out
    assert out.splitlines()[0] == f"Settle the change request {cid}", out
    new = lines_of(root)[n:]
    assert [(x["kind"], x["from"], x["to"], x["change"]) for x in new] == [("back", "tasking", "planning", cid)], new
    nxt(root, by=BY)
    assert count(root) == n + 1
    print("ok")
    return root, cid


def test_ac39_edited_tasks():
    """TC-39: an approved tasks.md edited later (its planned part) sends the effort back to the tasks jury, naming the
    file with its judged and current versions."""
    from nio import jury as j
    root = effort("implementing")
    flow.start(root, S, by=BY)
    tasks_md = root / ".nio/specs" / S / "tasks.md"
    commit = git(root, "log", "-1", "--format=%H", "--grep", "^nio: approve tasks$").strip()
    judged = j.blob(root, flow.planned("tasks.md", git(root, "show", f"{commit}:.nio/specs/{S}/tasks.md")))
    # TC-39 appends a line to a planned task; `nio check tasks` freezes planned tasks after approval, so that fails the
    # tasking guard and the effort stops at tasking (CT-6 takes the earlier stage). The edit goes in the epic's text
    # instead: still the planned part, above any `#### Fixes`, so CT-7 sends the effort back to the tasks jury.
    tasks_md.write_text(tasks_md.read_text().replace("(US-1)\n", "(US-1)\nRefunds are paid in EUR.\n", 1))
    current = j.blob(root, flow.planned("tasks.md", tasks_md.read_text()))
    # TC-39 calls next without --by and expects the `back` line; CT-9 records only with --by, so it is given here.
    out = nxt(root, by=BY)
    assert "state: tasks_jury" in out, out
    back = lines_of(root)[-1]
    assert back["kind"] == "back" and back["change"] == {"file": "tasks.md", "judged": judged, "current": current}, back
    print("ok")


def test_ac39_fix_task_is_not_an_edit():
    """CT-7 (RF-9): a fix task added under `#### Fixes` after approval doesn't count as an edit of tasks.md."""
    root = effort("implementing")
    tasks_md = root / ".nio/specs" / S / "tasks.md"
    tasks_md.write_text(tasks_md.read_text() + "\n#### Fixes\n\n### T-4 Fix the finding\n- Files: `app.py`\n")
    assert flow.changes(root, S, []) == [] and "state: implementing (working)" in nxt(root)
    print("ok")


def test_ac40_rejected_change():
    """TC-40: a rejected change record moves nothing."""
    root = effort("tasking")
    flow.start(root, S, by=BY)
    change_record(root, f".nio/specs/{S}/plan.md", outcome="rejected")
    n = count(root)
    assert "state: tasking" in nxt(root) and count(root) == n
    print("ok")


def test_ac41_done_refused_while_pending():
    """TC-41: done on the owning stage is refused while the change record is pending."""
    root, cid = test_ac38_pending_change()
    n = count(root)
    try:
        flow.done(root, "planning", S, by=BY)
        raise AssertionError("done while a change is pending")
    except ValueError as e:
        assert cid in str(e) and "outcome: pending" in str(e), e
    assert count(root) == n
    print("ok")


def test_ac42_parked_moves_back():
    """TC-42: a parked effort moves back with a pending change and stays parked."""
    root = effort("tasking")
    flow.start(root, S, by=BY)
    flow.park(root, S, "on hold", by=BY)
    change_record(root, f".nio/specs/{S}/research.md")
    line = line_for(root, S)
    assert " · grilling · " in line and "parked: on hold" in line, line
    print("ok")


def test_uj4_changed_spec_blocks():
    """TC-71: once the approved spec is edited, the effort is back at the spec gate and planning can't be passed."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    for name in ("plan.md", "contracts.md", "tests.md", "quickstart.md"):
        (root / ".nio/specs" / S / name).write_text((FIXTURES / "plan" / name).read_text().replace("checkout-refunds", S))
    spec = root / ".nio/specs" / S / "spec.md"
    spec.write_text(spec.read_text().replace("## Summary\n", "## Summary\nRefunds are paid in EUR.\n", 1))
    # TC-71 calls next without --by and expects a `back` line; CT-9 records only with --by, so it is given here.
    assert "state: spec_jury" in nxt(root, by=BY)
    assert any(x["kind"] == "back" and x["change"]["file"] == "spec.md" for x in lines_of(root))
    n = count(root)
    try:
        flow.done(root, "planning", S, by=BY)
        raise AssertionError("done planning against a changed spec")
    except ValueError as e:
        assert "spec_jury" in str(e), e
    assert count(root) == n
    print("ok")


def test_research_notes_send_nothing_back():
    """Q26 (C-261028-bdn6): later stages append notes to research.md, so an edit after approval moves nothing."""
    root = effort("planning")
    flow.start(root, S, by=BY)
    research = root / ".nio/specs" / S / "research.md"
    research.write_text(research.read_text() + "- **RF-6** Refunds settle in two days. Source: app.py:1\n")
    assert "state: planning" in nxt(root, by=BY) and flow.changes(root, S, flow.load(root, S)[1]) == []
    print("ok")


def test_unreadable_change_record_is_skipped():
    """CT-7: an unreadable change record is skipped and named, never fatal."""
    root = effort("tasking")
    path = records.new(root, "change", "project", "Broken")
    path.write_text(f"---\nagainst: [{S}\n---\n")
    here = flow.where(root, S)
    assert here["stage"] == "tasking" and here["unreadable"] == [str(path.relative_to(root))], here
    print("ok")


# --- the stop list (CT-8) ---

def auto_on(root, stage, slug=S):
    """Start the effort with the auto flag on, through flow.record (nothing in this spec sets it)."""
    history(root, slug, {"kind": "start", "from": None, "to": stage, "state": {"auto": True}})


def finding(fid, status="open", first=1, fixed_in=None):
    return {"id": fid, "title": f"finding {fid}", "status": status, "first_round": first, "last_round": first,
            "rounds": 0, "severity": "major", "kind": "gap", "cites": [], "sources": [], "validation": "confirmed",
            "disposition": "", "by": "", "note": "", "baseline": "new", "fixed_in": fixed_in}


def ledger(root, gate, slug=S, **fields):
    """Write a gate's ledger by hand: the jury's defaults (or the ledger there) with `fields` set."""
    path = root / ".nio/specs" / slug / "jury" / f"{gate}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({**jury.load(root, slug, gate), **fields}, indent=2))


CHANGED = {"versions": {str(n): "0" * 40 for n in range(1, 4)}}  # a version the artefact no longer has


def round_cap(auto=True):
    """TC-43's effort: at plan_jury, the plan ledger at round 3, rejected, the plan changed since, J-2 and J-5 open."""
    root = effort("plan_jury")
    if auto:
        auto_on(root, "plan_jury")
    else:
        flow.start(root, S, by=BY)
    ledger(root, "plan", round=3, outcome="rejected", findings=[finding("J-2"), finding("J-5", first=2)], **CHANGED)
    return root


def kinds(root, slug=S):
    return [x["kind"] for x in lines_of(root, slug)]


def test_ac43_round_cap():
    """TC-43: three plan rounds without approval pause an auto effort, listing the open findings."""
    root = round_cap()
    out = nxt(root, by=BY)
    assert "@nio:" not in out and "3 rounds" in out and "J-2" in out and "J-5" in out, out
    assert kinds(root)[-1] == "pause" and flow.load(root, S)[0]["waiting"]["round"] == 3
    print("ok")


def test_ac44_no_progress():
    """TC-44: a second spec round that closed none of the first round's findings pauses an auto effort."""
    root = effort("spec_jury")
    auto_on(root, "spec_jury")
    ledger(root, "spec", round=2, outcome="rejected", findings=[finding("J-1")], **CHANGED)
    out = nxt(root)
    assert "@nio:" not in out and "round 2" in out and "J-1" in out, out
    assert out.endswith("would record: pause (run with --by to record)"), out
    print("ok")


def test_ac45_jury_cap():
    """TC-45: an auto effort whose juries used reach `budgets.juries` is suspended on the cap at its next jury."""
    root = effort("plan_jury")
    spec_ledger = root / ".nio/specs" / S / "jury/spec.json"
    led = json.loads(spec_ledger.read_text())
    led["round"], led["versions"]["2"] = 2, led["versions"]["1"]
    spec_ledger.write_text(json.dumps(led, indent=2))
    git(root, "add", "-A")
    git(root, "commit", "-qm", "nio: approve spec")
    plan_keys = 7 - len(led.get("collected") or {})
    ledger(root, "plan", round=2, outcome="rejected", findings=[finding("J-1", "fixed", 1, 2)],
           collected={f"R-{i}/test-proof": "x" for i in range(plan_keys)}, **CHANGED)
    (root / ".nio/config.json").write_text(json.dumps({"memory": {"areas": ["auth", "project"]}, "budgets": {"juries": 4}}))
    auto_on(root, "plan_jury")
    assert flow.where(root, S)["stage"] == "plan_jury"
    out = nxt(root, by=BY)
    assert "suspended: cap" in line_for(root, S), line_for(root, S)
    assert "juries used: 4" in out and "subagent runs used: 7" in out and "@nio:" not in out, out
    assert kinds(root)[-1] == "suspend"
    print("ok")


def stuck_effort():
    """TC-46's effort: auto, at tasking, AC-2 left with no task (TC-46 names AC-4, which the fixture spec lacks)."""
    root = effort("tasking")
    auto_on(root, "tasking")
    text = (FIXTURES / "tasks/tasks.md").read_text().replace("checkout-refunds", S)
    (root / ".nio/specs" / S / "tasks.md").write_text(
        text.replace("- Serves: AC-2\n", "- Serves: AC-1\n").replace("- Serves: AC-1, AC-2\n", "- Serves: AC-1\n"))
    return root


def test_ac46_stuck():
    """TC-46: three identical failures in auto mode suspend the effort as stuck; a fourth done is refused."""
    root = stuck_effort()
    for _ in range(3):
        assert flow.done(root, "tasking", S, by=BY)[0] == 1
    fails = [x for x in lines_of(root) if x["kind"] == "fail"]
    assert len(fails) == 3 and len({(x["from"], x["evidence"]["output"]) for x in fails}) == 1, fails
    assert "AC-2" in fails[0]["evidence"]["output_text"] and kinds(root)[-1] == "suspend"
    assert "suspended: stuck" in line_for(root, S)
    n = count(root)
    code, out = flow.done(root, "tasking", S, by=BY)
    assert code == 1 and "@nio:" not in "\n".join(out) and count(root) == n, out
    print("ok")
    return root


def test_ac47_not_stuck():
    """TC-47: three different failures don't suspend the effort."""
    root = effort("tasking")
    auto_on(root, "tasking")
    tasks_md = root / ".nio/specs" / S / "tasks.md"
    text = (FIXTURES / "tasks/tasks.md").read_text().replace("checkout-refunds", S)
    for serves in ("- Serves: AC-1\n", "- Serves: AC-2\n", "- Serves: AC-1, AC-2\n"):
        text = text.replace(serves, "", 1)
        tasks_md.write_text(text)
        assert flow.done(root, "tasking", S, by=BY)[0] == 1
    fails = [x for x in lines_of(root) if x["kind"] == "fail"]
    assert len(fails) == 3 and len({x["evidence"]["output"] for x in fails}) == 3, fails
    assert " · working · " in line_for(root, S), line_for(root, S)
    print("ok")


def test_fail_hash_ignores_dates_and_paths():
    """CT-8 (FR-41): the failure hash drops ISO dates and times and every path, so a repeat hashes the same."""
    root = Path("/tmp/x")
    a = flow.fail_hash(root, ["ERROR /tmp/x/.nio/specs/a/tasks.md: AC-2 has no task (2026-10-20T10:00:00)"])
    b = flow.fail_hash(root, ["ERROR /tmp/x/.nio/specs/b/tasks.md: AC-2 has no task (2026-10-21 11:30)"])
    assert a == b != flow.fail_hash(root, ["ERROR tasks.md: AC-1 has no task"])
    print("ok")


def test_ac48_auto_change_pause():
    """TC-48: an auto effort waits before a change moves it back; start resumes it, naming the change, and moves it."""
    root = effort("tasking")
    auto_on(root, "tasking")
    cid = change_record(root, f".nio/specs/{S}/plan.md")
    out = nxt(root)
    assert "waiting_for_human" in out and cid in out and "state: tasking" in out and "@nio:" not in out, out
    assert "back" not in kinds(root)
    assert flow.start(root, S, by=BY) == (0, [f"resumed {S} at planning"])
    resume, back = lines_of(root)[-2:]
    assert (resume["kind"], resume["change"]) == ("resume", cid) and cid in resume["reason"], resume
    assert (back["kind"], back["to"], back["change"]) == ("back", "planning", cid), back
    assert "state: planning" in nxt(root)
    print("ok")


def test_ac49_suspended_shape():
    """TC-49: a suspended effort speaks in the human's shape; start resumes it to its work."""
    root = test_ac46_stuck()
    lines = nxt(root).splitlines()
    assert lines[0] == "Run this command to resume" and f"nio flow start {S} --by human" in lines, lines
    assert lines[-1].startswith("Refs:") and "@nio:" not in "\n".join(lines), lines
    assert flow.start(root, S, by=BY)[0] == 0
    assert "skill: @nio:tasks" in nxt(root)
    print("ok")


def test_ac50_manual_no_pause():
    """TC-50: the stop list ignores a manual effort."""
    root = round_cap(auto=False)
    out = nxt(root, by=BY)
    assert "skill: @nio:jury" in out and "pause" not in kinds(root), out
    print("ok")


def test_ac54_risk_waits():
    """TC-54: an auto effort whose spec carries a money risk waits for the human's --commit at the gate."""
    root = effort("spec_jury", risk="[money]")
    approve(root, S, "spec", commit=False)
    auto_on(root, "spec_jury")
    head = git(root, "rev-parse", "HEAD")
    code, out = flow.done(root, "spec_jury", S, by=BY)
    assert git(root, "rev-parse", "HEAD") == head and "nio flow done spec_jury --commit" in "\n".join(out), out
    assert "waiting_for_human: approve spec" in line_for(root, S)
    print("ok")


def test_ac60_round_one():
    """TC-60: a first round with an open finding doesn't pause an auto effort."""
    root = effort("spec_jury")
    auto_on(root, "spec_jury")
    ledger(root, "spec", round=1, outcome="rejected", findings=[finding("J-1")], **CHANGED)
    out = nxt(root, by=BY)
    assert "skill: @nio:jury" in out and "pause" not in kinds(root), out
    print("ok")


def test_round_pause_not_again_after_resume():
    """CT-8 (FR-39): once start resumes a round-cap pause, the same gate and round don't pause the effort again."""
    root = round_cap()
    nxt(root, by=BY)
    flow.start(root, S, by=BY)
    out = nxt(root, by=BY)
    assert "skill: @nio:jury" in out and kinds(root)[-2:] == ["pause", "resume"], (out, kinds(root))
    print("ok")


# --- review fixes ---

def test_done_stop_keeps_what_was_recorded_meanwhile():
    """Review 1: done's stop-list path reloads inside the lock, so a park recorded between its read and its lock stands."""
    import contextlib
    root = round_cap()
    real = flow.lock

    @contextlib.contextmanager
    def racing(root_, slug_):  # another writer parks the effort just before done gets the lock
        with real(root_, slug_):
            st = flow.load(root_, slug_)[0]
            flow.record(root_, slug_, [{"kind": "park", "from": "plan_jury", "to": "plan_jury", "reason": "meanwhile"}],
                        {**st, "pause": {"kind": "parked", "why": "meanwhile"}}, flow.who("human"), "")
            yield
    flow.lock = racing
    try:
        code, out = flow.done(root, "plan_jury", S, by=BY)
    finally:
        flow.lock = real
    assert code == 1 and flow.load(root, S)[0]["pause"] == {"kind": "parked", "why": "meanwhile"}, out
    assert kinds(root)[-1] == "park", kinds(root)
    print("ok")


def test_commit_is_the_humans():
    """Review 2 (FR-18, FR-48, FR-51): --commit from an agent is refused, auto off or on a risky spec; nothing recorded."""
    for risk, auto in (("[]", False), ("[money]", True)):
        root = effort("spec_jury", risk=risk)
        approve(root, S, "spec", commit=False)
        auto_on(root, "spec_jury") if auto else flow.start(root, S, by=BY)
        head, n = git(root, "rev-parse", "HEAD"), count(root)
        try:
            flow.done(root, "spec_jury", S, commit=True, by=BY)
            raise AssertionError((risk, auto))
        except ValueError as e:
            assert "--by human" in str(e), e
        assert git(root, "rev-parse", "HEAD") == head and count(root) == n
    print("ok")


def test_status_shows_a_damaged_ledger_broken():
    """Review 3 (FR-60): a ledger that isn't JSON shows its effort as broken; the others are listed as usual."""
    root = effort("spec_jury")
    other = "2026-10-21-refunds"
    effort("planning", slug=other, root=root)
    (root / ".nio/specs" / S / "jury").mkdir()
    (root / ".nio/specs" / S / "jury/spec.json").write_text("{bad")
    rows = flow.status(root)[1]
    assert any(x.startswith(f"{S} · broken: ") for x in rows) and any(x.startswith(other + " · ") for x in rows), rows
    print("ok")


def test_pick_skips_a_broken_effort():
    """Review 4: with no slug, a broken effort is skipped; with only broken ones left, the refusal names them."""
    root = effort("planning")
    other = "2026-10-21-refunds"
    effort("planning", slug=other, root=root)
    history(root, other, {"kind": "start", "from": None, "to": "planning", "at": at(9)})
    history(root, S, {"kind": "start", "from": None, "to": "planning", "at": at(11)})
    bad_key(root)  # S has the newest line, but is broken
    assert flow.pick(root) == other
    (root / ".nio/specs" / other / "history.jsonl").unlink()
    (root / ".nio/specs" / other / "state.json").unlink()
    try:
        flow.pick(root)
        raise AssertionError("picked a broken effort")
    except ValueError as e:
        assert "no current effort" in str(e) and f"broken: {S}: state.json, key stage" in str(e), e
    print("ok")


def test_crlf_file_is_not_an_edit():
    """Review 5: an override's blobs are hashed as the change scan hashes the file, so CRLF doesn't read as edited."""
    root = effort("spec_jury")
    spec = root / ".nio/specs" / S / "spec.md"
    spec.write_bytes(spec.read_bytes().replace(b"\n", b"\r\n"))
    assert jury.check(root, S, "spec", record=True, human="pack bug")[0] == "human"
    flow.start(root, S, by=BY)
    assert flow.done(root, "spec_jury", S, by=BY)[0] == 0
    assert flow.changes(root, S, flow.load(root, S)[1]) == [] and "state: planning" in nxt(root)
    print("ok")


def test_catch_up_at_a_gate_already_committed():
    """Review 6 (FR-17, FR-47): a gate whose approval commit for this round exists is recorded without --commit and
    without a second approval commit."""
    root = effort("spec_jury")
    flow.start(root, S, by=BY)  # history stands at spec_jury
    approve(root, S, "spec")  # approved and committed by hand meanwhile
    head, n = git(root, "rev-parse", "HEAD"), count(root)
    code, out = flow.done(root, "spec_jury", S, by=BY)
    assert code == 0 and out[0] == f"moved {S}: spec_jury → planning", out
    assert [x["kind"] for x in lines_of(root)[n:]] == ["pass", "skip"] and git(root, "rev-parse", "HEAD") == head
    print("ok")


def test_takeover_leaves_a_new_holders_lock():
    """Review 7 (CT-3): if the lock renamed for a takeover isn't the stale one judged, it is put back and Busy raised."""
    root = effort("drafting")
    path = root / ".nio/specs" / S / "flow.lock"
    (root / ".nio/specs" / S / ".gitignore").write_text("flow.lock*\nstate.json.new\n")
    live = old_lock(root, os.getpid(), socket.gethostname())  # a live holder's lock (old mtime)
    before = live.read_bytes()
    real, calls = flow.holder, []

    def judged_then_real(p):  # the first read saw a stale lock; by the rename a new holder had replaced it
        calls.append(p)
        return (999999, socket.gethostname(), "stale") if len(calls) == 1 else real(p)
    flow.holder = judged_then_real
    try:
        refused(root)
    finally:
        flow.holder = real
    assert path.read_bytes() == before and sorted(p.name for p in path.parent.glob("flow.lock*")) == ["flow.lock"]
    print("ok")


def test_closure_is_read_from_the_standing():
    """Review 8 (CT-5): a closed gate is `closed` whatever words the stage's own check uses for it."""
    from nio import tasks
    root = effort("tasks_jury")
    assert jury.check(root, S, "tasks", record=True, human="shipped by hand")[0] == "human"
    real = tasks.approved
    tasks.approved = lambda root_, slug_: (True, "gate closed by the human")
    try:
        result, output, _ = flow.guard(root, S, "tasks_jury")
    finally:
        tasks.approved = real
    assert (result, output) == ("closed", ["shipped by hand"]), (result, output)
    print("ok")


def test_planned_and_plan_files_come_from_their_modules():
    """Review 9: the Fixes stripping lives in jury.planned, which jury.artefact uses; the plan files are plan.FILES."""
    from nio import plan
    text = "## E-1 x\n\n### T-1 a\n\n#### Fixes\n\n### T-4 b\n"
    assert jury.planned("tasks.md", text) == "## E-1 x\n\n### T-1 a\n" and jury.planned("plan.md", text) == text
    assert flow.planned("tasks.md", text) == jury.planned("tasks.md", text) and not hasattr(flow, "PLAN_FILES")
    assert [f for f, g in flow.JUDGED_BY.items() if g == "plan_jury"] == list(plan.FILES)
    root = effort("tasks_jury")
    real = jury.planned
    jury.planned = lambda name, text_: "planned:" + name
    try:
        assert "planned:tasks.md" in jury.artefact(root, S, "tasks")
    finally:
        jury.planned = real
    print("ok")


# --- the task machine's refusals (tasks-stage AC-56, AC-57, AC-36), now that implement builds it ---

def test_ac56_the_change_is_refused():
    """T-1 claimed, the stage set to done: refused; it stays claimed and the message names red, green and review."""
    root = effort("implementing")
    history(root, S, {**task_line("claim", "T-1"), "state": {"claims": {"task": "T-1"}}})
    code, out = cli(root, "done", "implementing", S)
    assert code == 1 and "T-1 is claimed: needs red, green and review" in out, out
    assert flow.load(root, S)[1][-1]["kind"] == "claim" and flow.load(root, S)[0]["claims"] == {"task": "T-1"}
    print("ok")


def test_ac57_the_claim_is_refused_and_given_t_5_is_al():
    """A claim while T-2 waits on T-1 is refused (`waits on`); a claim while T-1 is claimed is refused (`is claimed`).
    The CLI picks the task, so neither names the one asked for."""
    root = effort("implementing")
    history(root, S, task_line("blocked", "T-1", cause="attempts"))
    code, out = cli(root, "claim", S, "--by", BY)
    assert code == 1 and "no ready task; T-2 waits on T-1" in out, out
    history(root, S, {**task_line("unblock", "T-1"), "state": {}}, {**task_line("claim", "T-1"), "state": {"claims": {"task": "T-1"}}})
    n = len(flow.load(root, S)[1])
    code, out = cli(root, "claim", S, "--by", BY)
    assert code == 1 and "T-1 is claimed" in out and len(flow.load(root, S)[1]) == n, out
    print("ok")


def test_ac36_the_change_is_refused():
    """T-1 green, the stage set to done without a review: refused; it stays green and the message names the review."""
    root = effort("implementing")
    history(root, S, *[task_line(k, "T-1") for k in ("claim", "red", "green")])
    code, out = cli(root, "done", "implementing", S)
    assert code == 1 and "T-1 is green: needs its review" in out, out
    from nio import implement
    assert implement.status(root, S, flow.load(root, S)[1])["T-1"] == "green"
    print("ok")


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
