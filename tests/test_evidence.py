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


def snapshot(root):
    """All TC-41 says must not change: the tree byte for byte, the refs, the config, the worktrees, and git's status."""
    tree = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(root).parts and p.relative_to(root).parts[:2] != (".nio", "runs")}
    return {"tree": tree, "refs": git(root, "for-each-ref"), "head": (root / ".git/HEAD").read_text(),
            "config": (root / ".git/config").read_text(), "worktrees": git(root, "worktree", "list", "--porcelain"),
            "status": git(root, "status", "--porcelain"), "log": git(root, "log", "--all", "--format=%H")}


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


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_") and callable(test):
            test()
