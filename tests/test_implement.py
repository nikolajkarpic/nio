"""Self-check for the implement stage (2026-10-29-implement-stage; per epic since 2026-11-15-faster-flow).
Run: uv run python tests/test_implement.py"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import selfcheck
import test_flow
from test_tasks import git, repo

from nio import agents, implement, pack, records, tasks
from nio import flow as nio_flow

S, BY = test_flow.S, test_flow.BY
REFUNDS = (Path(__file__).parent / "fixtures/tasks/tasks.md").read_text()
SUITE = "python -m unittest discover -s tests"




# --- tier and effort per epic, no mode (2026-11-15-faster-flow CT-6) ---

def approve_on(root, date):
    git(root, "add", "-A")
    env = {**os.environ, "GIT_COMMITTER_DATE": f"{date}T12:00:00Z", "GIT_AUTHOR_DATE": f"{date}T12:00:00Z"}
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "nio: approve tasks"],
                   cwd=root, check=True, capture_output=True, env=env)


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


def test_wrong_reason_unknown_runner_crash():
    for tail in ("SyntaxError: invalid syntax", "IndentationError: bad", "ImportError: x", "ModuleNotFoundError: No module named 'y'"):
        got = implement.wrong_reason(None, 1, "Traceback (most recent call last):\n  File \"t.py\"\n" + tail + "\n")
        assert got.startswith("collection, import or syntax error"), (tail, got)
    assert implement.wrong_reason(None, 1, "ran 3 tests\nImportError: x\n") == ""
    assert implement.wrong_reason(None, 1, "AssertionError: 1 != 2\n") == ""
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


# --- tasks_of, status, epics (CT-4) ---

LIST = """---
slug: s
retired: []
---
# Tasks: s

## E-1 First (Foundation)
- Tier: strong: x
- Effort: med

### T-1 One
- Files: `a.py`, `b.py` (unchanged)
- Serves: AC-1
- Test: TC-1
- Depends on: none
- Parallel: no

### T-2 Two
- Files: `a.py`
- Serves: AC-2
- Test: TC-2
- Depends on: T-1
- Parallel: no

## E-2 Second (US-1)

### T-3 Three
- Files: `c.py`
- Serves: AC-3
- Test: TC-3
- Depends on: T-2
- Parallel: no
- Tier: max: an old list rated per task
- Effort: high
- Mode: single: x
"""


def lst(text=LIST, config=None):
    root = Path(tempfile.mkdtemp())
    d = root / ".nio/specs/s"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text(text)
    (root / ".nio/config.json").write_text(json.dumps(config or {}))
    return root


def L(kind, task=None, **ev):
    return {"kind": kind, "from": "implementing", "to": "implementing", "evidence": {**({"task": task} if task else {}), **ev}}


def test_retired_dependency_is_met():
    """A task whose dependency was retired after approval is ready, not waiting forever (C-261115-ftot)."""
    text = LIST[:LIST.index("### T-1")] + LIST[LIST.index("### T-2"):]
    t2 = next(t for t in implement.tasks_of(lst(text), "s") if t["id"] == "T-2")
    assert t2["deps"] == [], t2
    print("ok")


def test_tasks_of_reads_fields_and_the_epic_rating():
    ts = implement.tasks_of(lst(), "s")
    assert [t["id"] for t in ts] == ["T-1", "T-2", "T-3"], ts
    t = ts[0]
    assert (t["title"], t["epic"], t["fix"], t["deps"], t["files"], t["serves"], t["tests"], t["tier"], t["effort"]) == \
        ("One", "E-1", False, [], ["a.py", "b.py"], ["AC-1"], ["TC-1"], "strong", "med"), t
    assert (ts[2]["tier"], ts[2]["effort"]) == ("max", "high") and "mode" not in t  # an old epic: its tasks' highest
    print("ok")


def test_status_and_epic_states_from_history():
    root = lst()
    assert implement.status(root, "s", []) == {"T-1": "ready", "T-2": "pending", "T-3": "pending"}
    assert implement.epics(root, "s", []) == {"E-1": ("waiting", 0), "E-2": ("waiting", 0)}
    lines = [L("claim", epic="E-1", tasks=["T-1", "T-2"])]
    assert implement.epics(root, "s", lines)["E-1"] == ("claimed", 0)
    lines += [L("epic_test", epic="E-1", passed=False)]
    assert implement.epics(root, "s", lines)["E-1"] == ("failed", 1)
    lines += [L("claim", epic="E-1"), L("epic_test", epic="E-1", passed=True), L("task_done", "T-1"), L("task_done", "T-2")]
    assert implement.epics(root, "s", lines)["E-1"] == ("closed", 1)
    assert implement.status(root, "s", lines) == {"T-1": "done", "T-2": "done", "T-3": "ready"}
    blocked = [L("epic_test", epic="E-2", passed=False)] * 3 + [L("blocked", epic="E-2", cause="runs")]
    assert implement.epics(root, "s", blocked)["E-2"] == ("blocked", 3)
    assert implement.epics(root, "s", blocked + [L("unblock", epic="E-2")])["E-2"] == ("waiting", 0)
    old = [L("task_done", "T-1"), L("task_done", "T-2")]  # FR-44: done under the per-task flow, no run of its own
    assert implement.epics(root, "s", old)["E-1"] == ("testing", 0)
    assert implement.status(root, "s", [L("blocked", "T-1", cause="spec")])["T-1"] == "blocked"
    assert implement.status(root, "s", [L("blocked", "T-1"), L("unblock", "T-1")])["T-1"] == "ready"
    print("ok")


# --- fixtures for the claim and later ---

REFUNDS = (Path(__file__).parent / "fixtures/tasks/tasks.md").read_text()
TWO = REFUNDS.replace("### T-3", "## E-2 Refunds hold under load (US-2)\n- Tier: strong: load\n- Effort: low\n\n### T-3")
IND = TWO.replace("- Depends on: T-2", "- Depends on: none")  # E-2 independent of E-1
RUN = "python -m unittest tests/test_refund.py"
TEST = "tests/test_refund.py"
METHODS = ("test_refund", "test_second_refund", "test_refund_p95", "test_concurrent_refunds")  # TC-1 to TC-4


def commit_all(root, message, date=None):
    git(root, "add", "-A")
    env = {**os.environ, **({"GIT_COMMITTER_DATE": f"{date}T12:00:00Z", "GIT_AUTHOR_DATE": f"{date}T12:00:00Z"} if date else {})}
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message], cwd=root, check=True,
                   capture_output=True, env=env)


def impl(cfg=None, tasks=None, commit=True, date=None, route="full", tests_md=lambda t: t):
    """A repo at implementing: the refunds effort, its TCs naming `tests/test_refund.py:T.<method>` before the plan is
    approved, `tasks` (else the refunds list, one epic) approved with its commit (`commit=False`: committed as `wip`;
    `date`: the commit's date; `route`: the spec's route), `tests.suite` set (merged with `cfg`; a None value removes the
    key), one passing test so the baseline runs clean, `__pycache__/` ignored as a project would, and a `start` line."""
    tasks = tasks or REFUNDS
    root = test_flow.effort("plan_jury", route=route)
    folder = root / ".nio/specs" / S
    if route == "lite":  # a lite effort has no spec jury: drop the ledger the full fixture's approval wrote
        for name in ("spec.json", "spec.md"):
            (folder / "jury" / name).unlink()
    tp = folder / "tests.md"
    tp.write_text(tests_md(tp.read_text().replace("tests/test_refunds.py:test_full_refund", "tests/test_refund.py:T.test_refund")
                  .replace("tests/test_refunds.py:test_", "tests/test_refund.py:T.test_")))
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


def write_test(root, name=TEST, fail=(), before=""):
    """The epic's tests: `test_refund` fails until app.py defines `refund`; the others pass, but those in `fail` assert
    1 == 2; `before` is code each test runs first."""
    body = "".join(f"    def {m}(self):\n        {before or 'pass'}\n        " +
                   ("self.assertEqual(getattr(app, 'refund', lambda x: 0)(40), 40)" if m == "test_refund" else
                    "self.assertEqual(1, 2)" if m in fail else "self.assertTrue(True)") + "\n\n" for m in METHODS)
    (root / name).write_text(f"import sys\nimport time\nimport unittest\n\nimport app\n\n\nclass T(unittest.TestCase):\n{body}")


def code_with(root, body="def refund(x):\n    return x\n"):
    (root / "app.py").write_text(body)
    shutil.rmtree(root / "__pycache__", ignore_errors=True)  # a same-size edit in the same second would reuse the stale .pyc


def flow(root, *args):
    """`nio flow <args>`, with `--by` added to the implement commands too."""
    extra = ["--by", BY] if args[0] in ("claim", "finish", "block", "unblock") and "--by" not in args else []
    return test_flow.cli(root, *args, *extra)


def close_epic(root, eid, by=BY):
    """Claim the next epic (it must be `eid`), write its tests and code, and finish it; finish's output."""
    code, out = flow(root, "claim", S, "--by", by)
    assert code == 0 and f"epic: {eid} " in out, out
    write_test(root)
    code_with(root)
    code, out = flow(root, "finish", S, eid, "--by", by)
    assert code == 0 and f"closed: {eid} " in out, out
    return out


def lines(root):
    return nio_flow.load(root, S)[1]


def state(root):
    return nio_flow.load(root, S)[0]


def epics(root):
    return implement.epics(root, S, lines(root))


def parts(text):
    """{## heading: body} of a pack."""
    out, name = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            name = line[3:]
            out[name] = []
        elif name:
            out[name].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def claimed(**kw):
    root = impl(**kw)
    code, out = flow(root, "claim", S)
    assert code == 0, out
    return root


def st(root, tid="T-1"):
    return implement.status(root, S, lines(root))[tid]


def of(root, kind, key="E-1"):
    return [x for x in lines(root) if x["kind"] == kind and key in (x["evidence"].get("task"), x["evidence"].get("epic"))]


def kinds(entries):
    return [x["kind"] for x in entries]


def pack_of(root, out):
    return (root / next(x[len("pack: "):] for x in out.splitlines() if x.startswith("pack: "))).read_text()


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
            assert "nio flow red" not in body and "nio flow green" not in body and "`nio flow finish`" in body, body
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
    assert ev["command"] == SUITE and new[1]["evidence"]["epic"] == "E-1", new
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
    assert got.index("baseline") < got.index("claim") and lines(root)[-1]["evidence"]["epic"] == "E-1", got
    assert state(root)["waiting"] is None, state(root)
    print("ok")


def test_ac35_unknown_runner_baseline_must_pass():
    root = impl(cfg={"tests": {"suite": "sh -c 'exit 1'"}})
    code, out = flow(root, "claim", S)
    assert code == 1 and "unknown" in flow(root, "next", S)[1], out
    assert "baseline" not in kinds(lines(root))
    print("ok")


# --- the claim's guards (CT-1) ---

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



def test_ac46_wrong_branch():
    root = impl()
    git(root, "branch", "-M", "main")
    assert flow(root, "claim", S)[0] == 0
    git(root, "checkout", "-q", "main")
    n = len(lines(root))
    code, out = flow(root, "claim", S, "E-1")
    assert code == 1 and f"nio/{S}" in out, out
    assert "claim" not in kinds(lines(root)[n:])
    print("ok")


def nio(root, *args):
    code, out, err = test_flow.run_main(root, *args)
    return code, out + err


def test_legacy_list_rated_per_task():
    """An old list rated per task, approved before TIER_SINCE, passes the check; its epic takes the highest tier."""
    base = REFUNDS.replace("- Tier: max: money moves, concurrent refunds must pay once\n- Effort: med\n", "")
    rates = {"T-1": "cheap: x\n- Effort: low", "T-2": "cheap: x\n- Effort: low", "T-3": "max: x\n- Effort: med"}
    per_task = re.sub(r"(### (T-\d) .*?- Parallel: no\n)", lambda m: m[1] + f"- Tier: {rates[m[2]]}\n- Mode: split: x\n", base, flags=re.S)
    old = impl(tasks=per_task, date="2026-11-14")
    code, out = nio(old, "check", "tasks", S)
    assert code == 0, out
    code, out = flow(old, "claim", S)
    assert code == 0 and "card: nio-worker-max" in out.splitlines() and "effort: med" in out.splitlines(), out
    new = impl(tasks=per_task, date="2026-11-16")
    code, out = nio(new, "check", "tasks", S)
    assert code == 1 and "E-1: needs `- Tier:`" in out, out
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
    root = claimed()
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
    assert "patch" not in ev and "def refund" in (root / "app.py").read_text(), ev  # the work stays for the epic's next agent
    assert st(root) == "blocked" and list(state(root)["claims"]["epics"]) == ["E-1"], state(root)  # CT-4: the claim is kept
    assert state(root)["waiting"] == {"why": "spec problem in T-1", "task": "T-1", "change": meta["id"]}, state(root)
    for bad in (HANDOFF.replace("blocked", "done"), HANDOFF.replace('  smallest_change: "add paid to Order"\n', ""), "no front matter\n"):
        n = len(lines(root))
        code, out = flow(root, "block", S, "T-1", "--handoff", handoff(root, bad))
        assert code == 1 and "handoff is not blocked with a change_request" in out and len(lines(root)) == n, out
    assert len(changes(root)) == len(before) + 1
    print("ok")


def test_ac48_block_twice():
    root = claimed()
    code_with(root)
    first = flow(root, "block", S, "T-1", "--handoff", handoff(root))[1].split()[-1]
    n = len(lines(root))
    code, out = flow(root, "block", S, "T-1", "--handoff", handoff(root))
    assert code == 0 and out.split()[-1] == first and len(lines(root)) == n, out
    assert len([p for p in changes(root) if first in p.name]) == 1 and len(of(root, "blocked", "T-1")) == 1
    code, out = flow(root, "next", S)
    assert "waiting_for_human" in out and "T-1" in out and first in out, out
    assert f"nio flow unblock {S} T-1" in out, out
    # a record exists but the blocked line is missing: reuse the record and write the rest
    root = claimed()
    code_with(root)
    rec = records.new(root, "change", "project", "Spec problem in T-1: refund any order")
    rec.write_text(rec.read_text().replace('against: ""', f'against: ".nio/specs/{S}/spec.md"') + "\nHandoff: "
                   + nio_flow.sha((Path(handoff(root))).read_bytes()) + "\n")
    cid = records.parse(rec)[0]["id"]
    code, out = flow(root, "block", S, "T-1", "--handoff", str(root / "handoff.md"))
    assert code == 0 and out.split()[-1] == cid and len(changes(root)) == 1, out
    assert st(root) == "blocked" and state(root)["waiting"]["change"] == cid and len(of(root, "blocked", "T-1")) == 1
    print("ok")


def blocked_record(root):
    """Run `nio flow block` on T-1 of the claimed E-1; returns the filed record."""
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
        assert changes(root) == before and len(lines(root)) == n and st(root) == "ready", out
    print("ok")


def test_ac21_block_empty_text():
    root = claimed()
    before = changes(root)
    code, out = flow(root, "block", S, "T-1", "--handoff", handoff(root, HANDOFF.replace("orders have no paid flag", "   ")))
    assert code == 1 and "not blocked with a change_request" in out and changes(root) == before and st(root) == "ready", out
    print("ok")


# --- no model calls (NFR-1 of the implement stage) ---

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
                        "write:app.py:def refund(x):\n    return x\n", f"finish|{S}|E-1|--by|{BY}"],
                       cwd=root, capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert st(root) == "done", st(root)
    got = json.loads(report.read_text())
    assert got["tried"] == [], got["tried"]
    loaded = [m for m in got["modules"] if m.split(".")[0] in ("anthropic", "openai")]  # API model clients (C-261029-e54w)
    assert not loaded, loaded
    print("ok")


# --- per-epic implementation (2026-11-15-faster-flow CT-1 to CT-5) ---

def test_claim_hands_the_whole_epic():
    """TC-1: one claim takes the whole epic and one pack holds its tasks, their ACs, contracts and tests."""
    root = impl(tasks=IND)
    code, out = flow(root, "claim", S)
    got = out.splitlines()
    assert code == 0 and "epic: E-1 Customer refunds a paid order (US-1)" in got and "tasks: T-1, T-2" in got, out
    assert not [x for x in got if x.startswith("task:") or x.startswith("mode:")], out
    assert "card: nio-worker-max" in got and "effort: med" in got and f"then: nio flow finish {S} E-1 --by \"{BY}\"" in got, out
    text = pack_of(root, out)
    p = parts(text)
    assert list(p)[1:] == ["Tasks", "Acceptance criteria", "Contracts", "Tests"] and list(p)[0] == "Memory for E-1", list(p)
    assert "#### T-1 Refund" in p["Tasks"] and "#### T-2 Reject" in p["Tasks"] and "T-3" not in p["Tasks"], p["Tasks"]
    assert "**AC-1**" in p["Acceptance criteria"] and "**AC-2**" in p["Acceptance criteria"]
    assert "#### CT-1 " in p["Contracts"] and "#### TC-1 " in p["Tests"] and "#### TC-2 " in p["Tests"] and "TC-3" not in p["Tests"], p
    last = lines(root)[-1]
    assert last["kind"] == "claim" and last["evidence"]["epic"] == "E-1" and last["evidence"]["tasks"] == ["T-1", "T-2"], last
    assert list(state(root)["claims"]["epics"]) == ["E-1"], state(root)
    print("ok")


def test_finish_runs_the_tests_and_closes():
    """TC-2: the flow runs the epic's tests itself; a pass writes `epic_test`, then `task_done` per task, in one commit."""
    root = claimed(tasks=TWO)
    write_test(root)
    code_with(root)
    code, out = flow(root, "finish", S, "E-1")
    assert code == 0 and out.startswith("closed: E-1 "), out
    ks = kinds(lines(root))
    test = of(root, "epic_test")[-1]["evidence"]
    assert test["passed"] and test["command"].startswith("python -m unittest tests.test_refund.T.test_refund"), test
    assert ks.index("epic_test") < ks.index("task_done") and [x["evidence"]["task"] for x in lines(root) if x["kind"] == "task_done"] == ["T-1", "T-2"]
    assert git(root, "log", "-1", "--format=%s").strip() == "E-1: Customer refunds a paid order (US-1)"
    assert epics(root)["E-1"] == ("closed", 0) and state(root)["claims"] == {}, state(root)
    crash = claimed(tasks=TWO)  # a run that crashes before its line closes nothing
    write_test(crash)
    code_with(crash)
    real, implement.run = implement.run, lambda *a: (_ for _ in ()).throw(OSError("crash"))
    try:
        flow(crash, "finish", S, "E-1")
    except OSError:
        pass
    finally:
        implement.run = real
    assert not of(crash, "task_done", "T-1") and not of(crash, "epic_test"), lines(crash)
    edited = claimed(tasks=TWO)
    write_test(edited)
    code_with(edited)
    sp = edited / ".nio/specs" / S / "spec.md"
    sp.write_text(sp.read_text() + "\nThe agent's edit.\n")
    code, out = flow(edited, "finish", S, "E-1")
    assert code != 0 and "spec.md" in out and not of(edited, "task_done", "T-1") and not of(edited, "epic_test"), out
    print("ok")


def test_finish_failing_test_keeps_the_epic_open():
    """TC-3: a failing named test keeps the epic open; the line names it and keeps the last 50 lines of output."""
    root = claimed(tasks=TWO)
    write_test(root, fail=("test_second_refund",), before="print('\\n'.join(f'line {i}' for i in range(80)), file=sys.stderr)")
    code_with(root)
    code, out = flow(root, "finish", S, "E-1")
    assert code != 0 and "E-1 failed (run 1 of 3)" in out, out
    assert epics(root)["E-1"] == ("failed", 1), epics(root)
    ev = of(root, "epic_test")[-1]["evidence"]
    assert not ev["passed"] and any("test_second_refund" in f for f in ev["failing"]), ev
    assert len(ev["tail"]) == 50 and ev["tail"][-1] == "FAILED (failures=1)", ev["tail"]
    assert not of(root, "task_done", "T-1") and state(root)["attempts"] == {"E-1": 1} and state(root)["claims"] == {}
    print("ok")


def test_finish_ignores_the_agents_claim():
    """TC-4: the agent says its tests pass; the flow's run fails; the epic stays open and its word is nowhere."""
    root = claimed(tasks=TWO)
    write_test(root)  # no code: test_refund fails
    (root / "handoff.md").write_text("---\nstatus: done\n---\ntests pass, all green\n")
    code, out = flow(root, "finish", S, "E-1")
    assert code != 0 and epics(root)["E-1"][0] == "failed", out
    assert "tests pass, all green" not in (root / f".nio/specs/{S}/history.jsonl").read_text()
    print("ok")


def test_second_claim_of_an_epic_is_refused():
    """TC-9: a claimed epic can't be claimed again, and the refusal changes nothing."""
    root = claimed(tasks=IND)
    folder = root / ".nio/specs" / S
    before = [(folder / n).read_bytes() for n in ("state.json", "history.jsonl")]
    code, out = flow(root, "claim", S, "E-1", "--by", "driver-b / test / test")
    assert code != 0 and "E-1 is claimed" in out, out
    assert [(folder / n).read_bytes() for n in ("state.json", "history.jsonl")] == before
    print("ok")


def test_finish_refuses_an_epic_with_no_test():
    """TC-10: an epic whose tasks name no test can't close."""
    root = claimed(tasks=re.sub(r"^- Test: .*$", "- Test: none", TWO, flags=re.M), route="lite")
    code, out = flow(root, "finish", S, "E-1")
    assert code != 0 and "E-1 has no test to run" in out, out
    assert not of(root, "epic_test") and epics(root)["E-1"][0] == "claimed"
    print("ok")


def test_epic_commit_leaves_untracked_files_out():
    """TC-11: the epic's commit holds its files, its TCs' test file and the flow files; a stray file stays out."""
    root = claimed(tasks=TWO)
    write_test(root)
    code_with(root)
    (root / "notes").mkdir()
    (root / "notes/scratch.txt").write_text("mine\n")
    (root / "tests/test_base.py").write_text("# the human's tracked edit\n")  # F-4: a tracked file no task lists
    code, out = flow(root, "finish", S, "E-1")
    assert code == 0, out
    assert "?? notes/" in git(root, "status", "--porcelain"), git(root, "status", "--porcelain")
    assert " M tests/test_base.py" in git(root, "status", "--porcelain"), git(root, "status", "--porcelain")
    got = set(git(root, "show", "--name-only", "--format=", "HEAD").split())
    assert got == {"app.py", TEST, f".nio/specs/{S}/history.jsonl", f".nio/specs/{S}/state.json"}, got
    print("ok")


def test_failed_epic_reclaim_and_block():
    """TC-41: a re-claim carries the failure; the third failed run blocks the epic for the human."""
    root = claimed(tasks=TWO)
    write_test(root, fail=("test_second_refund",))
    code_with(root)
    for n in (1, 2, 3):
        code, out = flow(root, "finish", S, "E-1")
        assert code != 0 and f"run {n} of 3" in out, out
        if n < 3:
            code, out = flow(root, "claim", S)
            assert code == 0 and "epic: E-1 " in out, out
            text = parts(pack_of(root, out))["Last failed run"]
            assert "test_second_refund" in text and "FAILED (failures=1)" in text, text
    assert epics(root)["E-1"] == ("blocked", 3) and state(root)["waiting"]["why"] == "E-1 blocked after 3 failed test runs"
    code, out = flow(root, "claim", S)
    assert code != 0 and "E-1 is blocked" in out, out
    print("ok")


def test_in_flight_effort_converts_per_epic():
    """TC-43: an effort at implementing under the per-task flow: E-1 done (its tests run once more), E-2 claimed whole
    with its undone tasks only."""
    three = TWO.replace("### T-3 Refunds stay fast and pay once under load", "### T-3 Refunds stay fast")
    extra = three[three.index("### T-3"):].replace("- Depends on: T-2", "- Depends on: none")
    three += "\n" + extra.replace("### T-3 Refunds stay fast", "### T-4 Refunds pay once").replace("- Depends on: none", "- Depends on: T-3") \
        + "\n" + extra.replace("### T-3 Refunds stay fast", "### T-5 Refunds log").replace("- Depends on: none", "- Depends on: T-4")
    root = impl(tasks=three)
    write_test(root)
    code_with(root)
    commit_all(root, "T-1: Refund a paid order in full")
    test_flow.history(root, S, {"kind": "baseline", "from": "implementing", "to": "implementing", "evidence": {}},
                      *[L("task_done", t, commit="c") for t in ("T-1", "T-2", "T-3")])
    git(root, "checkout", "-q", "-b", f"nio/{S}")
    commit_all(root, "T-3: old flow")
    shas = git(root, "log", "--format=%H").split()
    code, out = flow(root, "claim", S)
    assert code == 0 and "epic: E-1 (every task done: run its tests)" in out and "tasks: none" in out, out
    code, out = flow(root, "finish", S, "E-1")
    assert code == 0, out
    code, out = flow(root, "claim", S)
    assert code == 0 and "epic: E-2 " in out and "tasks: T-4, T-5" in out.splitlines(), out
    tasks_part = parts(pack_of(root, out))["Tasks"]
    assert "T-4" in tasks_part and "T-5" in tasks_part and "#### T-3" not in tasks_part, tasks_part
    ks = kinds(lines(root))
    assert of(root, "epic_test")[0]["evidence"]["passed"] and ks.index("epic_test") < len(ks) - 1 - ks[::-1].index("claim")
    assert git(root, "log", "--format=%H").split()[-len(shas):] == shas  # the old commits stand
    print("ok")


def test_hung_or_broken_run_counts_as_failed():
    """TC-45: a run past the limit, or a test file that doesn't import, is one failed run with a short tail."""
    root = claimed(tasks=TWO)
    write_test(root, before="print('\\n'.join(map(str, range(80))), file=sys.stderr); time.sleep(10)")
    code_with(root)
    implement.EPIC_LIMIT, limit = 2, implement.EPIC_LIMIT
    try:
        t = time.time()
        code, out = flow(root, "finish", S, "E-1")
        took = time.time() - t
    finally:
        implement.EPIC_LIMIT = limit
    ev = of(root, "epic_test")[-1]["evidence"]
    assert code != 0 and ev["cause"] == "time limit" and took < 5 and len(ev["tail"]) <= 50, (out, took)
    assert epics(root)["E-1"] == ("failed", 1)
    broken = claimed(tasks=TWO)
    (broken / TEST).write_text("def broken(:\n")
    code, out = flow(broken, "finish", S, "E-1")
    ev = of(broken, "epic_test")[-1]["evidence"]
    assert code != 0 and ev["cause"].startswith("collection, import or syntax error"), ev
    assert epics(broken)["E-1"] == ("failed", 1) and len(ev["tail"]) <= 50
    print("ok")


def test_live_old_wave_claim_converts():
    """TC-57: a live wave claim of the old flow is its epic's claim; finish lands the wave's worktree and commits it."""
    root = impl(tasks=TWO)
    git(root, "checkout", "-q", "-b", f"nio/{S}")
    head = git(root, "rev-parse", "HEAD").strip()
    tree = root / ".nio/runs/R-old/worktree"
    git(root, "worktree", "add", "--detach", str(tree), head)
    write_test(tree)
    code_with(tree)
    rel = str(tree.relative_to(root))
    (root / "old.txt").write_text("an old task's commit after the wave's claim\n")
    commit_all(root, "T-0: old flow")  # F-1: HEAD moved since the tree was made; landing must not revert this
    test_flow.history(root, S, {"kind": "baseline", "from": "implementing", "to": "implementing", "evidence": {}},
                      L("claim", "T-1", commit=head), L("claim", "T-2", commit=head, worktree=rel),
                      {**L("red", "T-2"), "state": {"claims": {"task": "T-1", "wave": ["T-1", "T-2"]}}})
    code, out = flow(root, "claim", S)
    assert code == 0 and "E-1 is claimed already" in out and f"worktree: {rel}" in out, out
    code, out = flow(root, "finish", S, "E-1")
    assert code == 0, out
    assert {"app.py", TEST} <= set(git(root, "show", "--name-only", "--format=", "HEAD").split())
    assert rel not in git(root, "worktree", "list") and (root / "old.txt").exists(), git(root, "show", "--stat", "HEAD")
    print("ok")


def test_rollback_old_status_reads_new_history():
    """TC-58: the implement module before this change reads an epic the new flow closed as done."""
    import importlib.util
    src = subprocess.run(["git", "show", "2153568:src/nio/implement.py"], cwd=Path(__file__).parent, capture_output=True, text=True)
    assert src.returncode == 0, f"TC-58 needs the old implement.py at 2153568 (a full clone): {src.stderr}"
    path = Path(tempfile.mkdtemp()) / "old_implement.py"
    path.write_text(src.stdout)
    spec_ = importlib.util.spec_from_file_location("old_implement", path)
    old = importlib.util.module_from_spec(spec_)
    spec_.loader.exec_module(old)
    root = impl(tasks=TWO)
    close_epic(root, "E-1")
    got = old.status(root, S, lines(root))
    assert got["T-1"] == "done" and got["T-2"] == "done", got
    print("ok")


def test_one_run_per_hand_back():
    """TC-48: the epic's tests run once per hand-back, whatever the task count."""
    root = claimed(tasks=TWO)
    write_test(root)
    code_with(root)
    calls, real = [], implement.run
    implement.run = lambda *a: calls.append(a) or real(*a)
    try:
        code, out = flow(root, "finish", S, "E-1")
    finally:
        implement.run = real
    assert code == 0 and len(calls) == 1, (out, calls)
    print("ok")


def test_no_close_without_the_flows_run():
    """TC-50: passing tests the flow never ran close nothing."""
    root = claimed(tasks=TWO)
    write_test(root)
    code_with(root)
    flow(root, "claim", S)
    assert epics(root)["E-1"][0] == "claimed" and not of(root, "task_done", "T-1") and not of(root, "task_done", "T-2")
    code, out = flow(root, "next", S)
    assert "state: implementing" in out and "pr" not in out.split("state:")[1].split()[0], out
    print("ok")


SKILL = Path(__file__).resolve().parent.parent / "skills/implement/SKILL.md"


def test_no_red_green_or_mode():
    """TC-5: no red, green or task mode is left: the check takes tasks with no Mode, the CLI has no red, the skill names none."""
    from test_tasks import repo as tasks_repo, errs
    assert errs(tasks_repo(lambda t: re.sub(r"^- Mode:.*\n", "", t, flags=re.M))) == []
    code, out = nio(impl(), "flow", "red", S, "T-1", "--run", "x", "--by", BY)
    assert code == 2 and "invalid choice" in out, out
    text = SKILL.read_text()
    for word in ("nio flow red", "nio flow green", "split", "single mode"):
        assert word not in text, word
    assert not re.search(r"\bdirect\b", text) and not hasattr(implement, "red") and not hasattr(implement, "green")
    print("ok")


def test_one_claim_one_card_per_attempt():
    """TC-49: one claim names one card, and the skill starts one agent per claimed epic."""
    code, out = flow(impl(), "claim", S)
    assert code == 0 and len([x for x in out.splitlines() if x.startswith("card: ")]) == 1, out
    step2 = SKILL.read_text().split("## Steps")[1].split("2. **")[1].split("3. **")[0]
    assert "one agent per claimed epic" in step2.lower(), step2
    print("ok")


def test_finish_refuses_an_agent_command_and_unclaimed_epic():
    """CT-2's refusals: an unclaimed epic; and the agent can't hand over a command of its own (F-3: `--run "true #
    tests/x.py"` closed an epic with no test run)."""
    root = impl(tasks=TWO)
    code, out = flow(root, "finish", S, "E-1")
    assert code != 0 and "E-1 is not claimed" in out, out
    assert flow(root, "claim", S)[0] == 0
    code, out = flow(root, "finish", S, "E-1", "--run", f"true # {TEST}")
    assert code != 0 and not of(root, "epic_test") and epics(root)["E-1"][0] == "claimed", out
    print("ok")


def test_finish_without_tcs_runs_the_suite():
    """F-3: an epic whose tests can't be built from TCs (a fix epic, a lite spec) runs the configured suite, not a
    command from the agent."""
    root = claimed(tasks=re.sub(r"^- Test: .*$", "- Test: the refund tests pass", TWO, flags=re.M), route="lite")
    write_test(root)
    code_with(root)
    code, out = flow(root, "finish", S, "E-1")
    assert code == 0, out
    assert of(root, "epic_test")[-1]["evidence"]["command"] == SUITE
    print("ok")


def test_unblock_an_epic():
    """CT-4: the human unblocks an epic blocked by its runs: waiting again, failed runs reset."""
    root = claimed(tasks=TWO)
    write_test(root, fail=("test_second_refund",))
    code_with(root)
    for _ in range(3):
        flow(root, "finish", S, "E-1")
        flow(root, "claim", S)
    assert epics(root)["E-1"] == ("blocked", 3)
    code, out = flow(root, "unblock", S, "E-2", "--human", "x")
    assert code != 0 and "E-2 is not blocked" in out, out
    code, out = flow(root, "unblock", S, "E-1", "--human", "fixed the fixture", "--by", "human")
    assert code == 0 and epics(root)["E-1"] == ("waiting", 0) and state(root)["waiting"] is None, out
    assert "E-1" not in state(root)["attempts"]
    print("ok")


# --- the pr gate's findings on per-epic implementation (F-1, F-4 to F-8) ---

PAD = "def refund(x):\n    return x\n" + "".join(f"# line {i}\n" for i in range(20))


def pair():
    """IND with app.py and the test file committed first (the far ends of app.py are two epics' separate hunks); E-1
    claimed in the main tree, E-2 in its worktree. Returns (root, E-2's worktree)."""
    root = impl(tasks=IND)
    write_test(root)
    code_with(root, PAD)
    commit_all(root, "app")
    assert flow(root, "claim", S)[0] == 0
    code, out = flow(root, "claim", S)
    assert code == 0 and "epic: E-2 " in out, out
    return root, root / next(x[10:] for x in out.splitlines() if x.startswith("worktree: "))


def test_reclaimed_worktree_lands_against_its_own_base():
    """F-1: E-2 fails in its worktree, E-1 closes, E-2 is claimed again on the same tree and passes: E-1's change stays."""
    root, w = pair()
    write_test(w, fail=("test_refund_p95",))
    code, out = flow(root, "finish", S, "E-2")
    assert code != 0 and "run 1 of 3" in out, out
    code_with(root, PAD + "# E-1's line\n")
    code, out = flow(root, "finish", S, "E-1")
    assert code == 0, out
    code, out = flow(root, "claim", S)
    assert code == 0 and "epic: E-2 " in out and f"worktree: {w.relative_to(root)}" in out, out
    write_test(w, before="pass  # E-2's test")
    code, out = flow(root, "finish", S, "E-2")
    assert code == 0, out
    assert "# E-1's line" in (root / "app.py").read_text(), git(root, "show", "HEAD")
    print("ok")


def test_worktree_finish_beside_main_tree_work():
    """F-5: E-2's worktree epic finishes while E-1's agent has uncommitted work in the main tree; E-1's work stays out."""
    root, w = pair()
    code_with(root, PAD + "# E-1 at work\n")
    write_test(w, before="pass  # E-2's test")
    code, out = flow(root, "finish", S, "E-2")
    assert code == 0 and "closed: E-2 " in out, out
    assert set(git(root, "show", "--name-only", "--format=", "HEAD").split()) == {TEST, f".nio/specs/{S}/history.jsonl", f".nio/specs/{S}/state.json"}
    assert "# E-1 at work" in (root / "app.py").read_text() and " M app.py" in git(root, "status", "--porcelain")
    print("ok")


def test_failed_main_tree_epic_is_reclaimed_in_the_main_tree():
    """F-6: E-1 fails in the main tree while E-2 holds a worktree; its re-claim gets the main tree back, where its work is."""
    root, w = pair()
    code_with(root, PAD + "# E-1's work\n")
    write_test(root, fail=("test_second_refund",))
    code, out = flow(root, "finish", S, "E-1")
    assert code != 0 and "run 1 of 3" in out, out
    code, out = flow(root, "claim", S)
    assert code == 0 and "epic: E-1 " in out and "worktree:" not in out, out
    assert "# E-1's work" in (root / "app.py").read_text()
    print("ok")


def test_converted_epic_keeps_its_old_trees_after_a_failed_run():
    """F-7: a converted wave epic whose first run fails keeps its old wave tree on the re-claim, and lands it after."""
    root = impl(tasks=TWO)
    git(root, "checkout", "-q", "-b", f"nio/{S}")
    head = git(root, "rev-parse", "HEAD").strip()
    tree = root / ".nio/runs/R-old/worktree"
    git(root, "worktree", "add", "--detach", str(tree), head)
    write_test(tree, fail=("test_second_refund",))
    code_with(tree)
    rel = str(tree.relative_to(root))
    test_flow.history(root, S, {"kind": "baseline", "from": "implementing", "to": "implementing", "evidence": {}},
                      L("claim", "T-1", commit=head), L("claim", "T-2", commit=head, worktree=rel),
                      {**L("red", "T-2"), "state": {"claims": {"task": "T-1", "wave": ["T-1", "T-2"]}}})
    assert flow(root, "claim", S)[0] == 0
    code, out = flow(root, "finish", S, "E-1")
    assert code != 0 and "run 1 of 3" in out, out
    code, out = flow(root, "claim", S)
    assert code == 0 and f"worktree: {rel}" in out, out
    write_test(tree)
    code, out = flow(root, "finish", S, "E-1")
    assert code == 0 and {"app.py", TEST} <= set(git(root, "show", "--name-only", "--format=", "HEAD").split()), out
    assert rel not in git(root, "worktree", "list")
    print("ok")


def test_interrupted_finish_undoes_its_landing():
    """F-8: a finish interrupted during its run leaves the main tree as it was, and the retry closes the epic."""
    root, w = pair()
    write_test(w, before="pass  # E-2's test")
    real, implement.run = implement.run, lambda *a: (_ for _ in ()).throw(KeyboardInterrupt())
    try:
        implement.finish(root, S, "E-2", by=BY)
        raise AssertionError("the run was not interrupted")
    except KeyboardInterrupt:
        pass
    finally:
        implement.run = real
    assert implement.dirty(root, S) == [], git(root, "status", "--porcelain")
    code, out = flow(root, "finish", S, "E-2")
    assert code == 0 and "closed: E-2 " in out, out
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


def test_runner_runs_every_test():
    src = Path(__file__).read_text()
    assert "def test_" not in src.rsplit("if __name__ ==", 1)[1], "tests defined after the runner never run"
    print("ok")


def test_ac14_finish_strips_nio_perf():
    """The epic's run strips NIO_PERF, so a perf-sensitive test doesn't fail the hand-back (CT-9, FR-11)."""
    root = impl()
    os.environ.pop("NIO_PERF", None)
    assert flow(root, "claim", S)[0] == 0
    write_test(root, before="import os; self.assertIsNone(os.environ.get('NIO_PERF'))")
    code_with(root)
    os.environ["NIO_PERF"] = "1"
    try:
        code, out = flow(root, "finish", S, "E-1")
    finally:
        del os.environ["NIO_PERF"]
    assert code == 0, out
    print("ok")


def test_suite_reads_self_check_name_with_spaces():
    cmd = "printf 'FAIL tests/x.py::a name with spaces\\nran 1 tests, 1 failed\\n'; exit 1"
    r = implement.suite(Path(tempfile.gettempdir()), {"tests": {"suite": cmd}})
    assert r["failing"] == ["tests/x.py::a name with spaces"], r["failing"]


if __name__ == "__main__":
    selfcheck.main([f for n, f in list(globals().items()) if n.startswith("test_") and callable(f)])
