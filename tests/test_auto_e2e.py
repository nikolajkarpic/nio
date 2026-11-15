"""Auto-run checks. Run: uv run python tests/test_auto_e2e.py
The full-auto runs (2026-11-15-faster-flow TC-18 to TC-20) drive a real model through the flow; they cost several
model runs each and run only with NIO_E2E=1: NIO_E2E=1 uv run python tests/test_auto_e2e.py"""
import json
import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path

from test_lenses import e2e
from test_spec import put, repo

from nio import flow, jury, spec, usage
import selfcheck

NIO = Path(__file__).resolve().parent.parent


def auto_repo(stage):
    """The refunds fixture at `stage`, with `gh` replaced on PATH by a stub that logs its argv and prints a PR URL, a bare
    local repo as `origin`, the usage hook installed, and auto granted by the human. Returns (root, env, gh log)."""
    import test_flow as tf
    root = tf.effort(stage)
    bare = Path(tempfile.mkdtemp()) / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    tf.git(root, "remote", "add", "origin", str(bare))
    bin_ = Path(tempfile.mkdtemp())
    log = bin_ / "gh.log"
    for name, body in (("gh", f'echo "$*" >> {log}\necho https://example.test/pr/1\n'),
                       ("nio", f'exec uv run --project {NIO} nio "$@"\n')):
        (bin_ / name).write_text("#!/bin/sh\n" + body)
        (bin_ / name).chmod((bin_ / name).stat().st_mode | stat.S_IEXEC)
    env = {**os.environ, "PATH": f"{bin_}:{os.environ['PATH']}"}
    env.pop("CLAUDE_CODE_PLUGIN_DIRS", None)
    usage.HOSTS["claude"]["install"](root, False)
    flow.start(root, tf.S, "human", auto=True)
    return root, env, log


def drive(root, env, prompt):
    """One driver session on a real model, the NIO plugin loaded from this repo; its stream-json transcript."""
    r = subprocess.run(["claude", "-p", prompt, "--plugin-dir", str(NIO), "--output-format", "stream-json", "--verbose",
                        "--dangerously-skip-permissions"], cwd=root, env=env, capture_output=True, text=True, timeout=7200)
    return r.stdout


def lines_after_grant(root, slug):
    lines = flow.load(root, slug)[1]
    at = max(i for i, x in enumerate(lines) if x["kind"] == "grant")
    return lines[at + 1:]


@e2e
def test_driver_runs_every_stage():
    """TC-18: under auto the driver runs each stage in a fresh agent, with no human approval between them."""
    import test_flow as tf
    root, env, _ = auto_repo("spec_jury")
    drive(root, env, f"drive {tf.S} under auto from nio flow next (skills/jury/SKILL.md)")
    after = lines_after_grant(root, tf.S)
    passed = [x["from"] for x in after if x["kind"] == "pass"]
    want = ["spec_jury", "planning", "plan_jury", "tasking", "tasks_jury"]
    assert [s for s in passed if s in want] == want, passed
    assert not [x for x in after if x["who"]["role"] == "human"], after
    called = [x for x in usage.report(root, tf.S) if "agent_called" in str(x)]
    assert len(called) >= len(want), called


@e2e
def test_auto_implements_per_epic():
    """TC-19: the run goes on through the implement stage per epic, then one pr gate and no epic jury."""
    import test_flow as tf
    root, env, log = auto_repo("spec_jury")
    drive(root, env, f"drive {tf.S} under auto from nio flow next (skills/jury/SKILL.md) until it stops")
    after = lines_after_grant(root, tf.S)
    epics = {x["evidence"]["epic"] for x in after if x["kind"] == "claim" and x["evidence"].get("epic")}
    passed = {x["evidence"]["epic"] for x in after if x["kind"] == "epic_test" and x["evidence"].get("passed")}
    assert epics and epics == passed, (epics, passed)
    assert any(x["kind"] == "pass" and (x["from"], x["to"]) == ("implementing", "pr") for x in after), after
    folder = root / ".nio/specs" / tf.S / "jury"
    assert (folder / "pr.json").exists() and not list(folder.glob("implementation-E-*")), list(folder.iterdir())
    assert "pr merge" not in log.read_text()


@e2e
def test_one_fix_agent_per_round():
    """TC-20: three confirmed plan findings go to one fix agent in one batch; round 2 follows its edits."""
    import test_flow as tf
    root, env, _ = auto_repo("plan_jury")
    folder = root / ".nio/specs" / tf.S
    for name, old, new in (("tests.md", "- Assert: p95 ≤ 2 s\n", ""), ("contracts.md", "- Binding: `app.py:refund_order` (new)\n", ""),
                           ("plan.md", "| AC-2 |", "| AC-9 |")):
        (folder / name).write_text((folder / name).read_text().replace(old, new, 1))
    drive(root, env, f"drive {tf.S} under auto from nio flow next (skills/jury/SKILL.md) through the plan gate")
    led = jury.load(root, tf.S, "plan")
    confirmed = [f["id"] for f in led["findings"] if f["validation"] == "confirmed" and f["severity"] != "minor" and f["first_round"] == 1]
    assert led["round"] >= 2 and len(confirmed) >= 3, led["findings"]
    assert all(f["by"] == "auto" for f in led["findings"] if f["id"] in confirmed), led["findings"]
    prompts = [str(x) for x in usage.report(root, tf.S) if "fix" in str(x).lower()]
    assert any(all(i in p for i in confirmed) for p in prompts), prompts


def test_grill_under_auto():
    """A [derived: ID] item may cite an [auto] item: [auto] is settled like [human] (J-14)."""
    root = repo()
    slug = put(root, "spec.md", lambda t: t.replace("[default]", "[auto]").replace(
        "- **OP-1** (decision; FR-1) Can support refund an order after 30 days?\n", "").replace("retired: []", "retired: [OP-1]").replace(
        "reject the refund request. [human]", "reject the refund request. [auto]").replace(
        "then it is rejected. [human]", "then it is rejected. [derived: FR-2]"))
    errs, _ = spec.check(root, slug, gate=True)
    assert errs == [], errs


@e2e
def test_installed_mod_backgrounds_evidence():
    """TC-15: after `nio mods install` (the install skill's mods step, #142) a fresh session, started with no
    --plugin-dir and no CLAUDE_CODE_PLUGIN_DIRS, runs `nio jury evidence` in the background, with no sleep loop; the
    control session, mod not installed, runs it in the foreground, so the mod is what backgrounds it."""
    import shutil

    def session(install):
        """The Bash calls running `nio jury evidence`, their results and every tool use, in a fresh clone and config."""
        work = Path(tempfile.mkdtemp())
        try:
            root, cfg = work / "nio", work / "cfg"
            subprocess.run(["git", "clone", "-q", "--local", str(NIO), str(root)], check=True)
            cfg.mkdir()
            creds = Path.home() / ".claude/.credentials.json"  # the model calls need the person's login in the fresh config
            if creds.exists():
                shutil.copy(creds, cfg / ".credentials.json")
            env = {**os.environ, "CLAUDE_CONFIG_DIR": str(cfg)}
            env.pop("CLAUDE_CODE_PLUGIN_DIRS", None)
            if install:
                r = subprocess.run(["uv", "run", "nio", "mods", "install"], cwd=root, env=env, capture_output=True, text=True)
                assert "background-nio-commands: installed" in r.stdout, r.stdout + r.stderr
            r = subprocess.run(["claude", "-p", "run uv run nio jury evidence --help and report its first line", "--output-format",
                                "stream-json", "--verbose", "--dangerously-skip-permissions"], cwd=root, env=env, capture_output=True,
                               text=True, timeout=900)
        finally:
            shutil.rmtree(work, ignore_errors=True)  # the copied login goes with it
        events = [json.loads(x) for x in r.stdout.splitlines() if x.startswith("{")]
        uses = [c for e in events if e.get("type") == "assistant" for c in e["message"].get("content", []) if c.get("type") == "tool_use"]
        results = {c.get("tool_use_id"): str(c.get("content")) for e in events if e.get("type") == "user"
                   for c in e["message"].get("content", []) if isinstance(c, dict) and c.get("type") == "tool_result"}
        runs = [u for u in uses if u["name"] == "Bash" and "nio jury evidence" in u["input"].get("command", "")]
        assert runs, uses
        return runs, results, uses

    backgrounded = lambda u, results: u["input"].get("run_in_background") or "background" in results.get(u["id"], "")
    runs, results, uses = session(install=True)
    assert all(backgrounded(u, results) for u in runs), (runs, results)
    assert not [u for u in uses if "sleep" in json.dumps(u["input"])], uses
    runs, results, _ = session(install=False)  # the control: no mod, no background
    assert not any(backgrounded(u, results) for u in runs), (runs, results)

if __name__ == "__main__":
    selfcheck.main([test_installed_mod_backgrounds_evidence, test_grill_under_auto, test_driver_runs_every_stage, test_auto_implements_per_epic, test_one_fix_agent_per_round])
