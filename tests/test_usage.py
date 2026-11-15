"""Self-check for run recording. Run: uv run python tests/test_usage.py"""
import io
import json
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from test_records import repo

from nio import usage
import selfcheck

SLUG = "2026-10-30-demo"
T0 = datetime(2026, 10, 30, 12, tzinfo=timezone.utc)


def at(minutes):
    return (T0 + timedelta(minutes=minutes)).isoformat()


def transcript(path, rows):
    """rows: (request, minutes, output tokens). Each request is written twice, as Claude Code does."""
    lines = []
    for req, minutes, out in rows:
        line = {"type": "assistant", "requestId": req, "timestamp": at(minutes), "effort": "high",
                "message": {"model": "m1", "usage": {"output_tokens": out, "output_tokens_details": {"thinking_tokens": 1}}}}
        lines += [json.dumps(line)] * 2
    path.write_text("\n".join(lines) + "\n")
    return str(path)


def event(root, payload):
    usage.record("claude", io.StringIO(json.dumps({"cwd": str(root), "session_id": "s", "transcript_path": "/none", **payload})))


def test_event_never_holds_a_prompt_or_a_command():
    root = repo()
    (root / ".nio/specs" / SLUG).mkdir(parents=True)
    event(root, {"hook_event_name": "PreToolUse", "tool_name": "Agent", "tool_use_id": "c",
                 "tool_input": {"description": "T-1 test phase", "subagent_type": "w", "prompt": f"SECRET .nio/specs/{SLUG}/tasks.md"}})
    event(root, {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_use_id": "b",
                 "tool_input": {"command": "curl -H 'token: SECRET' x"}})
    event(root, {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_use_id": "b2",
                 "tool_input": {"command": f"uv run nio flow red {SLUG} T-1 --run 'SECRET'"}})
    event(root, {"hook_event_name": "PreToolUse", "tool_name": "Read", "tool_use_id": "r", "tool_input": {}})
    text = (root / usage.EVENTS).read_text()
    assert "SECRET" not in text, text
    rows = [json.loads(x) for x in text.splitlines()]
    assert [r["kind"] for r in rows] == ["agent_called", "bash_start", "bash_start"], rows
    assert rows[0]["effort"] == SLUG and rows[0]["task"] == "T-1", rows[0]
    assert rows[1]["name"] == "bash" and rows[2]["name"] == "nio flow red" and rows[2]["effort"] == SLUG, rows


def test_a_bad_payload_never_raises():
    usage.record("claude", io.StringIO("not json"))
    usage.record("nope", io.StringIO("{}"))


def test_link_reads_the_run():
    root = repo()
    run = root / ".nio/runs/R-261030-abcd"
    run.mkdir(parents=True)
    (run / "flow.json").write_text(json.dumps({"effort": SLUG, "task": "T-7"}))
    assert usage.link(root, "pack at .nio/runs/R-261030-abcd/packs/T-7.md") == {"effort": SLUG, "task": "T-7"}
    assert usage.link(root, "nothing here 2026-01-01-no-such") == {}


def test_report():
    """Two parallel agents and a shell call in 60 minutes, 20 of them waiting for the human, and another effort's noise."""
    root = repo()
    subprocess.run(["git", "config", "user.name", "t"], cwd=root)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=root)
    folder = root / ".nio/specs" / SLUG
    folder.mkdir(parents=True)
    tmp = Path(tempfile.mkdtemp())
    main = transcript(tmp / "main.jsonl", [("m", 1, 100), ("before", -5, 999)])  # the session started before this effort
    a, b = transcript(tmp / "a.jsonl", [("x", 2, 10)]), transcript(tmp / "b.jsonl", [("y", 3, 20)])
    base = {"session": "s", "transcript": main}
    events = [
        {"at": at(0), "kind": "bash_start", "call": "b0", "name": "nio flow claim", "effort": SLUG, **base},
        {"at": at(1), "kind": "bash_end", "call": "b0", "name": "nio flow claim", **base},
        {"at": at(2), "kind": "agent_called", "call": "c1", "type": "w", "task": "T-1", **base},
        {"at": at(2), "kind": "agent_start", "agent": "a", "type": "w", **base},
        {"at": at(2), "kind": "agent_launched", "call": "c1", "agent": "a", **base},
        {"at": at(2), "kind": "agent_called", "call": "c2", "type": "w", "task": "T-1", **base},
        {"at": at(2), "kind": "agent_start", "agent": "b", "type": "w", **base},
        {"at": at(2), "kind": "agent_launched", "call": "c2", "agent": "b", **base},
        {"at": at(5), "kind": "bash_start", "call": "b1", "name": "bash", "agent": "a", **base},  # inside the agent's span
        {"at": at(6), "kind": "bash_end", "call": "b1", "name": "bash", "agent": "a", **base},
        {"at": at(10), "kind": "agent_stop", "agent": "a", "log": a, **base},
        {"at": at(12), "kind": "agent_stop", "agent": "b", "log": b, **base},
        {"at": at(20), "kind": "turn_end", **base},
        {"at": at(40), "kind": "turn_start", **base},
        {"at": at(60), "kind": "turn_end", **base},
        {"at": at(5), "kind": "agent_called", "call": "z", "session": "other", "effort": "2026-10-30-else", "task": "T-9"},
    ]
    (root / usage.EVENTS).parent.mkdir(parents=True, exist_ok=True)
    (root / usage.EVENTS).write_text("\n".join(map(json.dumps, events)) + "\n{torn")
    (folder / "history.jsonl").write_text("\n".join(json.dumps(x) for x in [
        {"kind": "claim", "evidence": {"task": "T-1"}},
        {"kind": "refused", "evidence": {"task": "T-1"}},
        {"kind": "review", "evidence": {"task": "T-1", "passed": False}},
        {"kind": "review", "evidence": {"task": "T-1", "passed": True}}]) + "\n")
    r = usage.report(root, SLUG)
    assert r["wall_seconds"] == 3600 and r["waiting_for_human_seconds"] == 1200, r
    assert r["agents_seconds"] == 600, r  # 2 to 12: the parallel agents count once
    assert r["shell_seconds"] == 60, r  # the worker's own shell call isn't counted again
    assert r["orchestrator_thinking_seconds"] == 3600 - 1200 - 660, r
    assert r["orchestrator_tokens"]["output_tokens"] == 100, r  # not the 999 from before this effort started
    t = r["tasks"]["T-1"]
    assert (t["agents"], t["seconds"], t["attempts"], t["tokens"]["output_tokens"]) == (2, 1080, 3, 30), t
    assert t["tokens"]["thinking"] == 2, t  # each request counted once
    assert r["by_agent"]["w m1 high"]["agents"] == 2, r
    assert "T-9" not in r["tasks"], r
    assert usage.report(root, "2026-10-30-nothing") is None
    out = usage.finish(root, SLUG)
    assert out == [f"usage: committed .nio/specs/{SLUG}/usage.json"], out
    assert json.loads((folder / "usage.json").read_text())["effort"] == SLUG


def test_install_replaces_and_keeps():
    root = repo()
    path = root / ".claude/settings.local.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "mine"}]}]}, "model": "x"}))
    usage.claude_install(root, False, "/bin/nio")
    usage.claude_install(root, False, "/bin/nio")
    cfg = json.loads(path.read_text())
    assert cfg["model"] == "x", cfg
    assert len(cfg["hooks"]["Stop"]) == 2 and cfg["hooks"]["Stop"][0]["hooks"][0]["command"] == "mine", cfg
    assert len(cfg["hooks"]["PreToolUse"]) == 1 and cfg["hooks"]["PreToolUse"][0]["matcher"] == "Agent|Bash", cfg
    assert "/bin/nio usage event claude" in cfg["hooks"]["Stop"][1]["hooks"][0]["command"], cfg
    usage.claude_install(root, True)
    shared = json.loads((root / ".claude/settings.json").read_text())
    assert shared["hooks"]["Stop"][0]["hooks"][0]["command"].startswith("nio usage event"), shared


def so_far_setup(events, hist, step=None):
    root = repo()
    (root / ".nio/specs" / SLUG).mkdir(parents=True)
    if step:
        run = root / ".nio/runs/R-261110-aaaa/jury/packs"
        run.mkdir(parents=True)
        (run / "step.json").write_text(json.dumps(step))
    (root / usage.EVENTS).parent.mkdir(parents=True, exist_ok=True)
    (root / usage.EVENTS).write_text("\n".join(map(json.dumps, events)) + "\n")
    lines = [{"kind": "pass" if a != b else "claim", "at": at(m), "from": a, "to": b} for m, a, b in hist]
    return root, lines


def agent(tmp, name, start, stop, out, juror=False):
    log = transcript(tmp / f"{name}.jsonl", [(name, start, out)])
    if juror:
        prompt = json.dumps({"type": "user", "message": {"content": "read .nio/runs/R-261110-aaaa/jury/packs/logic.md"}})
        Path(log).write_text(prompt + "\n" + Path(log).read_text())
    base = {"session": "s", "effort": SLUG}
    return [{"at": at(start), "kind": "agent_start", "agent": name, "type": "w", **base},
            {"at": at(stop), "kind": "agent_stop", "agent": name, "log": log, **base}]


def test_so_far():
    tmp = Path(tempfile.mkdtemp())
    main = transcript(tmp / "main.jsonl", [("m1", 5, 100), ("m2", 35, 50)])
    events = [{"at": at(0), "kind": "turn_start", "session": "s", "effort": SLUG, "transcript": main}]
    events += agent(tmp, "j1", 2, 6, 10, juror=True) + agent(tmp, "w1", 12, 20, 20)
    root, lines = so_far_setup(events, [(0, "grilling", "spec_jury"), (10, "spec_jury", "planning"), (30, "planning", "plan_jury")],
                               {"gate": "spec", "round": 0, "lenses": ["logic"]})
    r = usage.so_far(root, SLUG, lines, now=usage.when(at(40)))
    got = [(s["stage"], s["seconds"], s["tokens"], s["juries"]) for s in r["stages"]]
    assert got == [("spec_jury", 600, 110, [{"gate": "spec", "tokens": 10, "seconds": 240}]),
                   ("planning", 1200, 20, []), ("plan_jury", 600, 50, [])], got
    assert r["total"] == {"tokens": 180, "seconds": 2400}, r
    assert not (root / ".nio/specs" / SLUG / "usage.json").exists()


def test_so_far_visits_and_unattributed():
    tmp = Path(tempfile.mkdtemp())
    events = agent(tmp, "e", 1, 3, 7) + agent(tmp, "a", 12, 14, 5) + agent(tmp, "b", 32, 34, 8) + agent(tmp, "j", 22, 24, 4, juror=True)
    root, lines = so_far_setup(events, [(10, "tasks_jury", "implementing"), (20, "implementing", "tasks_jury"), (30, "tasks_jury", "implementing")],
                               {"gate": "tasks", "round": 0, "lenses": ["logic"]})
    r = usage.so_far(root, SLUG, lines, now=usage.when(at(40)))
    st = {s["stage"]: s for s in r["stages"]}
    assert (st["implementing"]["tokens"], st["implementing"]["seconds"]) == (13, 1200), st
    assert st["tasks_jury"]["tokens"] == 4 and st["tasks_jury"]["juries"] == [{"gate": "tasks", "tokens": 4, "seconds": 120}], st
    assert r["unattributed"] == {"tokens": 7, "seconds": 120}, r
    assert r["total"]["tokens"] == 24, r


def test_so_far_nothing_recorded():
    root, lines = so_far_setup([], [(0, "grilling", "spec_jury")])
    r = usage.so_far(root, SLUG, lines, now=usage.when(at(40)))
    dash = {"tokens": "-", "seconds": "-"}
    assert r["stages"] == [] and r["unattributed"] == dash and r["total"] == dash, r


if __name__ == "__main__":
    selfcheck.main([test_event_never_holds_a_prompt_or_a_command, test_a_bad_payload_never_raises, test_link_reads_the_run, test_report, test_install_replaces_and_keeps, test_so_far, test_so_far_visits_and_unattributed, test_so_far_nothing_recorded])
