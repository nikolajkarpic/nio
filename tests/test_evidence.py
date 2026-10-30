"""Self-check for the implementation jury's evidence pieces (2026-10-27-implementation-jury). Run: uv run python tests/test_evidence.py"""
import importlib
import importlib.util
import json
import os
import re
import tempfile
import time
from pathlib import Path

from test_tasks import git


def evidence():
    """The module under test, looked up here so its absence fails on an assertion, not on an import error."""
    assert importlib.util.find_spec("nio.evidence"), "src/nio/evidence.py doesn't exist yet"
    return importlib.import_module("nio.evidence")


def in_copy(*args):
    return evidence().in_copy(*args)


# --- T-1: the throwaway copy (CT-2) ---

BIG = b"".join(b"%09d\n" % i for i in range(100_000))  # 1 MB exactly; every position differs, so a wrong cut shows
ACCENTS = ("é" * 500_000).encode()  # 1 MB in 500,000 characters: `cut N bytes` counts bytes
# what TC-41 names: it reports that it ran, so a check on an untouched repo can't pass by the attack never running
ATTACK = ("pwd; rm -rf ./*; test ! -e app.txt && echo deleted; git branch -D feature; git config nio.secret hacked; "
          "git update-ref refs/heads/main HEAD~1; git push origin HEAD:refs/heads/pwned; "
          "git push --force origin HEAD~1:refs/heads/main; rm -rf .git; echo attacked")


def human():
    """A repo as the human has it: two commits, a branch, a local setting, a hook, and an uncommitted change and file.
    (root, first commit, last commit, the file the hook would write)."""
    root = Path(tempfile.mkdtemp(prefix="nio-human-"))
    hooked = Path(tempfile.mkdtemp()) / "hook-ran"
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "t")
    git(root, "config", "user.email", "t@t")
    git(root, "config", "nio.secret", "kept")
    (root / "app.txt").write_text("one\n")
    (root / "big.bin").write_bytes(BIG)
    (root / "accents.txt").write_bytes(ACCENTS)
    (root / "medium.bin").write_bytes(BIG[:150_000])
    git(root, "add", "-A")
    git(root, "commit", "-qm", "first")
    first = git(root, "rev-parse", "HEAD").strip()
    (root / "app.txt").write_text("two\n")
    git(root, "commit", "-qam", "second")
    last = git(root, "rev-parse", "HEAD").strip()
    git(root, "branch", "feature")
    hook = root / ".git/hooks/post-checkout"
    hook.write_text(f"#!/bin/sh\ntouch {hooked}\n")
    hook.chmod(0o755)
    (root / "app.txt").write_text("uncommitted\n")
    (root / "notes.txt").write_text("untracked\n")
    return root, first, last, hooked


JURY = r"\.nio/specs/[^/]+/jury/\S*"  # the gate's own ledger isn't the human's tree (C-261030-aemp)


def snapshot(root):
    """All TC-41 says must not change: the tree byte for byte, the refs, the config, the worktrees, and git's status."""
    tree = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(root).parts and p.relative_to(root).parts[:2] != (".nio", "runs")
            and not re.fullmatch(JURY, p.relative_to(root).as_posix())}
    status = [x for x in git(root, "status", "--porcelain").splitlines() if not re.fullmatch(rf"\s*\S+\s+{JURY}", x)]
    return {"tree": tree, "refs": git(root, "for-each-ref"), "head": (root / ".git/HEAD").read_text(),
            "config": (root / ".git/config").read_text(), "worktrees": git(root, "worktree", "list", "--porcelain"),
            "status": status, "log": git(root, "log", "--all", "--format=%H")}


def same(root, before, what):
    now = snapshot(root)
    for key, value in before.items():
        assert now[key] == value, f"{what}: the human's {key} changed"


def is_gone(pid):
    """Whether a process has ended; a killed one may take a moment to be reaped."""
    for _ in range(40):
        try:
            os.kill(pid, 0)
            if " Z " in Path(f"/proc/{pid}/stat").read_text():
                return True
        except (ProcessLookupError, FileNotFoundError):
            return True
        time.sleep(0.05)
    return False


def test_in_copy_stops_a_never_ending_command_and_goes_on():
    root, _, last, _ = human()
    pidfile = Path(tempfile.mkdtemp()) / "pid"
    start = time.monotonic()
    # a child holds stdout open too: stopping only the shell would leave the run waiting on it
    out = in_copy(root, last, [f"sleep 60 & echo $! > {pidfile}; wait", "echo next"], 1)
    assert time.monotonic() - start < 30, "the limit didn't stop the run"
    assert out[0]["result"] == "failed", out[0]
    assert re.search(r"timed out after 1\b", out[0]["output"]), out[0]
    assert is_gone(int(pidfile.read_text())), "the command's child outlived the limit"
    assert out[1]["result"] == "passed" and "next" in out[1]["output"], out[1]
    print("ok")


def test_in_copy_runs_each_command_at_the_commit_in_its_own_clone():
    root, first, _, hooked = human()
    commands = ["cat app.txt", "git rev-parse HEAD", "git symbolic-ref -q HEAD", "git remote", "git config --get nio.secret",
                "test -e notes.txt", "pwd", "echo oops >&2; exit 3", None, "echo after"]
    out = in_copy(root, first, commands, 30)
    assert [r["command"] for r in out] == commands, out
    for r in out:
        assert set(r) == {"command", "result", "output", "cut"}, r
        assert r["cut"] == 0, r
    by = dict(zip(commands, out))
    assert by["cat app.txt"]["output"] == "one\n", "not the commit's file, or not the commit"
    assert by["git rev-parse HEAD"]["output"].strip() == first
    assert by["git symbolic-ref -q HEAD"]["result"] == "failed", "the copy isn't detached"
    assert (by["git remote"]["result"], by["git remote"]["output"].strip()) == ("passed", ""), "the copy keeps a remote"
    assert by["git config --get nio.secret"]["result"] == "failed", "the copy shares the human's config"
    assert by["test -e notes.txt"]["result"] == "failed", "the copy holds the human's untracked file"
    assert not hooked.exists(), "the human's hook ran"
    where = Path(by["pwd"]["output"].strip())
    assert root not in [where, *where.parents], f"the copy is inside the repo: {where}"
    assert not where.exists(), "the copy outlived the runs"
    assert (by["echo oops >&2; exit 3"]["result"], by["echo oops >&2; exit 3"]["output"]) == ("failed", "oops\n")
    assert by[None]["result"] == "not configured", by[None]
    assert by["echo after"]["result"] == "passed", "an unset command stopped the rest"
    print("ok")


def test_in_copy_leaves_the_human_repo_alone():
    root, _, last, hooked = human()
    before = snapshot(root)
    assert "pwned" not in before["refs"] and before["tree"]["app.txt"] == b"uncommitted\n"
    for what, command, limit in (("a normal run", ATTACK, 30), ("a timeout", f"{ATTACK}; sleep 60", 5)):
        out = in_copy(root, last, [command], limit)[0]
        assert "deleted" in out["output"] and "attacked" in out["output"], f"{what}: the attack didn't run: {out}"
        same(root, before, what)
        where = Path(out["output"].splitlines()[0])
        assert where != root and not where.exists(), f"{what}: the copy outlived the run: {where}"
    assert not hooked.exists(), "the human's hook ran"
    assert "timed out after 5" in out["output"], out
    print("ok")


def test_in_copy_cuts_long_output_to_its_ends():
    root, _, last, _ = human()
    for name, data in (("big.bin", BIG), ("accents.txt", ACCENTS)):
        out = in_copy(root, last, [f"cat {name}"], 30)[0]
        assert out["result"] == "passed", out["result"]
        m = re.search(r"\bcut (\d+) bytes\b", out["output"])
        assert m, f"{name}: no `cut N bytes` line"
        n = int(m[1])
        assert out["cut"] == n, (out["cut"], n)
        kept = (len(data) - n) // 2
        assert kept in (100_000, 102_400), f"{name}: {n} bytes cut leaves {kept} at each end, not 100 KB"
        text = data.decode()
        size = len(out["output"].encode())
        assert size < 2 * kept + 200, f"{name}: {size} bytes kept"
        assert out["output"].startswith(text[:len(data[:kept].decode())]), f"{name}: the first 100 KB are not kept"
        assert out["output"].endswith(text[-len(data[-kept:].decode()):]), f"{name}: the last 100 KB are not kept"
    out = in_copy(root, last, ["cat medium.bin"], 30)[0]
    assert (out["cut"], out["output"]) == (0, BIG[:150_000].decode()), "output under the limit was cut"
    print("ok")


def test_in_copy_runs_nothing_when_the_clone_fails():
    root, _, last, _ = human()
    mark = Path(tempfile.mkdtemp()) / "ran"
    for what, where, commit in (("not a repo", Path(tempfile.mkdtemp()), last), ("no such commit", root, "0" * 40)):
        try:
            in_copy(where, commit, [f"touch {mark}"], 30)
        except ValueError as e:
            assert "fatal" in str(e), f"{what}: git's error isn't named: {e}"
        else:
            raise AssertionError(f"{what}: no ValueError")
        assert not mark.exists(), f"{what}: a command ran"
    print("ok")


# --- T-1: the results file (CT-7) ---

SHAPE = {"commit", "tests", "checks", "attacks", "journeys", "hints", "requests", "evidence"}


def test_results_are_read_and_written_under_the_run():
    e = evidence()
    assert e.RESULTS == "results.json", e.RESULTS
    root = Path(tempfile.mkdtemp())
    empty = e.load(root, "R-1")
    assert set(empty) == SHAPE and not any(empty.values()), empty
    assert not (root / ".nio").exists(), "reading wrote something"
    results = {**empty, "commit": "abc", "tests": [{"name": "t", "file": "tests/t.py", "line": 3, "result": "passed"}],
               "checks": [{"command": "lint", "result": "not configured", "output": "", "cut": 0}],
               "requests": [{"tc": "TC-1"}], "evidence": [{"ac": "AC-1", "file": "tests/t.py", "line": 3, "result": "passed"}]}
    e.save(root, "R-1", results)
    assert json.loads((root / ".nio/runs/R-1/results.json").read_text()) == results
    assert e.load(root, "R-1") == results
    assert not any(e.load(root, "R-2").values()), "a run read another run's results"
    print("ok")


def test_results_keep_a_cut_run_at_about_200_kb():
    e = evidence()
    root, _, last, _ = human()
    out = in_copy(root, last, ["cat big.bin"], 30)[0]
    e.save(root, "R-1", {**e.load(root, "R-1"), "commit": last, "checks": [out]})
    assert e.load(root, "R-1")["checks"] == [out]
    size = (root / ".nio/runs/R-1/results.json").stat().st_size
    assert 200_000 <= size < 250_000, f"{size} bytes on disk"  # JSON writes each newline as two characters
    print("ok")


# --- T-3: the gate runs only on a finished epic (CT-1, AC-2, AC-3) ---

EPICS = """---
slug: s
retired: []
---
# Tasks: s

## E-1 First (Foundation)

### T-1 One
- Files: `a.py`
- Serves: AC-1
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: cheap: x
- Effort: low

### T-2 Two
- Files: `b.py`
- Serves: AC-2
- Test: TC-2
- Depends on: T-1
- Parallel: no
- Tier: cheap: x
- Effort: low
"""


def epic_repo(finished):
    """A repo whose spec `s` has epic E-1 of T-1 and T-2, with the tasks in `finished` done in its history."""
    root = Path(tempfile.mkdtemp(prefix="nio-epic-"))
    git(root, "init", "-q", "-b", "main")
    d = root / ".nio/specs/s"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text(EPICS)
    (root / ".nio/config.json").write_text("{}")
    lines = [{"kind": k, "from": "implementing", "to": "implementing", "end": True, "evidence": {"task": t, "commit": "c", "passed": True}}
             for t in finished for k in ("claim", "red", "green", "review", "task_done")]
    (d / "history.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines))
    return root


def refuses(root, gate, *words):
    """The gate name is refused by the function and by the CLI, naming `words`, and no ledger is written."""
    import subprocess
    import sys
    from nio import jury
    assert hasattr(jury, "epic_gate"), "jury.epic_gate doesn't exist yet"
    try:
        jury.epic_gate(root, "s", gate)
        raise AssertionError("epic_gate accepted " + gate)
    except ValueError as e:
        assert all(w in str(e) for w in words), f"{e!r} lacks {words}"
    out = subprocess.run([sys.executable, "-c", "from nio.cli import main; main()", "jury", "plan", "s", gate],
                         cwd=root, capture_output=True, text=True)
    assert out.returncode != 0 and "invalid choice" not in out.stderr, out.stderr
    assert all(w in out.stderr for w in words), out.stderr
    assert not (root / ".nio/specs/s/jury").exists(), "a ledger was written"


def test_it_refuses():
    from nio import jury
    assert hasattr(jury, "epic_gate"), "jury.epic_gate doesn't exist yet"
    assert jury.epic_gate(epic_repo(["T-1", "T-2"]), "s", "implementation-E-1") == "E-1"
    refuses(epic_repo(["T-1"]), "implementation-E-1", "T-2")
    print("ok")


def test_it_refuses_again():
    root = epic_repo(["T-1", "T-2"])
    refuses(root, "implementation", "epic")
    refuses(root, "implementation-E-9", "epic")
    print("ok")


# --- T-5: the gate collects evidence (CT-3, CT-2, CT-7) ---

MISUSE = """---
slug: s
retired: []
---
# Tests: s

## Misuse tests

### TC-1 The agent attacks (UJ-1 misuse; integration) [derived: FR-2]
- File: `tests/test_attack.py:AttackTest.test_refused` (new)
- Covers: CT-1
- Setup: x
- Action: y
- Assert: z
"""
QUICKSTART = """---
slug: s
retired: []
---
# Quickstart: s

## Prerequisites
- none

## Scenarios

### QS-1 Run it (UJ-1; auto) [derived: UJ-1]

1. `echo journey ran`
   Expected:
   ```
   contains: journey ran
   ```
- Pass when: every step matched

### QS-2 Look at it (UJ-2; manual) [derived: UJ-2]

1. `echo never run`
   Expected:
   ```
   never run
   ```
- Pass when: a person sees it
"""
ATTACK_TEST = "import unittest\n\n\nclass AttackTest(unittest.TestCase):\n    def test_refused(self):\n        print('MISUSE-RAN')\n        self.assertTrue(False)\n"
TYPECHECK = 'echo "b.py:3: error: Incompatible types" >&2; exit 1'


def gate_repo(lint=None, typecheck=None, timeout=None, remote=False):
    """A finished epic E-1 whose commits are `T-1: One` and `T-2: Two`, with a misuse test in tests.md, an auto and a
    manual scenario in quickstart.md, and the given checks in the config. (root, last commit); with `remote`, also the
    bare repo `origin` points at."""
    root = epic_repo(["T-1", "T-2"])
    git(root, "config", "user.name", "t")
    git(root, "config", "user.email", "t@t")
    tests = {"suite": "python3 -m unittest discover -s tests -t .", "lint": lint, "typecheck": typecheck}
    cfg = {"tests": {k: v for k, v in tests.items() if v}, "jury": {"run_timeout": timeout} if timeout else {}}
    (root / ".nio/config.json").write_text(json.dumps(cfg))
    (root / ".gitignore").write_text(".nio/runs/\n")
    (root / ".nio/specs/s/tests.md").write_text(MISUSE)
    (root / ".nio/specs/s/quickstart.md").write_text(QUICKSTART)
    (root / "tests").mkdir()
    (root / "tests/test_attack.py").write_text(ATTACK_TEST)
    (root / "app.txt").write_text("one\n")
    (root / "big.bin").write_bytes(BIG)
    (root / "a.py").write_text("a = 1\n")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "T-1: One")
    (root / "b.py").write_text("b = 1\n# line 3\n")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "T-2: Two")
    bare = Path(tempfile.mkdtemp(prefix="nio-origin-"))
    if remote:
        git(bare, "init", "-q", "--bare", "-b", "main")
        git(root, "remote", "add", "origin", str(bare))
        git(root, "push", "-q", "origin", "main")
    return (root, git(root, "rev-parse", "HEAD").strip(), bare) if remote else (root, git(root, "rev-parse", "HEAD").strip())


def start(root, run="R-1"):
    """The gate starts on epic E-1 of spec `s`; the run's results."""
    e = evidence()
    assert hasattr(e, "collect"), "evidence.collect doesn't exist yet"
    e.collect(root, "s", "E-1", run)
    return e.load(root, run)


def entry(results, kind, command):
    found = [x for x in results[kind] if x["command"] == command]
    assert len(found) == 1, f"{kind} holds {len(found)} entries for {command!r}: {results[kind]}"
    return found[0]


def test_the_results_record_the_failed_check_and_its_output():
    import subprocess
    import sys
    root, last = gate_repo(typecheck=TYPECHECK)
    out = subprocess.run([sys.executable, "-c", "from nio.cli import main; main()", "jury", "evidence", "s", "E-1", "--run", "R-1"],
                         cwd=root, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "results.json" in out.stdout and "not configured" in out.stdout, out.stdout  # the path; lint is unset
    results = evidence().load(root, "R-1")
    assert results["commit"] == last, results["commit"]
    failed = entry(results, "checks", TYPECHECK)
    assert failed["result"] == "failed" and "b.py:3" in failed["output"], failed
    assert any(c["result"] == "not configured" for c in results["checks"]), results["checks"]
    print("ok")


def test_both_are_run_and_their_results_are_recorded():
    root, _ = gate_repo()
    results = start(root)
    assert len(results["attacks"]) == 1, results["attacks"]  # tests.md's one misuse test
    attack = results["attacks"][0]
    assert attack["result"] == "failed" and "MISUSE-RAN" in attack["output"], attack
    assert len(results["journeys"]) == 1, results["journeys"]  # the auto scenario; the manual one is for the human
    journey = results["journeys"][0]
    assert journey["result"] == "passed" and "journey ran" in journey["output"], journey
    assert "never run" not in json.dumps(results), "a manual scenario was run"
    print("ok")


def test_it_is_stopped_at_the_time_limit_recorded_as():
    root, _ = gate_repo(lint="sleep 60", typecheck="echo next", timeout=1)
    began = time.monotonic()
    results = start(root)
    assert time.monotonic() - began < 45, "the limit didn't stop the run"
    stuck = entry(results, "checks", "sleep 60")
    assert stuck["result"] == "failed" and re.search(r"timed out after 1\b", stuck["output"]), stuck
    nxt = entry(results, "checks", "echo next")
    assert nxt["result"] == "passed" and "next" in nxt["output"], nxt
    assert (root / ".nio/runs/R-1/results.json").exists(), "the gate didn't reach its results"
    print("ok")


def test_only_the_throwaway_copy_is_touched():
    for what, command, timeout in (("a normal run", ATTACK, None), ("a timeout", f"{ATTACK}; sleep 60", 3)):
        root, _, bare = gate_repo(lint=command, timeout=timeout, remote=True)
        before, origin = snapshot(root), git(bare, "for-each-ref")
        assert before["tree"]["app.txt"] == b"one\n" and "pwned" not in origin
        out = entry(start(root), "checks", command)
        assert "deleted" in out["output"] and "attacked" in out["output"], f"{what}: the attack didn't run: {out}"
        same(root, before, what)
        assert git(bare, "for-each-ref") == origin, f"{what}: origin changed"
        where = Path(out["output"].splitlines()[0])
        assert where != root and not where.exists(), f"{what}: the copy outlived the run: {where}"
    assert out["result"] == "failed" and "timed out after 3" in out["output"], out
    print("ok")


def test_the_result_holds_its_first_and_last_100_kb():
    e = evidence()
    text = BIG.decode()
    shown, n = e.cut(text)
    assert n == 800_000 and "cut 800000 bytes" in shown, (n, shown[100_000:100_050])
    assert shown.startswith(text[:100_000]) and shown.endswith(text[-100_000:]), "the ends are not kept"
    root, _ = gate_repo(lint="cat big.bin")
    results = start(root)
    out = entry(results, "checks", "cat big.bin")
    assert out["cut"] == 800_000 and "cut 800000 bytes" in out["output"], out["cut"]
    assert out["output"].startswith(text[:100_000]) and out["output"].endswith(text[-100_000:]), "the ends are not kept"
    size = (root / ".nio/runs/R-1/results.json").stat().st_size
    assert 200_000 <= size < 260_000, f"{size} bytes on disk"
    print("ok")


# --- T-6: phantom completion (CT-4, AC-7, AC-8, AC-9) ---

def phantom_repo(before, epic):
    """A repo with `before` ({path: text}) committed first, then one commit per `epic` entry (task id, {path: text}) as
    `T-n: work`. (root, base, head): base is the parent of the first T-n commit, head the last."""
    root = Path(tempfile.mkdtemp(prefix="nio-phantom-"))
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "t")
    git(root, "config", "user.email", "t@t")

    def commit(files, subject):
        for name, text in files.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(text)
        git(root, "add", "-A")
        git(root, "commit", "-q", "--allow-empty", "-m", subject)

    commit(before, "before")
    base = git(root, "rev-parse", "HEAD").strip()
    for tid, files in epic:
        commit(files, f"{tid}: work")
    return root, base, git(root, "rev-parse", "HEAD").strip()


def task(tid, *files, serves=("AC-1",)):
    return {"id": tid, "title": "t", "epic": "E-1", "fix": False, "deps": [], "files": list(files), "serves": list(serves),
            "tests": [], "tier": "cheap", "effort": "low", "mode": "split"}


def phantoms(root, tasks, base, head):
    e = evidence()
    assert hasattr(e, "phantoms"), "evidence.phantoms doesn't exist yet"
    found = e.phantoms(root, tasks, base, head)
    for f in found:
        assert f["severity"] == "major", f
    return found


def naming(found, *words):
    return [f for f in found if all(w in json.dumps(f) for w in words)]


def test_the_task_is_flagged_as_phantom_completion_despite_its_status():
    # T-1's commit exists and its work is real, but it also names src/gone.py, which was never written
    root, base, head = phantom_repo({}, [("T-1", {"src/real.py": "def real():\n    return 1\n\n\nreal()\n"})])
    found = phantoms(root, [task("T-1", "src/real.py", "src/gone.py")], base, head)
    assert len(naming(found, "T-1", "src/gone.py")) == 1, found
    assert not naming(found, "src/real.py"), found
    print("ok")


def test_it_is_flagged():
    # src/old.py exists, but no commit of the epic touched it
    root, base, head = phantom_repo({"src/old.py": "x = 1\n"}, [("T-1", {"src/new.py": "y = 2\n"})])
    found = phantoms(root, [task("T-1", "src/old.py", "src/new.py")], base, head)
    assert len(naming(found, "T-1", "src/old.py")) == 1, found
    assert not naming(found, "src/new.py"), found
    print("ok")


def test_it_is_flagged_as_dead_code():
    code = "def used_one():\n    return 1\n\n\ndef orphan_helper():\n    return 2\n"
    caller = "from mod import used_one\n\nprint(used_one())\n"
    root, base, head = phantom_repo({}, [("T-1", {"src/mod.py": code, "src/caller.py": caller})])
    found = phantoms(root, [task("T-1", "src/mod.py", "src/caller.py")], base, head)
    assert len(naming(found, "orphan_helper", "src/mod.py")) == 1, found
    assert not naming(found, "used_one"), found
    assert len(found) == 1, found
    print("ok")


# --- T-7: test tampering (CT-6, AC-11, AC-12) ---

def tampering(root, base, head):
    e = evidence()
    assert hasattr(e, "tampering"), "evidence.tampering doesn't exist yet"
    found = e.tampering(root, base, head)
    for f in found:
        assert f["severity"] == "major", f
    return found


def test_it_is_flagged_as_test_tampering():
    tests = "def test_keeps():\n    assert 1\n\n\ndef test_doomed():\n    assert 2\n"
    root, base, head = phantom_repo({"tests/test_app.py": tests}, [("T-1", {"tests/test_app.py": tests.split("\n\n\n")[0] + "\n"})])
    found = tampering(root, base, head)
    assert len(naming(found, "tampering", "test_doomed")) == 1, found
    assert not naming(found, "test_keeps"), found
    print("ok")


def test_it_is_flagged_as_test_tampering_again():
    tests = "def test_keeps():\n    assert 1\n\n\ndef test_shaky():\n    assert 2\n"
    skipped = tests.replace("def test_shaky", "@pytest.mark.skip\ndef test_shaky")
    root, base, head = phantom_repo({"tests/test_app.py": tests}, [("T-1", {"tests/test_app.py": skipped})])
    found = tampering(root, base, head)
    assert len(naming(found, "tampering", "test_shaky")) == 1, found
    assert not naming(found, "test_keeps"), found
    print("ok")


# --- T-8: hints (CT-5, AC-10, AC-16) ---

def hints(root, base, head):
    e = evidence()
    assert hasattr(e, "hints"), "evidence.hints doesn't exist yet"
    found = e.hints(root, base, head)
    for h in found:
        assert {"kind", "file", "name", "line", "interpretive"} <= set(h), h
        assert "severity" not in h, f"a hint is not a ledger finding: {h}"
    return found


def test_it_is_flagged_as_a_possible_stub_marked_interpretive():
    src = "def hollow():\n    pass\n\n\ndef todo_only():\n    # TODO\n    ...\n\n\ndef real():\n    return 1\n"
    root, base, head = phantom_repo({}, [("T-1", {"src/mod.py": src, "src/use.py": "hollow(); todo_only(); real()\n"})])
    found = hints(root, base, head)
    for name in ("hollow", "todo_only"):
        mine = naming(found, name)
        assert len(mine) == 1 and mine[0]["interpretive"] is True and mine[0]["file"] == "src/mod.py", found
    assert not naming(found, "real"), found
    # the gate starts: every lens's pack carries the hint, marked interpretive, and the ledger holds no finding for it
    root = pack_repo({"src/mod.py": src, "src/use.py": "hollow(); todo_only(); real()\n"})
    start(root)
    for lens in PACK_LENSES:
        text = pack(root, lens)
        for name in ("hollow", "todo_only"):
            assert has_line(text, name, "interpretive"), f"{lens}: no interpretive hint naming {name}:\n{text}"
        assert not has_line(text, "real", "interpretive"), f"{lens}: a real function is hinted"
    for name in ("hollow", "todo_only"):
        assert not naming(gate_findings(root), name), f"{name} is in the ledger: {gate_findings(root)}"
    print("ok")


def test_it_is_flagged_not_passed():
    # the only hit for `handler` outside its definition is a string, as with a dynamic call
    root, base, head = phantom_repo({}, [("T-1", {"src/mod.py": "def handler():\n    return 1\n",
                                                  "src/use.py": 'import mod\ngetattr(mod, "handler")()\n'})])
    found = naming(hints(root, base, head), "handler")
    assert len(found) == 1 and "uncertain" in json.dumps(found[0]).lower(), found
    root = pack_repo({"src/mod.py": "def handler():\n    return 1\n", "src/use.py": 'import mod\ngetattr(mod, "handler")()\n'})
    start(root)
    for lens in PACK_LENSES:
        text = pack(root, lens)
        assert has_line(text, "handler", "uncertain"), f"{lens}: no hint naming handler and saying the check was uncertain:\n{text}"
    assert not naming(gate_findings(root), "handler"), f"handler is in the ledger: {gate_findings(root)}"
    print("ok")


def test_a_test_with_no_assertion_and_a_changed_assertion_are_flagged():
    before = "def test_weak():\n    assert 1 == 1\n\n\ndef test_firm():\n    assert 2 == 2\n"
    after = "def test_weak():\n    assert 1\n\n\ndef test_firm():\n    assert 2 == 2\n\n\ndef test_empty():\n    x = 1\n"
    root, base, head = phantom_repo({"tests/test_app.py": before}, [("T-1", {"tests/test_app.py": after})])
    found = hints(root, base, head)
    assert len(naming(found, "test_empty")) == 1, found
    assert len(naming(found, "test_weak")) == 1, found
    assert not naming(found, "test_firm"), found
    print("ok")


# --- T-9: the CLI's findings in the ledger (CT-20, TC-42, TC-62, TC-63) ---

# 500 error lines, and the command's text doesn't say "type check": only the gate can name the check
MANY_ERRORS = "seq 1 500 | sed 's/.*/b.py:&: error: Incompatible types/' >&2; exit 1"
MODEL_CLIENTS = ("anthropic", "openai", "litellm", "cohere", "mistralai", "ollama", "groq", "google.generativeai", "google.genai")
BLOCKED_COLLECT = f"""
import json, sys
tried = []
class Block:
    def find_spec(self, name, path=None, target=None):
        if any(name == m or name.startswith(m + ".") for m in {MODEL_CLIENTS!r}):
            tried.append(name)
            raise ImportError(name + " is blocked")
sys.meta_path.insert(0, Block())
from nio import evidence
evidence.collect(".", "s", "E-1", "R-1")
print(json.dumps(tried))
"""


def ledger(root):
    """The findings in the ledger of the gate on epic E-1 of spec `s`, each checked to be the CLI's own."""
    from nio import jury
    found = jury.load(root, "s", "implementation-E-1")["findings"]
    for f in found:
        assert [s["lens"] for s in f["sources"]] == ["cli"], f
        assert f["kind"] == "gap" and f["validation"] == "confirmed", f
    return found


def gate_cli(root):
    import subprocess
    import sys
    return subprocess.run([sys.executable, "-c", "from nio.cli import main; main()", "jury", "evidence", "s", "E-1", "--run", "R-1"],
                          cwd=root, capture_output=True, text=True)


def type_check_findings(found):
    return [f for f in found if re.search(r"type ?check", json.dumps(f), re.I)]


def test_a_major_finding_names_the_check_and_its_first():
    root, _ = gate_repo(lint="echo clean", typecheck=MANY_ERRORS)
    start(root)
    mine = type_check_findings(ledger(root))
    assert len(mine) == 1, ledger(root)
    assert mine[0]["severity"] == "major", mine[0]
    text = json.dumps(mine[0])
    assert "b.py:1: error: Incompatible types" in text, mine[0]
    assert "b.py:500:" not in text, f"the finding holds the whole output, not the first errors: {mine[0]}"
    assert not naming(ledger(root), "lint"), "a check that passed has a finding"
    print("ok")


def test_cli_checks_make_no_model_calls():
    import ast
    import subprocess
    import sys
    root, _ = gate_repo(typecheck=TYPECHECK)
    out = subprocess.run([sys.executable, "-c", BLOCKED_COLLECT], cwd=root, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert json.loads(out.stdout.splitlines()[-1]) == [], f"tried to import a model client: {out.stdout}"
    assert (root / ".nio/runs/R-1/results.json").exists(), "the gate didn't reach its results"
    assert len(type_check_findings(ledger(root))) == 1, "the gate didn't reach the ledger"
    imported = []
    for node in ast.walk(ast.parse(Path(evidence().__file__).read_text())):
        if isinstance(node, ast.Import):
            imported += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert not [m for m in imported if any(m == c or m.startswith(c + ".") for c in MODEL_CLIENTS)], imported
    print("ok")


def test_the_gate_refuses_an_unfinished_epic_whose_lens_would_take_done_as_proof():
    # T-2 isn't done: refused by name, and nothing is written
    root = epic_repo(["T-1"])
    out = gate_cli(root)
    assert out.returncode != 0 and "T-2" in out.stderr, (out.returncode, out.stderr)
    assert not (root / ".nio/specs/s/jury").exists(), "a ledger was written"
    assert not (root / ".nio/runs/R-1/results.json").exists(), "results were written"
    # T-2 is done in the history, but the file it names was never written
    root, _ = gate_repo()
    (root / ".nio/specs/s/tasks.md").write_text(EPICS.replace("`b.py`", "`src/gone.py`"))
    git(root, "commit", "-qa", "--amend", "--no-edit")
    out = gate_cli(root)
    assert out.returncode == 0, out.stderr
    found = ledger(root)
    mine = naming(found, "T-2", "src/gone.py")
    assert len(mine) == 1 and mine[0]["severity"] == "major", found
    assert not naming(found, "a.py"), f"T-1's file is real and in the epic's diff, whose first commit has no parent: {found}"
    print("ok")


def test_conformance_correctness_and_risk_and_rollback_cards_exist_each():
    agents = Path(__file__).resolve().parent.parent / "src/nio/agents"
    for name in ("conformance", "correctness", "risk-rollback"):
        card = agents / f"{name}.md"
        assert card.is_file(), f"{card} is missing"
        assert "\n## At implementation\n" in card.read_text(), f"{name} has no ## At implementation section"
    print("ok")


def test_each_has_an_at_implementation_section():
    agents = Path(__file__).resolve().parent.parent / "src/nio/agents"
    for name in ("security", "adversary", "consistency"):
        card = agents / f"{name}.md"
        assert card.is_file(), f"{card} is missing"
        assert "\n## At implementation\n" in card.read_text(), f"{name} has no ## At implementation section"
    print("ok")


# --- T-12: the lens plan for an epic (CT-8, CT-1, AC-1, AC-18..21) ---

CORE_TWO = {"conformance", "correctness"}
ROWS = {"auth": "security", "pii": "security", "secrets": "security", "external-input": "adversary", "multi-party": "adversary",
        "public-api": "adversary", "money": None, "migration": "risk-rollback", "data-deletion": "risk-rollback"}  # the spec's table


def lens_repo(risk=(), modify_old=False):
    """A finished epic E-1 in spec `s` flagged `risk`; T-1 and T-2 either only add files or also change old.py, which a
    commit before the epic added."""
    root = epic_repo(["T-1", "T-2"])
    git(root, "config", "user.name", "t")
    git(root, "config", "user.email", "t@t")
    (root / ".nio/specs/s/spec.md").write_text(f"---\nslug: s\nrisk: [{', '.join(risk)}]\n---\n# s\n")
    (root / "old.py").write_text("x = 1\n")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "before the epic")
    (root / "a.py").write_text("a = 1\n")
    if modify_old:
        (root / "old.py").write_text("x = 2\n")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "T-1: One")
    (root / "b.py").write_text("b = 1\n")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "T-2: Two")
    return root


def lens_plan(risk=(), modify_old=False):
    """(lens names the gate plans for epic E-1, the plan's lines, ok)."""
    root = lens_repo(risk, modify_old)
    from nio import jury
    lines, ok = jury.plan(root, "s", "implementation-E-1")
    line = next((x for x in lines if x.startswith("lenses: ")), "")
    assert line, lines
    return set(re.findall(r"([a-z][a-z-]*) \(", line)), lines, ok


def test_it_starts():
    import subprocess
    import sys
    root = epic_repo(["T-1", "T-2"])
    (root / ".nio/specs/s/spec.md").write_text("---\nslug: s\nrisk: []\n---\n# s\n")
    out = subprocess.run([sys.executable, "-c", "from nio.cli import main; main()", "jury", "plan", "s", "implementation-E-1"],
                         cwd=root, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "conformance" in out.stdout and "correctness" in out.stdout, out.stdout
    print("ok")


def test_the_plan_holds_conformance_and_correctness_only():
    names, lines, _ = lens_plan()
    assert names == CORE_TWO, (names, lines)
    print("ok")


def test_security_and_risk_and_rollback_are_added():
    names, lines, _ = lens_plan(["auth", "migration"])
    assert names == CORE_TWO | {"security", "risk-rollback"}, (names, lines)
    print("ok")


def test_the_adversary_is_added():
    names, lines, _ = lens_plan(["external-input"])
    assert names == CORE_TWO | {"adversary"}, (names, lines)
    print("ok")


def test_consistency_is_added():
    names, lines, _ = lens_plan(modify_old=True)
    assert names == CORE_TWO | {"consistency"}, (names, lines)
    print("ok")


def test_every_row_of_the_trigger_table():
    for flag, lens in ROWS.items():
        names, lines, _ = lens_plan([flag])
        assert names == CORE_TWO | ({lens} if lens else set()), (flag, names, lines)
    print("ok")


def test_secrets_brings_no_security_lens_at_the_plan_gate():
    """CT-18: the plan gate's security trigger is its own list, not the implementation table's `secrets` row."""
    from test_jury import PSLUG, plan_repo
    from nio import jury
    for risk, want in (("[secrets]", False), ("[auth]", True)):
        lines, ok = jury.plan(plan_repo(risk), PSLUG, "plan")
        line = next(x for x in lines if x.startswith("lenses: "))
        assert ("security (" in line) == want, (risk, line)
    print("ok")


# --- T-13: over the cap, the human picks (CT-8, CT-16, AC-22, AC-23) ---

GATE = "implementation-E-1"
FIVE = ["conformance", "correctness", "security", "adversary", "risk-rollback"]


def capped():
    """Epic E-1 whose plan holds the five runs in FIVE, with jury.max_runs at 4."""
    root = lens_repo(["auth", "external-input", "migration"])
    (root / ".nio/config.json").write_text('{"jury": {"max_runs": 4}}')
    return root


def test_no_lens_runs_until_the_human_picks_and_the():
    from nio import jury
    root = capped()
    lines, ok = jury.plan(root, "s", GATE)
    text = "\n".join(lines)
    assert ok, lines
    for lens in FIVE:
        assert any(re.search(rf"\b{lens}\b", x) and re.search(r"\b(cheap|medium|strong|max)\b", x) for x in lines), (lens, text)
    assert "over the cap" in text and "all" in text and "pick" in text, text
    assert "hit rate" not in text.lower() or "no hit rates" in text.lower(), text  # none are recorded yet
    out = root / ".nio/runs/R-1/jury"
    out.mkdir(parents=True)
    (out / f"{GATE}-conformance.md").write_text("# conformance\n")
    try:
        jury.collect(root, "s", GATE, "R-1")
        raise AssertionError("collect took a lens output with no pick")
    except ValueError as e:
        assert "pick" in str(e), e
    print("ok")


def test_a_pick_that_drops_a_core_lens_is_refused():
    from nio import jury
    root = capped()
    for lens in sorted(CORE_TWO):
        keep = [x for x in FIVE if x != lens][:4]
        try:
            jury.plan(root, "s", GATE, pick=",".join(keep))
            raise AssertionError("a pick without " + lens + " was taken")
        except ValueError as e:
            assert lens in str(e), e
    assert not (root / ".nio/specs/s/jury").exists(), "a refused pick wrote a ledger"
    print("ok")


def test_the_dropped_lens_is_named_in_the_verdict():
    import subprocess
    import sys
    from nio import jury
    root = capped()
    keep = ["conformance", "correctness", "security", "adversary"]
    out = subprocess.run([sys.executable, "-c", "from nio.cli import main; main()", "jury", "plan", "s", GATE,
                          "--pick", ",".join(keep)], cwd=root, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    led = jury.load(root, "s", GATE)
    assert led["picked"] == keep and led["dropped"] == ["risk-rollback"], led
    path = jury.verdict(root, led, "approved", [])
    said = [x for x in path.read_text().splitlines() if "dropped" in x.lower()]
    assert any("risk-rollback" in x for x in said), path.read_text()
    assert not any(c in x for x in said for c in CORE_TWO), said
    print("ok")


# --- T-14: a lens's pack (CT-9, CT-5, CT-10, AC-10, AC-16, AC-24, AC-25) ---

PACK_LENSES = ("conformance", "correctness", "security")  # a hint is in every lens's pack, whichever lens
PACK_SPEC = """---
slug: s
retired: []
---
# s

## Functional requirements
- **FR-1** THE SYSTEM SHALL do FR1_TEXT. [human]
- **FR-2** THE SYSTEM SHALL do FR2_TEXT. [human]

## User stories
### US-1 Story (P1) [human]
- **AC-1** Given AC1_TEXT, when it runs, then it holds. [human]
  Observable: AC1_OBSERVABLE. Level: unit.
- **AC-3** Given AC3_TEXT, when it runs, then it holds. [human]
  Observable: AC3_OBSERVABLE. Level: unit.
"""
PACK_CONTRACTS = """---
slug: s
retired: []
---
# Contracts: s

## Contracts

### CT-1 First (FR-2) [derived: FR-2]
- Binding: `src/one.py:f`
- Rules: CT1_TEXT

### CT-2 Second (FR-1) [derived: FR-1]
- Binding: `src/two.py:g`
- Rules: CT2_TEXT
"""
PACK_TASKS = """---
slug: s
retired: []
---
# Tasks: s

## E-1 First (Foundation)

### T-1 One
- Files: {files}
- Serves: AC-3, FR-2
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: cheap: x
- Effort: low

## E-2 Second (Foundation)

### T-2 Two
- Files: `src/two.py`
- Serves: AC-1, FR-1
- Test: TC-2
- Depends on: T-1
- Parallel: no
- Tier: cheap: x
- Effort: low
"""


def pack_repo(files, before=None):
    """A finished epic E-1 (T-1) in spec `s`, whose one commit adds `files` ({path: text}) and src/one.py; epic E-2 is for
    AC-1, FR-1 and CT-2, which T-1 and its diff never touch. Lint is `echo RESULT-MARK-7`."""
    root = epic_repo(["T-1"])
    git(root, "config", "user.name", "t")
    git(root, "config", "user.email", "t@t")
    files = {"src/one.py": "DIFF_MARK = 42\n\n\ndef f():\n    return DIFF_MARK\n", **files}
    d = root / ".nio/specs/s"
    (d / "tasks.md").write_text(PACK_TASKS.format(files=", ".join(f"`{x}`" for x in files)))
    (d / "spec.md").write_text(PACK_SPEC)
    (d / "contracts.md").write_text(PACK_CONTRACTS)
    (root / ".nio/config.json").write_text(json.dumps({"tests": {"lint": "echo RESULT-MARK-7"}}))
    (root / ".gitignore").write_text(".nio/runs/\n")
    for name, text in (before or {}).items():  # files that exist before the epic
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    git(root, "add", "-A")
    git(root, "commit", "-qm", "before the epic")
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    git(root, "add", "-A")
    git(root, "commit", "-qm", "T-1: One")
    return root


def pack(root, lens):
    e = evidence()
    assert hasattr(e, "pack"), "evidence.pack doesn't exist yet"
    text = e.pack(root, "s", "implementation-E-1", lens, "R-1")
    assert isinstance(text, str) and text.strip(), text
    return text


def has_line(text, *words):
    return any(all(w in line.lower() for w in words) for line in text.splitlines())


def gate_findings(root):
    from nio import jury
    return jury.load(root, "s", "implementation-E-1")["findings"]


def test_it_holds_the_diff_the_text_of_ac_3():
    root = pack_repo({})
    start(root)
    text = pack(root, "conformance")
    assert "DIFF_MARK = 42" in text, f"the diff is not in the pack:\n{text}"
    for mark in ("AC3_TEXT", "FR2_TEXT", "CT1_TEXT"):
        assert mark in text, f"{mark} (an item the diff touches) is not in the pack:\n{text}"
    assert "RESULT-MARK-7" in text, f"the run results are not in the pack:\n{text}"
    for mark in ("AC1_TEXT", "AC1_OBSERVABLE", "FR1_TEXT", "CT2_TEXT"):
        assert mark not in text, f"{mark} (an item the diff doesn't touch) is in the pack:\n{text}"
    print("ok")


def test_it_can_open_any_project_file_and_can_t():
    from nio import agents, records
    shipped = Path(__file__).resolve().parent.parent / "src/nio/agents"
    assert agents.TOOLS["read"] == ["Read", "Grep", "Glob"], agents.TOOLS["read"]
    for name in ("conformance", "correctness", "risk-rollback", "security", "adversary", "consistency"):
        meta, body = records.parse(shipped / f"{name}.md")
        assert "## At implementation" in body, f"{name} has no ## At implementation section"
        assert meta["tools"] == ["read"], f"{name}: tools are {meta['tools']}, not read-only"
        assert 'tools: "Read, Grep, Glob"' in agents.render_claude(name, meta, "\n".join(body), "sonnet", "medium"), name
        assert "shell_tool = false" in agents.render_codex(name, meta, "\n".join(body), "gpt", "medium"), name
    # the pack tells the lens it may open any project file, and building it writes nothing the human would see
    root = pack_repo({})
    start(root)
    before = snapshot(root)
    text = pack(root, "conformance")
    assert re.search(r"any (project )?file", text, re.I), f"the pack doesn't say the lens may open any project file:\n{text}"
    same(root, before, "building a pack")
    print("ok")


# --- T-15: a juror's requested run (CT-11, CT-7, AC-26, AC-27, AC-44, AC-45) ---

ASKED_TCS = {"TC-2": "test_two", "TC-3": "test_three", "TC-4": "test_four", "TC-5": "test_five", "TC-6": "test_six"}
ASKED_ACCEPTANCE = "".join(
    f"### {tc} Asked ({tc}; unit) [derived: FR-1]\n- File: `tests/test_asked.py:AskedTest.{name}` (new)\n- Covers: CT-1\n"
    f"- Setup: x\n- Action: y\n- Assert: z\n\n" for tc, name in ASKED_TCS.items())
ASKED_TEST = """import unittest
from pathlib import Path


def ran(tc):
    with open({log!r}, "a") as f:
        f.write(tc + "\\n")
    Path("left-behind.txt").write_text(tc)  # a run in the human's tree shows
    print("ASKED-" + "MARK-" + tc)  # split, so the epic's diff doesn't hold what only a run prints


class AskedTest(unittest.TestCase):
""" + "".join(f"    def {name}(self):\n        ran({tc!r})\n\n" for tc, name in ASKED_TCS.items())
ASKED_SPEC = "---\nslug: s\nretired: []\n---\n# s\n\n## User stories\n### US-1 Story (P1) [human]\n" + "".join(
    f"- **AC-{i}** Given x, when it runs, then it holds. [human]\n  Observable: y. Level: unit.\n" for i in range(1, 11))


def asked_repo(suite=None):
    """A gate started on epic E-1 whose tests.md also names TC-2..TC-6, tests that log their TC when run, each only after
    the gate's own run of the suite. (root, the log)."""
    root, _ = gate_repo()
    log = Path(tempfile.mkdtemp(prefix="nio-asked-")) / "ran"
    (root / ".nio/specs/s/tests.md").write_text(MISUSE.replace("## Misuse tests", f"## Acceptance tests\n\n{ASKED_ACCEPTANCE}## Misuse tests"))
    (root / ".nio/specs/s/spec.md").write_text(ASKED_SPEC)
    (root / "tests/test_asked.py").write_text(ASKED_TEST.format(log=str(log)))
    if suite:
        (root / ".nio/config.json").write_text(json.dumps({"tests": {"suite": suite}}))
    git(root, "add", "-A")
    git(root, "commit", "-qm", "T-2: Two")
    start(root)
    log.write_text("")
    return root, log


def asked_round(root, rnd, **lenses):
    """Round `rnd`'s lens outputs go into the ledger, through the path that reads a finding's fields. Each lens gives
    [(n, run or None)]: a finding on AC-n asking for that run."""
    from nio import jury
    paths = []
    for lens, findings in lenses.items():
        body = "".join(f'### F{i} finding on AC-{n}\n- cites: AC-{n}\n- kind: gap\n- severity: major\n- evidence: observed\n- gap: missing\n'
                       f'- where: a.py\n- quote: "it holds"\n- situation: x\n- fix: y\n' + (f"- run: {run}\n" if run else "") + "\n"
                       for i, (n, run) in enumerate(findings, 1))
        path = root / f".nio/runs/R-1/jury/{GATE}-{lens}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'---\nlens: {lens}\ngate: {GATE}\nsubject: s\nby: "juror / claude-code / sonnet"\ncontext: sufficient\n---\n'
                        f"## Reasoning\nChecked.\n\n## Findings\n{body}")
        paths.append(path)
    led = jury.load(root, "s", GATE)
    led["round"] = rnd
    led.setdefault("versions", {})[str(rnd)] = git(root, "rev-parse", "HEAD").strip()
    said = jury.merge(led, paths, GATE, "s", ASKED_SPEC)
    assert not [x for x in said if "INVALID" in x or "ungrounded" in x], said
    jury.save(root, led)


def asked_run(root):
    """(results, for the human) of `evidence.requested` on the gate's ledger as it stands."""
    from nio import jury
    e = evidence()
    assert hasattr(e, "requested"), "evidence.requested doesn't exist yet"
    return e.requested(root, jury.load(root, "s", GATE), "R-1")


def next_packs(root):
    """The next round's pack both ways it is built: a full pack, and the fix check of a re-review, whose empty diff shows
    only what the requested runs put there."""
    from nio import jury
    led = jury.load(root, "s", GATE)
    full = pack(root, "conformance")
    head, rnd = git(root, "rev-parse", "HEAD").strip(), led["round"]
    jury.save(root, {**led, "round": rnd + 1, "recorded": [[rnd, "rejected"]], "versions": {str(rnd): head, str(rnd + 1): head}})
    check = pack(root, "conformance")
    jury.save(root, led)
    assert "fix check" in check, check
    return full, check


def asked_saved(root):
    return json.dumps(evidence().load(root, "R-1")["requests"], ensure_ascii=False)


def finding_id(root, n):
    from nio import jury
    return next(f["id"] for f in jury.load(root, "s", GATE)["findings"] if f["title"] == f"finding on AC-{n}")


def on_the_list(human, request, jid):
    """The human's list holds one entry naming both the request and its finding."""
    return any(request in json.dumps(h, ensure_ascii=False) and re.search(rf"\b{jid}\b", json.dumps(h)) for h in human)


def test_they_hold_that_run_s_result():
    # the second juror's request is on a finding the first already raised; TC-1 is one of the spec's attacks
    root, log = asked_repo()
    asked_round(root, 1, conformance=[(1, None), (3, "TC-1")], correctness=[(1, "TC-2")])
    assert "ASKED-MARK" not in pack(root, "conformance"), "the pack holds a run that wasn't made"
    before = snapshot(root)
    asked_run(root)
    same(root, before, "a requested run")
    assert log.read_text().split() == ["TC-2"], log.read_text()
    for text in next_packs(root):
        assert "ASKED-MARK-TC-2" in text and "MISUSE-RAN" in text, f"the requested runs' output is not in the pack:\n{text}"
    saved = asked_saved(root)
    assert all(x in saved for x in ("TC-1", "TC-2", "MISUSE-RAN", "ASKED-MARK-TC-2")), saved
    start(root)  # CT-7: a later `nio jury evidence` on the same run keeps `requests`
    assert "ASKED-MARK-TC-2" in pack(root, "conformance"), "a later evidence run lost the requested run"
    print("ok")


def test_they_say_the_run_couldn_t_start_and_why():
    # a runner with no known way to run one test, and a program that doesn't exist
    for suite, why in (("make test", "runner|one test"), ("/nonexistent/pytest", "not found")):
        root, log = asked_repo(suite)
        asked_round(root, 1, conformance=[(1, "TC-2")])
        assert "couldn't run" not in pack(root, "conformance"), suite
        asked_run(root)
        assert log.read_text() == "", f"{suite}: the test ran: {log.read_text()}"
        saved = asked_saved(root)
        assert "TC-2" in saved and "couldn't run" in saved and re.search(why, saved, re.I), f"{suite}: {saved}"
        full, check = next_packs(root)
        assert "couldn't run" in full, f"{suite}: the full pack doesn't say it:\n{full}"
        assert "TC-2" in check and "couldn't run" in check and re.search(why, check, re.I), f"{suite}: the fix check doesn't say it:\n{check}"
    print("ok")


def test_the_command_is_not_run_and_is_listed_for():
    # command text from a model, however it is dressed, even one that would run a real test of the project; never a shell
    root, log = asked_repo()
    mark = Path(tempfile.mkdtemp(prefix="nio-shell-")) / "started"
    shell = [f"touch {mark}", f"TC-2; touch {mark}", f"TC-2 && touch {mark}", f"$(touch {mark})", f"`touch {mark}`",
             "TC-99", "python3 -m unittest tests.test_asked.AskedTest.test_two"]
    asked_round(root, 1, conformance=[(i, run) for i, run in enumerate(shell[:5], 1)],
                correctness=[(i, run) for i, run in enumerate([*shell[5:], "TC-3"], 6)])
    _, human = asked_run(root)
    assert not mark.exists(), "a request's shell text ran"
    assert log.read_text().split() == ["TC-3"], f"refused requests must neither run nor use up the round's runs: {log.read_text()}"
    assert len(human) == len(shell), human
    for i, run in enumerate(shell, 1):
        assert on_the_list(human, run, finding_id(root, i)), f"{run!r} and its finding are not on the list: {human}"
    for text in next_packs(root):
        assert "ASKED-MARK-TC-3" in text and "ASKED-MARK-TC-2" not in text, text
    print("ok")


def test_only_3_are_run_and_the_fourth_is_listed():
    root, log = asked_repo()
    four = {1: "TC-2", 2: "TC-3", 3: "TC-4", 4: "TC-5"}
    asked_round(root, 1, conformance=[(1, four[1]), (2, four[2])], correctness=[(3, four[3]), (4, four[4])])
    _, human = asked_run(root)
    ran = log.read_text().split()
    assert len(ran) == 3 == len(set(ran)) and set(ran) < set(four.values()), ran
    (n, left), = [(n, tc) for n, tc in four.items() if tc not in ran]
    assert len(human) == 1 and on_the_list(human, left, finding_id(root, n)), human
    for text in next_packs(root):
        assert set(re.findall(r"ASKED-MARK-(TC-\d+)", text)) == set(ran), text
    asked_run(root)  # the same round again: no more runs, or the cap means nothing
    assert log.read_text().split() == ran, log.read_text()
    asked_round(root, 2, conformance=[(5, "TC-6")])  # the next round has its own three; what was listed stays the human's
    asked_run(root)
    assert log.read_text().split() == [*ran, "TC-6"], log.read_text()
    print("ok")


# --- T-16: a finding's gap, where and cites are read and grounded (CT-12, AC-28, AC-29, AC-30, AC-47) ---

def finding_collected(**fields):
    """Collect one conformance finding (on AC-3, in src/one.py, gap missing) with `fields` replacing or, when None,
    removing its lines. (the lines collect printed, the gate's findings)"""
    from nio import jury
    root = pack_repo({})
    lines = {"cites": "AC-3", "kind": "gap", "severity": "major", "evidence": "observed", "gap": "missing", "where": "src/one.py",
             "quote": '"return DIFF_MARK"', "situation": "x", "fix": "y", **fields}
    body = "".join(f"- {k}: {v}\n" for k, v in lines.items() if v is not None)
    path = root / f".nio/runs/R-1/jury/{GATE}-conformance.md"
    path.parent.mkdir(parents=True)
    path.write_text(f'---\nlens: conformance\ngate: {GATE}\nsubject: s\nby: "juror / claude-code / sonnet"\ncontext: sufficient\n---\n'
                    f"## Reasoning\nChecked.\n\n## Findings\n### F1 the finding\n{body}")
    return jury.collect(root, "s", GATE, "R-1"), gate_findings(root)


def invalid_naming(field, **fields):
    said, found = finding_collected(**fields)
    assert any("INVALID" in x and field in x for x in said), (field, said)
    assert not found, found  # an invalid output adds nothing to the ledger


def test_the_output_is_invalid():
    invalid_naming("gap", gap=None)
    print("ok")


def test_it_is_dropped_as_ungrounded():
    said, found = finding_collected(cites="FR-99")
    assert not any("INVALID" in x for x in said), said
    (f,) = found
    assert f["status"] == "dropped" and "FR-99" in f["reason"], f
    print("ok")


def test_it_is_kept():
    said, found = finding_collected(quote='"def f(): … return the constant, not computed"')
    assert not any("INVALID" in x for x in said), said
    (f,) = found
    assert f["status"] == "open", f
    assert f["gap"] == "missing", f  # the gap type is on the ledger entry (CT-12)
    print("ok")


def test_the_output_is_invalid_again():
    invalid_naming("cites", cites=None)
    invalid_naming("cites", cites="a label, no ID")
    invalid_naming("where", where=None)
    print("ok")


# --- T-17: blockers and majors go to the refuter; a confirmed weakening is tampering (CT-12, CT-6, CT-20) ---

STRONG = "def test_weak():\n    assert compute() == 2\n    assert other() == 3\n"
WEAKER = "def test_weak():\n    assert compute() == 2\n"  # `assert other() == 3` is removed
CHANGED = "def test_weak():\n    assert compute() == 2\n    assert other() == 4\n"  # an expected value changes
TEST_FILE = "tests/test_app.py"


def lens_out(root, lens, findings="none", name=None, rnd="R-1"):
    """Write a lens output at the gate: `findings` is a list of dicts of lines (title included) or the text `none`."""
    if findings != "none":
        base = {"kind": "gap", "severity": "major", "evidence": "observed", "gap": "partial", "where": TEST_FILE,
                "quote": '"assert other"', "situation": "x", "fix": "y", "cites": "AC-3"}
        findings = "".join(f"### F{i} {f['title']}\n" + "".join(f"- {k}: {v}\n" for k, v in {**base, **f}.items() if k != "title") + "\n"
                           for i, f in enumerate(findings, 1))
    path = root / f".nio/runs/{rnd}/jury/{name or GATE + '-' + lens}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'---\nlens: {lens}\ngate: {GATE}\nsubject: s\nby: "juror / claude-code / sonnet"\ncontext: sufficient\n---\n'
                    f"## Reasoning\nChecked.\n\n## Findings\n{findings}")
    return path


def test_it_is_recorded_as_test_tampering():
    from nio import jury
    root = pack_repo({TEST_FILE: WEAKER}, before={TEST_FILE: STRONG})
    start(root)
    lens_out(root, "correctness", [{"title": "test_weak lost `assert other() == 3`", "tampering": "yes"}])
    jury.collect(root, "s", GATE, "R-1")
    (f,) = [x for x in gate_findings(root) if x["sources"][0]["lens"] == "correctness"]
    assert f["tampering"] is True and f["severity"] == "major", f
    assert "test_weak" in f["title"] and "assert other() == 3" in f["title"], f  # names the test and the removed assertion
    print("ok")


def test_the_cli_flags_the_assertion_and_the_correctness_lens():
    from nio import jury
    root = pack_repo({TEST_FILE: CHANGED}, before={TEST_FILE: STRONG})
    results = start(root)
    (h,) = [x for x in results["hints"] if x["name"] == "test_weak"]
    assert h["file"] == TEST_FILE and h["kind"] == "changed assertion", h
    lens_out(root, "correctness", [{"title": "test_weak expects 4 now", "where": f"{TEST_FILE}:{h['line']}"}])
    jury.collect(root, "s", GATE, "R-1")
    (f,) = gate_findings(root)
    assert f["sources"][0]["lens"] == "correctness" and f"{TEST_FILE}:{h['line']}" in f["where"], f
    print("ok")


def test_the_finding_goes_to_the_refuter_before_the_human():
    from nio import jury
    root = pack_repo({})
    start(root)
    lens_out(root, "conformance", [{"title": "a major one", "quote": '"DIFF_MARK"'}])
    said = jury.collect(root, "s", GATE, "R-1")
    (f,) = gate_findings(root)
    assert f["severity"] == "major" and f["validation"] == "pending", f
    assert any(x.startswith("### J-1") for x in said) and any("Refuter batch" in x for x in said), said
    led = jury.load(root, "s", GATE)
    assert jury.compose(led, led["versions"][str(led["round"])])[0] == "pending", "the outcome doesn't wait on the refuter"
    print("ok")


def test_it_is_not_open_and_no_fix_task_is():
    from nio import jury
    root = pack_repo({})
    start(root)
    tasks = (root / ".nio/specs/s/tasks.md").read_text()
    lens_out(root, "conformance", [{"title": "a refuted one", "quote": '"DIFF_MARK"'}])
    jury.collect(root, "s", GATE, "R-1")
    (root / f".nio/runs/R-1/jury/{GATE}-refuter.md").write_text("### J-1\n- result: refuted\n- reason: the code does it\n")
    jury.collect(root, "s", GATE, "R-1")
    (f,) = gate_findings(root)
    assert f["status"] == "refuted", f
    led = jury.load(root, "s", GATE)
    assert jury.compose(led, led["versions"][str(led["round"])])[0] != "pending"
    now = (root / ".nio/specs/s/tasks.md").read_text()
    assert now == tasks and "J-1" not in now and "refuted one" not in now, "a task was written for a refuted finding"
    print("ok")


def test_no_tampering_finding_is_recorded():
    from nio import jury
    root = pack_repo({TEST_FILE: CHANGED}, before={TEST_FILE: STRONG})
    start(root)
    lens_out(root, "correctness", "none")  # the lens says the test did not get weaker
    jury.collect(root, "s", GATE, "R-1")
    assert has_line(pack(root, "correctness"), "test_weak", "assertion"), "the hint is not in the pack"
    assert not [x for x in gate_findings(root) if x.get("tampering") or "test_weak" in json.dumps(x)], gate_findings(root)
    print("ok")


def test_cli_findings_skip_the_refuter():
    from nio import jury
    root = pack_repo({TEST_FILE: "def test_keeps():\n    assert 1\n"}, before={TEST_FILE: STRONG + "\n\ndef test_keeps():\n    assert 1\n"})
    start(root, "R-1")
    start(root, "R-2")
    lens_out(root, "conformance", "none", rnd="R-2")
    said = jury.collect(root, "s", GATE, "R-2")
    (f,) = gate_findings(root)
    assert f["sources"][0]["lens"] == "cli" and f["validation"] == "confirmed" and f["tampering"] is True, f
    assert not any(x.startswith("### " + f["id"]) for x in said), said
    try:
        jury.dispose(root, "s", GATE, f["id"], "accepted-risk", "agent", "fine")
        raise AssertionError("an agent accepted tampering")
    except ValueError:
        pass
    assert gate_findings(root)[0]["status"] == "open"
    print("ok")


def test_a_tampering_lens_finding_that_merges_stays_tampering():
    from nio import jury
    for first, second in (("conformance", "correctness"), ("correctness", "conformance")):
        root = pack_repo({})
        start(root)
        for lens in (first, second):
            lens_out(root, lens, [{"title": f"{lens} says test_weak got weaker", **({"tampering": "yes"} if lens == "correctness" else {}),
                                   "quote": '"DIFF_MARK"'}])
        jury.collect(root, "s", GATE, "R-1")
        (f,) = gate_findings(root)  # same kind and cited IDs: one entry
        assert len(f["sources"]) == 2, f
        assert f["tampering"] is True, f"{first} then {second}: the merge lost the tampering mark: {f}"
        try:
            jury.dispose(root, "s", GATE, f["id"], "accepted-risk", "agent", "fine")
            raise AssertionError("an agent accepted tampering")
        except ValueError:
            pass
        jury.dispose(root, "s", GATE, f["id"], "accepted-risk", "human", "the human accepts it")
        assert gate_findings(root)[0]["disposition"] == "accepted-risk"
    print("ok")


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_") and callable(test):
            test()
