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


def test_a_lens_isn_t_dropped_without_the_human():
    import subprocess
    import sys
    from nio import jury
    root = capped()  # the plan holds five runs, the cap is four, and no pick is recorded
    four = ["conformance", "correctness", "security", "adversary"]
    jury_dir = root / ".nio/runs/R-1/jury"
    jury_dir.mkdir(parents=True)
    for lens in four:  # four lens outputs, the fifth lens (risk-rollback) never reports
        (jury_dir / f"{GATE}-{lens}.md").write_text(
            f'---\nlens: {lens}\ngate: {GATE}\nsubject: s\nby: "juror / claude-code / sonnet"\ncontext: sufficient\n---\n'
            "## Reasoning\nChecked.\n\n## Findings\nnone\n")
    for expect in ([], ["risk-rollback"], four, four + ["risk-rollback"]):
        args = [sys.executable, "-c", "from nio.cli import main; main()", "jury", "collect", "s", GATE, "--run", "R-1"]
        for lens in expect:
            args += ["--expect", lens]
        out = subprocess.run(args, cwd=root, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
        assert out.returncode != 0 and "--pick" in out.stderr and "pick" in out.stderr, (expect, out.returncode, out.stderr)
        assert "invalid choice" not in out.stderr, out.stderr
    led = jury.load(root, "s", GATE)
    assert not led["collected"] and not led["findings"], "a refused collect merged outputs"
    assert "picked" not in led and "dropped" not in led, led
    outcome, reasons, _ = jury.compose(led, "no version judged yet")
    assert outcome != "approved", (outcome, reasons)
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


def gate_findings(root, cli=False):
    """The gate's findings; the CLI's own (lens `cli`, e.g. an AC with no evidence) only when `cli`."""
    from nio import jury
    return [f for f in jury.load(root, "s", "implementation-E-1")["findings"] if cli or f["sources"][0]["lens"] != "cli"]


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


def fill(root, gate, run, matches=()):
    """Write a valid empty output for each planned lens the run has none for (a setup: the round expects them all)."""
    from nio import jury
    try:
        text = next(x for x in jury.plan(root, "s", gate)[0] if x.startswith("lenses: "))
    except (ValueError, StopIteration):
        return
    d = root / f".nio/runs/{run}/jury"
    for lens in re.findall(r"([a-z][a-z-]*) \(", text):
        path = d / f"{gate}-{lens}.md"
        if not path.exists() and lens != "refuter":
            body = "## Matches\n" + "".join(f"- {x}\n" for x in matches) + "\n" if lens == "conformance" else ""
            d.mkdir(parents=True, exist_ok=True)
            path.write_text(f'---\nlens: {lens}\ngate: {gate}\nsubject: s\nby: "juror / claude-code / sonnet"\ncontext: sufficient\n---\n'
                            f"## Reasoning\nChecked.\n\n{body}## Findings\nnone\n")


def lens_out(root, lens, findings="none", name=None, rnd="R-1", rest=True):
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
    if rest:
        fill(root, GATE, rnd, E1_MATCHES)
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
    (f,) = [x for x in gate_findings(root, cli=True) if x.get("tampering")]
    assert f["sources"][0]["lens"] == "cli" and f["validation"] == "confirmed" and f["tampering"] is True, f
    assert not any(x.startswith("### " + f["id"]) for x in said), said
    try:
        jury.dispose(root, "s", GATE, f["id"], "accepted-risk", "agent", "fine")
        raise AssertionError("an agent accepted tampering")
    except ValueError:
        pass
    assert f["status"] == "open"
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


# --- T-18: the conformance lens's matches are joined to the results (CT-21, CT-3, CT-7, AC-4, AC-5, AC-6, AC-17, AC-51) ---

JOIN_SPEC = PACK_SPEC.replace("AC-3", "AC-2").replace("AC3_", "AC2_")
JOIN_SUITE = "python3 -m unittest discover -s tests -t ."
JOIN_TESTS_MD = "---\nslug: s\nretired: []\n---\n# Tests: s\n\n## Tests\n\n" + "".join(
    f"### TC-{n} Checks {name} (AC-1; unit) [derived: AC-1]\n- File: `tests/test_calc.py:CalcTest.{name}` (new)\n- Covers: CT-1\n"
    "- Setup: x\n- Action: y\n- Assert: z\n\n" for n, name in enumerate(
        ("test_adds_two_numbers", "test_multiplies_two_numbers", "test_subtracts_two_numbers", "test_lists_the_items"), 1))
CALC = '''import unittest


class CalcTest(unittest.TestCase):
    def test_adds_two_numbers(self):
        """Adding two numbers gives their sum."""
        self.assertEqual(1 + 1, 2)

    def test_multiplies_two_numbers(self):
        """Multiplying two numbers gives their product."""
        self.assertEqual(2 * 2, {product})

    def test_subtracts_two_numbers(self):
        """Subtracting a number from another gives the difference."""
        self.assertEqual(3 - 1, {difference})

    def test_lists_the_items(self):
        """Lists the items of an order."""
        items = [1, 2]
        len(items)
'''


def join_repo(product=4, difference=2, header=""):
    """A finished epic E-1 (T-1 serves AC-1, T-2 serves AC-2) whose tests/test_calc.py holds four tests, all named in
    tests.md and none carrying a spec ID: multiplies passes or fails by `product`, subtracts by `difference` (a wrong
    number makes it fail), adds always passes, and lists has no assertion. `header` goes above the file. (root, the
    file's text)"""
    root = epic_repo(["T-1", "T-2"])
    git(root, "config", "user.name", "t")
    git(root, "config", "user.email", "t@t")
    d = root / ".nio/specs/s"
    (d / "spec.md").write_text(JOIN_SPEC)
    (d / "tests.md").write_text(JOIN_TESTS_MD)
    (root / ".nio/config.json").write_text(json.dumps({"tests": {"suite": JOIN_SUITE}}))
    (root / ".gitignore").write_text(".nio/runs/\n")
    source = header + CALC.format(product=product, difference=difference)
    (root / "tests").mkdir()
    (root / "tests/__init__.py").write_text("")
    (root / "tests/test_calc.py").write_text(source)
    (root / "a.py").write_text("a = 1\n")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "T-1: One")
    (root / "b.py").write_text("b = 1\n")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "T-2: Two")
    return root, source


def def_line(source, name):
    return next(n for n, x in enumerate(source.splitlines(), 1) if re.match(rf"\s*def {name}\(", x))


def matches_out(root, *lines):
    """The conformance lens's fixed output: only `## Matches` lines and no findings."""
    path = root / f".nio/runs/R-1/jury/{GATE}-conformance.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'---\nlens: conformance\ngate: {GATE}\nsubject: s\nby: "juror / claude-code / sonnet"\ncontext: sufficient\n---\n'
                    "## Reasoning\nRead the tests.\n\n## Matches\n" + "".join(f"- {x}\n" for x in lines) + "\n## Findings\nnone\n")


def joined(root, *lines):
    """The gate collects evidence, then the lens's matches are collected. (the run's results, the blocker findings)"""
    from nio import jury
    start(root)
    matches_out(root, *lines)
    jury.collect(root, "s", GATE, "R-1")
    return evidence().load(root, "R-1"), [f for f in gate_findings(root, cli=True) if f["severity"] == "blocker"]


def missing_for(blockers, *acs):
    """Exactly one blocker per AC in `acs`, each a CLI missing-evidence finding citing it, never sent to the refuter."""
    assert sorted(c for f in blockers for c in f["cites"]) == sorted(acs), [(f["title"], f["cites"]) for f in blockers]
    for f in blockers:
        assert f["gap"] == "missing" and len(f["cites"]) == 1, f
        assert f["sources"][0]["lens"] == "cli" and f["validation"] == "confirmed" and f["status"] == "open", f


def test_the_results_list_each_ac_with_that_test_s():
    root, source = join_repo(difference=5)  # a third test of the same suite fails, so the suite as a whole fails
    assert "AC-" not in source, "the tests carry spec IDs"
    adds, times = def_line(source, "test_adds_two_numbers"), def_line(source, "test_multiplies_two_numbers")
    results, blockers = joined(root, f"AC-1 -> tests/test_calc.py:{adds}", f"AC-2 -> tests/test_calc.py:{times}")
    assert results["evidence"] == [{"ac": "AC-1", "file": "tests/test_calc.py", "line": adds, "result": "passed"},
                                   {"ac": "AC-2", "file": "tests/test_calc.py", "line": times, "result": "passed"}], results["evidence"]
    assert not blockers, [f["title"] for f in blockers]
    print("ok")


def test_a_missing_evidence_finding_is_recorded_for_it():
    root, source = join_repo()
    results, blockers = joined(root, f"AC-1 -> tests/test_calc.py:{def_line(source, 'test_adds_two_numbers')}")  # AC-2 has no test
    missing_for(blockers, "AC-2")
    assert not [x for x in results["evidence"] if x["ac"] == "AC-2" and x["result"] == "passed"], results["evidence"]
    print("ok")


def test_a_missing_evidence_finding_is_recorded_for_it_again():
    root, source = join_repo(product=5)  # test_multiplies fails; the suite's other tests pass
    adds, times = def_line(source, "test_adds_two_numbers"), def_line(source, "test_multiplies_two_numbers")
    results, blockers = joined(root, f"AC-1 -> tests/test_calc.py:{adds}", f"AC-2 -> tests/test_calc.py:{times}")
    missing_for(blockers, "AC-2")
    assert "test_multiplies_two_numbers" in json.dumps(blockers[0]), f"the finding doesn't name the failing test: {blockers[0]}"
    assert results["evidence"] == [{"ac": "AC-1", "file": "tests/test_calc.py", "line": adds, "result": "passed"},
                                   {"ac": "AC-2", "file": "tests/test_calc.py", "line": times, "result": "failed"}], results["evidence"]
    print("ok")


def test_every_ac_is_recorded_without_passing_evidence_the_cli():
    root, source = join_repo(header="import no_such_module_for_crash\n")  # the suite dies on import; no test runs
    adds, times = def_line(source, "test_adds_two_numbers"), def_line(source, "test_multiplies_two_numbers")
    results, blockers = joined(root, f"AC-1 -> tests/test_calc.py:{adds}", f"AC-2 -> tests/test_calc.py:{times}")
    missing_for(blockers, "AC-1", "AC-2")
    assert "no_such_module_for_crash" in json.dumps(results), f"the crash output is not in the results: {json.dumps(results)[:500]}"
    assert [x["ac"] for x in results["evidence"]] == ["AC-1", "AC-2"] and not [x for x in results["evidence"] if x["result"] == "passed"], results["evidence"]
    print("ok")


def test_the_packs_hold_a_hint_naming_it_and_a():
    root, source = join_repo()
    adds, lists = def_line(source, "test_adds_two_numbers"), def_line(source, "test_lists_the_items")
    results, blockers = joined(root, f"AC-1 -> tests/test_calc.py:{adds}", f"AC-2 -> tests/test_calc.py:{lists}")
    ran = [t for t in results["tests"] if t["name"].endswith("test_lists_the_items")]
    assert len(ran) == 1 and ran[0]["result"] == "passed", f"the no-assertion test should have run and passed: {results['tests']}"
    for lens in PACK_LENSES:
        assert has_line(pack(root, lens), "test_lists_the_items", "no assertion"), f"no hint naming the test in the {lens} pack"
    missing_for(blockers, "AC-2")  # it passed, but a test that asserts nothing is not evidence
    assert [x["result"] for x in results["evidence"] if x["ac"] == "AC-2"] != ["passed"], results["evidence"]
    print("ok")


def test_a_lens_cant_claim_a_pass():
    root, source = join_repo(product=5)
    times = def_line(source, "test_multiplies_two_numbers")
    results, blockers = joined(root, f"AC-1 -> tests/test_calc.py:{times} (passed)", "AC-2 -> tests/test_ghost.py:3 (passed)")
    missing_for(blockers, "AC-1", "AC-2")  # the second test is in no results: it didn't run
    first, second = results["evidence"]
    assert first == {"ac": "AC-1", "file": "tests/test_calc.py", "line": times, "result": "failed"}, first
    assert second["ac"] == "AC-2" and second["result"] != "passed", second
    print("ok")


def test_an_unreadable_runner_s_passing_suite_blocks_no_matched_ac():
    # the split quotes keep the runner's name out of the command's words, so NIO reads no runner in it
    loop = "for d in tests; do " + JOIN_SUITE.replace("unittest", 'unit""test') + "; done"
    for product, passes in ((4, True), (5, False)):
        root, source = join_repo(product=product)
        (root / ".nio/config.json").write_text(json.dumps({"tests": {"suite": loop}}))
        adds = def_line(source, "test_adds_two_numbers")
        results, blockers = joined(root, f"AC-1 -> tests/test_calc.py:{adds}")  # AC-2 has no match
        ac1 = [x for x in results["evidence"] if x["ac"] == "AC-1"]
        if passes:
            assert [x["result"] for x in ac1] == ["unknown"], results["evidence"]
            missing_for(blockers, "AC-2")
            for lens in PACK_LENSES:
                assert has_line(pack(root, lens), "unknown", "per-test"), f"no unknown-results warning in the {lens} pack"
        else:
            missing_for(blockers, "AC-1", "AC-2")
    print("ok")


# --- T-19: the epic's outcome (CT-13, AC-49) ---

def composed(root):
    from nio import jury
    led = jury.load(root, "s", GATE)
    return jury.compose(led, led["versions"][str(led["round"])])


def invalid_out(root, lens, extra=""):
    """A `lens` output missing its required fields, so it is invalid; `extra` makes each write a new file."""
    path = root / f".nio/runs/R-1/jury/{GATE}-{lens}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nlens: {lens}\n---\nnot an output {extra}\n")


def test_it_is_rerun_and_never_approved_after_a_second():
    from nio import jury
    root = pack_repo({})
    start(root)
    lens_out(root, "conformance", "none", rest=False)
    jury.collect(root, "s", GATE, "R-1", expect=("conformance", "correctness"))  # correctness has no output
    outcome, reasons, _ = composed(root)
    assert outcome == "rerun" and any("correctness" in r for r in reasons), (outcome, reasons)
    invalid_out(root, "correctness", "1")  # an invalid output
    jury.collect(root, "s", GATE, "R-1")
    outcome, reasons, _ = composed(root)
    assert outcome == "rerun" and any("correctness" in r for r in reasons), (outcome, reasons)
    invalid_out(root, "correctness", "2")  # invalid a second time
    jury.collect(root, "s", GATE, "R-1")
    outcome, reasons, _ = composed(root)
    assert outcome == "human" and any("correctness" in r for r in reasons), (outcome, reasons)
    print("ok")


def test_a_cli_finding_found_not_fixed_counts_as_unresolved():
    from nio import jury
    root = pack_repo({TEST_FILE: "def test_keeps():\n    assert 1\n"}, before={TEST_FILE: STRONG + "\n\ndef test_keeps():\n    assert 1\n"})
    start(root, "R-1")
    lens_out(root, "conformance", "none")
    jury.collect(root, "s", GATE, "R-1")
    (f,) = [x for x in gate_findings(root, cli=True) if x.get("tampering")]
    assert f["sources"][0]["lens"] == "cli", f
    led = jury.load(root, "s", GATE)
    f = next(x for x in led["findings"] if x["id"] == f["id"])  # the CLI marked it not fixed after a fix: open again, with no juror's verdict on it
    f.update(status="open", baseline="unchanged", disposition="", by="", note="", reason="not fixed: the assertion is still gone")
    jury.save(root, led)
    outcome, reasons, _ = composed(root)
    assert outcome != "approved" and any(f["id"] in r for r in reasons), (outcome, reasons)
    print("ok")


def test_no_matches_section_leaves_each_ac_with_a_finding_and_the_epic_unapproved():
    from nio import jury
    root, _ = join_repo()
    start(root)
    path = root / f".nio/runs/R-1/jury/{GATE}-conformance.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'---\nlens: conformance\ngate: {GATE}\nsubject: s\nby: "juror / claude-code / sonnet"\ncontext: sufficient\n---\n'
                    "## Reasoning\nChecked.\n\n## Findings\nnone\n")  # no `## Matches` at all
    jury.collect(root, "s", GATE, "R-1")
    missing_for([f for f in gate_findings(root, cli=True) if f["severity"] == "blocker"], "AC-1", "AC-2")  # SC-1: evidence or a finding
    assert composed(root)[0] != "approved", composed(root)
    print("ok")


# --- T-20: refuse a lens output the human didn't pick (CT-8, AC-22, FR-16) ---

def test_a_lens_the_human_didn_t_pick_is_refused():
    from nio import jury
    root = capped()
    four = ["conformance", "correctness", "security", "adversary"]
    jury.plan(root, "s", GATE, pick=",".join(four))  # the human picks four; risk-rollback is dropped
    assert jury.load(root, "s", GATE)["dropped"] == ["risk-rollback"], jury.load(root, "s", GATE)
    jury_dir = root / ".nio/runs/R-1/jury"
    jury_dir.mkdir(parents=True)

    def write(lens):
        (jury_dir / f"{GATE}-{lens}.md").write_text(
            f'---\nlens: {lens}\ngate: {GATE}\nsubject: s\nby: "juror / claude-code / sonnet"\ncontext: sufficient\n---\n'
            "## Reasoning\nChecked.\n\n## Findings\nnone\n")

    write("risk-rollback")  # a dropped lens's output, which the human never picked
    try:
        jury.collect(root, "s", GATE, "R-1")
        raise AssertionError("collect took a lens output from a lens the human dropped")
    except ValueError as e:
        assert "risk-rollback" in str(e), e
    led = jury.load(root, "s", GATE)
    assert not led["collected"] and not led["findings"], "a refused lens output reached the ledger"
    (jury_dir / f"{GATE}-risk-rollback.md").unlink()
    for lens in four:
        write(lens)
    jury.collect(root, "s", GATE, "R-1")  # the picked lenses still collect
    led = jury.load(root, "s", GATE)
    assert {k.split("/")[-1] for k in led["collected"]} == {f"{GATE}-{x}.md" for x in four}, led["collected"]
    print("ok")


# --- T-21: the secrets flag adds the security lens at the implementation gate and the spec gate (CT-18, AC-60, AC-61) ---

def test_the_plan_holds_the_security_lens():
    names, lines, ok = lens_plan(["secrets"])
    line = next(x for x in lines if x.startswith("lenses: "))
    assert ok and "security" in names and "security (risk: secrets)" in line, (names, lines)
    print("ok")


def test_the_security_lens_is_listed():
    from nio import spec
    from test_spec import put, repo
    root = repo()
    slug = put(root, "spec.md", lambda t: t.replace("risk: [money, external-input]", "risk: [secrets]"))
    errs, notes = spec.check(root, slug)
    assert errs == [] and "lenses: testability, logic, security" in notes, (errs, notes)
    print("ok")


# --- T-22: a fix task for a finding, once, without touching any existing task (CT-14, AC-33, AC-35, AC-50) ---

FIX_SPEC = """---
slug: s
route: full
retired: []
---
# s

## Functional requirements
- **FR-1** THE SYSTEM SHALL do one thing. [human]
- **FR-2** THE SYSTEM SHALL do another. [human]

## User stories
### US-1 Story (P1) [human]
- **AC-1** Given a, when it runs, then it holds. [human]
- **AC-2** Given b, when it runs, then it holds. [human]
- **AC-4** Given d, when it runs, then it holds. [human]
### US-2 Story (P1) [human]
- **AC-3** Given c, when it runs, then it holds. [human]
"""
FIX_CONTRACTS = """---
slug: s
retired: []
---
# Contracts: s

## Contracts

### CT-1 First (FR-1) [derived: FR-1]
- Binding: `src/one.py:one`

### CT-2 Second (FR-2) [derived: FR-2]
- Binding: `src/two.py:two`
"""
# AC-4 has no TC: TC-4 covers AC-44, which only looks like it. Nothing covers FR-2.
FIX_TESTS_MD = "---\nslug: s\nretired: []\n---\n# Tests: s\n\n## Tests\n\n" + "".join(
    f"### TC-{n} Checks {name} ({ac}; unit) [derived: {ac}]\n- File: `tests/test_calc.py:CalcTest.{name}` (new)\n- Covers: {ct}\n"
    "- Setup: x\n- Action: y\n- Assert: z\n\n" for n, name, ac, ct in (
        (1, "test_one", "AC-1", "CT-1"), (2, "test_two", "AC-2", "CT-2"), (3, "test_three", "AC-3", "CT-1"), (4, "test_four", "AC-44", "CT-1")))
FIX_SUITE = '''import unittest


class CalcTest(unittest.TestCase):
    def test_one(self):
        """One holds."""
        self.assertEqual(1, 1)

    def test_two(self):
        """Two holds."""
        self.assertEqual(2, 2)

    def test_three(self):
        """Three holds."""
        self.assertEqual(3, 3)

    def test_four(self):
        """Four holds."""
        self.assertEqual(4, 4)
'''
FIX_HEAD = """---
slug: s
retired: {retired}
---
<!-- Hand-owned: a comment may show what a task file looks like.
#### Fixes
## E-2 not an epic
### T-99 not a task
-->
# Tasks: s

"""


def planned_task(tid, file, serves, tc, deps="none"):
    return (f"### {tid} Build {file}\n- Files: `{file}`\n- Serves: {serves}\n- Test: {tc}\n- Depends on: {deps}\n"
            "- Parallel: no\n- Tier: cheap: x\n- Effort: low\n- Mode: split: x\n\n")


FIX_E1 = "## E-1 First (US-1)\n\n" + planned_task("T-1", "src/one.py", "AC-1", "TC-1") + planned_task("T-2", "src/two.py", "AC-2", "TC-2", "T-1") \
    + planned_task("T-3", "src/three.py", "AC-4", "TC-1", "T-2")
FIX_E2 = "## E-2 Second (US-2)\n\n" + planned_task("T-4", "src/four.py", "AC-3", "TC-3")


def earlier_fix(cite):
    return ("#### Fixes\n<!-- Tasks added after approval. -->\n" f"### T-5 An earlier fix\n- From: {cite} (implementation-E-1, round 1)\n"
            f"- Files: `src/five.py`\n- Serves: {cite}\n- Test: TC-1\n- Depends on: none\n- Parallel: no\n"
            "- Tier: strong: a fix from a jury finding\n- Effort: med\n- Mode: single: a fix from a jury finding\n\n")


def fix_repo(earlier="J-11", retired="[]"):
    """A full spec `s`, tasks approved. E-1 has four tasks, the last, T-5, an earlier fix for finding `earlier` under its
    `#### Fixes` (none when `earlier` is empty); E-2 has T-4. All are done, each with its own commit, and the tests pass."""
    root = epic_repo(["T-1", "T-2", "T-3", "T-4", "T-5"])
    git(root, "config", "user.name", "t")
    git(root, "config", "user.email", "t@t")
    d = root / ".nio/specs/s"
    for name, text in (("spec.md", FIX_SPEC), ("contracts.md", FIX_CONTRACTS), ("tests.md", FIX_TESTS_MD), ("plan.md", "---\nslug: s\n---\n# Plan: s\n")):
        (d / name).write_text(text)
    (root / ".nio/config.json").write_text(json.dumps({"tests": {"suite": JOIN_SUITE}}))
    (root / ".gitignore").write_text(".nio/runs/\n")
    head = FIX_HEAD.format(retired=retired)
    (d / "tasks.md").write_text(head + FIX_E1 + FIX_E2)
    git(root, "add", "-A")
    git(root, "commit", "-qm", "nio: approve tasks")
    (root / "tests").mkdir()
    (root / "tests/__init__.py").write_text("")
    (root / "tests/test_calc.py").write_text(FIX_SUITE)
    (root / "src").mkdir()
    for tid, name in (("T-1", "one"), ("T-2", "two"), ("T-3", "three"), ("T-5", "five"), ("T-4", "four")):
        (root / f"src/{name}.py").write_text(f"{name.upper()}_MARK = 1\n")
        if tid == "T-5":
            (d / "tasks.md").write_text(head + FIX_E1 + (earlier_fix(earlier) if earlier else "") + FIX_E2)
        git(root, "add", "-A")
        git(root, "commit", "-qm", f"{tid}: Build {name}")
    return root


def fix_gate(root, *findings, epic="E-1"):
    """Round 1 of the epic's gate: each AC has a passing test, the conformance lens raises `findings` (dicts of lines,
    title included; base below) and the refuter confirms each. Returns the ledger's findings."""
    from nio import jury
    gate = f"implementation-{epic}"
    evidence().collect(root, "s", epic, "R-1")
    lines = {"E-1": ("AC-1 -> tests/test_calc.py:5", "AC-2 -> tests/test_calc.py:9", "AC-4 -> tests/test_calc.py:17"), "E-2": ("AC-3 -> tests/test_calc.py:13",)}[epic]
    base = {"kind": "gap", "severity": "major", "evidence": "observed", "gap": "missing", "where": "src/one.py", "quote": '"ONE_MARK"',
            "situation": "x", "fix": "y", "cites": "AC-1"}
    body = "".join(f"### F{i} {f['title']}\n" + "".join(f"- {k}: {v}\n" for k, v in {**base, **f}.items() if k != "title") + "\n"
                   for i, f in enumerate(findings, 1)) or "none\n"
    jd = root / ".nio/runs/R-1/jury"
    jd.mkdir(parents=True, exist_ok=True)
    (jd / f"{gate}-conformance.md").write_text(
        f'---\nlens: conformance\ngate: {gate}\nsubject: s\nby: "juror / claude-code / sonnet"\ncontext: sufficient\n---\n'
        "## Reasoning\nChecked.\n\n## Matches\n" + "".join(f"- {x}\n" for x in lines) + f"\n## Findings\n{body}")
    fill(root, gate, "R-1", lines)
    said = jury.collect(root, "s", gate, "R-1")
    assert not [x for x in said if "INVALID" in x], said
    pending = [f["id"] for f in jury.load(root, "s", gate)["findings"] if f["validation"] == "pending"]
    if pending:
        (jd / f"{gate}-refuter.md").write_text("".join(f"### {i}\n- result: confirmed\n- reason: it is so\n\n" for i in pending))
        jury.collect(root, "s", gate, "R-1")
    found = jury.load(root, "s", gate)["findings"]
    assert [f["id"] for f in found] == [f"J-{n}" for n in range(1, len(findings) + 1)], f"the fixture isn't clean: {[f['title'] for f in found]}"
    return found


def nio(root, *args):
    import subprocess
    import sys
    return subprocess.run([sys.executable, "-c", "from nio.cli import main; main()", *args], cwd=root, capture_output=True, text=True)


def append_fix(root, finding, epic="E-1"):
    from nio import tasks
    assert hasattr(tasks, "append_fix"), "tasks.append_fix doesn't exist yet"
    return tasks.append_fix(root, "s", epic, finding)


def task_file(root):
    from nio import tasks
    return tasks.path(root, "s")


def parsed_tasks(root):
    from nio import records, tasks
    return tasks.parse("\n".join(records.parse(task_file(root))[1]))["tasks"]


def fix_tasks_for(root, gate=GATE):
    """{finding ID: [its fix tasks]}, from the `From:` lines naming this gate; the fixture's earlier fix, J-11, left out."""
    out = {}
    for t in parsed_tasks(root).values():
        m = re.fullmatch(r"(J-\d+) \(([\w-]+), round \d+\)", t["fields"].get("From", ""))
        if m and m[2] == gate and m[1] != "J-11":
            out.setdefault(m[1], []).append(t)
    return out


def tasks_pass(root):
    done = nio(root, "check", "tasks", "s")
    assert done.returncode == 0, f"nio check tasks refuses the file:\n{done.stdout}{done.stderr}\n{task_file(root).read_text()}"


def recorded(root, gate=GATE):
    """`nio jury check <gate> --record`, as the human runs it. (exit code, printed lines)"""
    done = nio(root, "jury", "check", "s", gate, "--record")
    assert "Traceback" not in done.stderr, done.stderr
    return done.returncode, done.stdout


def test_each_finding_has_exactly_one_fix_task():
    from nio import jury
    root = fix_repo()
    fix_gate(root, {"title": "a missing one"}, {"title": "a partial one", "gap": "partial", "cites": "AC-2"},
             {"title": "a small one", "severity": "minor", "cites": "AC-4"})
    assert recorded(root)[0] == 1, "the outcome isn't rejected"
    once = task_file(root).read_text()
    by = fix_tasks_for(root)
    assert sorted(by) == ["J-1", "J-2"], f"one task per open major and none for the minor, not {sorted(by)}"
    assert [len(x) for x in by.values()] == [1, 1], by
    tasks_pass(root)
    code, out = recorded(root)  # the same round's outcome, composed a second time
    assert code != 0 and "outcome: approved" not in out, f"a fix task nobody has done yet approved the epic: {out}"
    assert task_file(root).read_text() == once, "composing the same round again changed tasks.md"
    led = jury.load(root, "s", GATE)
    for fid in ("J-1", "J-2"):
        f = next(x for x in led["findings"] if x["id"] == fid)
        assert (f["status"], f["disposition"]) == ("disposed", "fix-task"), f
        assert fid in jury.pack_ids(led, "conformance"), f"{fid}: its lens gets no fix verdict on it"
        assert append_fix(root, f) is None, f"{fid} got a second task"
    assert task_file(root).read_text() == once
    print("ok")


def test_the_four_tasks_are_unchanged_and_the_new_one():
    root = fix_repo()
    (f,) = fix_gate(root, {"title": "the next finding"})
    path = task_file(root)
    old, old_ids = path.read_text(), set(parsed_tasks(root))
    old_blocks = {t: x["block"] for t, x in parsed_tasks(root).items()}
    inode, around = path.stat().st_ino, sorted(os.listdir(path.parent))
    assert append_fix(root, f) == "T-6", "T-1 to T-5 are taken"  # J-11 already has a task; J-1 doesn't
    new = path.read_text()
    head, tail = old.split("\n## E-2 Second")
    assert new.startswith(head) and new.endswith("\n## E-2 Second" + tail), f"bytes around the new task changed:\n{new}"
    now = parsed_tasks(root)
    assert set(now) - old_ids == {"T-6"} and {t: now[t]["block"] for t in old_ids} == old_blocks, now
    assert now["T-6"]["fix"] and now["T-6"]["epic"] == "E-1", now["T-6"]
    assert path.stat().st_ino != inode, "tasks.md was written in place, not through a rename"
    assert sorted(os.listdir(path.parent)) == around, "the temporary file stayed"
    tasks_pass(root)
    print("ok")


def test_the_next_free_id_skips_a_retired_one():
    root = fix_repo(earlier="", retired="[T-8]")
    (f,) = fix_gate(root, {"title": "the next finding"})
    assert append_fix(root, f) == "T-9", "T-8 is retired and is never used again"
    tasks_pass(root)
    print("ok")


def test_a_first_fix_opens_the_section_inside_its_epic():
    root = fix_repo(earlier="")
    (f,) = fix_gate(root, {"title": "the first finding"})
    path = task_file(root)
    old = path.read_text()
    assert append_fix(root, f) == "T-5", "T-1 to T-4 are taken"
    new, task = path.read_text(), parsed_tasks(root)["T-5"]
    assert task["fix"] and task["epic"] == "E-1", task
    head, tail = old.split("\n## E-2 Second")
    assert new.startswith(head) and new.endswith("\n## E-2 Second" + tail), f"bytes around the new task changed:\n{new}"
    tasks_pass(root)
    print("ok")


def test_a_finding_of_another_epic_with_the_same_id_is_another_finding():
    root = fix_repo(earlier="J-1")  # E-1's J-1 has its task; E-2's ledger counts from J-1 too
    (f,) = fix_gate(root, {"title": "E-2's own finding", "cites": "AC-3", "where": "src/four.py", "quote": '"FOUR_MARK"'}, epic="E-2")
    path = task_file(root)
    path.write_text(path.read_text().rstrip("\n"))  # E-2 ends the file, here with no last newline
    old = path.read_text()
    assert append_fix(root, f, "E-2") == "T-6", "E-1's J-1 isn't E-2's"
    new, task = path.read_text(), parsed_tasks(root)["T-6"]
    assert new.startswith(old) and task["fix"] and task["epic"] == "E-2", new
    assert task["fields"]["From"] == "J-1 (implementation-E-2, round 1)", task
    tasks_pass(root)
    print("ok")


def test_a_fix_task_holds_each_field_of_its_contract_and_passes_the_check():
    from nio import jury, tasks
    root = fix_repo()
    fix_gate(root, {"title": "cited AC has a TC"},
             {"title": "asks for a run", "run": "TC-3", "where": "src/two.py", "quote": '"TWO_MARK"'},
             {"title": "cited CT has a TC", "cites": "CT-2"},
             {"title": "cited AC has none", "cites": "AC-4"},
             {"title": "cited FR has none", "cites": "FR-2"})
    assert jury.load(root, "s", GATE)["findings"][1]["sources"][0]["run"] == "TC-3", "the fixture's run is on its source"
    assert recorded(root)[0] == 1, "the outcome isn't rejected"
    by = fix_tasks_for(root)
    assert sorted(by) == ["J-1", "J-2", "J-3", "J-4", "J-5"], sorted(by)
    tests = {"J-1": "TC-1", "J-2": "TC-3", "J-3": "TC-2", "J-4": "new: AC-4", "J-5": "new: FR-2"}
    cites = {"J-1": "AC-1", "J-2": "AC-1", "J-3": "CT-2", "J-4": "AC-4", "J-5": "FR-2"}
    for fid, (task,) in by.items():
        f = task["fields"]
        assert task["fix"] and task["epic"] == "E-1", task
        assert f["From"] == f"{fid} (implementation-E-1, round 1)", f
        assert f["Test"] == tests[fid], (fid, f["Test"])
        assert cites[fid] in tasks.ids(f["Serves"]), (fid, f["Serves"])
        assert tasks.files(f["Files"]) == ["src/two.py" if fid == "J-2" else "src/one.py"], f["Files"]
        assert (f["Depends on"], f["Parallel"], f["Effort"]) == ("none", "no", "med"), f
        assert f["Tier"] == "strong: a fix from a jury finding" and f["Mode"] == "single: a fix from a jury finding", f
        assert "justify or remove" not in " ".join(task["block"]).lower(), f"{fid} isn't unrequested: {task['block']}"
    tasks_pass(root)
    print("ok")


def test_a_cli_finding_with_no_cite_still_gets_a_task_the_check_passes():
    from nio import jury
    root = fix_repo()
    fix_gate(root)
    jury.record_cli(root, "s", GATE, [{"title": "UNUSED in src/one.py is never used", "severity": "major", "gap": "unrequested", "cite": "", "where": "src/one.py"}])
    assert recorded(root)[0] == 1, "the outcome isn't rejected"
    (task,) = fix_tasks_for(root)["J-1"]
    assert "justify or remove" in " ".join(task["block"]).lower(), task
    tasks_pass(root)
    print("ok")


def test_only_the_findings_the_decision_table_sends_to_a_task_get_one():
    root = fix_repo()
    fix_gate(root, {"title": "the spec is right", "gap": "contradicts", "right": "spec"},
             {"title": "the code is right", "gap": "contradicts", "right": "code", "cites": "AC-2"})
    assert recorded(root)[0] == 1, "the outcome isn't rejected"
    assert sorted(fix_tasks_for(root)) == ["J-1"], "a contradicts finding whose code is right goes to a change request, not a task"
    print("ok")


def test_test_new_needs_a_from_line():
    from test_tasks import SLUG, chain, errs, field, fix, repo
    assert errs(repo(chain(fix(), field("T-4", "Test", "new: AC-1")))) == [], "a fix task may say `Test: new: <cite>`"
    assert errs(repo(chain(fix(), field("T-4", "Test", "new: FR-1")))) == [], "a fix task may cite an FR"
    for route in ("full", "lite"):
        found = [e for e in errs(repo(field("T-1", "Test", "new: AC-1"), route=route)) if e.startswith("T-1")]
        assert any("new:" in e and "From" in e for e in found), f"{route}: a planned task said `Test: new:` and passed: {found}"
    root = repo(chain(fix(), field("T-4", "Test", "new: AC-1"), lambda t: t.replace("- From: J-4 (implementation-E-1, round 1)\n", "")))
    done = nio(root, "check", "tasks", SLUG)
    assert done.returncode != 0 and "From" in done.stdout + done.stderr, done.stdout + done.stderr
    print("ok")


def test_the_fix_task_disposition_belongs_to_this_gate_only():
    from nio import jury
    assert "fix-task" in jury.DISPOSITIONS and "fix-task" in jury.FIXES, "`fix-task` isn't a disposition that a lens checks"
    root = fix_repo()
    (f,) = fix_gate(root, {"title": "a finding"})
    (root / ".nio/specs/s/spec.md").write_text(FIX_SPEC)
    led = jury.load(root, "s", "spec")
    led["findings"].append({**f, "sources": [{**f["sources"][0], "lens": "logic"}]})
    jury.save(root, led)
    try:
        jury.dispose(root, "s", "spec", f["id"], "fix-task", "agent", "a note")
        raise AssertionError("the spec gate took a fix-task disposition")
    except ValueError as e:
        assert "fix-task" in str(e), e
    print("ok")


def test_a_justify_or_remove_task_is_appended_and_the():
    root = fix_repo()
    (f,) = fix_gate(root, {"title": "nobody asked for this", "gap": "unrequested"})
    code = (root / "src/one.py").read_bytes()
    tid = append_fix(root, f)
    assert tid == "T-6", tid
    assert "justify or remove" in " ".join(parsed_tasks(root)[tid]["block"]).lower(), parsed_tasks(root)[tid]
    assert list(fix_tasks_for(root)) == ["J-1"] and len(fix_tasks_for(root)["J-1"]) == 1, fix_tasks_for(root)
    assert (root / "src/one.py").read_bytes() == code, "the code was touched"
    assert git(root, "diff", "--stat", "HEAD", "--", "src", "tests") == "", "the code differs from the epic's commit"
    print("ok")


def test_an_old_task_is_never_rewritten_and_code_never_deleted():
    root = fix_repo()
    fix_gate(root, {"title": "nobody asked for this", "gap": "unrequested"})
    old = parsed_tasks(root)
    code = (root / "src/one.py").read_bytes()
    for _ in range(2):
        code_exit, out = recorded(root)
        assert code_exit != 0 and "outcome: approved" not in out, out
    now = parsed_tasks(root)
    assert {t: now[t]["block"] for t in old} == {t: x["block"] for t, x in old.items()}, "an old task changed"
    (new,) = set(now) - set(old)
    assert "justify or remove" in " ".join(now[new]["block"]).lower(), now[new]
    assert (root / "src/one.py").read_bytes() == code, "the code was touched"
    assert git(root, "diff", "--stat", "HEAD", "--", "src", "tests") == "", "the code differs from the epic's commit"
    tasks_pass(root)
    print("ok")


# --- T-23: close the loop on a round (CT-13, CT-14, CT-17, CT-20; AC-32, AC-34, AC-38, AC-40, AC-56) ---

E1_MATCHES = ("AC-1 -> tests/test_calc.py:5", "AC-2 -> tests/test_calc.py:9", "AC-4 -> tests/test_calc.py:17")
LINT = "grep -q LINT_OK src/one.py || (echo LINT-ERROR-7 in src/one.py; exit 1)"


def said(root, *args):
    """A `nio` call that must work: (no crash, exit 0, no invalid lens output). What it printed."""
    done = nio(root, *args)
    assert "Traceback" not in done.stderr, f"nio {' '.join(args)} crashed:\n{done.stderr}"
    assert done.returncode == 0 and "INVALID" not in done.stdout, f"nio {' '.join(args)}: {done.returncode}\n{done.stdout}{done.stderr}"
    return done.stdout


def looked(root, gate=GATE):
    """`nio jury check <gate>`, recording nothing, as the agent runs it first. (exit code, printed lines)"""
    done = nio(root, "jury", "check", "s", gate)
    assert "Traceback" not in done.stderr, done.stderr
    return done.returncode, done.stdout


def impl_out(root, run, lens="conformance", findings=(), verdicts=()):
    """A lens's output in `run`: `findings` are dicts of lines, title included; `verdicts` are `J-n: fixed - why` lines. A
    conformance output matches each of E-1's ACs to its test."""
    base = {"kind": "gap", "severity": "major", "evidence": "observed", "gap": "missing", "where": "src/one.py", "quote": '"ONE_MARK"',
            "situation": "x", "fix": "y", "cites": "AC-1"}
    body = "".join(f"### F{i} {f['title']}\n" + "".join(f"- {k}: {v}\n" for k, v in {**base, **f}.items() if k != "title") + "\n"
                   for i, f in enumerate(findings, 1)) or "none\n"
    matches = "## Matches\n" + "".join(f"- {x}\n" for x in E1_MATCHES) + "\n" if lens == "conformance" else ""
    said_verdicts = "## Verdicts\n" + "".join(f"- {v}\n" for v in verdicts) + "\n" if verdicts else ""
    path = root / f".nio/runs/{run}/jury/{GATE}-{lens}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'---\nlens: {lens}\ngate: {GATE}\nsubject: s\nby: "juror / claude-code / sonnet"\ncontext: sufficient\n---\n'
                    f"## Reasoning\nChecked.\n\n{matches}{said_verdicts}## Findings\n{body}")
    fill(root, GATE, run, E1_MATCHES)


def collected(root, run):
    """`nio jury collect`, and the refuter confirming whatever waits on it."""
    from nio import jury
    said(root, "jury", "collect", "s", GATE, "--run", run)
    pending = [f["id"] for f in jury.load(root, "s", GATE)["findings"] if f["validation"] == "pending" and f["status"] in ("open", "disposed")]
    if pending:
        (root / f".nio/runs/{run}/jury/{GATE}-refuter.md").write_text("".join(f"### {i}\n- result: confirmed\n- reason: it is so\n\n" for i in pending))
        said(root, "jury", "collect", "s", GATE, "--run", run)
    return {f["id"]: f for f in jury.load(root, "s", GATE)["findings"]}


def finish_fixes(root, edits=None):
    """The implement stage finishes every task of E-1 not done, in order, each with its own commit: `edits[T-n]` is what it
    appends to src/one.py, by default a comment."""
    from nio import flow, implement
    lines = flow.read(root, "s")[1]
    states = implement.status(root, "s", lines)
    history = root / ".nio/specs/s/history.jsonl"
    done = [t for t in implement.tasks_of(root, "s") if t["epic"] == "E-1" and states[t["id"]] != "done"]
    assert done, "there is no fix task to finish"
    for t in done:
        with (root / "src/one.py").open("a") as f:
            f.write((edits or {}).get(t["id"], f"# touched by {t['id']}\n"))
        with history.open("a") as f:
            f.writelines(json.dumps({"kind": k, "from": "implementing", "to": "implementing", "end": True,
                                     "evidence": {"task": t["id"], "commit": "c", "passed": True}}) + "\n"
                         for k in ("claim", "red", "green", "review", "task_done"))
        git(root, "add", "-A")
        git(root, "commit", "-qm", f"{t['id']}: {t['title']}")
    return [t["id"] for t in done]


def rerun_lenses(root):
    """The lenses `nio jury changed` says to re-run."""
    line = next(x for x in said(root, "jury", "changed", "s", GATE).splitlines() if x.startswith("re-run: "))
    return line[len("re-run: "):].split(", ")


def rejected_round(root, *findings, run="R-1"):
    """Round 1 through the CLI, conformance raising `findings`, recorded as rejected. {finding ID: its fix task's ID}."""
    said(root, "jury", "evidence", "s", "E-1", "--run", run)
    impl_out(root, run, findings=findings)
    collected(root, run)
    code, out = recorded(root)
    assert code == 1 and "outcome: rejected" in out, f"round 1 isn't rejected: {code}\n{out}"
    return {fid: tasks[0]["id"] for fid, tasks in fix_tasks_for(root).items()}


def broken_repo():
    """fix_repo at whose last commit the lint check fails (src/one.py has no LINT_OK) and test_one, AC-1's test, fails."""
    root = fix_repo()
    (root / ".nio/config.json").write_text(json.dumps({"tests": {"suite": JOIN_SUITE, "lint": LINT}}))
    (root / "tests/test_calc.py").write_text(FIX_SUITE.replace("self.assertEqual(1, 1)", "self.assertEqual(1, 2)"))
    git(root, "add", "-A")
    git(root, "commit", "-qm", "T-1: Build one, as it ended up")
    return root


def cli_round(root):
    """Round 1 of `broken_repo` through the CLI, with no finding from any lens: J-1 is the failed lint check, J-2 AC-1's
    missing evidence. Rejected, with one fix task each. {finding ID: its fix task's ID}."""
    tasks = rejected_round(root)
    assert sorted(tasks) == ["J-1", "J-2"], f"the fixture isn't clean: {tasks}"
    tasks_pass(root)
    led = {f["id"]: f for f in gate_findings(root, cli=True)}
    assert "lint" in led["J-1"]["title"] and "AC-1" in led["J-2"]["title"], led
    assert all(f["sources"][0]["lens"] == "cli" and f["disposition"] == "fix-task" for f in led.values()), led
    return tasks


def is_not_fixed(f, rounds=1):
    assert (f["status"], f["disposition"], f["baseline"], f["rounds"]) == ("open", "", "unchanged", rounds), f"{f['id']} isn't `not fixed`: {f}"


def is_fixed(f):
    assert (f["status"], f["baseline"]) == ("fixed", "absent"), f"{f['id']} isn't `fixed`: {f}"


def test_it_is_rejected_one_fix_task_is_appended_for():
    root = fix_repo()
    fix_gate(root, {"title": "a missing one"}, {"title": "a small one", "severity": "minor", "cites": "AC-2"})
    before = task_file(root).read_bytes()
    code, out = looked(root)
    assert code == 1 and "outcome: rejected" in out, (code, out)
    assert task_file(root).read_bytes() == before, "a check that records nothing wrote a task"
    code, out = recorded(root)
    assert code == 1 and "outcome: rejected" in out, (code, out)
    by = fix_tasks_for(root)
    assert sorted(by) == ["J-1"] and len(by["J-1"]) == 1, f"exactly one new task, for the major, not {by}"
    assert "AC-1" in by["J-1"][0]["fields"]["Serves"], by["J-1"]
    print("ok")


def test_it_is_rejected_and_a_fix_task_is_appended():
    from nio import flow, implement, jury
    root = fix_repo()
    fix_gate(root, {"title": "a missing one"})
    code, out = recorded(root)
    assert code == 1 and "outcome: rejected" in out, (code, out)
    ((fid, tasks),) = fix_tasks_for(root).items()
    assert fid == "J-1" and len(tasks) == 1 and "From" in tasks[0]["fields"], tasks
    tid = tasks[0]["id"]
    assert tid in out, f"the outcome doesn't name the new task: {out}"
    assert jury.load(root, "s", GATE)["outcome"] == "rejected"
    assert implement.next_ready(root, "s", flow.read(root, "s")[1])["id"] == tid, "the epic isn't back with the implement stage"
    done = nio(root, "jury", "evidence", "s", "E-1", "--run", "R-2")
    assert done.returncode and tid in done.stderr and "Traceback" not in done.stderr, f"the gate ran with {tid} not done: {done.stderr}"
    print("ok")


def test_it_is_approved_and_no_task_is_written():
    root = fix_repo()
    fix_gate(root)
    before = task_file(root).read_bytes()
    code, out = looked(root)
    assert code == 0 and "outcome: approved" in out, (code, out)
    code, out = recorded(root)
    assert code == 0 and "outcome: approved" in out, (code, out)
    assert task_file(root).read_bytes() == before, "an approved gate changed tasks.md"
    print("ok")


def test_it_is_human_not_rejected_as_at_the_spec():
    root = fix_repo()
    fix_gate(root, {"title": "a missing one"})
    assert recorded(root)[0] == 1, "round 1 isn't rejected"
    finish_fixes(root)
    tasks = task_file(root).read_bytes()
    said(root, "jury", "evidence", "s", "E-1", "--run", "R-2")
    impl_out(root, "R-2", findings=[{"title": "a new major", "cites": "AC-2", "where": "src/two.py", "quote": '"TWO_MARK"'}],
             verdicts=["J-1: fixed - it is there now"])
    found = collected(root, "R-2")
    is_fixed(found["J-1"])
    assert found["J-2"]["status"] == "noted", found["J-2"]
    code, out = looked(root)
    assert code == 3 and "outcome: human" in out and "J-2" in out, (code, out)
    code, out = recorded(root)
    assert code == 3 and "outcome: human" in out and "J-2" in out, f"nothing else is open: a new major goes to the human, not {code}\n{out}"
    assert task_file(root).read_bytes() == tasks, "a new major in a re-review got a task"
    print("ok")


def test_that_round_is_a_re_review_of_the_open():
    from nio import jury
    root = fix_repo()
    said(root, "jury", "evidence", "s", "E-1", "--run", "R-1")
    impl_out(root, "R-1", findings=[{"title": "conformance's own", "fix": "FIX-ASKED-5"}])
    impl_out(root, "R-1", "correctness", [{"title": "correctness's own", "cites": "AC-2", "where": "src/two.py", "quote": '"TWO_MARK"', "fix": "FIX-ASKED-6"}])
    collected(root, "R-1")
    code, out = recorded(root)
    assert code == 1 and "outcome: rejected" in out, (code, out)
    led = jury.load(root, "s", GATE)
    assert led["round"] == 1 and sorted(fix_tasks_for(root)) == ["J-1", "J-2"], led
    judged = led["versions"]["1"]
    finish_fixes(root, {"T-6": "FIX_MARK_ONE = 1\n", "T-7": "FIX_MARK_TWO = 1\n"})
    said(root, "jury", "evidence", "s", "E-1", "--run", "R-2")
    assert rerun_lenses(root) == ["conformance", "correctness"], rerun_lenses(root)
    for lens, mine, other, fix in (("conformance", "J-1", "J-2", "FIX-ASKED-5"), ("correctness", "J-2", "J-1", "FIX-ASKED-6")):
        for name, text in (("nio jury fixcheck", said(root, "jury", "fixcheck", "s", GATE, "--lens", lens)),
                           ("evidence.pack", evidence().pack(root, "s", GATE, lens, "R-2"))):
            heads = text.splitlines()
            assert "fix check" in text.lower(), f"{name} for {lens} isn't a fix check:\n{text}"
            assert any(x.startswith(f"### {mine} ") for x in heads) and fix in text, f"{name} for {lens} lacks {mine} and its fix:\n{text}"
            assert not any(x.startswith(f"### {other} ") for x in heads), f"{name} for {lens} holds another lens's {other}:\n{text}"
            assert judged[:8] in text, f"{name} for {lens} doesn't start its diff at the commit round 1 judged, {judged[:8]}:\n{text}"
            assert "+FIX_MARK_ONE = 1" in text and "+FIX_MARK_TWO = 1" in text, f"{name} for {lens} lacks the fixes' diff:\n{text}"
            assert "+THREE_MARK = 1" not in text, f"{name} for {lens} holds code from before the commit round 1 judged:\n{text}"
    impl_out(root, "R-2", verdicts=["J-1: fixed - it is there now"])
    impl_out(root, "R-2", "correctness", verdicts=["J-2: fixed - it is there now"])
    found = collected(root, "R-2")
    led = jury.load(root, "s", GATE)
    assert led["round"] == 2, f"the round number didn't rise by 1: {led['round']}"
    assert jury.phase(led) == "re-review", jury.phase(led)
    is_fixed(found["J-1"])
    is_fixed(found["J-2"])
    code, out = recorded(root)
    assert code == 0 and "outcome: approved" in out, (code, out)
    print("ok")


def test_an_unset_right_side_goes_to_a_fix_task():
    root = fix_repo()
    fix_gate(root, {"title": "it says otherwise", "gap": "contradicts"})
    code, out = looked(root)
    assert code == 1 and "outcome: rejected" in out, (code, out)
    code, out = recorded(root)
    assert code == 1 and "outcome: rejected" in out, (code, out)
    by = fix_tasks_for(root)
    assert sorted(by) == ["J-1"] and len(by["J-1"]) == 1 and "AC-1" in by["J-1"][0]["fields"]["Serves"], by
    assert not list((root / ".nio/memory").rglob("C-*.md")), "an unset right side raised a change record"
    print("ok")


def test_a_fix_task_that_did_not_fix_the_check():
    """The failing test stays failing, by the T-7 commit touching nothing of it; the lint check passes after T-6."""
    root = broken_repo()
    tasks = cli_round(root)
    finish_fixes(root, {tasks["J-1"]: "LINT_OK = 1\n"})
    file = task_file(root).read_bytes()
    said(root, "jury", "evidence", "s", "E-1", "--run", "R-2")
    found = {f["id"]: f for f in gate_findings(root, cli=True)}
    assert sorted(found) == ["J-1", "J-2"], f"the fix tasks raised new findings: {list(found.values())}"
    is_fixed(found["J-1"])
    assert found["J-2"]["status"] != "fixed", f"evidence alone marked the failing test's finding fixed: {found['J-2']}"
    assert "conformance" in rerun_lenses(root), "no lens re-runs, so nothing would ever join the results again"
    impl_out(root, "R-2")  # no verdict: no juror can give one on a CLI finding
    found = collected(root, "R-2")
    assert sorted(found) == ["J-1", "J-2"], found
    is_fixed(found["J-1"])
    is_not_fixed(found["J-2"])
    code, out = looked(root)
    assert code == 3 and "outcome: human" in out and "J-2" in out, f"a `not fixed` with no new task goes to the human: {code}\n{out}"
    code, out = recorded(root)
    assert code == 3 and "outcome: human" in out and "J-2" in out, f"a `not fixed` with no new task goes to the human: {code}\n{out}"
    assert task_file(root).read_bytes() == file, "the `not fixed` finding got a second task"
    print("ok")


def test_a_failed_check_its_fix_task_left_failing_is_not_fixed():
    root = broken_repo()
    tasks = cli_round(root)
    (root / "tests/test_calc.py").write_text(FIX_SUITE)
    finish_fixes(root)  # the suite passes now; the lint check still doesn't
    file = task_file(root).read_bytes()
    for _ in range(2):  # a second run in the round is no second failed round
        said(root, "jury", "evidence", "s", "E-1", "--run", "R-2")
        found = {f["id"]: f for f in gate_findings(root, cli=True)}
        assert sorted(found) == ["J-1", "J-2"], f"a repeat raised a new finding: {list(found.values())}"
        is_not_fixed(found["J-1"])
    assert found["J-2"]["status"] != "open", f"evidence reopened the finding only `join` can judge: {found['J-2']}"
    impl_out(root, "R-2")
    found = collected(root, "R-2")
    is_not_fixed(found["J-1"])
    is_fixed(found["J-2"])
    assert tasks["J-1"] in {t["id"] for t in fix_tasks_for(root)["J-1"]} and len(fix_tasks_for(root)["J-1"]) == 1, fix_tasks_for(root)
    code, out = recorded(root)
    assert code == 3 and "outcome: human" in out and "J-1" in out, f"a `not fixed` with no new task goes to the human: {code}\n{out}"
    assert task_file(root).read_bytes() == file, "the `not fixed` finding got a second task"
    print("ok")


def test_a_lens_blocker_not_fixed_with_its_task_done_goes_to_the_human():
    root = fix_repo()
    rejected_round(root, {"title": "a blocker", "severity": "blocker"})
    finish_fixes(root)
    file = task_file(root).read_bytes()
    said(root, "jury", "evidence", "s", "E-1", "--run", "R-2")
    impl_out(root, "R-2", verdicts=["J-1: not fixed - it is still gone"])
    found = collected(root, "R-2")
    assert (found["J-1"]["status"], found["J-1"]["validation"]) == ("open", "confirmed"), found["J-1"]
    code, out = recorded(root)
    assert code == 3 and "outcome: human" in out and "J-1" in out, f"rejected with no new task leaves the epic going nowhere: {code}\n{out}"
    assert task_file(root).read_bytes() == file, "the `not fixed` finding got a second task"
    print("ok")


def test_a_not_fixed_finding_beside_a_new_blocker_is_rejected_with_the_new_task():
    root = fix_repo()
    rejected_round(root, {"title": "a blocker", "severity": "blocker"})
    finish_fixes(root)
    said(root, "jury", "evidence", "s", "E-1", "--run", "R-2")
    impl_out(root, "R-2", findings=[{"title": "a new blocker", "severity": "blocker", "cites": "AC-2", "where": "src/two.py", "quote": '"TWO_MARK"'}],
             verdicts=["J-1: not fixed - it is still gone"])
    collected(root, "R-2")
    code, out = recorded(root)
    assert code == 1 and "outcome: rejected" in out, f"a new blocker has new work to send back: {code}\n{out}"
    by = fix_tasks_for(root)
    assert len(by["J-1"]) == 1 and len(by["J-2"]) == 1, by
    print("ok")


def test_every_cli_fix_that_held_approves_the_epic_with_no_juror_verdict():
    root = broken_repo()
    tasks = cli_round(root)
    (root / "tests/test_calc.py").write_text(FIX_SUITE)
    finish_fixes(root, {tasks["J-1"]: "LINT_OK = 1\n"})
    said(root, "jury", "evidence", "s", "E-1", "--run", "R-2")
    assert "conformance" in rerun_lenses(root), "no lens re-runs, so the gate could never compose again"
    impl_out(root, "R-2")
    found = collected(root, "R-2")
    is_fixed(found["J-1"])
    is_fixed(found["J-2"])
    code, out = recorded(root)
    assert code == 0 and "outcome: approved" in out, (code, out)
    print("ok")


def test_only_a_fix_task_entry_takes_the_clis_fix_verdict():
    from nio import jury
    root = broken_repo()
    said(root, "jury", "evidence", "s", "E-1", "--run", "R-1")
    assert [f["id"] for f in gate_findings(root, cli=True)] == ["J-1"], gate_findings(root, cli=True)
    said(root, "jury", "evidence", "s", "E-1", "--run", "R-1")  # no fix task yet: still open, no failed round
    (f,) = gate_findings(root, cli=True)
    assert (f["status"], f["rounds"], f["baseline"]) == ("open", 0, "new"), f
    jury.dispose(root, "s", GATE, "J-1", "accepted-risk", "human", "we live with it")
    (root / ".nio/config.json").write_text(json.dumps({"tests": {"suite": JOIN_SUITE}}))  # the check isn't run any more
    said(root, "jury", "evidence", "s", "E-1", "--run", "R-1")
    (f,) = gate_findings(root, cli=True)
    assert (f["status"], f["disposition"]) == ("disposed", "accepted-risk"), f"what the human ruled was changed: {f}"
    print("ok")


def test_a_fix_tasks_pack_says_what_to_fix():
    from nio import implement
    root = fix_repo()
    rejected_round(root, {"title": "a missing one", "situation": "SITUATION-MARK-3 is wrong", "fix": "FIX-MARK-4 instead"},
                   {"title": "cites a contract", "cites": "CT-2", "where": "src/two.py", "quote": '"TWO_MARK"', "situation": "SITUATION-MARK-5 is wrong"})
    by_id = {t["id"]: t for t in implement.tasks_of(root, "s")}
    text = implement.worker_pack(root, "s", by_id["T-6"])
    assert "SITUATION-MARK-5" in implement.worker_pack(root, "s", by_id["T-7"]), "a task serving a CT has to pack too"
    assert "SITUATION-MARK-3" in text and "FIX-MARK-4" in text, f"the worker can't see what to fix:\n{text}"
    assert len(re.findall(r"^## ", text, re.M)) == 5, f"a worker pack has exactly five parts:\n{text}"
    plain = implement.worker_pack(root, "s", by_id["T-1"])
    assert "SITUATION-MARK-3" not in plain and "FIX-MARK-4" not in plain, f"a planned task got a finding's text:\n{plain}"
    implement.worker_pack(root, "s", by_id["T-5"])  # its From: names J-11, which no ledger holds: it still packs
    print("ok")


def test_a_fix_tasks_pack_holds_the_errors_of_the_check_it_fixes():
    from nio import implement
    root = broken_repo()
    tasks = cli_round(root)
    task = next(t for t in implement.tasks_of(root, "s") if t["id"] == tasks["J-1"])
    text = implement.worker_pack(root, "s", task)
    assert "LINT-ERROR-7" in text, f"a CLI finding has no `fix`: its errors are what the worker has to go on:\n{text}"
    print("ok")


# --- T-24: a code-is-right finding becomes a change request and holds the epic (CT-15; AC-36, AC-58, AC-59, FR-44) ---

def code_right(n=1):
    """A contradicts finding whose code is the right side. n=1 cites AC-2, n=2 cites AC-1 (a second, separate finding)."""
    one = {"title": "the code is right", "gap": "contradicts", "right": "code", "cites": "AC-2", "where": "src/two.py", "quote": '"TWO_MARK"'}
    two = {"title": "the code is right too", "gap": "contradicts", "right": "code", "cites": "AC-1"}
    return one if n == 1 else two


def cr_files(root):
    return sorted((root / ".nio/memory").rglob("C-*.md"))


def cr_one(root, found=None):
    found = cr_files(root) if found is None else found
    assert len(found) == 1, f"expected one change request, found {len(found)}"
    return found[0]


def cr_rule(root, path, outcome):
    """The human rules on a change request: its `outcome:` line."""
    path.write_text(re.sub(r"^outcome: \w+", f"outcome: {outcome}", path.read_text(), count=1, flags=re.M))


def cr_state(out):
    """The epic's state, from the `state:` line `nio jury check` prints at this gate as it does at the plan gate."""
    m = re.search(r"^state: (\S+)", out, re.M)
    assert m, f"`nio jury check` prints no `state:` line for the epic:\n{out}"
    return m[1]


def cr_naming(root, fid="J-1"):
    """The change records whose text names the finding and the gate."""
    return [p for p in cr_files(root) if re.search(rf"(?<![\w-]){fid}(?!\d)", p.read_text()) and GATE in p.read_text()]


def waiting_repo(*findings):
    """Round 1 of E-1 with `findings` confirmed, recorded: the epic waits on change. (root, spec.md's bytes before)"""
    root = fix_repo()
    fix_gate(root, *findings)
    spec_md = root / ".nio/specs/s/spec.md"
    before = spec_md.read_bytes()
    code, out = recorded(root)
    assert code == 1 and "outcome: rejected" in out and cr_state(out) == "waiting-on-change", f"the epic isn't waiting on change: {code}\n{out}"
    return root, before


def test_the_epic_waits_on_the_change_request_and_no():
    from nio import flow, implement
    root = fix_repo()
    fix_gate(root, code_right())
    tasks = task_file(root).read_bytes()
    code, out = looked(root)
    assert code == 1 and cr_state(out) == "waiting-on-change", f"the only open major is a code-is-right finding: {code}\n{out}"
    assert not cr_files(root), "a check that records nothing raised a change request"
    code, out = recorded(root)
    assert code == 1 and "outcome: rejected" in out and cr_state(out) == "waiting-on-change", (code, out)
    path = cr_one(root)
    assert path.name[:13] in out, f"the outcome doesn't name the change request it waits on: {out}"
    assert task_file(root).read_bytes() == tasks and not fix_tasks_for(root), "a fix task was appended while a change request is open"
    assert implement.next_ready(root, "s", flow.read(root, "s")[1]) is None, "the epic is back with the implement stage"
    code, out = recorded(root)  # asked again with the change request still pending: held, never approved
    assert code != 0 and "outcome: approved" not in out and cr_state(out) == "waiting-on-change", (code, out)
    print("ok")


def test_a_fix_task_citing_the_finding_is_appended_and():
    from nio import flow, implement
    root, _ = waiting_repo(code_right())
    path = cr_one(root)
    cr_rule(root, path, "rejected")
    code, out = recorded(root)
    assert code == 1 and cr_state(out) == "implementing", f"the ruling is recorded: the epic goes back to implementing:\n{code}\n{out}"
    by = fix_tasks_for(root)
    assert sorted(by) == ["J-1"] and len(by["J-1"]) == 1, f"exactly one new task, citing J-1, not {by}"
    tasks_pass(root)
    tid = by["J-1"][0]["id"]
    assert tid in out and implement.next_ready(root, "s", flow.read(root, "s")[1])["id"] == tid, "the epic isn't back with the implement stage"
    recorded(root)  # a repeat appends no second task
    assert len(fix_tasks_for(root)["J-1"]) == 1 and len(cr_files(root)) == 1, "a repeat appended a second task or raised a second request"
    print("ok")


def test_a_change_request_is_raised_and_spec_md_is():
    from nio import jury
    root = fix_repo()
    fix_gate(root, code_right())
    spec_md = root / ".nio/specs/s/spec.md"
    before = spec_md.read_bytes()
    recorded(root)
    path = cr_one(root)
    meta = jury.change_record(root, path.name[:13])[1]
    text = path.read_text()
    assert meta.get("type") == "change" and meta.get("outcome") == "pending", f"the request isn't a pending change record: {meta}"
    assert "spec.md" in meta.get("against", ""), f"it isn't against the spec: {meta}"
    assert "J-1" in text and GATE in text and "AC-2" in text, f"the record doesn't cite the finding, the gate and the spec item:\n{text}"
    assert spec_md.read_bytes() == before, "spec.md changed"
    print("ok")


def test_the_spec_is_never_edited_to_match_the_code():
    root = fix_repo()
    fix_gate(root, code_right())
    spec_dir = root / ".nio/specs/s"
    before = {n: (spec_dir / n).read_bytes() for n in ("spec.md", "contracts.md", "tests.md", "plan.md")}
    code, out = recorded(root)
    assert code == 1, (code, out)
    assert {n: (spec_dir / n).read_bytes() for n in before} == before, "the spec or the plan changed to match the code"
    path = cr_one(root, cr_naming(root))
    assert re.search(r"^outcome: pending", path.read_text(), re.M) and len(cr_files(root)) == 1, "not exactly one pending change request"
    print("ok")


def test_a_repeat_raises_no_second_change_request():
    from nio import jury
    root = fix_repo()
    fix_gate(root, code_right())
    real = jury.save

    def flaky(r, led):  # the ledger save fails once the change request is raised
        if cr_files(r):
            raise OSError("disk full")
        real(r, led)

    jury.save = flaky
    try:
        jury.check(root, "s", GATE, record=True)
        raise AssertionError("the save never failed: no change request was raised before the ledger save")
    except OSError:
        pass
    finally:
        jury.save = real
    assert len(cr_naming(root)) == 1, f"a stop before the ledger save lost or doubled the request: {cr_files(root)}"
    for _ in range(2):  # twice more through the CLI, as the human runs it
        code, out = recorded(root)
        assert code == 1 and cr_state(out) == "waiting-on-change", (code, out)
    assert len(cr_files(root)) == 1 and len(cr_naming(root)) == 1, f"a repeat raised a second change request: {cr_files(root)}"
    print("ok")


def test_two_change_requests_hold_the_epic_until_the_human_rules_on_each():
    root, before = waiting_repo(code_right(1), code_right(2))
    assert len(cr_naming(root, "J-1")) == 1 and len(cr_naming(root, "J-2")) == 1 and set(cr_files(root)) == {*cr_naming(root, "J-1"), *cr_naming(root, "J-2")}, \
        "not one change request per finding"
    cr_rule(root, cr_naming(root, "J-1")[0], "accepted")
    code, out = recorded(root)
    assert cr_state(out) == "waiting-on-change" and "outcome: approved" not in out and not fix_tasks_for(root), \
        f"one request ruled, one still pending: the epic stays held\n{code}\n{out}"
    cr_rule(root, cr_naming(root, "J-2")[0], "rejected")
    code, out = recorded(root)
    assert cr_state(out) == "implementing", f"both ruled, one rejected: the epic goes back to implementing\n{code}\n{out}"
    assert sorted(fix_tasks_for(root)) == ["J-2"] and len(fix_tasks_for(root)["J-2"]) == 1, \
        f"only the rejected request's finding becomes a task: {sorted(fix_tasks_for(root))}"
    assert (root / ".nio/specs/s/spec.md").read_bytes() == before, "spec.md changed"
    print("ok")


def test_every_change_request_accepted_releases_the_epic_with_no_task():
    root, before = waiting_repo(code_right(1), code_right(2))
    for path in cr_files(root):
        cr_rule(root, path, "accepted")
    code, out = recorded(root)
    assert "waiting-on-change" not in out and not fix_tasks_for(root), f"every request accepted: the gate composes again, with no task\n{code}\n{out}"
    assert (root / ".nio/specs/s/spec.md").read_bytes() == before, "spec.md changed"
    print("ok")


def approved_with_minors():
    """Epic E-1 with two minor findings and nothing else open, recorded as the human does. Returns (root, printed lines)."""
    root = fix_repo()
    fix_gate(root, {"title": "a small one", "severity": "minor", "cites": "AC-2"}, {"title": "another small one", "severity": "minor", "cites": "AC-4"})
    code, out = recorded(root)
    assert code == 0 and "outcome: approved" in out, (code, out)
    return root, out


def verdict_records(root):
    return [p.read_text() for p in (root / ".nio/memory").rglob("V-*.md")]


def test_it_is_approved_and_the_verdict_lists_both():
    root, _ = approved_with_minors()
    (text,) = verdict_records(root)
    assert "approved" in text and "a small one" in text and "another small one" in text, text
    print("ok")


def test_the_record_names_the_epic_the_outcome_and_the():
    root, _ = approved_with_minors()
    (text,) = verdict_records(root)
    head = text.split("\n---\n", 1)[0]
    assert "implementation-E-1" in head and "outcome: approved" in head and "(round 1)" in head, head
    print("ok")


def test_an_approved_verdict_names_every_minor_however_many_findings_were_settled_before():
    root = fix_repo()
    from nio import jury
    found = fix_gate(root, {"title": "a small one", "severity": "minor", "cites": "AC-2"},
                     {"title": "another small one", "severity": "minor", "cites": "AC-4"})
    led = jury.load(root, "s", GATE)
    early = [{**found[0], "id": f"J-{n}", "title": f"settled earlier {n}", "severity": "major", "status": "disposed",
              "disposition": "accepted-risk", "by": "human", "note": "fine"} for n in range(3, 12)]
    led["findings"] = early + led["findings"]  # nine settled findings sit ahead of the two minors
    jury.save(root, led)
    code, out = recorded(root)
    assert code == 0 and "outcome: approved" in out, (code, out)
    (text,) = verdict_records(root)
    assert "a small one" in text and "another small one" in text, f"a minor is cut off the approved verdict:\n{text}"
    assert len(text.splitlines()) < 40, len(text.splitlines())
    done = nio(root, "check")
    assert done.returncode == 0, done.stdout + done.stderr
    print("ok")


def noted_major_on_the_list():
    """J-1 fixed, J-2 a new major noted in the re-review: the recorded outcome is human, J-2 on the list. (root, J-2)"""
    from nio import jury
    root = fix_repo()
    fix_gate(root, {"title": "a missing one"})
    recorded(root)
    finish_fixes(root)
    said(root, "jury", "evidence", "s", "E-1", "--run", "R-2")
    impl_out(root, "R-2", findings=[{"title": "a new major", "cites": "AC-2", "where": "src/two.py", "quote": '"TWO_MARK"'}],
             verdicts=["J-1: fixed - it is there now"])
    collected(root, "R-2")
    assert recorded(root)[0] == 3, "the list isn't with the human"
    led = jury.load(root, "s", GATE)
    return root, next(f for f in led["findings"] if f["id"] == "J-2")


def test_the_human_can_rule_on_a_noted_major_fix_or_accept():
    from nio import jury
    root, f = noted_major_on_the_list()
    assert f["status"] == "noted", f
    jury.dispose(root, "s", GATE, "J-2", "accepted-risk", "human", "fine")  # accept: refused today, the finding isn't open
    assert jury.load(root, "s", GATE)["findings"][-1]["status"] == "disposed"
    print("ok")


def test_a_fix_task_for_it_is_appended_to_the():
    from nio import jury
    root, f = noted_major_on_the_list()
    tid = append_fix(root, f)
    assert tid, "no fix task for the noted major the human chose to fix"
    (task,) = fix_tasks_for(root)["J-2"]
    assert task["fields"]["From"].startswith("J-2 "), task
    jury.dispose(root, "s", GATE, "J-2", "fix-task", "human", "fix it")
    code, out = recorded(root)
    assert code != 0 and "outcome: approved" not in out, f"the final fix check ran before the task was done:\n{out}"
    finish_fixes(root)
    assert "approved" not in recorded(root)[1] or "final" in recorded(root)[1], "approved with no final fix check"
    print("ok")


def epic_done(root, gate=GATE):
    """`nio flow done <gate> s --by human`, as the human runs it."""
    done = nio(root, "flow", "done", gate, "s", "--by", "human")
    assert "Traceback" not in done.stderr, done.stderr
    return done


def flow_lines(root, kind):
    from nio import flow
    return [x for x in flow.read(root, "s")[1] if x["kind"] == kind]


def gate_files_clean(root):
    """Nothing of the ledger, tasks.md or a verdict record is left uncommitted."""
    dirty = [x for x in git(root, "status", "--porcelain", "--untracked-files=all").splitlines()
             if "/jury/" in x or "tasks.md" in x or "/V-" in x]
    assert not dirty, f"left uncommitted: {dirty}"


def test_each_recorded_outcome_is_committed():
    root = fix_repo()
    fix_gate(root, {"title": "a missing one"})
    code, out = recorded(root)
    assert code == 1 and "outcome: rejected" in out, (code, out)
    assert f"nio: jury {GATE} round 1" in git(root, "log", "--format=%s"), "the rejected outcome isn't committed"
    gate_files_clean(root)
    assert "tasks.md" in git(root, "show", "--name-only", "--format=", "HEAD"), "the commit doesn't hold the new task"
    tasks_pass(root)
    print("ok")


def test_an_approved_outcome_is_committed_by_flow_done_not_by_the_check():
    root, _ = approved_with_minors()
    assert "nio: jury" not in git(root, "log", "--format=%s"), "an approved outcome took a `nio: jury` commit"
    done = epic_done(root)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"nio: approve {GATE}" in git(root, "log", "--format=%s"), "no approval commit"
    gate_files_clean(root)
    print("ok")


def test_flow_done_writes_the_epic_line_with_the_outcome_as_its_reason():
    root, _ = approved_with_minors()
    assert not flow_lines(root, "epic")
    done = epic_done(root)
    assert done.returncode == 0, done.stdout + done.stderr
    (line,) = flow_lines(root, "epic")
    assert line["evidence"]["epic"] == "E-1" and line["reason"] == "approved", line
    assert not flow_lines(root, "pass") and "merge:" not in done.stdout, f"E-2 isn't closed yet:\n{done.stdout}"
    again = epic_done(root)
    assert len(flow_lines(root, "epic")) == 1, f"a second call wrote a second line:\n{again.stdout}"
    print("ok")


def test_flow_done_takes_a_gate_the_human_closed():
    root = fix_repo()
    fix_gate(root, {"title": "a missing one"})
    closed = nio(root, "jury", "check", "s", GATE, "--human", "good enough", "--record")
    assert closed.returncode == 3 or "outcome: human" in closed.stdout, closed.stdout + closed.stderr
    done = epic_done(root)
    assert done.returncode == 0, done.stdout + done.stderr
    (line,) = flow_lines(root, "epic")
    assert line["evidence"]["epic"] == "E-1" and line["reason"] == "human", line
    print("ok")


def test_flow_done_refuses_while_the_gate_is_not_approved_or_closed():
    untouched = fix_repo()  # no gate has run
    rejected = fix_repo()
    fix_gate(rejected, {"title": "a missing one"})
    recorded(rejected)
    for root in (untouched, rejected):
        head, history = git(root, "rev-parse", "HEAD"), (root / ".nio/specs/s/history.jsonl").read_bytes()
        done = epic_done(root)
        said_ = done.stdout + done.stderr
        assert done.returncode != 0 and "invalid choice" not in said_ and GATE in said_, f"not a refusal naming the gate:\n{said_}"
        assert (root / ".nio/specs/s/history.jsonl").read_bytes() == history and git(root, "rev-parse", "HEAD") == head, "a refusal wrote something"
    print("ok")


def test_flow_done_on_the_last_epic_writes_the_pass_line_and_prints_merge():
    root, _ = approved_with_minors()
    assert epic_done(root).returncode == 0
    fix_gate(root, epic="E-2")
    code, out = recorded(root, "implementation-E-2")
    assert code == 0 and "outcome: approved" in out, (code, out)
    done = epic_done(root, "implementation-E-2")
    assert done.returncode == 0, done.stdout + done.stderr
    assert [(x["evidence"]["epic"], x["reason"]) for x in flow_lines(root, "epic")] == [("E-1", "approved"), ("E-2", "approved")]
    (line,) = flow_lines(root, "pass")
    assert (line["from"], line["to"]) == ("implementing", "done"), line
    assert "merge:" in done.stdout, done.stdout
    print("ok")


def test_the_last_epics_gate_ends_the_effort():
    """TC-69. ponytail: one approving round; the reject-and-fix round is covered by the T-26 tests."""
    from nio import flow, implement
    root, _ = approved_with_minors()
    assert epic_done(root).returncode == 0
    task = next(t for t in implement.tasks_of(root, "s") if t["id"] == "T-4")
    entries, report = implement.epic_end(root, "s", task, {})
    assert not [e for e in entries if e["kind"] in ("epic", "pass")], entries
    assert not any(x.startswith("merge:") for x in report) and any("implementation-E-2" in x for x in report), report
    fix_gate(root, epic="E-2")
    code, out = recorded(root, "implementation-E-2")
    assert code == 0 and "outcome: approved" in out and "merge:" not in out, (code, out)
    assert not [x for x in flow_lines(root, "epic") if x["evidence"]["epic"] == "E-2"] and not flow_lines(root, "pass")
    done = epic_done(root, "implementation-E-2")
    assert done.returncode == 0 and "merge:" in done.stdout, done.stdout + done.stderr
    (e2,) = [x for x in flow_lines(root, "epic") if x["evidence"]["epic"] == "E-2"]
    assert e2["reason"] == "approved" and len(flow_lines(root, "pass")) == 1
    assert flow_lines(root, "pass")[0]["to"] == "done", flow_lines(root, "pass")
    print("ok")


def test_an_old_skipped_epic_stays_closed():
    """TC-70."""
    import test_flow
    import test_implement as ti
    from nio import implement
    root = ti.impl(tasks=ti.TWO)
    ti.finish(root, "T-1")
    ti.finish(root, "T-2")
    if not ti.epics(root):
        test_flow.history(root, ti.S, {"kind": "epic", "from": "implementing", "to": "implementing",
                                       "reason": "skipped: not built", "evidence": {"epic": "E-1"}})
    out = ti.flow(root, "next", ti.S)[1]
    assert "E-1" in out and "never reviewed" in out, out
    code, out = ti.flow(root, "claim", ti.S)
    assert code == 0 and "task: T-3 " in out, out
    assert not any("E-1" in x for x in implement.left(root, ti.S, ti.lines(root))), implement.left(root, ti.S, ti.lines(root))
    print("ok")


def test_the_cli_prints_the_pack():
    root = pack_repo({})
    start(root)
    done = nio(root, "jury", "pack", "s", GATE, "--lens", "conformance", "--run", "R-1")
    assert done.returncode == 0 and "DIFF_MARK = 42" in done.stdout, done.stdout + done.stderr
    print("ok")


def demo(which):
    """Print what quickstart.md's scenario `which` expects; the real path, fixed lens outputs, no model."""
    if which == "cap":
        print("\n".join(__import__("nio.jury", fromlist=["plan"]).plan(capped(), "s", GATE)[0]))
        return
    root = fix_repo()
    fix_gate(root, *({"approved": [], "rejected": [{"title": "a missing one"}], "stale": [code_right()]}[which]))
    out = recorded(root)[1]
    print(out)
    if "state: waiting-on-change" in out:
        print("the epic is waiting on change")  # the CLI's `state: waiting-on-change`, said in words


def test_a_later_open_gate_doesnt_hold_a_fix_in_an_earlier_epic():
    """C-261030-gk3z: an earlier epic with work left comes first, whatever a later epic's gate says."""
    from nio import implement
    status, tasks_of = implement.status, implement.tasks_of
    ts = [{"id": "T-1", "epic": "E-1"}, {"id": "T-2", "epic": "E-2"}]
    implement.tasks_of = lambda root, slug: ts
    try:
        implement.status = lambda root, slug, lines: {"T-1": "ready", "T-2": "done"}
        assert implement.open_gate(None, "s", []) is None
        implement.status = lambda root, slug, lines: {"T-1": "done", "T-2": "done"}
        assert implement.open_gate(None, "s", []) == "E-1"
        assert implement.open_gate(None, "s", [{"kind": "epic", "evidence": {"epic": "E-1"}}]) == "E-2"
    finally:
        implement.status, implement.tasks_of = status, tasks_of
    print("ok")


def test_expect_adversary_alone_cant_reach_approved():
    """J-2: at an implementation gate the core lenses are expected whatever --expect says."""
    from nio import jury
    root = lens_repo()
    gate = "implementation-E-1"
    out = root / ".nio/runs/R-1/jury"
    out.mkdir(parents=True)
    (out / f"{gate}-adversary.md").write_text("# adversary\n")
    jury.collect(root, "s", gate, "R-1", expect=("adversary",))
    led = jury.load(root, "s", gate)
    assert {"conformance", "correctness"} <= set(led["expect"]), led["expect"]
    assert jury.compose(led, jury.version(led, led["round"]))[0] != "approved"
    print("ok")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        demo(sys.argv[sys.argv.index("--demo") + 1])
        sys.exit()
    for name, test in list(globals().items()):
        if name.startswith("test_") and callable(test):
            test()
