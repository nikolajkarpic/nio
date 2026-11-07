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
import selfcheck

TASK = ("### T-{n} Task {n}\n- Files: `app.py`, `m{n}.py`, `m{n}_new.py`\n- Serves: AC-1\n- Test: TC-1\n- Depends on: none\n- Parallel: {par}\n"
        "- Tier: strong: fixture\n- Effort: med\n- Mode: {mode}: fixture\n")


def waves(n=3, modes=None, parallel=None, cfg=None):
    """A repo at implementing whose one epic holds n independent tasks, `Parallel: yes` unless `parallel` says (T-1 to
    n: yes or no), direct unless `modes` says; `cfg` is merged into the config."""
    body = "".join(TASK.format(n=i, par=(parallel or {}).get(f"T-{i}", "yes"), mode=(modes or {}).get(f"T-{i}", "direct"))
                   + "\n" for i in range(1, n + 1))
    text = f"---\nslug: {S}\nretired: []\n---\n# Tasks: Refunds\n\n## E-1 Customer refunds a paid order (US-1)\n\n{body}"
    root = impl(tasks=text, cfg=cfg)
    for i in range(1, n + 1):
        (root / f"m{i}.py").write_text("v = 0\n")
    commit_all(root, "modules")
    return root


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

    def fake(r, *args, full=False, **kw):
        if args[:2] == ("worktree", "add"):
            seen.append(args)
            if len(seen) == 2:
                return (128, "", "fatal: boom") if full else []
        return real(r, *args, full=full, **kw)
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
    """A change to app.py and m<n>.py, and a new m<n>_new.py, in the task's worktree."""
    w, n = root / wt(out, tid), tid[2:]
    (w / "app.py").write_text("def refund(x):\n    return x\n") if tid == "T-1" else None
    (w / f"m{n}.py").write_text("v = 1\n")
    (w / f"m{n}_new.py").write_text("w = 1\n")


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


def land(root, tid):
    """A direct wave task's green: (code, output)."""
    return flow(root, "green", S, tid, "--run", "true")


def subjects(root, n):
    return git(root, "log", f"-{n}", "--format=%s").splitlines()


def kept(root):
    """The main tree's porcelain, the effort's state and history and the run folders (gitignored in a project) left out."""
    return sorted(x for x in git(root, "status", "--porcelain", "--untracked-files=all").splitlines()
                  if not x.endswith(("state.json", "history.jsonl")) and ".nio/runs/" not in x)


def test_ac4_no_claim_while_the_wave_is_open():
    root = waves(n=3, cfg={"budgets": {"parallel": 2}})
    code, out = flow(root, "claim", S)
    work(root, out, "T-1")
    code, o = land(root, "T-1")
    assert code == 0, o
    sp = root / ".nio/specs" / S / "state.json"
    saved, before = sp.read_bytes(), len(lines(root))
    code, o = flow(root, "claim", S)
    assert code == 1 and "T-2 is claimed" in o and "task:" not in o, o
    assert sp.read_bytes() == saved and len(lines(root)) == before
    assert state(root)["claims"] == {"task": "T-2", "wave": ["T-2"]}, state(root)
    print("ok")


def test_ac7_each_task_lands_as_one_commit_in_green_order():
    root = waves()
    code, out = flow(root, "claim", S)
    work(root, out, "T-1")
    work(root, out, "T-2")
    c2, o2 = land(root, "T-2")
    c1, o1 = land(root, "T-1")
    assert c2 == 0 and "done: T-2" in o2 and c1 == 0 and "done: T-1" in o1, (o2, o1)
    assert subjects(root, 2) == ["T-1: Task 1", "T-2: Task 2"], subjects(root, 2)
    prev = git(root, "show", "--name-only", "--format=", "HEAD~1").split()
    last = git(root, "show", "--name-only", "--format=", "HEAD").split()
    assert "m2.py" in prev and "m2_new.py" in prev and "m1.py" not in prev, prev
    assert "m1.py" in last and "m1_new.py" in last, last
    assert (root / "m2_new.py").read_text() == "w = 1\n"
    print("ok")


def test_ac8_a_clash_blocks_only_its_task():
    root = waves(n=3, cfg={"budgets": {"parallel": 3}})
    code, out = flow(root, "claim", S)
    for t in ("T-1", "T-2", "T-3"):
        work(root, out, t)
    (root / wt(out, "T-1") / "shared.py").write_text("x = 1\n")
    (root / wt(out, "T-2") / "shared.py").write_text("x = 2\n")
    assert land(root, "T-1")[0] == 0
    c2, o2 = land(root, "T-2")
    assert c2 == 1 and "T-2 blocked: its changes don't apply" in o2, o2
    assert implement.status(root, S, lines(root))["T-2"] == "blocked"
    assert state(root)["waiting"]["task"] == "T-2", state(root)
    ev = [x for x in lines(root) if x["kind"] == "blocked" and x["evidence"]["task"] == "T-2"][-1]["evidence"]
    assert ev["cause"] == "apply" and "x = 2" in (root / ev["patch"]).read_text(), ev
    assert (root / "shared.py").read_text() == "x = 1\n" and not (root / "m2_new.py").exists()
    c3, o3 = land(root, "T-3")
    assert c3 == 0 and "done: T-3" in o3 and subjects(root, 1)[0].startswith("T-3: "), o3
    listed = trees(root)
    for t in ("T-2", "T-3"):
        assert str((root / wt(out, t)).resolve()) not in listed and not (root / wt(out, t)).exists(), (t, listed)
    print("ok")


def test_ac9_failed_review_restores_the_main_tree():
    root = waves()
    code, out = flow(root, "claim", S)
    work(root, out, "T-1")
    w = root / wt(out, "T-1")
    sp = f".nio/specs/{S}/spec.md"
    with open(w / sp, "a") as f:
        f.write("x\n")
    (root / sp).write_text("# mine\n" + (root / sp).read_text())
    before, spec_b, m1 = kept(root), (root / sp).read_bytes(), (root / "m1.py").read_bytes()
    code, o = land(root, "T-1")
    assert code == 1 and "review: failed" in o and "the task edited spec.md" in o, o
    assert kept(root) == before and (root / sp).read_bytes() == spec_b and (root / "m1.py").read_bytes() == m1
    assert not (root / "m1_new.py").exists() and (w / "m1_new.py").exists() and (w / sp).read_text().endswith("x\n")
    assert implement.status(root, S, lines(root))["T-1"] == "claimed"
    print("ok")


def test_ac9_failed_review_restores_a_non_ascii_path():
    root = waves()
    code, out = flow(root, "claim", S)
    work(root, out, "T-1")
    w = root / wt(out, "T-1")
    (w / "\u00e9.py").write_text("w = 1\n")
    with open(w / f".nio/specs/{S}/spec.md", "a") as f:
        f.write("x\n")
    before = kept(root)
    code, o = land(root, "T-1")
    assert code == 1 and "review: failed" in o, o
    assert not (root / "\u00e9.py").exists() and kept(root) == before
    print("ok")


def test_ac10_suite_runs_for_the_last_task_only():
    log = Path(tempfile.mkdtemp()) / "log"
    root = waves(n=2, cfg={"tests": {"suite": f"git log --format=%s >> {log}; ls >> {log}; echo END >> {log}; "
                                         "python -m unittest discover -s tests"}})
    code, out = flow(root, "claim", S)
    work(root, out, "T-1")
    work(root, out, "T-2")
    ends = lambda: log.read_text().splitlines().count("END")
    assert land(root, "T-1")[0] == 0 and ends() == 1, log.read_text()
    assert land(root, "T-2")[0] == 0 and ends() == 2, log.read_text()
    block = log.read_text().split("END\n")[1].splitlines()
    assert any(x.startswith("T-1: ") for x in block) and "m2_new.py" in block, block
    print("ok")


def test_ac13_green_refuses_on_a_dirty_main_tree():
    root = waves()
    code, out = flow(root, "claim", S)
    work(root, out, "T-1")
    (root / "stray.txt").write_text("mine\n")
    marker, before, m1 = Path(tempfile.mkdtemp()) / "m", len(lines(root)), (root / "m1.py").read_bytes()
    code, o = flow(root, "green", S, "T-1", "--run", f"touch {marker}")
    assert code == 1 and "uncommitted changes outside the effort folder" in o and "stray.txt" in o, o
    assert not marker.exists() and len(lines(root)) == before and (root / "stray.txt").read_text() == "mine\n"
    assert (root / "m1.py").read_bytes() == m1 and not (root / "m1_new.py").exists()
    print("ok")


def test_ac14_review_ignores_a_landed_sibling():
    root = waves()
    code, out = flow(root, "claim", S)
    work(root, out, "T-1")
    work(root, out, "T-2")
    assert land(root, "T-2")[0] == 0
    code, o = land(root, "T-1")
    assert code == 0, o
    ev = [x for x in lines(root) if x["kind"] == "review" and x["evidence"]["task"] == "T-1"][-1]["evidence"]
    assert ev["passed"] and ev["outside"] == [], ev
    print("ok")


def test_ac15_outside_file_is_recorded_and_a_clash_blocks():
    root = waves()
    code, out = flow(root, "claim", S)
    work(root, out, "T-1")
    work(root, out, "T-2")
    (root / wt(out, "T-1") / "extra.txt").write_text("e\n")
    for t, v in (("T-1", 1), ("T-2", 2)):
        (root / wt(out, t) / "shared.py").write_text(f"x = {v}\n")
    c1, o1 = land(root, "T-1")
    assert c1 == 0 and "outside the task's files: extra.txt" in o1 and "outside the task's files: shared.py" in o1, o1
    ev = [x for x in lines(root) if x["kind"] == "review" and x["evidence"]["task"] == "T-1"][-1]["evidence"]
    assert sorted(ev["outside"]) == ["extra.txt", "shared.py"], ev
    c2, o2 = land(root, "T-2")
    assert c2 == 1 and implement.status(root, S, lines(root))["T-2"] == "blocked", o2
    assert lines(root)[-1]["kind"] == "blocked" and lines(root)[-1]["evidence"]["cause"] == "apply", lines(root)[-1]
    print("ok")


def test_ac9_failed_commit_restores_and_retry_lands():
    root = waves()
    code, out = flow(root, "claim", S)
    work(root, out, "T-1")
    before, m1 = kept(root), (root / "m1.py").read_bytes()
    real = records.git

    def fake(r, *args, full=False, **kw):
        if args[:1] == ("commit",):
            return (1, "", "hook said no") if full else []
        return real(r, *args, full=full, **kw)
    records.git = fake
    try:
        code, said = implement.green(root, S, "T-1", "true", BY)
    finally:
        records.git = real
    assert code == 1 and any("stays green" in x for x in said), said
    assert kept(root) == before and (root / "m1.py").read_bytes() == m1 and not (root / "m1_new.py").exists()
    assert implement.status(root, S, lines(root))["T-1"] == "green"
    assert (root / wt(out, "T-1") / "m1_new.py").exists()
    code, o = land(root, "T-1")
    assert code == 0 and "done: T-1" in o and subjects(root, 1)[0].startswith("T-1: "), o
    print("ok")


def test_ac9_raising_commit_restores_the_main_tree():
    root = waves()
    out = flow(root, "claim", S)[1]
    work(root, out, "T-1")
    before, m1 = kept(root), (root / "m1.py").read_bytes()
    real = records.git

    def fake(r, *args, full=False, **kw):
        if args[:1] == ("write-tree",):
            return (1, "", "no tree") if full else []
        return real(r, *args, full=full, **kw)
    records.git = fake
    try:
        implement.green(root, S, "T-1", "true", BY)
        raised = False
    except ValueError:
        raised = True
    finally:
        records.git = real
    assert raised and kept(root) == before and (root / "m1.py").read_bytes() == m1 and not (root / "m1_new.py").exists()
    print("ok")


def test_ac12_worktree_removed_at_commit_and_block():
    root = waves()
    out = flow(root, "claim", S)[1]
    w1, w2 = wt(out, "T-1"), wt(out, "T-2")
    work(root, out, "T-1"), work(root, out, "T-2")
    (root / w2 / f".nio/specs/{S}").mkdir(parents=True, exist_ok=True)
    (root / w2 / f".nio/specs/{S}/notes.md").write_text("effort edit\n")
    code, o = land(root, "T-1")
    listed = lambda: git(root, "worktree", "list")
    assert code == 0 and w1 not in listed() and not (root / w1).exists(), o
    for _ in range(3):
        o = flow(root, "green", S, "T-2", "--run", "false")[1]
    assert "blocked: T-2 after 3 attempts" in o and w2 not in listed() and not (root / w2).exists(), o
    patch = (root / w2).parent / "T-2.patch"
    assert patch.exists() and "m2_new.py" in patch.read_text()
    assert "notes.md" in patch.read_text()
    print("ok")


def test_ac4_two_blocked_siblings_hold_the_claim():
    root = waves(n=3)
    out = flow(root, "claim", S)[1]
    for t in ("T-1", "T-2"):
        work(root, out, t)
    for t in ("T-1", "T-2"):
        for _ in range(3):
            flow(root, "green", S, t, "--run", "false")
    flow(root, "unblock", S, "T-2", "--human", "x", "--by", "human")
    n = len(lines(root))
    code, o = flow(root, "claim", S)
    assert code == 1 and "T-1 is blocked" in o and "nio flow unblock" in o and len(lines(root)) == n, o
    print("ok")


def demo():
    """A repo with three independent parallel direct tasks, the quickstart's demo (T-1 and T-2 both direct)."""
    return waves(n=3)


def test_gone_worktree_refuses_red_and_green():
    root = waves(modes={"T-1": "split"})
    code, out = flow(root, "claim", S)
    w1 = root / wt(out, "T-1")
    git(root, "worktree", "remove", "--force", str(w1))
    before, mark = len(lines(root)), Path(tempfile.mkdtemp()) / "ran"
    for verb in ("green", "red"):
        extra = ("--run", f"touch {mark}; python -m unittest tests/test_refund.py") if verb == "red" else ()
        code, o = flow(root, verb, S, "T-1", *extra)
        assert code == 1 and "the worktree of T-1 is gone" in o and wt(out, "T-1") in o, o
    assert not mark.exists() and len(lines(root)) == before
    print("ok")


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


def test_ac5b_shelve_keeps_bytes():
    root, base = byte_repo({"win.txt": b"a\r\nb\r\n"})
    for n, b in FILES.items():
        (root / n).write_bytes(b)
    rel = implement.shelve(root, "s", "R-1", "T-1")
    assert (root / "win.txt").read_bytes() == b"a\r\nb\r\n" and not (root / "added.txt").exists()
    git(root, "apply", "--binary", str(root / rel))
    for n, b in FILES.items():
        assert (root / n).read_bytes() == b, n
    git(root, "add", "-A")
    git(root, "commit", "-qm", "kept")
    implement.shelve(root, "s", "R-2", "T-2")
    assert (root / ".nio/runs/R-2/T-2.patch").read_bytes() == b""
    print("ok")


def test_shelve_refuses_when_diff_fails():
    root, base = byte_repo({"win.txt": b"a\r\nb\r\n"})
    for n, b in FILES.items():
        (root / n).write_bytes(b)
    real = records.git

    def fake(r, *args, **kw):
        if args[:1] == ("diff",):
            return 128, b"", "fatal: boom"
        return real(r, *args, **kw)
    records.git = fake
    try:
        implement.shelve(root, "s", "R-1", "T-1")
        raise AssertionError("shelve must raise")
    except ValueError as e:
        assert "boom" in str(e), e
    finally:
        records.git = real
    for n, b in FILES.items():
        assert (root / n).read_bytes() == b, n
    assert not (root / ".nio/runs/R-1/T-1.patch").exists()
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


def test_failed_diff_keeps_the_worktree_and_names_it():
    root = waves(n=2)
    code, out = flow(root, "claim", S)
    work(root, out, "T-1")
    w = root / wt(out, "T-1")
    real = records.git

    def fake(r, *args, **kw):
        if args[:1] == ("diff",) and "--binary" in args:
            return 128, b"", "fatal: boom"
        return real(r, *args, **kw)
    records.git = fake
    try:
        code, o = land(root, "T-1")
    finally:
        records.git = real
    assert code == 1 and "boom" in o, o
    assert (w / "m1_new.py").is_file() and (w / "m1_new.py").read_text() == "w = 1\n", o
    said = next(x for x in o.splitlines() if "its changes are in" in x)
    assert said.split("its changes are in", 1)[1].strip() and str(w.relative_to(root)) in said, said
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
