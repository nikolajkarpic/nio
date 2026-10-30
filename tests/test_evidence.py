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
            if p.is_file() and ".git" not in p.relative_to(root).parts}
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


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_") and callable(test):
            test()
