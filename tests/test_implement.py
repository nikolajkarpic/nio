"""Self-check for the implement stage's pieces (2026-10-29-implement-stage). Run: uv run python tests/test_implement.py"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import selfcheck
import test_flow
from test_tasks import SLUG, TASKS, approve_commit, chain, errs, field, git, has, repo

from nio import agents, implement, pack, records, tasks
from nio import flow as nio_flow

S, BY = test_flow.S, test_flow.BY
REFUNDS = (Path(__file__).parent / "fixtures/tasks/tasks.md").read_text()
SUITE = "python -m unittest discover -s tests"


# --- T-4: the Mode field (CT-16) ---

def approve_on(root, date):
    git(root, "add", "-A")
    env = {**os.environ, "GIT_COMMITTER_DATE": f"{date}T12:00:00Z", "GIT_AUTHOR_DATE": f"{date}T12:00:00Z"}
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "nio: approve tasks"],
                   cwd=root, check=True, capture_output=True, env=env)


def test_ac40_mode_is_checked():
    assert "Mode" in tasks.FIELDS and tasks.MODE_SINCE == "2026-10-30"
    root = repo(field("T-1", "Mode", None))
    has(errs(root), "T-1: needs `- Mode:`")  # not approved yet: a new list needs it
    root = repo(chain(field("T-1", "Mode", "single"), field("T-2", "Mode", "fast: x"), field("T-3", "Mode", "direct: ")))
    e = errs(root)
    assert e == ["T-1: `Mode: single` needs a reason, as `Mode: single: <why>`",
                 "T-2: `fast` is not split, single or direct", "T-3: `Mode: direct` needs a reason, as `Mode: direct: <why>`"], e
    assert errs(repo()) == []
    print("ok")


def test_ac40_missing_mode_allowed_before_mode_since():
    root = repo(chain(*[field(t, "Mode", None) for t in ("T-1", "T-2", "T-3")]))
    approve_on(root, "2026-10-29")
    assert errs(root) == [], errs(root)
    root = repo(chain(*[field(t, "Mode", None) for t in ("T-1", "T-2", "T-3")]))
    approve_on(root, "2026-10-30")
    has(errs(root), "T-1: needs `- Mode:`")
    print("ok")


# --- T-1: run, runner, wrong_reason (CT-1, CT-2) ---

def test_ac38_run_limit_missing_program_and_group_kill():
    root = Path(tempfile.mkdtemp())
    assert implement.run(root, "echo hi; echo err >&2; exit 3", 5) == (3, "hi\nerr\n", "")
    code, out, cause = implement.run(root, "nonexistent-prog-xyz", 5)
    assert (code, cause) == (127, "program not found"), (code, out, cause)
    start = time.time()
    code, out, cause = implement.run(root, "echo before; sleep 60 & echo $! > child.pid; sleep 60", 1)
    assert (code, cause) == (None, "time limit") and "before" in out and time.time() - start < 10, (code, out, cause)
    pid = int((root / "child.pid").read_text())
    time.sleep(0.2)
    try:
        os.kill(pid, 0)
        raise AssertionError("the child outlived the time limit")
    except ProcessLookupError:
        pass
    print("ok")


def test_ac38_runner_names_known_runners_only():
    want = {"pytest -x": "pytest", "python -m pytest t": "pytest", "uv run python -m unittest": "unittest",
            "npx jest": "jest", "vitest run": "vitest", "mocha": "mocha", "go test ./...": "go test",
            "cargo test": "cargo test", "bundle exec rspec": "rspec", "rspec": "rspec",
            "npm test": None, "bash run.sh": None, "mvn test": None, "gradle test": None}
    for cmd, name in want.items():
        assert implement.runner(cmd) == name, (cmd, implement.runner(cmd))
    print("ok")


ERRORS = {"pytest": (2, "ERROR collecting tests/t.py"), "unittest": (1, "ImportError: Failed to import test module: t"),
          "jest": (1, "Test suite failed to run"), "vitest": (1, " Failed Suites 1"), "mocha": (1, "Exception during run: x"),
          "go test": (1, "FAIL pkg [build failed]"), "cargo test": (101, "error[E0425]: cannot find"),
          "rspec": (1, "An error occurred while loading ./spec/a_spec.rb\n1 error occurred outside of examples")}
NONE = {"pytest": (5, "no tests ran in 0.01s"), "unittest": (0, "Ran 0 tests in 0.000s"), "jest": (1, "No tests found, exiting"),
        "vitest": (1, "No test files found"), "mocha": (1, "Error: No test files found"), "go test": (0, "? pkg [no test files]"),
        "rspec": (0, "No examples found.")}


def test_ac12_wrong_reason_on_each_runner():
    for name, (code, out) in ERRORS.items():
        got = implement.wrong_reason(name, code, out)
        assert got.startswith("collection, import or syntax error: "), (name, got)
    for name, (code, out) in NONE.items():
        assert implement.wrong_reason(name, code, out) == "no tests ran", name
    # a real assertion failure is the right reason
    assert implement.wrong_reason("pytest", 1, "FAILED t.py::test_a - assert 1 == 2\n1 failed in 0.1s") == ""
    assert implement.wrong_reason("unittest", 1, "FAIL: test_a (t.T)\nRan 1 test\nFAILED (failures=1)") == ""
    assert implement.wrong_reason("pytest", 4, "usage error").startswith("collection, import or syntax error")
    assert implement.wrong_reason("pytest", 5, "") == "no tests ran"
    assert implement.wrong_reason(None, 1, "ERROR collecting") == ""
    print("ok")


# --- T-2: suite (CT-3) ---

def suite_of(root, command):
    return implement.suite(root, {"tests": {"suite": command, "timeout": 5}})


def test_ac44_suite_reads_unittest_output():
    root = Path(tempfile.mkdtemp())
    out = "FAIL: test_a (t.T.test_a)\nERROR: test_b (t.T.test_b)\nRan 4 tests in 0.1s\nFAILED (failures=1, errors=1)\n"
    (root / "out.txt").write_text(out)
    r = suite_of(root, "cat out.txt; echo '# python -m unittest'; exit 1")
    assert r["runner"] == "unittest" and r["code"] == 1 and r["cause"] == "", r
    assert r["failing"] == ["test_a (t.T.test_a)", "test_b (t.T.test_b)"] and r["collected"] == 4 and not r["broken"], r
    assert r["command"].startswith("cat out.txt") and len(r["output_hash"]) == 64, r
    (root / "out.txt").write_text("ImportError: Failed to import test module: t\nFAIL: x\nRan 1 test in 0s\n")
    r = suite_of(root, "cat out.txt; echo '# python -m unittest'; exit 1")
    assert r["broken"] and r["failing"] == ["x"], r
    r = implement.suite(root, {"tests": {"suite": "sleep 30 # unittest", "timeout": 1}})
    assert r["cause"] == "time limit" and r["broken"], r
    print("ok")


def test_ac35_suite_unknown_runner_keeps_exit_code():
    root = Path(tempfile.mkdtemp())
    r = suite_of(root, "echo FAILED x; exit 4")
    assert (r["runner"], r["code"], r["failing"], r["collected"], r["broken"]) == (None, 4, None, None, False), r
    r = suite_of(root, "exit 0")
    assert r["code"] == 0 and r["failing"] is None, r
    try:
        implement.suite(root, {})
        raise AssertionError("no tests.suite must raise")
    except ValueError:
        pass
    print("ok")


def test_ac44_suite_reads_pytest_output():
    root = Path(tempfile.mkdtemp())
    (root / "o").write_text("collected 5 items\nFAILED tests/t.py::test_a - assert 0\nERROR tests/t.py::test_b\n")
    r = suite_of(root, "cat o; echo pytest; exit 1")
    assert r["failing"] == ["tests/t.py::test_a", "tests/t.py::test_b"] and r["collected"] == 5, r
    print("ok")


# --- T-3: tasks_of, status, next_ready (CT-4) ---

LIST = """---
slug: s
retired: []
---
# Tasks: s

## E-1 First (Foundation)

### T-1 One
- Files: `a.py`, `b.py`
- Serves: AC-1
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: strong: x
- Effort: med
- Mode: direct: config

### T-2 Two
- Files: `a.py`
- Serves: AC-2
- Test: TC-2
- Depends on: T-1
- Parallel: no
- Tier: cheap: x
- Effort: low

## E-2 Second (US-1)

### T-3 Three
- Files: `c.py`
- Serves: AC-3
- Test: TC-3
- Depends on: T-2
- Parallel: no
- Tier: cheap: x
- Effort: low
- Mode: single: x
"""
FIXES = """
#### Fixes

### T-4 Fix
- From: J-1 (implementation-E-1, round 1)
- Files: `a.py`
- Serves: J-1
- Test: x
- Depends on: T-2
- Parallel: no
- Tier: cheap: x
- Effort: low
- Mode: split: x
"""


def lst(text=LIST, config=None):
    root = Path(tempfile.mkdtemp())
    d = root / ".nio/specs/s"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text(text)
    (root / ".nio/config.json").write_text(json.dumps(config or {}))
    return root


def L(kind, task, **ev):
    return {"kind": kind, "from": "implementing", "to": "implementing", "evidence": {"task": task, **ev}}


def done(task):
    return [L("claim", task), L("red", task), L("green", task), L("review", task, passed=True), L("task_done", task, commit="c")]


def test_ac8_tasks_of_reads_fields_and_mode():
    root = lst()
    ts = implement.tasks_of(root, "s")
    assert [t["id"] for t in ts] == ["T-1", "T-2", "T-3"], ts
    t = ts[0]
    assert (t["title"], t["epic"], t["fix"], t["deps"], t["files"], t["serves"], t["tests"], t["tier"], t["effort"], t["mode"]) == \
        ("One", "E-1", False, [], ["a.py", "b.py"], ["AC-1"], ["TC-1"], "strong", "med", "direct"), t
    assert [t["mode"] for t in ts] == ["direct", "split", "single"]  # a missing Mode: reads as split
    assert [t["mode"] for t in implement.tasks_of(lst(config={"implement": {"mode": "split"}}), "s")] == ["split"] * 3
    print("ok")


def test_ac8_status_and_next_ready_follow_epic_and_dependency_order():
    root = lst()
    assert implement.status(root, "s", []) == {"T-1": "ready", "T-2": "pending", "T-3": "pending"}
    assert implement.next_ready(root, "s", [])["id"] == "T-1"
    lines = [L("claim", "T-1")]
    assert implement.status(root, "s", lines)["T-1"] == "claimed" and implement.next_ready(root, "s", lines) is None
    for k, state in (("red", "red"), ("green", "green")):
        lines.append(L(k, "T-1"))
        assert implement.status(root, "s", lines)["T-1"] == state
    lines.append(L("refused", "T-1", cause="x"))
    assert implement.status(root, "s", lines)["T-1"] == "green"
    lines.append(L("review", "T-1", passed=True))
    assert implement.status(root, "s", lines)["T-1"] == "green"  # done only with its task_done line (a failed commit stays green)
    lines.append(L("task_done", "T-1", commit="c"))
    st = implement.status(root, "s", lines)
    assert st == {"T-1": "done", "T-2": "ready", "T-3": "pending"} and implement.next_ready(root, "s", lines)["id"] == "T-2"
    lines += done("T-2")
    assert implement.next_ready(root, "s", lines)["id"] == "T-3"
    lines += done("T-3")
    assert implement.next_ready(root, "s", lines) is None
    print("ok")


def test_ac8_review_failure_and_block_states():
    root = lst()
    base = [L("claim", "T-1"), L("red", "T-1"), L("green", "T-1")]
    # T-1 is direct: a failed review sets it back to claimed (FR-45); T-2 is split: back to red
    assert implement.status(root, "s", base + [L("review", "T-1", passed=False)])["T-1"] == "claimed"
    two = done("T-1") + [L("claim", "T-2"), L("red", "T-2"), L("green", "T-2"), L("review", "T-2", passed=False)]
    assert implement.status(root, "s", two)["T-2"] == "red"
    blocked = base + [L("blocked", "T-1", cause="attempts")]
    assert implement.status(root, "s", blocked)["T-1"] == "blocked" and implement.next_ready(root, "s", blocked) is None
    assert implement.status(root, "s", blocked + [L("unblock", "T-1")])["T-1"] == "ready"
    print("ok")


def test_ac32_open_fix_task_holds_its_epic():
    root = lst(LIST.replace("## E-2", FIXES.lstrip("\n") + "\n## E-2"))
    lines = done("T-1") + done("T-2")
    assert implement.status(root, "s", lines)["T-4"] == "ready"
    nxt = implement.next_ready(root, "s", lines)
    assert nxt["id"] == "T-4" and nxt["fix"] and nxt["epic"] == "E-1", nxt  # E-2's T-3 waits
    assert implement.next_ready(root, "s", lines + done("T-4"))["id"] == "T-3"
    print("ok")


def test_ac39_changed_task_returns_under_a_new_id_and_old_stays_done():
    # re-approved list: T-2 retired and rewritten as T-5; T-1 and T-2 keep their done lines
    text = LIST.replace("### T-2 Two", "### T-5 Two again").replace("Depends on: T-2", "Depends on: T-5").replace("Depends on: T-1", "Depends on: T-1")
    root = lst(text)
    lines = done("T-1") + done("T-2")
    st = implement.status(root, "s", lines)
    assert st["T-1"] == "done" and st["T-2"] == "done" and st["T-5"] == "ready", st
    assert implement.next_ready(root, "s", lines)["id"] == "T-5"
    print("ok")



# --- fixtures for the claim and later (tests.md "Fixtures:") ---

def with_modes(text=REFUNDS, modes=None):
    """The task list with each task's `- Mode:` line set from `modes` ({"T-1": "direct"}), split by default."""
    out, tid = [], None
    for line in text.splitlines():
        tid = (re.match(r"^### (T-\d+)", line) or [None, tid])[1]
        out.append(f"- Mode: {(modes or {}).get(tid, 'split')}: fixture" if line.startswith("- Mode:") else line)
    return "\n".join(out) + "\n"


def commit_all(root, message, date=None):
    git(root, "add", "-A")
    env = {**os.environ, **({"GIT_COMMITTER_DATE": f"{date}T12:00:00Z", "GIT_AUTHOR_DATE": f"{date}T12:00:00Z"} if date else {})}
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message], cwd=root, check=True,
                   capture_output=True, env=env)


def impl(modes=None, cfg=None, tasks=None, commit=True, date=None, alone=False):
    """A repo at implementing: the refunds effort, TC-1 naming `tests/test_refund.py:test_refund` before the plan is
    approved, `tasks` (else the refunds list with `modes`) approved with its commit (`commit=False`: committed as `wip`;
    `date`: the commit's date), `tests.suite` set (merged with `cfg`; a None value removes the key), one passing test
    so the baseline runs clean, `__pycache__/` ignored as a project would, and a `start` line."""
    tasks = tasks or with_modes(modes=modes)
    if alone:  # T-1 closes its epic, so its review runs the full suite
        tasks = tasks.replace("### T-2", "## E-9 The rest (US-2)\n\n### T-2", 1)
    root = test_flow.effort("plan_jury")
    folder = root / ".nio/specs" / S
    tp = folder / "tests.md"
    tp.write_text(tp.read_text().replace("tests/test_refunds.py:test_full_refund", "tests/test_refund.py:test_refund"))
    test_flow.approve(root, S, "plan")
    (folder / "tasks.md").write_text(tasks.replace("slug: checkout-refunds", f"slug: {S}"))
    conf = records.merge({"memory": {"areas": ["auth", "project"]}, "tests": {"suite": SUITE}}, cfg or {})
    conf = {k: {x: y for x, y in v.items() if y is not None} if isinstance(v, dict) else v for k, v in conf.items()}
    (root / ".nio/config.json").write_text(json.dumps(conf))
    (root / ".gitignore").write_text("__pycache__/\n")
    (root / "tests").mkdir()
    (root / "tests/test_base.py").write_text("import unittest\n\n\nclass B(unittest.TestCase):\n"
                                             "    def test_base(self):\n        self.assertTrue(True)\n")
    test_flow.approve(root, S, "tasks", commit=False)
    commit_all(root, "nio: approve tasks" if commit else "wip", date)
    test_flow.history(root, S, {"kind": "start", "from": None, "to": "implementing"})
    return root


def write_test(root, name="tests/test_refund.py"):
    """A test phase's test: it fails on an assertEqual until app.py defines `refund`."""
    (root / name).write_text("import unittest\n\nimport app\n\n\nclass T(unittest.TestCase):\n"
                             "    def test_refund(self):\n        self.assertEqual(getattr(app, 'refund', lambda x: 0)(40), 40)\n")


def flow(root, *args):
    """`nio flow <args>`, with `--by` added to the task commands too."""
    extra = ["--by", BY] if args[0] in ("claim", "red", "green", "block", "unblock") and "--by" not in args else []
    return test_flow.cli(root, *args, *extra)


def lines(root):
    return nio_flow.load(root, S)[1]


def state(root):
    return nio_flow.load(root, S)[0]


def parts(text):
    """{## heading: body} of a worker pack."""
    out, name = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            name = line[3:]
            out[name] = []
        elif name:
            out[name].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


# --- T-5: the worker pack (CT-6) ---

def test_ac1_pack_holds_only_its_parts():
    two = with_modes().replace("- Files: `app.py`\n- Serves: AC-1\n", "- Files: `app.py`, `refunds.py`\n- Serves: AC-1\n", 1)
    root = impl(tasks=two)
    task = next(t for t in implement.tasks_of(root, S) if t["id"] == "T-1")
    text = implement.worker_pack(root, S, task)
    got = parts(text)
    assert len(got) == 5, list(got)
    mem, tsk, acs, cts, tcs = got.values()
    want, _ = pack.build(root, task["title"], ["app.py", "refunds.py"], ["AC-1"], "T-1", worker=False)
    assert list(got)[0] == "Memory for T-1" and mem.strip() == "\n".join(implement.nest(want.splitlines()[1:])).strip(), mem
    assert "#### T-1 Refund a paid order in full" in tsk and "`app.py`, `refunds.py`" in tsk and "T-2" not in tsk, tsk
    assert "**AC-1**" in acs and "Observable: order state is `refunded`" in acs and "AC-2" not in acs, acs
    assert "#### CT-1 Refund an order" in cts and "#### CT-2 Refund over HTTP" in cts, cts
    assert "#### TC-1 " in tcs and "tests/test_refund.py:test_refund" in tcs and "TC-2" not in tcs, tcs
    for gone in ("@nio:remember", "Mode", "status: blocked", "change_request", "Build order", "How to use this"):
        assert gone not in text, gone
    print("ok")


# --- T-6: the worker cards (CT-15) ---

WORKER = Path(__file__).resolve().parent.parent / "src/nio/agents/worker.md"


def test_ac2_worker_card_per_tier():
    root = repo()
    os.environ["NIO_HOME"] = tempfile.mkdtemp()
    os.environ.pop("CLAUDE_CODE_SUBAGENT_MODEL", None)
    (root / ".nio/config.json").write_text(json.dumps({"agents": {"hosts": ["claude", "codex"], "tiers": {
        "codex": {"cheap": "c1", "strong": "c2", "max": "c3", "frontier": "c4"}}}}))
    out, errors = agents.sync(root)
    assert not errors, errors
    for tier, model, codex in zip(agents.ORDER, ["haiku", "sonnet", "opus", "fable"], ["c1", "c2", "c3", "c4"]):
        text = (root / f".claude/agents/nio-worker-{tier}.md").read_text()
        assert f'name: "nio-worker-{tier}"' in text and f'model: "{model}"' in text, text[:300]
        toml = (root / f".codex/agents/nio-worker-{tier}.toml").read_text()
        assert f'model = "{codex}"' in toml, toml[:300]
        for body in (text, toml):
            never = body.index("never edit")
            assert body.index("state.json", never) and body.index("history.jsonl", never)
            assert re.search(r"`nio flow red`.*`nio flow green`|single mode.*`nio flow red`", body, re.S), body
    assert not (root / ".claude/agents/nio-worker.md").exists() and not (root / ".codex/agents/nio-worker.toml").exists()
    print("ok")


def test_ac24_card_rules():
    text = WORKER.read_text()
    for word in ("status: blocked", "change_request:", "spec_says", "code_shows", "smallest_change"):
        assert word in text, word
    assert re.search(r"[Nn]ever edit `spec.md`, the plan files \(.*\) or `tasks.md`", text, re.S)
    print("ok")


# --- T-7: the first claim starts the stage (CT-5) ---

def failing(root, *names, body="self.assertEqual(1, 2)"):
    for name in names:
        (root / f"tests/{name}.py").write_text(f"import unittest\n\n\nclass T(unittest.TestCase):\n    def {name}(self):\n"
                                               f"        {body}\n")


def kinds(entries):
    return [x["kind"] for x in entries]


def test_ac19_baseline_first():
    root = impl()
    failing(root, "test_a", "test_c")
    commit_all(root, "two failing tests")
    before = len(lines(root))
    code, out = flow(root, "claim", S)
    assert code == 0, out
    new = lines(root)[before:]
    assert kinds(new) == ["baseline", "claim"], new
    ev = new[0]["evidence"]
    assert ev["runner"] == "unittest" and ev["code"] == 1 and ev["collected"] == 3, ev
    assert any("test_a" in f for f in ev["failing"]) and any("test_c" in f for f in ev["failing"]) and len(ev["failing"]) == 2, ev
    assert ev["command"] == SUITE and new[1]["evidence"]["task"] == "T-1", new
    print("ok")


def test_ac27_branch():
    root = impl()
    git(root, "branch", "-M", "main")
    head = git(root, "rev-parse", "main")
    code, out = flow(root, "claim", S)
    assert code == 0, out
    assert git(root, "branch", "--show-current").strip() == f"nio/{S}" and git(root, "rev-parse", "main") == head
    print("ok")


def test_ac34_no_suite():
    root = impl(cfg={"tests": {"suite": None}})
    code, out = flow(root, "claim", S)
    assert code == 1 and "tests.suite" in out, out
    code, out = flow(root, "next", S)
    assert "waiting_for_human" in out and "tests.suite" in out, out
    assert "baseline" not in kinds(lines(root)) and "claim" not in kinds(lines(root)) and state(root)["claims"] == {}
    print("ok")


def test_ac51_broken_baseline():
    root = impl()
    (root / "tests/test_old.py").write_text("import nosuchmodule\n")
    commit_all(root, "old test")
    code, out = flow(root, "claim", S)
    assert code == 1, out
    code, out = flow(root, "next", S)
    assert "waiting_for_human" in out and "tests/test_old.py" in out, out
    assert not {"baseline", "claim"} & set(kinds(lines(root))), lines(root)
    (root / "tests/test_old.py").write_text("import os\n")
    commit_all(root, "fix the import")
    code, out = flow(root, "claim", S)
    assert code == 0, out
    got = kinds(lines(root))
    assert got.index("baseline") < got.index("claim") and lines(root)[-1]["evidence"]["task"] == "T-1", got
    assert state(root)["waiting"] is None, state(root)
    print("ok")


def test_ac35_unknown_runner_baseline_must_pass():
    root = impl(cfg={"tests": {"suite": "sh -c 'exit 1'"}})
    code, out = flow(root, "claim", S)
    assert code == 1 and "unknown" in flow(root, "next", S)[1], out
    assert "baseline" not in kinds(lines(root))
    print("ok")


# --- T-8: the claim's guards and the start instruction (CT-5) ---

def test_ac3_claim_names_card_and_effort():
    text = with_modes().replace("- Tier: strong: money moves, and the state table guards it\n- Effort: med",
                                "- Tier: cheap: fixture\n- Effort: low", 1)
    root = impl(tasks=text)
    code, out = flow(root, "claim", S)
    assert code == 0, out
    got = out.splitlines()
    assert "task: T-1 Refund a paid order in full" in got and "card: nio-worker-cheap" in got and "effort: low" in got, out
    path = next(x[len("pack: "):] for x in got if x.startswith("pack: "))
    assert re.fullmatch(r"\.nio/runs/R-[\w-]+/packs/T-1\.md", path) and "## Tests" in (root / path).read_text(), path
    assert state(root)["claims"] == {"task": "T-1"} and lines(root)[-1]["evidence"]["commit"] == git(root, "rev-parse", "HEAD").strip()
    print("ok")


def test_ac4_dependency_not_done():
    root = impl()
    test_flow.history(root, S, {"kind": "blocked", "from": "implementing", "to": "implementing",
                                "evidence": {"task": "T-1", "cause": "attempts"}})
    before = len(lines(root))
    code, out = flow(root, "claim", S)
    assert code == 1 and "no ready task; T-2 waits on T-1" in out, out
    assert state(root)["claims"] == {} and "claim" not in kinds(lines(root)[before:]), lines(root)
    print("ok")


def test_ac5_one_claim_at_a_time():
    root = impl()
    assert flow(root, "claim", S)[0] == 0
    n = len(lines(root))
    code, out = flow(root, "claim", S)
    assert code == 1 and "T-1 is claimed" in out, out
    assert state(root)["claims"] == {"task": "T-1"} and len(lines(root)) == n
    print("ok")


def test_ac6_no_approve_commit():
    root = impl(commit=False)
    n = len(lines(root))
    code, out = flow(root, "claim", S)
    assert code == 1 and 'no "nio: approve tasks" commit' in out, out
    assert len(lines(root)) == n
    print("ok")


def test_ac7_dirty_tree():
    root = impl()
    (root / "README.md").write_text("draft\n")
    (root / "app.py").write_text("x = 1\n")
    code, out = flow(root, "claim", S)
    assert code == 1 and "uncommitted changes outside the effort folder:" in out and "README.md" in out and "app.py" in out, out
    assert state(root)["claims"] == {} and "claim" not in kinds(lines(root))
    print("ok")


def test_ac40_mode():
    for cfg, want in ((None, "mode: direct"), ({"implement": {"mode": "split"}}, "mode: split")):
        root = impl(modes={"T-1": "direct"}, cfg=cfg)
        code, out = flow(root, "claim", S)
        assert code == 0 and want in out.splitlines(), out
    print("ok")


def test_ac46_wrong_branch():
    root = impl()
    git(root, "branch", "-M", "main")
    assert flow(root, "claim", S)[0] == 0
    test_flow.history(root, S, *[{"kind": k, "from": "implementing", "to": "implementing", "evidence": {"task": "T-1", **ev}}
                                 for k, ev in (("red", {}), ("green", {}), ("review", {"passed": True}))],
                      {"kind": "task_done", "from": "implementing", "to": "implementing",
                       "evidence": {"task": "T-1", "commit": "c"}, "state": {"claims": {}}})
    commit_all(root, "T-1: Refund a paid order in full")
    git(root, "checkout", "-q", "main")
    n = len(lines(root))
    code, out = flow(root, "claim", S)
    assert code == 1 and f"nio/{S}" in out, out
    assert "claim" not in kinds(lines(root)[n:]) and state(root)["claims"] == {}
    print("ok")


def nio(root, *args):
    code, out, err = test_flow.run_main(root, *args)
    return code, out + err


def test_ac40_legacy_list_without_mode():
    bare = "".join(x for x in REFUNDS.splitlines(keepends=True) if not x.startswith("- Mode:"))
    old = impl(tasks=bare, date="2026-10-29")
    code, out = nio(old, "check", "tasks", S)
    assert code == 0, out
    code, out = flow(old, "claim", S)
    assert code == 0 and "mode: split" in out.splitlines(), out
    new = impl(tasks=bare, date="2026-10-31")
    code, out = nio(new, "check", "tasks", S)
    assert code == 1 and all(f"{t}: needs `- Mode:`" in out for t in ("T-1", "T-2", "T-3")), out
    print("ok")


# --- T-9: the @nio:implement skill (CT-17) ---

def test_implement_skill_steps():
    text = (Path(__file__).resolve().parent.parent / "skills/implement/SKILL.md").read_text()
    steps = text[text.index("## Steps"):]
    steps = steps[:steps.index("\n## ", 3)]
    for word in ("`nio flow claim", "`nio flow red", "`nio flow green", "`nio flow block", "split", "single", "direct",
                 "notify:", "waiting_for_human"):
        assert word in steps, word
    assert text.count(test_flow.RULE) == 1 and re.search(r"single mode.*`nio flow red`.*`nio flow green`", text), text[:900]
    print("ok")


# --- T-10: red (CT-7) ---

RUN = "python -m unittest tests/test_refund.py"
TEST = "tests/test_refund.py"


def claimed(**kw):
    root = impl(**kw)
    code, out = flow(root, "claim", S)
    assert code == 0, out
    return root


def red_one(**kw):
    """TC-9's red: T-1 claimed, its test written and red accepted."""
    root = claimed(**kw)
    write_test(root)
    code, out = flow(root, "red", S, "T-1", "--run", RUN)
    assert code == 0, out
    return root


def code_with(root, body="def refund(x):\n    return x\n"):
    (root / "app.py").write_text(body)


def sha_of(root, name=TEST):
    return nio_flow.sha((root / name).read_bytes())


def st(root, tid="T-1"):
    return implement.status(root, S, lines(root))[tid]


def of(root, kind, tid="T-1"):
    return [x for x in lines(root) if x["kind"] == kind and x["evidence"].get("task") == tid]


def test_ac9_red_accepted():
    root = claimed()
    write_test(root)
    code, out = flow(root, "red", S, "T-1", "--run", RUN)
    assert code == 0 and "red: T-1 accepted" in out and f"frozen:\n  {TEST}" in out, out
    last = lines(root)[-1]
    ev = last["evidence"]
    assert last["kind"] == "red" and ev["task"] == "T-1" and ev["command"] == RUN and ev["runner"] == "unittest", last
    assert re.fullmatch(r"[0-9a-f]{64}", ev["output"]) and ev["frozen"] == {TEST: sha_of(root)}, ev
    assert st(root) == "red"
    print("ok")


def test_ac12_unknown_runner():
    root = claimed()
    write_test(root)
    with open(root / TEST, "a") as f:
        f.write("\n\nunittest.main()\n")
    code, out = flow(root, "red", S, "T-1", "--run", f"PYTHONPATH=. python {TEST}")
    assert code == 0, out
    assert lines(root)[-1]["evidence"]["runner"] == "unknown", lines(root)[-1]
    print("ok")


def test_ac33_shared_test_file():
    root = impl()
    shared = "tests/test_refunds.py"  # TC-1 and TC-2's file in the plan fixture
    write_test(root, shared)
    first = sha_of(root, shared)
    L1 = lambda kind, **ev: {"kind": kind, "from": "implementing", "to": "implementing", "evidence": {"task": "T-1", **ev}}
    test_flow.history(root, S, L1("baseline", command=SUITE, code=0, failing=[], collected=2, runner="unittest"),
                      L1("claim"), L1("red", command=f"python -m unittest {shared}", frozen={shared: first}),
                      L1("green"), L1("review", passed=True), L1("task_done", commit="c"))
    code_with(root)
    git(root, "checkout", "-q", "-b", f"nio/{S}")
    commit_all(root, "T-1: Refund a paid order in full")
    code, out = flow(root, "claim", S)
    assert code == 0 and "task: T-2" in out, out
    with open(root / shared, "a") as f:
        f.write("\n    def test_second_refund(self):\n        self.assertEqual(getattr(app, 'refund_again', lambda x: 0)(1), 1)\n")
    code, out = flow(root, "red", S, "T-2", "--run", f"python -m unittest {shared}")
    assert code == 0, out
    frozen = of(root, "red", "T-2")[-1]["evidence"]["frozen"]
    assert frozen == {shared: sha_of(root, shared)} and frozen[shared] != first, frozen
    print("ok")


def test_ac42_single():
    root = claimed(modes={"T-1": "single"})
    write_test(root)
    code, out = flow(root, "red", S, "T-1", "--run", RUN, "--by", "worker / test / test")
    assert code == 0, out
    last = lines(root)[-1]
    assert last["kind"] == "red" and last["who"]["role"] == "worker" and last["evidence"]["command"] == RUN, last
    assert last["evidence"]["frozen"] == {TEST: sha_of(root)} and last["evidence"]["runner"] == "unittest", last
    # in split mode the worker never reports red itself (CT-15)
    root = claimed()
    write_test(root)
    n = len(lines(root))
    code, out = flow(root, "red", S, "T-1", "--run", RUN, "--by", "worker / test / test")
    assert code == 1 and "single mode" in out and len(lines(root)) == n, out
    print("ok")


# --- T-11: refusals, attempts and the cap (CT-7, CT-10) ---

def test_ac10_test_passes_first():
    root = claimed()
    write_test(root)
    code_with(root)
    code, out = flow(root, "red", S, "T-1", "--run", RUN)
    assert code == 1 and "the test passes before the code exists" in out and "collection, import or syntax error" not in out, out
    assert st(root) == "claimed" and lines(root)[-1]["kind"] == "refused" and state(root)["attempts"] == {"T-1": 1}
    print("ok")


def test_ac11_wrong_reason():
    def nomodule(root):
        write_test(root)
        (root / TEST).write_text("import nosuchmodule\n" + (root / TEST).read_text())

    def syntax(root):
        (root / TEST).write_text("import unittest\n\ndef broken(:\n")

    def package(root):
        write_test(root)
        (root / "tests/__init__.py").write_text("raise RuntimeError('boom')\n")

    for make in (nomodule, syntax, package):
        root = claimed()
        make(root)
        code, out = flow(root, "red", S, "T-1", "--run", RUN)
        assert code == 1 and "collection, import or syntax error" in out, (make.__name__, out)
        assert st(root) == "claimed", make.__name__
    print("ok")


def test_ac38_cargo_and_mvn():
    assert implement.runner(f"cargo test {TEST}") == "cargo test" and implement.runner(f"mvn test {TEST}") is None
    assert implement.wrong_reason("cargo test", 101, "error[E0308]: mismatched types").startswith("collection, import or syntax")
    assert implement.wrong_reason(None, 1, "") == ""
    bin_ = Path(tempfile.mkdtemp())
    for name, body in (("cargo", "echo 'error[E0308]: mismatched types'\nexit 101"), ("mvn", "exit 1")):
        (bin_ / name).write_text(f"#!/bin/sh\n{body}\n")
        (bin_ / name).chmod(0o755)
    root = claimed()
    write_test(root)
    old = os.environ["PATH"]
    os.environ["PATH"] = f"{bin_}:{old}"
    try:
        code, out = flow(root, "red", S, "T-1", "--run", f"cargo test {TEST}")
        assert code == 1 and "error[E" in out and st(root) == "claimed", out
        code, out = flow(root, "red", S, "T-1", "--run", f"mvn test {TEST}")
        assert code == 0 and lines(root)[-1]["evidence"]["runner"] == "unknown", out
    finally:
        os.environ["PATH"] = old
    print("ok")


def test_ac43_no_test_command():
    root = claimed()
    write_test(root)
    code, out = flow(root, "red", S, "T-1", "--run", f"{RUN} -k nothing")
    assert code == 1 and "no tests ran" in out and "collection, import or syntax error" not in out, out
    code, out = flow(root, "red", S, "T-1", "--run", "test -e src/new.py")
    assert code == 1 and f"doesn't name {TEST}" in out, out
    assert st(root) == "claimed" and state(root)["attempts"] == {"T-1": 2}
    print("ok")


def test_ac49_time_limit():
    root = claimed(cfg={"tests": {"timeout": 1}})
    (root / TEST).write_text("import os\nimport time\nimport unittest\n\n\nclass T(unittest.TestCase):\n"
                             "    @classmethod\n    def setUpClass(cls):\n"
                             "        open('pgid', 'w').write(str(os.getpgid(0)))\n        time.sleep(5)\n\n"
                             "    def test_refund(self):\n        pass\n")
    start = time.time()
    code, out = flow(root, "red", S, "T-1", "--run", RUN)
    assert code == 1 and "time limit" in out and time.time() - start < 3, (out, time.time() - start)
    code, out = flow(root, "red", S, "T-1", "--run", f"nosuchprog {TEST}")
    assert code == 1 and "program not found" in out, out
    assert state(root)["attempts"] == {"T-1": 2}
    time.sleep(0.2)
    try:
        os.killpg(int((root / "pgid").read_text()), 0)
        raise AssertionError("the timed-out test is still running")
    except ProcessLookupError:
        pass
    print("ok")


def blocked_one():
    """TC-23's T-1: red, then three greens on code that fails its test."""
    root = red_one()
    code_with(root, "def refund(x):\n    return 0\n")
    for n in (1, 2):
        code, out = flow(root, "green", S, "T-1")
        assert code == 1 and state(root)["attempts"] == {"T-1": n}, out
    code, out = flow(root, "green", S, "T-1")
    assert code == 1 and "blocked" in out, out
    return root


def test_ac23_third_attempt_blocks():
    root = blocked_one()
    block = lines(root)[-1]
    ev = block["evidence"]
    assert block["kind"] == "blocked" and ev["cause"] == "attempts" and ev["task"] == "T-1", block
    assert re.fullmatch(r"\.nio/runs/R-[\w-]+/T-1\.patch", ev["patch"]) and "return 0" in (root / ev["patch"]).read_text(), ev
    assert implement.dirty(root, S) == [] and not (root / TEST).exists() and (root / "app.py").read_text() == ""
    assert st(root) == "blocked" and state(root)["claims"] == {}
    assert state(root)["waiting"] == {"why": "T-1 blocked after 3 attempts", "task": "T-1"}, state(root)
    code, out = flow(root, "next", S)
    assert "waiting_for_human" in out and "T-1" in out, out
    assert flow(root, "claim", S)[0] == 1
    print("ok")


# --- T-12: unblock (CT-12) ---

def test_ac36_unblock():
    root = blocked_one()
    old = of(root, "red")[0]["evidence"]["frozen"][TEST]
    code, out = flow(root, "unblock", S, "T-1", "--human", "")
    assert code == 1 and "--human needs a reason" in out, out
    code, out = flow(root, "unblock", S, "T-2", "--human", "x")
    assert code == 1 and "T-2 is pending" in out, out
    code, out = flow(root, "unblock", S, "T-1", "--human", "fixed the fixture", "--by", "human")
    assert code == 0 and "unblocked: T-1" in out, out
    assert lines(root)[-1]["kind"] == "unblock" and lines(root)[-1]["reason"] == "fixed the fixture"
    assert st(root) == "ready" and "T-1" not in state(root)["attempts"] and state(root)["waiting"] is None, state(root)
    assert flow(root, "claim", S)[0] == 0
    code, out = flow(root, "green", S, "T-1")
    assert code == 1 and "has no failing test first" in out, out
    write_test(root)
    (root / TEST).write_text((root / TEST).read_text().replace("(40), 40)", "(50), 50)"))
    code, out = flow(root, "red", S, "T-1", "--run", RUN)
    assert code == 0, out
    new = of(root, "red")[-1]["evidence"]["frozen"][TEST]
    assert new == sha_of(root) and new != old
    print("ok")


# --- T-13: green (CT-8) ---

def passed(root, tid="T-1"):
    last = lines(root)[-1]
    return last["kind"] == "review" and last["evidence"]["task"] == tid and last["evidence"]["passed"]


def test_ac13_green_same_command():
    root = red_one()
    code_with(root)
    code, out = flow(root, "green", S, "T-1")
    assert code == 0 and "green: T-1 accepted" in out and "review: passed" in out and re.search(r"done: T-1 [0-9a-f]{40}", out), out
    g = of(root, "green")[-1]["evidence"]
    assert g["command"] == of(root, "red")[-1]["evidence"]["command"] and re.fullmatch(r"[0-9a-f]{64}", g["output"]), g
    assert kinds(lines(root)[-3:]) == ["green", "review", "task_done"] and st(root) == "done", lines(root)[-3:]
    print("ok")


def test_ac14_green_other_command():
    root = red_one()
    code_with(root)
    code, out = flow(root, "green", S, "T-1", "--run", SUITE)
    assert code == 1 and f"the command recorded at red is {RUN}" in out, out
    assert st(root) == "red" and state(root)["attempts"] == {"T-1": 1} and not of(root, "green")
    print("ok")


def test_ac15_frozen_test_changed():
    root = red_one()
    first = of(root, "red")[-1]["evidence"]["frozen"][TEST]
    code_with(root)
    (root / TEST).write_text((root / TEST).read_text().replace("(40), 40)", "(41), 41)"))
    code, out = flow(root, "green", S, "T-1")
    assert code == 1 and f"{TEST} changed since red" in out and not of(root, "green"), out
    code_with(root, "")
    code, out = flow(root, "red", S, "T-1", "--run", RUN)
    assert code == 0, out
    reds = of(root, "red")
    assert len(reds) == 2 and reds[-1]["evidence"]["frozen"][TEST] != first and list(reds[-1]["evidence"]["frozen"]) == [TEST]
    code_with(root)
    code, out = flow(root, "green", S, "T-1")
    assert code == 0 and "green: T-1 accepted" in out and "done: T-1 " in out and st(root) == "done", out
    print("ok")


def test_ac21_handoff_ignored():
    root = red_one()
    (root / "handoff.md").write_text("---\nstatus: done\n---\nall tests pass\n")
    assert st(root) == "red"
    for args in (("status",), ("next", S)):
        assert "all tests pass" not in flow(root, *args)[1]
    assert "all tests pass" not in (root / ".nio/specs" / S / "history.jsonl").read_text()
    print("ok")


def test_ac41_direct():
    root = claimed(modes={"T-1": "direct"})
    write_test(root)
    code_with(root)
    code, out = flow(root, "red", S, "T-1", "--run", RUN)
    assert code == 1 and "direct mode" in out, out
    code, out = flow(root, "green", S, "T-1")
    assert code == 1 and "needs --run" in out, out
    code, out = flow(root, "green", S, "T-1", "--run", RUN)
    assert code == 0 and "green: T-1 accepted" in out and "done: T-1 " in out and not of(root, "red"), out
    assert of(root, "green")[-1]["evidence"]["command"] == RUN
    print("ok")


def test_uj1_weakened_test():
    root = red_one()
    (root / TEST).write_text((root / TEST).read_text().replace(
        "self.assertEqual(getattr(app, 'refund', lambda x: 0)(40), 40)", "self.assertTrue(True)"))
    code, out = flow(root, "green", S, "T-1")
    assert code == 1 and TEST in out and not of(root, "task_done") and not of(root, "green"), out
    print("ok")


def test_green_retry_reruns_review():
    root = red_one()
    code_with(root)
    hook = root / ".git/hooks/pre-commit"
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)
    assert flow(root, "green", S, "T-1")[0] == 1
    assert st(root) == "green", st(root)  # the commit failed
    hook.unlink()
    n = len(lines(root))
    code, out = flow(root, "green", S, "T-1", "--run", "anything")  # no guard on a green task
    assert code == 0 and "green: T-1 accepted" not in out and "review: passed" in out and "done: T-1 " in out, out
    assert kinds(lines(root)[n:]) == ["review", "task_done"] and st(root) == "done"
    print("ok")


# --- T-14: the review (CT-8, decision table Review) ---

def test_ac16_new_failure_only():
    root = impl(alone=True)
    failing(root, "test_a")
    commit_all(root, "test_a fails")
    assert flow(root, "claim", S)[0] == 0
    write_test(root)
    assert flow(root, "red", S, "T-1", "--run", RUN)[0] == 0
    code_with(root)
    failing(root, "test_b")
    code, out = flow(root, "green", S, "T-1")
    assert code == 1 and "review: failed" in out, out
    ev = lines(root)[-1]["evidence"]
    assert lines(root)[-1]["kind"] == "review" and not ev["passed"], ev
    assert any("test_b" in f for f in ev["failing"]) and not any("test_a" in f for f in ev["failing"]), ev
    assert "test_b" in out and "test_a" not in out, out
    assert st(root) == "red" and state(root)["attempts"]["T-1"] == 1
    print("ok")


def test_ac17_outside_files():
    root = red_one()
    code_with(root, "from helpers import half\n\n\ndef refund(x):\n    return x\n")
    (root / "helpers.py").write_text("def half(x):\n    return x / 2\n")
    code, out = flow(root, "green", S, "T-1")
    review = of(root, "review")[-1]["evidence"]
    assert code == 0 and review["passed"] and review["outside"] == ["helpers.py"] and "done: T-1 " in out, review
    assert "outside the task's files: helpers.py" in out, out
    print("ok")


def test_ac18_spec_edited():
    for name in ("spec.md", "tests.md"):  # tests.md: TC-45
        root = red_one()
        code_with(root)
        with open(root / ".nio/specs" / S / name, "a") as f:
            f.write("\nOne more line.\n")
        code, out = flow(root, "green", S, "T-1")
        assert code == 1 and f"the task edited {name}" in out, out
        assert st(root) not in ("done", "green") and not lines(root)[-1]["evidence"]["passed"]
    print("ok")


def test_ac35_unknown_runner_review():
    root = impl(cfg={"tests": {"suite": "python check.py"}}, alone=True)
    (root / "check.py").write_text("import sys\nsys.exit(0)\n")
    commit_all(root, "check")
    assert flow(root, "claim", S)[0] == 0
    write_test(root)
    assert flow(root, "red", S, "T-1", "--run", RUN)[0] == 0
    code_with(root)
    (root / "check.py").write_text("import sys\nsys.exit(1)\n")
    code, out = flow(root, "green", S, "T-1")
    assert code == 1 and "new failure" in out and not lines(root)[-1]["evidence"]["passed"], out
    print("ok")


def test_ac37_review_fail_to_red():
    root = red_one(alone=True)
    frozen = of(root, "red")[-1]["evidence"]["frozen"]
    code_with(root)
    failing(root, "test_c")
    code, out = flow(root, "green", S, "T-1")
    assert code == 1 and "test_c" in out, out
    assert st(root) == "red" and state(root)["attempts"] == {"T-1": 1}
    assert of(root, "red")[-1]["evidence"]["frozen"] == frozen == {TEST: sha_of(root)}
    print("ok")


def test_ac44_broken_or_fewer():
    many = "import unittest\n\n\nclass M(unittest.TestCase):\n" + "".join(
        f"    def test_{i}(self):\n        pass\n\n" for i in range(40))
    for case in ("import", "fewer"):
        root = impl(alone=True)
        (root / "tests/test_base.py").unlink()
        (root / "tests/test_many.py").write_text(many)
        commit_all(root, "40 tests")
        assert flow(root, "claim", S)[0] == 0
        assert lines(root)[-2]["evidence"]["collected"] == 40, lines(root)[-2]
        write_test(root)
        assert flow(root, "red", S, "T-1", "--run", RUN)[0] == 0
        code_with(root)
        if case == "import":
            (root / "tests/test_many.py").write_text("import nosuchmodule\n" + many)
        else:  # three gone, with T-1's own test added: 38
            (root / "tests/test_many.py").write_text(many.replace("    def test_0(", "    def _0(")
                                                     .replace("    def test_1(", "    def _1(").replace("    def test_2(", "    def _2("))
        code, out = flow(root, "green", S, "T-1")
        want = "the suite is broken: collection, import or syntax error" if case == "import" else "38 tests collected against the baseline's 40"
        assert code == 1 and want in out, (case, out)
    print("ok")


def test_ac50_direct_review_fail():
    root = claimed(modes={"T-1": "direct"}, alone=True)
    write_test(root)
    code_with(root)
    failing(root, "test_c")
    code, out = flow(root, "green", S, "T-1", "--run", RUN)
    assert code == 1 and "review: failed" in out, out
    assert st(root) == "claimed" and state(root)["attempts"] == {"T-1": 1} and not of(root, "red")
    print("ok")


# --- T-15, T-16: the commit (CT-9) ---

def on_main():
    """TC-9's red on a repo whose default branch is main, with `refund` written; (root, main's HEAD)."""
    root = impl()
    git(root, "branch", "-M", "main")
    head = git(root, "rev-parse", "main").strip()
    assert flow(root, "claim", S)[0] == 0
    write_test(root)
    assert flow(root, "red", S, "T-1", "--run", RUN)[0] == 0
    code_with(root)
    return root, head


def reject(root, body="exit 1"):
    hook = root / ".git/hooks/pre-commit"
    hook.write_text(f"#!/bin/sh\n{body}\n")
    hook.chmod(0o755)
    return hook


def test_ac26_commit():
    root, head = on_main()
    code, out = flow(root, "green", S, "T-1")
    assert code == 0, out
    assert git(root, "log", "-1", "--format=%s").strip() == "T-1: Refund a paid order in full"
    names = git(root, "show", "--name-only", "--format=", "HEAD").split()
    assert "app.py" in names and f".nio/specs/{S}/history.jsonl" in names and f".nio/specs/{S}/state.json" in names, names
    assert git(root, "rev-parse", "main").strip() == head and git(root, "branch", "--show-current").strip() == f"nio/{S}"
    assert out.strip().splitlines()[-1] == f"done: T-1 {git(root, 'rev-parse', 'HEAD').strip()}", out
    assert git(root, "status", "--porcelain", "--", "app.py", TEST) == ""
    print("ok")


def test_ac46_commit_refuses_off_branch():
    root, _ = on_main()
    git(root, "checkout", "-q", "-b", "other")
    code, out = flow(root, "green", S, "T-1")
    assert code == 1 and f"nio/{S}" in out and not of(root, "task_done"), out
    assert "T-1:" not in git(root, "log", "--format=%s")
    print("ok")


def test_ac20_status_from_history():
    root, _ = on_main()
    assert flow(root, "green", S, "T-1")[0] == 0
    got = state(root)
    assert set(got) <= set(nio_flow.STATE_KEYS) and got["claims"] == {}, got
    assert not re.search(r'"(done|red)"', json.dumps(got)), got
    assert implement.status(root, S, lines(root))["T-1"] == "done"
    print("ok")


def test_ac22_done_refuses():
    root, _ = on_main()
    assert flow(root, "green", S, "T-1")[0] == 0
    n = len(lines(root))
    for args in (("red", S, "T-1", "--run", RUN), ("green", S, "T-1")):
        code, out = flow(root, *args)
        assert code == 1 and "T-1 is done" in out, out
    assert len(lines(root)) == n
    print("ok")


def test_ac47_commit_rejected():
    root, _ = on_main()
    folder = root / ".nio/specs" / S
    hook = reject(root, "echo hook-says-no-T1 >&2\nexit 1")
    before = (folder / "history.jsonl").read_bytes()
    code, out = flow(root, "green", S, "T-1")
    assert code == 1 and "hook-says-no-T1" in out, out
    assert "T-1:" not in git(root, "log", "--format=%s") and not of(root, "task_done") and st(root) == "green"
    code, out = flow(root, "next", S)
    assert "waiting_for_human" in out and "hook-says-no-T1" in out and "nio flow green" in out, out
    after = (folder / "history.jsonl").read_bytes()
    assert after.startswith(before) and kinds(lines(root)[-3:]) == ["green", "review", "fail"], kinds(lines(root))
    assert after[len(before):].count(b"\n") == 3
    assert state(root)["waiting"] == {"why": "commit failed: hook-says-no-T1", "task": "T-1"}, state(root)
    assert git(root, "diff", "--cached") == ""
    hook.unlink()
    code, out = flow(root, "green", S, "T-1")
    assert code == 0 and git(root, "log", "-1", "--format=%s").startswith("T-1:"), out
    assert state(root)["waiting"] is None
    print("ok")


SITE = """import atexit, json, os, socket, sys
real = socket.socket.connect
tried = []
def connect(self, addr):
    if self.family != socket.AF_UNIX:
        tried.append(repr(addr))
        raise OSError("network blocked")
    return real(self, addr)
socket.socket.connect = connect
if os.environ.setdefault("NIO_MAIN_PID", str(os.getpid())) == str(os.getpid()):
    atexit.register(lambda: open(os.environ["NIO_REPORT"], "w").write(json.dumps({"modules": sorted(sys.modules), "tried": tried})))
"""
DRIVER = """import pathlib, sys
from nio.cli import main
for arg in sys.argv[1:]:
    if arg.startswith("write:"):
        name, text = arg[6:].split(":", 1)
        pathlib.Path(name).write_text(text)
        continue
    sys.argv = ["nio", "flow", *arg.split("|")]
    try:
        main()
    except SystemExit as e:
        assert not e.code, arg
"""


def test_nfr1_no_model_calls():
    root = impl()  # with memory records: the pack's recall may load nio's local embedder (C-261029-e54w)
    site = Path(tempfile.mkdtemp())
    (site / "sitecustomize.py").write_text(SITE)
    report = site / "report.json"
    write_test(site, "t.py")
    test_text = (site / "t.py").read_text()
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(filter(None, [str(site), os.environ.get("PYTHONPATH")])), "NIO_REPORT": str(report)}
    env.pop("NIO_MAIN_PID", None)
    r = subprocess.run([sys.executable, "-c", DRIVER, f"claim|{S}|--by|{BY}", f"write:{TEST}:{test_text}",
                        f"red|{S}|T-1|--run|{RUN}|--by|{BY}", "write:app.py:def refund(x):\n    return x\n",
                        f"green|{S}|T-1|--by|{BY}"], cwd=root, capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert st(root) == "done", st(root)
    got = json.loads(report.read_text())
    assert got["tried"] == [], got["tried"]
    loaded = [m for m in got["modules"] if m.split(".")[0] in ("anthropic", "openai")]  # API model clients (C-261029-e54w)
    assert not loaded, loaded
    print("ok")


# --- T-17, T-18: block on a spec problem (CT-11) ---

HANDOFF = ("---\nstatus: blocked\nchange_request:\n  spec_says: \"refund any order\"\n  code_shows: \"orders have no paid flag\"\n"
           "  smallest_change: \"add paid to Order\"\n---\nNotes.\n")


def changes(root):
    return sorted((root / ".nio/memory").rglob("C-*.md"))


def handoff(root, text=HANDOFF):
    (root / "handoff.md").write_text(text)
    return str(root / "handoff.md")


def test_ac25_block_files_change():
    root = red_one()
    code_with(root)
    before = changes(root)
    code, out = flow(root, "block", S, "T-1", "--handoff", handoff(root))
    new = [p for p in changes(root) if p not in before]
    assert code == 0 and len(new) == 1 and "blocked: T-1" in out, out
    text = new[0].read_text()
    meta = records.parse(new[0])[0]
    assert meta["outcome"] == "pending" and meta["against"] == f".nio/specs/{S}/spec.md" and meta["id"] in out, text
    for part in ("refund any order", "orders have no paid flag", "add paid to Order"):
        assert part in text, part
    line = lines(root)[-1]
    ev = line["evidence"]
    assert line["kind"] == "blocked" and ev["cause"] == "spec" and line["change"] == meta["id"] and len(ev["handoff"]) == 64, line
    assert "def refund" in (root / ev["patch"]).read_text() and implement.dirty(root, S) == [], ev  # the record is the human's
    assert (root / "app.py").read_text() == ""
    assert st(root) == "blocked" and state(root)["claims"] == {} and state(root)["attempts"] == {}, state(root)
    assert state(root)["waiting"] == {"why": "spec problem in T-1", "task": "T-1", "change": meta["id"]}, state(root)
    for bad in (HANDOFF.replace("blocked", "done"), HANDOFF.replace('  smallest_change: "add paid to Order"\n', ""), "no front matter\n"):
        n = len(lines(root))
        code, out = flow(root, "block", S, "T-1", "--handoff", handoff(root, bad))
        assert code == 1 and "handoff is not blocked with a change_request" in out and len(lines(root)) == n, out
    assert len(changes(root)) == len(before) + 1
    print("ok")


def test_ac48_block_twice():
    root = red_one()
    code_with(root)
    first = flow(root, "block", S, "T-1", "--handoff", handoff(root))[1].split()[-1]
    n = len(lines(root))
    code, out = flow(root, "block", S, "T-1", "--handoff", handoff(root))
    assert code == 0 and out.split()[-1] == first and len(lines(root)) == n, out
    assert len([p for p in changes(root) if first in p.name]) == 1 and len(of(root, "blocked")) == 1
    code, out = flow(root, "next", S)
    assert "waiting_for_human" in out and "T-1" in out and first in out, out
    assert f"nio flow unblock {S} T-1" in out, out
    # a record exists but the blocked line is missing: reuse the record and write the rest
    root = red_one()
    code_with(root)
    rec = records.new(root, "change", "project", "Spec problem in T-1: refund any order")
    rec.write_text(rec.read_text().replace('against: ""', f'against: ".nio/specs/{S}/spec.md"') + "\nHandoff: "
                   + nio_flow.sha((Path(handoff(root))).read_bytes()) + "\n")
    cid = records.parse(rec)[0]["id"]
    code, out = flow(root, "block", S, "T-1", "--handoff", str(root / "handoff.md"))
    assert code == 0 and out.split()[-1] == cid and len(changes(root)) == 1, out
    assert st(root) == "blocked" and state(root)["waiting"]["change"] == cid and len(of(root, "blocked")) == 1
    print("ok")


def blocked_record(root):
    """Run `nio flow block` on a claimed T-1; returns the filed record."""
    code, out = flow(root, "block", S, "T-1", "--handoff", handoff(root, HANDOFF.replace("refund any order", "FR-2 says X")
                     .replace("orders have no paid flag", "the code does Y").replace("add paid to Order", "say Y in FR-2")))
    assert code == 0, out
    return changes(root)[-1]


def nio_check(root):
    r = subprocess.run([sys.executable, "-c", "from nio.cli import main; main()", "check"], cwd=root, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def test_ac1_block_record_passes_check():
    root = claimed()
    rec = blocked_record(root)
    errors = records.check(root)[0]
    assert not [e for e in errors if rec.name in e], errors
    git(root, "add", str(rec.relative_to(root)))
    code, out = nio_check(root)
    assert code == 0, out
    print("ok")


def test_ac2_block_sections():
    root = claimed()
    body = blocked_record(root).read_text()
    wrong = body.partition("## What is wrong")[2].partition("## Proposed change")[0]
    prop = body.partition("## Proposed change")[2].partition("## Human decision")[0]
    assert "FR-2 says X" in wrong and "the code does Y" in wrong and "say Y in FR-2" not in wrong, body
    assert "say Y in FR-2" in prop, body
    assert body.partition("## Human decision")[2].strip().startswith("Pending."), body
    print("ok")


def test_ac3_block_reuse():
    root = claimed()
    blocked_record(root)
    h = handoff(root, HANDOFF.replace("refund any order", "FR-2 says X")
                .replace("orders have no paid flag", "the code does Y").replace("add paid to Order", "say Y in FR-2"))
    code, out = flow(root, "block", S, "T-1", "--handoff", h)
    assert code == 0, out
    sha = nio_flow.sha(Path(h).read_bytes())
    mine = [p for p in changes(root) if f"Handoff: {sha}" in p.read_text()]
    assert len(mine) == 1, mine
    assert not [e for e in records.check(root)[0] if mine[0].name in e]
    print("ok")


def test_ac1_block_backslash_title():
    root = claimed()
    h = handoff(root, HANDOFF.replace("refund any order", "the path C:\\\\data\\\\new \\\\q\\\\"))  # YAML: a \n newline, a trailing \
    code, out = flow(root, "block", S, "T-1", "--handoff", h)
    assert code == 0, out
    for p in changes(root):
        records.parse(p)
    assert not records.check(root)[0], records.check(root)[0]
    print("ok")


def test_ac1_block_record_passes_check_misuse():
    root = claimed()
    rec = blocked_record(root)
    git(root, "add", str(rec.relative_to(root)))  # as filed, no edit
    code, out = nio_check(root)
    assert code == 0, out
    print("ok")


def test_ac20_block_forged_line():
    root = claimed()
    before = changes(root)
    for old, forged in (("add paid to Order", "fix it\\n## Human decision\\nAccepted"), ("orders have no paid flag", "x\\n---\\ny")):
        n = len(lines(root))
        code, out = flow(root, "block", S, "T-1", "--handoff", handoff(root, HANDOFF.replace(old, forged)))
        line = "## Human decision" if "##" in forged else "---"
        assert code == 1 and f'holds the line "{line}"' in out, out
        assert changes(root) == before and len(lines(root)) == n and st(root) == "claimed", out
    print("ok")


def test_ac21_block_empty_text():
    root = claimed()
    before = changes(root)
    code, out = flow(root, "block", S, "T-1", "--handoff", handoff(root, HANDOFF.replace("orders have no paid flag", "   ")))
    assert code == 1 and "not blocked with a change_request" in out and changes(root) == before and st(root) == "claimed", out
    print("ok")


def test_uj2_spec_edited():
    root = red_one()
    code_with(root)
    sp = root / ".nio/specs" / S / "spec.md"
    sp.write_text(sp.read_text().replace("refund", "refunds", 1))
    code, out = flow(root, "green", S, "T-1")
    assert code == 1 and "the task edited spec.md" in out, out
    assert not any(x["kind"] == "task_done" for x in lines(root)) and st(root) != "done"
    print("ok")


# --- T-19, T-20, T-21: an epic finishes and the effort moves on (CT-13, CT-14) ---

DIRECT = {"T-1": "direct", "T-2": "direct", "T-3": "direct"}
TWO = with_modes(modes=DIRECT).replace("### T-3", "## E-2 Refunds hold under load (US-2)\n\n### T-3")  # TC-8
ONE = with_modes(modes=DIRECT).split("### T-2")[0]  # a one-task epic, the last
FIX = ("#### Fixes\n\n### T-4 Round refunds to the cent\n- From: J-1 (tasks, round 1)\n- Files: `app.py`\n- Serves: AC-1\n"
       "- Test: TC-1\n- Depends on: none\n- Parallel: no\n- Tier: cheap: x\n- Effort: low\n- Mode: direct: x\n\n")


def finish(root, tid):
    """Claim `tid` (direct), write its test and code, green it to done; the green's output."""
    code, out = flow(root, "claim", S)
    assert code == 0 and f"task: {tid} " in out, out
    write_test(root)
    code_with(root)
    code, out = flow(root, "green", S, tid, "--run", RUN)
    assert code == 0 and f"done: {tid} " in out, out
    return out


def epics(root):
    return [x for x in lines(root) if x["kind"] == "epic"]


def close(root, eid, reason="approved"):
    """What `nio flow done implementation-<eid>` writes once the gate is approved."""
    test_flow.history(root, S, {"kind": "epic", "from": "implementing", "to": "implementing", "reason": reason,
                                "evidence": {"epic": eid}})


def test_ac8_order():
    root = impl(tasks=TWO)
    for tid, nxt in (("T-1", "T-2"), ("T-2", "T-3"), ("T-3", None)):
        finish(root, tid)
        if tid == "T-2":
            close(root, "E-1")
        if nxt:
            assert f"task: {nxt} " in flow(root, "next", S)[1], flow(root, "next", S)
    print("ok")


def test_ac29_epic_waits_on_its_gate():
    root = impl(tasks=TWO)
    finish(root, "T-1")
    assert not epics(root)
    out = finish(root, "T-2")
    assert not epics(root) and "skipped: not built" not in out and "merge:" not in out, (epics(root), out)
    assert any(x.startswith("next:") and "implementation-E-1" in x for x in out.splitlines()), out
    assert lines(root)[-1]["to"] == "implementing", out
    assert "@nio:jury" in flow(root, "next", S)[1], flow(root, "next", S)
    code, out = flow(root, "claim", S)
    assert code == 1 and "E-1" in out and "implementation-E-1" in out, (code, out)
    close(root, "E-1")
    code, out = flow(root, "claim", S)
    assert code == 0 and "task: T-3 " in out, out
    print("ok")


def test_ac29_epic_skipped():
    root = impl(tasks=TWO)
    finish(root, "T-1")
    finish(root, "T-2")
    close(root, "E-1", "skipped: not built")  # an old line: the epic stays closed
    code, out = flow(root, "next", S)
    assert "never reviewed: E-1" in out.splitlines() and "task: T-3 " in out, out
    code, out = flow(root, "claim", S)
    assert code == 0 and "task: T-3 " in out, out
    print("ok")


def test_ac29_last_epic_merge_names_never_reviewed():
    root = impl(tasks=TWO)
    finish(root, "T-1")
    finish(root, "T-2")
    close(root, "E-1", "skipped: not built")
    finish(root, "T-3")
    close(root, "E-2")  # closed but the pass line is missing: done writes it and prints the merge
    code, out = flow(root, "done", "implementation-E-2", S, "--by", "human")
    rows = out.splitlines()
    assert code == 0 and any(x.startswith("merge:") for x in rows) and "never reviewed: E-1" in rows, (code, out)
    print("ok")


def test_full_suite_waits_for_the_epic_to_close():
    """#66: T-1 breaks another test and still passes its review; the task closing the epic answers for it."""
    root = impl(tasks=TWO)
    assert flow(root, "claim", S)[0] == 0
    write_test(root)
    code_with(root)
    failing(root, "test_b")
    code, out = flow(root, "green", S, "T-1", "--run", RUN)
    assert code == 0 and "review: passed" in out, out
    assert flow(root, "claim", S)[0] == 0
    code, out = flow(root, "green", S, "T-2", "--run", RUN)
    assert code == 1 and "review: failed" in out and "test_b" in out, out
    assert not epics(root), epics(root)
    (root / "tests/test_b.py").unlink()
    code, out = flow(root, "green", S, "T-2", "--run", RUN)
    assert code == 0 and "review: passed" in out and "epic: E-1 finished" in out, out
    print("ok")


def test_tests_epic_replaces_the_suite_until_the_last_epic():
    """#66: `tests.epic` closes E-1 past a break only the full suite sees; the last epic's close still catches it."""
    root = impl(tasks=TWO, cfg={"tests": {"epic": "python -m unittest tests/test_base.py"}})
    assert flow(root, "claim", S)[0] == 0
    write_test(root)
    code_with(root)
    failing(root, "test_b")
    assert flow(root, "green", S, "T-1", "--run", RUN)[0] == 0
    finish(root, "T-2")
    close(root, "E-1")  # E-1 closed: fewer tests collected than the baseline is no failure here
    while True:
        code, out = flow(root, "claim", S)
        assert code == 0, out
        tid = re.search(r"task: (T-\d+)", out)[1]
        write_test(root)
        code_with(root)
        code, out = flow(root, "green", S, tid, "--run", RUN)
        if code:
            break
    assert "review: failed" in out and "test_b" in out and len(epics(root)) == 1, out
    (root / "tests/test_b.py").unlink()
    code, out = flow(root, "green", S, tid, "--run", RUN)
    assert code == 0 and "epic: E-2 finished" in out, out
    print("ok")


def test_ac30_epic_report():
    root = impl(tasks=ONE)
    failing(root, "test_a")
    commit_all(root, "a failing test")
    assert flow(root, "claim", S)[0] == 0
    write_test(root)
    code_with(root)
    (root / "helpers.py").write_text("x = 1\n")
    code, out = flow(root, "green", S, "T-1", "--run", RUN)
    assert code == 0, out
    sha = git(root, "rev-parse", "HEAD").strip()
    rows = out.splitlines()
    assert any(f"T-1 {sha}" in x for x in rows), out
    assert any("baseline" in x and "test_a" in x for x in rows), out
    assert any("helpers.py" in x and "T-1" in x for x in rows), out
    print("ok")


def fixed():
    """TC-32's setup: TWO with T-1 done, a fix task T-4 under E-1's `#### Fixes`, committed, then T-2 done."""
    root = impl(tasks=TWO)
    finish(root, "T-1")
    tp = root / ".nio/specs" / S / "tasks.md"
    tp.write_text(tp.read_text().replace("## E-2", FIX + "## E-2"))
    commit_all(root, "fix task T-4")
    return root, finish(root, "T-2")


def test_ac32_fix_task_next():
    root, out = fixed()
    assert not epics(root) and "notify:" not in out, out
    code, out = flow(root, "claim", S)
    assert code == 0 and "task: T-4 " in out, out
    print("ok")


def test_uj3_open_fix_task():
    root, _ = fixed()
    task = next(t for t in implement.tasks_of(root, S) if t["id"] == "T-2")
    review = [x for x in lines(root) if x["kind"] == "review" and x["evidence"]["task"] == "T-2"][-1]
    entries, report = implement.epic_end(root, S, task, review)
    assert entries == [] and not any(x.startswith("notify:") for x in report) and not epics(root), (entries, report)
    print("ok")


def one_done():
    """TC-28: one direct task greened to done on a repo whose default branch is main; (root, main's HEAD, output)."""
    root = impl(tasks=ONE)
    git(root, "branch", "-M", "main")
    head = git(root, "rev-parse", "main").strip()
    return root, head, finish(root, "T-1")


def test_ac28_no_merge():
    root, head, out = one_done()
    assert git(root, "rev-parse", "main").strip() == head and git(root, "branch", "--show-current").strip() == f"nio/{S}"
    assert f"merge: nio/{S}" not in out.splitlines() and not epics(root), out
    print("ok")


def test_ac31_effort_done():
    root, _, _ = one_done()
    out = flow(root, "next", S)[1]
    assert "state: implementing" in out and "@nio:jury" in out, out  # done only after `flow done implementation-E-1`
    assert lines(root)[-1]["kind"] != "pass", lines(root)[-1]
    folder = f".nio/specs/{S}"
    assert git(root, "status", "--porcelain", "--", f"{folder}/history.jsonl", f"{folder}/state.json") == ""  # in T-1's commit
    print("ok")


def test_ac39_changed_task_new_number():
    root = impl(modes=DIRECT)
    finish(root, "T-1")
    finish(root, "T-2")
    test_flow.history(root, S, {"kind": "back", "from": "implementing", "to": "tasking", "change": "C-261029-xxxx"})
    tp = root / ".nio/specs" / S / "tasks.md"
    text = tp.read_text()
    block = text[text.index("### T-2"):text.index("### T-3")]
    changed_ = block.replace("### T-2 Reject a second refund", "### T-4 Reject a second refund, naming the order")
    tp.write_text(text.replace(block, changed_).replace("retired: []", "retired: [T-2]").replace("Depends on: T-2", "Depends on: T-4"))
    test_flow.approve(root, S, "tasks", run="R-tasks-round-2")
    st_ = implement.status(root, S, lines(root))
    assert st_["T-1"] == "done" and st_["T-2"] == "done", st_
    code, out = flow(root, "claim", S)
    assert code == 0 and "task: T-4 " in out, out
    subjects = git(root, "log", "--format=%s", f"nio/{S}")
    assert "T-1: Refund a paid order in full" in subjects and "T-2: Reject a second refund" in subjects, subjects
    print("ok")


def test_memory_records_are_the_humans():
    """Follow-up to QS-3: a spec problem's change record, untracked under .nio/memory/, holds no claim and never rides
    along in a task's commit."""
    root = red_one()
    code_with(root)
    code, out = flow(root, "block", S, "T-1", "--handoff", handoff(root))
    assert code == 0, out
    rec = [p for p in changes(root)][-1]
    rel = str(rec.relative_to(root))
    rec.write_text(rec.read_text().replace("outcome: pending", "outcome: rejected"))  # the human decided it
    assert flow(root, "unblock", S, "T-1", "--human", "spec settled", "--by", "human")[0] == 0
    code, out = flow(root, "claim", S)
    assert code == 0 and "task: T-1 " in out, out
    write_test(root)
    assert flow(root, "red", S, "T-1", "--run", RUN)[0] == 0, out
    code_with(root)
    code, out = flow(root, "green", S, "T-1")
    assert code == 0 and "done: T-1" in out, out
    assert rel not in git(root, "show", "--name-only", "--format=", "HEAD").split()
    assert git(root, "status", "--porcelain", "--", rel).startswith("??")
    print("ok")

# --- T-4: red reads the task's own TC IDs (CT-2, CT-3) ---
# TC-1's file is tests/test_refund.py, TC-2 to TC-4's is tests/test_refunds.py; they stand in for the plan's TC-10 / TC-38.

def own_red(test_line, command, name="tests/test_refund.py"):
    """T-1 claimed with `test_line` as its Test: line, `name` failing on `assert False`, then red with `command`."""
    old = "- Test: TC-1\n"
    assert old in REFUNDS
    root = claimed(tasks=with_modes().replace(old, f"- Test: {test_line}\n", 1))
    (root / name).write_text("import unittest\n\n\nclass T(unittest.TestCase):\n    def test_x(self):\n        assert False\n")
    code, out = flow(root, "red", S, "T-1", "--run", command)
    return root, code, out


def test_ac4_red_deferred_not_required():
    root, code, out = own_red("TC-1; TC-2 proved later by T-2", "python -m unittest tests/test_refund.py")
    assert code == 0 and st(root) == "red", out
    print("ok")


def test_ac5_red_deferred_file_only():
    root, code, out = own_red("TC-1; TC-2 proved later by T-2", "python -m unittest tests/test_refunds.py", "tests/test_refunds.py")
    assert code == 1 and "tests/test_refund.py" in out and "tests/test_refunds.py" not in out, out
    assert lines(root)[-1]["kind"] == "refused"
    print("ok")


def test_ac6_red_all_deferred():
    root, code, out = own_red("a direct unit check calling `load`; TC-2 and TC-3 proved later by T-2",
                              "python -m unittest tests/test_c.py", "tests/test_c.py")
    assert code == 0 and st(root) == "red", out
    print("ok")


def test_ac7_red_proving_task():
    root, code, out = own_red("TC-2", "python -m unittest tests/test_refund.py")
    assert code == 1 and "tests/test_refunds.py" in out and st(root) == "claimed", out
    print("ok")


def test_ac22_red_one_of_two():
    root, code, out = own_red("TC-1 and TC-2", "python -m unittest tests/test_refund.py")
    assert code == 0 and st(root) == "red", out
    print("ok")


def test_ac23_red_own_wins():
    line = "TC-2, plus a direct check; TC-2 proved later by T-2"
    assert tasks.own(line) == ["TC-2"]
    root, code, out = own_red(line, "python -m unittest tests/test_c.py", "tests/test_c.py")
    assert code == 1 and "tests/test_refunds.py" in out, out
    print("ok")


def test_ac5_red_deferred_file_only_misuse():
    root, code, out = own_red("TC-1; TC-2 proved later by T-2", "python -m unittest tests/test_z.py", "tests/test_z.py")
    assert code == 1 and "tests/test_refund.py" in out, out
    print("ok")


def test_closing_review_records_its_suite():
    """TC-20: only the review of the task that closes its epic carries the suite command and exit code it ran."""
    root = impl(tasks=TWO)
    for tid in ("T-1", "T-2"):
        assert flow(root, "claim", S)[0] == 0
        write_test(root)
        code_with(root)
        code, out = flow(root, "green", S, tid, "--run", RUN)
        assert code == 0 and "review: passed" in out, out
    reviews = [x for x in lines(root) if x["kind"] == "review"]
    assert len(reviews) == 2 and "suite" not in reviews[0]["evidence"], reviews
    assert reviews[1]["evidence"].get("suite") == {"command": SUITE, "code": 0}, reviews[1]
    print("ok")

def script(root, body, code):
    """A self-check-style test file at TEST: prints `body`, exits `code`."""
    (root / TEST).write_text(f"import sys\nprint({body!r})\nsys.exit({code})\n")


def scripted(root):
    """A test file that fails like a new test until app.py defines refund, then passes."""
    (root / TEST).write_text(
        "import sys\nif 'def refund' in open('app.py').read():\n    print('ok " + TEST + "::test_new\\nran 1 tests, 0 failed')\n"
        "    sys.exit(0)\nprint('FAIL " + TEST + "::test_new\\nran 1 tests, 1 failed')\nsys.exit(1)\n")


SCOPED = f"python {TEST} test_new"


def test_ac4_red_takes_a_scoped_command():
    root = claimed()
    script(root, f"FAIL {TEST}::test_new\nran 1 tests, 1 failed", 1)
    code, out = flow(root, "red", S, "T-1", "--run", SCOPED)
    assert code == 0 and "red: T-1 accepted" in out, out
    ev = lines(root)[-1]["evidence"]
    assert lines(root)[-1]["kind"] == "red" and ev["command"] == SCOPED and ev["runner"] == "self-check", lines(root)[-1]
    print("ok")


def test_ac5_red_refuses_zero_tests():
    for exit_code in (1, 0):
        root = claimed()
        script(root, "no test named test_typo\nran 0 tests, 0 failed", exit_code)
        code, out = flow(root, "red", S, "T-1", "--run", f"python {TEST} test_typo")
        assert code == 1 and "refused: no tests ran" in out, (exit_code, out)
        assert of(root, "refused")[-1]["evidence"]["cause"] == "no tests ran" and not of(root, "red"), lines(root)[-1]
    print("ok")


def test_ac6_green_runs_only_the_scoped_command():
    marker = tempfile.mktemp(prefix="suite-ran-")
    root = impl(cfg={"tests": {"suite": f"touch {marker}"}})
    code, out = flow(root, "claim", S)
    assert code == 0, out
    scripted(root)
    code, out = flow(root, "red", S, "T-1", "--run", SCOPED)
    assert code == 0, out
    code_with(root)
    Path(marker).unlink(missing_ok=True)
    code, out = flow(root, "green", S, "T-1")
    assert code == 0, out
    assert of(root, "green")[-1]["evidence"]["command"] == SCOPED and "suite" not in of(root, "review")[-1]["evidence"], out
    assert not Path(marker).exists()
    print("ok")


def test_review_fails_a_crashed_self_check_suite():
    suite = "python suite.py"
    root = impl(cfg={"tests": {"suite": suite}}, alone=True)
    (root / "suite.py").write_text("import sys\nif 'def refund' in open('app.py').read():\n"
                                   "    print('ok tests/test_b.py::test_one\\nran 1 tests, 0 failed')\n"
                                   "    print('Traceback (most recent call last):')\n    sys.exit(1)\n")
    commit_all(root, "suite")
    code, out = flow(root, "claim", S)
    assert code == 0, out
    scripted(root)
    code, out = flow(root, "red", S, "T-1", "--run", SCOPED)
    assert code == 0, out
    code_with(root)
    code, out = flow(root, "green", S, "T-1")
    assert code == 1 and "review: failed" in out and "the suite exits 1 and names no failing test" in out, out
    assert of(root, "review")[-1]["evidence"]["passed"] is False
    print("ok")


REPO_SUITE = json.loads((Path(__file__).parent.parent / ".nio/config.json").read_text())["tests"]["suite"]


def suite_dir(files):
    folder = Path(tempfile.mkdtemp())
    (folder / "tests").mkdir()
    for name, body in files.items():
        (folder / "tests" / name).write_text(body)
    return folder


def run_suite(folder):
    t = time.time()
    p = subprocess.run(["sh", "-c", REPO_SUITE], cwd=folder, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr, time.time() - t


def test_parallel_suite_fails_on_any_file():
    files = {"test_a.py": "import os, signal\nos.kill(os.getpid(), signal.SIGKILL)\n",
             "test_b.py": 'assert 1 == 2, "B FAILED"\n',
             "test_c.py": 'raise SystemExit("D FAILED")\n', "test_z.py": 'print("Z RAN")\n'}
    for n in "defghi":
        files[f"test_{n}.py"] = f'import time; time.sleep(1); print("{n.upper()} RAN")\n'
    code, out, _ = run_suite(suite_dir(files))
    assert code != 0, out
    for want in ("B FAILED", "D FAILED", "D RAN", "E RAN", "F RAN", "G RAN", "H RAN", "I RAN", "Z RAN"):
        assert want in out, (want, out)
    print("ok")


def test_parallel_suite_takes_about_its_slowest_file():
    folder = suite_dir({f"test_{i}.py": 'import time; time.sleep(4); print("ok")\n' for i in range(1, 9)})
    t = time.time()
    subprocess.run(["uv", "run", "python", "tests/test_1.py"], cwd=folder, capture_output=True, check=True)
    one = time.time() - t
    code, out, took = run_suite(folder)
    assert code == 0, out
    assert took <= 1.5 * one, (took, one)
    print("ok")


def test_parallel_suite_reads_as_unknown_runner():
    folder = suite_dir({"test_ok.py": 'print("ok")\n', "test_bad.py": 'assert False, "BAD"\n'})
    assert implement.runner(REPO_SUITE) is None
    assert implement.runner('for f in tests/test_*.py; do uv run python "$f" || exit 1; done') is None
    got = implement.suite(folder, {"tests": {"suite": REPO_SUITE}})
    assert got["code"] != 0 and got["runner"] is None and got["failing"] is None, got
    assert got["broken"] is False and "BAD" in got["output"], got
    print("ok")


def test_parallel_suite_fails_when_only_the_last_file_fails():
    files = {f"test_{i}.py": 'print("ok")\n' for i in range(1, 8)}
    files["test_z.py"] = 'assert False, "LAST"\n'
    code, out, _ = run_suite(suite_dir(files))
    assert code != 0 and "LAST" in out, (code, out)
    print("ok")


def demo():
    """quickstart.md's demo effort: the refunds tasks with T-1 split and T-2, T-3 direct; its folder."""
    root = impl(modes={"T-2": "direct", "T-3": "direct"})
    (root / "app.py").write_text("")
    commit_all(root, "an empty app.py; QS-1's test phase writes the test")
    git(root, "branch", "-M", "main")  # QS-1 checks main is untouched
    return root


def test_runner_runs_every_test():
    src = Path(__file__).read_text()
    assert "def test_" not in src.rsplit("if __name__ ==", 1)[1], "tests defined after the runner never run"
    print("ok")


# --- T-5: the review strips NIO_PERF (CT-9, FR-11) ---

def perf_suite(root, body):
    (root / "tests/test_base.py").write_text(f"import os\nimport unittest\n\n\nclass B(unittest.TestCase):\n    def test_sum(self):\n        {body}\n")


def test_ac14_review_strips_nio_perf():
    root = impl(alone=True)
    perf_suite(root, "self.assertIsNone(os.environ.get('NIO_PERF'))")
    commit_all(root, "perf-sensitive test")
    os.environ.pop("NIO_PERF", None)
    assert flow(root, "claim", S)[0] == 0
    write_test(root)
    assert flow(root, "red", S, "T-1", "--run", RUN)[0] == 0
    code_with(root)
    os.environ["NIO_PERF"] = "1"
    try:
        code, out = flow(root, "green", S, "T-1")
    finally:
        del os.environ["NIO_PERF"]
    assert code == 0 and lines(root)[-1]["kind"] != "fail", out
    rv = of(root, "review")[-1]["evidence"]
    assert rv["passed"] and not rv["failing"], rv
    assert not state(root)["attempts"].get("T-1"), state(root)["attempts"]
    print("ok")


def test_ac15_review_still_fails():
    root = impl(alone=True)
    perf_suite(root, "self.assertEqual(1, 1)")
    commit_all(root, "sum test")
    os.environ.pop("NIO_PERF", None)
    assert flow(root, "claim", S)[0] == 0
    write_test(root)
    assert flow(root, "red", S, "T-1", "--run", RUN)[0] == 0
    code_with(root)
    perf_suite(root, "assert 1 == 2")
    code, out = flow(root, "green", S, "T-1")
    assert code == 1 and "test_sum" in out, out
    assert state(root)["attempts"] == {"T-1": 1}, state(root)["attempts"]
    print("ok")


def test_ac14_review_strips_nio_perf_misuse():
    root = impl(alone=True)
    perf_suite(root, "self.assertIsNone(os.environ.get('NIO_PERF'))")
    commit_all(root, "perf-sensitive test")
    os.environ.pop("NIO_PERF", None)
    assert flow(root, "claim", S)[0] == 0
    write_test(root)
    assert flow(root, "red", S, "T-1", "--run", RUN)[0] == 0
    code_with(root)
    os.environ["NIO_PERF"] = "1"
    try:
        flow(root, "green", S, "T-1")
    finally:
        del os.environ["NIO_PERF"]
    assert not state(root)["attempts"].get("T-1"), state(root)["attempts"]
    print("ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        tempfile.tempdir = tempfile.mkdtemp(prefix="nio-demo-", dir=Path(tempfile.tempdir).parent)  # outlives this run
        print(demo())
        sys.exit()
    selfcheck.main([f for n, f in list(globals().items()) if n.startswith("test_") and callable(f)])
