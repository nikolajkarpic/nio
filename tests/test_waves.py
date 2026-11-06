"""Self-check for parallel waves (2026-11-05-parallel-waves). Run: uv run python tests/test_waves.py"""
import sys
import tempfile
from pathlib import Path

from test_implement import BY, S, commit_all, flow, impl, lines, state
from test_tasks import git

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
