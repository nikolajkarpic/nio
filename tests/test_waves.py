"""Self-check for parallel epics (2026-11-05-parallel-waves; per epic since 2026-11-15-faster-flow).
Run: uv run python tests/test_waves.py"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import test_flow
from test_implement import BY, IND, RUN, S, TWO, code_with, epics, flow, impl, lines, state, write_test
from test_tasks import git

from nio import flow as nio_flow
from nio import implement, records
import selfcheck


def trees(root):
    return [x.split()[0] for x in git(root, "worktree", "list").splitlines()]  # paths: a first claim's branch switch stays


def tree_of(out):
    return next(x.split(": ", 1)[1] for x in out.splitlines() if x.startswith("worktree: "))


def test_two_independent_epics_claim_at_once():
    """TC-42: E-1 and E-2 share no dependency: both are claimed at once, E-2 in its own worktree, and its finish lands
    the worktree's changes and commits them; a second finish while the first runs is refused."""
    root = impl(tasks=IND)
    code, a = flow(root, "claim", S, "--by", "a / test / test")
    code2, b = flow(root, "claim", S, "--by", "b / test / test")
    assert code == 0 and code2 == 0 and "epic: E-1 " in a and "epic: E-2 " in b and "worktree:" not in a, (a, b)
    assert len(trees(root)) == 2 and sorted(state(root)["claims"]["epics"]) == ["E-1", "E-2"], trees(root)
    w = root / tree_of(b)
    sleeper = subprocess.Popen(["sleep", "30"])
    try:
        (root / f".nio/specs/{S}/running.json").write_text(json.dumps({
            "command": f"nio flow finish {S} E-2 --by x", "at": "2026-11-15T00:00:00Z", "pid": sleeper.pid,
            "host": __import__("socket").gethostname()}))
        code, out = flow(root, "finish", S, "E-2", "--by", "b / test / test")
        assert code != 0 and "E-2's tests are running" in out, out
    finally:
        sleeper.kill()
        (root / f".nio/specs/{S}/running.json").unlink()
    write_test(w)
    code_with(w)
    code, out = flow(root, "finish", S, "E-2", "--by", "b / test / test")
    assert code == 0 and "closed: E-2 " in out, out
    shown = set(git(root, "show", "--name-only", "--format=", "HEAD").split())
    assert {"app.py", "tests/test_refund.py"} <= shown and len(trees(root)) == 1, (shown, trees(root))
    assert epics(root)["E-2"][0] == "closed" and epics(root)["E-1"][0] == "claimed"
    print("ok")


def test_second_driver_gets_another_epic_or_none():
    """TC-52: E-2 waits on E-1, which driver A holds: driver B gets none, and A's claim stands."""
    root = impl(tasks=TWO)
    assert flow(root, "claim", S, "--by", "a / test / test")[0] == 0
    before = state(root)["claims"]
    code, out = flow(root, "claim", S, "--by", "b / test / test")
    assert code != 0 and "no epic ready; E-2 waits on E-1" in out, out
    assert state(root)["claims"] == before
    print("ok")


def test_ac17_bad_parallel_budget_is_refused():
    for v in (0, "two", True):
        root = impl(tasks=IND, cfg={"budgets": {"parallel": v}})
        before = len(lines(root))
        code, out = flow(root, "claim", S)
        assert code == 1 and "budgets.parallel" in out and repr(v) in out and len(lines(root)) == before, (v, out)
    root = impl(tasks=IND, cfg={"budgets": {"parallel": 1}})
    assert flow(root, "claim", S)[0] == 0
    code, out = flow(root, "claim", S)
    assert code == 1 and "budgets.parallel is 1" in out, out
    print("ok")


def test_ac16_worktree_failure_refuses_the_claim():
    root = impl(tasks=IND)
    assert flow(root, "claim", S)[0] == 0
    before, listed = len(lines(root)), trees(root)
    real = records.git

    def fake(r, *args, full=False, **kw):
        if args[:2] == ("worktree", "add"):
            return (128, "", "fatal: boom") if full else []
        return real(r, *args, full=full, **kw)
    records.git = fake
    try:
        implement.claim(root, S, by=BY)
        raise AssertionError("the claim must be refused")
    except ValueError as e:
        assert "can't create a worktree for E-2" in str(e) and "fatal: boom" in str(e), e
    finally:
        records.git = real
    assert len(lines(root)) == before and trees(root) == listed, (trees(root), listed)
    print("ok")


def test_ac5_nio_in_a_worktree_writes_the_root_state():
    root = impl(tasks=IND)
    flow(root, "claim", S)
    code, out = flow(root, "claim", S)
    w = root / tree_of(out)
    cwd = os.getcwd()
    try:
        os.chdir(w)
        assert records.repo_root() == root.resolve()
        other = Path(tempfile.mkdtemp()) / "other"
        git(root, "worktree", "add", str(other))
        os.chdir(other)
        assert records.repo_root() == other.resolve()
    finally:
        os.chdir(cwd)
    print("ok")


def test_ac6_second_guard_is_told_to_try_again():
    root = impl(tasks=TWO)
    flow(root, "claim", S)
    before, calls, real = len(lines(root)), [], implement.run
    implement.run = lambda *a: calls.append(a) or real(*a)
    try:
        with nio_flow.lock(root, S):
            t = time.time()
            code, o = flow(root, "finish", S, "E-1")
    finally:
        implement.run = real
    assert code == 1 and time.time() - t < 5 and "is being written by another nio flow call" in o and "try again" in o, o
    assert not calls and len(lines(root)) == before
    print("ok")


def test_failed_claim_removes_its_worktrees():
    """TC-31: a claim that made a worktree and then failed leaves none behind."""
    root = impl(tasks=IND)
    assert flow(root, "claim", S)[0] == 0
    before, real = git(root, "worktree", "list"), nio_flow.write
    nio_flow.write = lambda *a, **k: (_ for _ in ()).throw(OSError("disk full"))
    try:
        code, out = flow(root, "claim", S)
    except OSError:
        code, out = 1, "raised"
    finally:
        nio_flow.write = real
    assert code != 0 and git(root, "worktree", "list") == before, (out, git(root, "worktree", "list"))
    print("ok")


def demo():
    """A repo with two independent epics, the quickstart's demo."""
    return impl(tasks=IND)


FILES = {"win.txt": b"a\r\nB\r\n", "added.txt": b"new\r\nfile\r\n", "latin.txt": b"caf\xe9\n", "bin.dat": bytes(range(256))}


def byte_repo(files):
    root = Path(tempfile.mkdtemp()) / "r"
    root.mkdir()
    for a in (["init", "-q"], ["config", "user.name", "t"], ["config", "user.email", "t@t"]):
        git(root, *a)
    for n, b in files.items():
        (root / n).write_bytes(b)
    git(root, "add", "-A")
    git(root, "commit", "-qm", "base")
    return root, git(root, "rev-parse", "HEAD").strip()


def byte_tree(root, base):
    tree = root / ".nio/runs/R-1/worktree"
    git(root, "worktree", "add", "-q", "--detach", str(tree), base)
    return tree


def test_ac4b_land_keeps_bytes():
    root, base = byte_repo({"win.txt": b"a\r\nb\r\n"})
    tree = byte_tree(root, base)
    for n, b in FILES.items():
        (tree / n).write_bytes(b)
    out = implement.land(root, "s", "T-1", tree, base)
    assert out[2] == "", out[2]
    for n, b in FILES.items():
        assert (root / n).read_bytes() == b, n
    assert b"\r\n" in (root / out[0]).read_bytes()
    print("ok")


def test_ac6b_lf_patch_unchanged():
    root, base = byte_repo({"a.txt": b"x\n"})
    tree = byte_tree(root, base)
    (tree / "a.txt").write_bytes(b"y\n")
    out = implement.land(root, "s", "T-1", tree, base)
    want = subprocess.run(["git", "diff", "--cached", "--binary", "--no-renames", base], cwd=tree, capture_output=True, check=True).stdout
    assert (root / out[0]).read_bytes() == want and (root / "a.txt").read_bytes() == b"y\n"
    print("ok")


def test_misuse_crlf_edit_lands():
    root, base = byte_repo({"win.txt": b"a\r\nb\r\n"})
    tree = byte_tree(root, base)
    (tree / "win.txt").write_bytes(b"a\r\nB\r\n")
    out = implement.land(root, "s", "T-1", tree, base)
    assert out[2] == "", out[2]
    assert (root / "win.txt").read_bytes() == b"a\r\nB\r\n"
    print("ok")


def test_land_returns_error_when_diff_fails():
    root, base = byte_repo({"a.txt": b"x\n"})
    tree = byte_tree(root, base)
    (tree / "a.txt").write_bytes(b"y\n")
    real = records.git

    def fake(r, *args, **kw):
        if args[:1] == ("diff",) and "--binary" in args:
            return 128, b"", "fatal: boom"
        return real(r, *args, **kw)
    records.git = fake
    try:
        out = implement.land(root, "s", "T-1", tree, base)
    finally:
        records.git = real
    assert out[2] and "boom" in out[2], out
    assert (root / "a.txt").read_bytes() == b"x\n"
    print("ok")


def test_land_applies_edit_with_empty_error():
    root, base = byte_repo({"a.txt": b"x\n"})
    tree = byte_tree(root, base)
    (tree / "a.txt").write_bytes(b"y\n")
    out = implement.land(root, "s", "T-1", tree, base)
    assert out[2] == "" and (root / "a.txt").read_bytes() == b"y\n", out
    print("ok")


def test_land_returns_git_error_when_patch_does_not_apply():
    root, base = byte_repo({"a.txt": b"x\n"})
    tree = byte_tree(root, base)
    (tree / "a.txt").write_bytes(b"y\n")
    (root / "a.txt").write_bytes(b"z\n")
    out = implement.land(root, "s", "T-1", tree, base)
    assert out[2], out
    assert (root / "a.txt").read_bytes() == b"z\n"
    print("ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        tempfile.tempdir = tempfile.mkdtemp(prefix="nio-demo-", dir=Path(tempfile.tempdir).parent)
        print(demo())
        sys.exit()
    selfcheck.main([f for n, f in list(globals().items()) if n.startswith("test_") and callable(f)])
