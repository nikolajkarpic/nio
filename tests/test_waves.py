"""Self-check for parallel waves (2026-11-05-parallel-waves). Run: uv run python tests/test_waves.py"""
import hashlib
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import test_flow
from test_implement import BY, S, commit_all, flow, impl, lines, state, write_test
from test_tasks import git

from nio import flow as nio_flow
from nio import implement, records

TASK = ("### T-{n} Task {n}\n- Files: `app.py`\n- Serves: AC-1\n- Test: TC-1\n- Depends on: none\n- Parallel: {par}\n"
        "- Tier: strong: fixture\n- Effort: med\n- Mode: {mode}: fixture\n")


def waves(n=3, modes=None, parallel=None, cfg=None):
    """A repo at implementing whose one epic holds n independent tasks, `Parallel: yes` unless `parallel` says (T-1 to
    n: yes or no), direct unless `modes` says; `cfg` is merged into the config."""
    body = "".join(TASK.format(n=i, par=(parallel or {}).get(f"T-{i}", "yes"), mode=(modes or {}).get(f"T-{i}", "direct"))
                   + "\n" for i in range(1, n + 1))
    text = f"---\nslug: {S}\nretired: []\n---\n# Tasks: Refunds\n\n## E-1 Customer refunds a paid order (US-1)\n\n{body}"
    return impl(tasks=text, cfg=cfg)


def tasks_in(out):
    return [x.split()[1] for x in out.splitlines() if x.startswith("task: ")]


def trees(root):
    return [x.split()[0] for x in git(root, "worktree", "list").splitlines()]  # paths: a first claim's branch switch stays


def test_ac1_claims_a_wave_of_two():
    root = waves(n=3, modes={"T-1": "split"})
    code, out = flow(root, "claim", S)
    assert code == 0 and tasks_in(out) == ["T-1", "T-2"] and "task: T-3" not in out, out
    blocks = out.split("task: ")[1:]
    assert "mode: split" in blocks[0] and "mode: direct" in blocks[1], out
    assert all("worktree: .nio/runs/" in b for b in blocks), out
    assert state(root)["claims"] == {"task": "T-1", "wave": ["T-1", "T-2"]}, state(root)
    last = lines(root)[-2:]
    assert [(x["kind"], x["evidence"]["task"]) for x in last] == [("claim", "T-1"), ("claim", "T-2")], last
    code, out = flow(waves(n=3, parallel={"T-2": "no"}), "claim", S)
    assert tasks_in(out) == ["T-1", "T-3"], out
    print("ok")


def test_ac2_one_task_when_no_wave():
    for kw in ({"cfg": {"budgets": {"parallel": 1}}}, {"parallel": {"T-1": "no"}}, {"parallel": {"T-2": "no", "T-3": "no"}}):
        root = waves(n=3, **kw)
        code, out = flow(root, "claim", S)
        assert code == 0 and tasks_in(out) == ["T-1"] and "worktree:" not in out, (kw, out)
        assert state(root)["claims"] == {"task": "T-1"} and len(trees(root)) == 1, (kw, trees(root))
    print("ok")


def test_ac16_worktree_failure_refuses_the_claim():
    root = waves()
    before, listed = len(lines(root)), trees(root)
    real, seen = records.git, []

    def fake(r, *args, full=False):
        if args[:2] == ("worktree", "add"):
            seen.append(args)
            if len(seen) == 2:
                return (128, "", "fatal: boom") if full else []
        return real(r, *args, full=full)
    records.git = fake
    try:
        implement.claim(root, S, by=BY)
        raise AssertionError("the claim must be refused")
    except ValueError as e:
        assert "can't create a worktree for T-2" in str(e) and "fatal: boom" in str(e), e
    finally:
        records.git = real
    assert len(lines(root)) == before and trees(root) == listed, (trees(root), listed)
    print("ok")


def test_ac17_bad_parallel_budget_is_refused():
    for v in (0, "two", True):
        root = waves(cfg={"budgets": {"parallel": v}})
        before = len(lines(root))
        code, out = flow(root, "claim", S)
        assert code == 1 and "budgets.parallel" in out and repr(v) in out and len(lines(root)) == before, (v, out)
    print("ok")


def wt(out, tid):
    """The worktree (relative to the root) the claim output names for `tid`."""
    block = next(b for b in out.split("task: ")[1:] if b.split()[0] == tid)
    return next(x.split(": ", 1)[1] for x in block.splitlines() if x.startswith("worktree: "))


def work(root, out, tid):
    """A change to app.py in the task's worktree."""
    (root / wt(out, tid) / "app.py").write_text("def refund(x):\n    return x\n")


def test_ac3_red_and_green_run_in_the_worktree():
    root = waves(modes={"T-1": "split"})
    head = git(root, "rev-parse", "HEAD").strip()
    code, out = flow(root, "claim", S)
    w1, w2 = (root / wt(out, t) for t in ("T-1", "T-2"))
    log = Path(tempfile.mkdtemp()) / "log"
    write_test(w1)
    code, o = flow(root, "red", S, "T-1", "--run", f"pwd >> {log}; python -m unittest tests/test_refund.py")
    assert code == 0 and "red: T-1 accepted" in o and "frozen:\n  tests/test_refund.py" in o, o
    frozen = lines(root)[-1]["evidence"]["frozen"]
    assert frozen == {"tests/test_refund.py": hashlib.sha256((w1 / "tests/test_refund.py").read_bytes()).hexdigest()}, frozen
    work(root, out, "T-2")
    flow(root, "green", S, "T-2", "--run", f"pwd > {log}2")
    with open(w1 / "tests/test_refund.py", "a") as f:
        f.write("# edited\n")
    code, o = flow(root, "green", S, "T-1")
    assert code == 1 and "tests/test_refund.py changed since red" in o, o
    assert log.read_text().splitlines()[0] == str(w1.resolve()), log.read_text()
    assert not (root / "tests/test_refund.py").exists()
    assert ".nio/runs/" in str(w1) and str(w1).endswith("/worktree")
    assert git(w1, "rev-parse", "HEAD").strip() == head
    assert subprocess.run(["git", "-C", str(w1), "symbolic-ref", "-q", "HEAD"], capture_output=True).returncode
    assert Path(f"{log}2").read_text().strip() == str(w2.resolve())
    print("ok")


def test_ac5_nio_in_a_worktree_writes_the_root_state():
    root = waves(modes={"T-1": "single"})
    code, out = flow(root, "claim", S)
    w1 = root / wt(out, "T-1")
    write_test(w1)
    code, o = test_flow.cli(w1, "red", S, "T-1", "--run", "python -m unittest tests/test_refund.py", "--by", "worker / test / test")
    assert code == 0 and lines(root)[-1]["kind"] == "red" and lines(root)[-1]["evidence"]["task"] == "T-1", o
    assert git(w1, "status", "--porcelain", "--", ".nio/specs").strip() == ""
    cwd = os.getcwd()
    try:
        os.chdir(w1)
        assert records.repo_root() == root.resolve()
        other = Path(tempfile.mkdtemp()) / "other"
        git(root, "worktree", "add", str(other))
        os.chdir(other)
        assert records.repo_root() == other.resolve()
    finally:
        os.chdir(cwd)
    print("ok")


def test_ac6_second_guard_is_told_to_try_again():
    root = waves()
    code, out = flow(root, "claim", S)
    work(root, out, "T-2")
    marker, before = Path(tempfile.mkdtemp()) / "m", len(lines(root))
    with nio_flow.lock(root, S):
        t = time.time()
        code, o = flow(root, "green", S, "T-2", "--run", f"touch {marker}")
    assert code == 1 and time.time() - t < 5 and "is being written by another nio flow call" in o and "try again" in o, o
    assert not marker.exists() and len(lines(root)) == before
    print("ok")


def test_ac11_skill_dispatches_a_wave():
    root = Path(__file__).resolve().parent.parent
    skill = (root / "skills/implement/SKILL.md").read_text()
    worker = (root / "src/nio/agents/worker.md").read_text()
    for phrase in ("one worker per claimed task at the same time", "the task's worktree as its working directory",
                   "by its own ID", "try again", "while a wave is open, `is claimed` means wait"):
        assert phrase in skill, phrase
    single = worker.split("- **single:**", 1)[1].split("- **direct:**", 1)[0]
    assert "try again" in single, single
    print("ok")


def demo():
    """A repo with three independent parallel tasks, T-1 split and the rest direct."""
    return waves(n=3, modes={"T-1": "split"})


if __name__ == "__main__":
    if "--demo" in sys.argv:
        tempfile.tempdir = tempfile.mkdtemp(prefix="nio-demo-", dir=Path(tempfile.tempdir).parent)
        print(demo())
        sys.exit()
    for name, test in list(globals().items()):
        if name.startswith("test_") and callable(test):
            test()
