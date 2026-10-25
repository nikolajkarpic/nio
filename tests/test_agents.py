"""Self-check for nio agents sync / verify. Run: uv run python tests/test_agents.py"""
import json
import os
import re
import tempfile
import tomllib
from pathlib import Path

from test_records import repo

from nio import agents

CARD = """---
name: {name}
description: "Does one thing."
tier: {tier}
effort: med
tools: [read]
---

## Job
Check it.
## Inputs
A pack.
## Output format
Findings.
## Stop when
Done.
"""


def setup():
    root = repo()
    os.environ["NIO_HOME"] = str(Path(tempfile.mkdtemp()))
    os.environ["CLAUDE_CONFIG_DIR"] = str(Path(tempfile.mkdtemp()))
    os.environ.pop("CLAUDE_CODE_SUBAGENT_MODEL", None)
    cfg = json.loads((root / ".nio/config.json").read_text())
    cfg["agents"] = {"hosts": ["claude", "codex"]}
    (root / ".nio/config.json").write_text(json.dumps(cfg))
    return root


def test_shipped_cards_are_valid():
    for name, (meta, body, path) in agents.load(setup()).items():
        assert not agents.check(name, meta, body), (path, agents.check(name, meta, body))
    print("ok")


def test_sync():
    root = setup()
    team = root / ".nio/agents"
    team.mkdir()
    (team / "triage.md").write_text(CARD.format(name="triage", tier="cheap"))
    (team / "logic.append.md").write_text("Also check the glossary.")
    # a personal layer and a local override: config layers merge key by key
    Path(os.environ["NIO_HOME"], "config.json").write_text(json.dumps({"agents": {"tiers": {"codex": {"cheap": "gpt-mini"}}}}))
    (root / ".nio/config.local.json").write_text(json.dumps({"agents": {"override": {"logic": {"tier": "max"}}}}))
    (team / "triage.md").write_text((team / "triage.md").read_text().replace("Does one thing.", "Does one thing 🚀."))
    out, errors = agents.sync(root)
    assert not errors, errors
    for toml in (root / ".codex/agents").glob("*.toml"):  # the hand-built TOML parses, emoji and all
        assert tomllib.loads(toml.read_text())["description"].startswith("Does one thing") or "logic" in toml.name
    logic = (root / ".claude/agents/nio-logic.md").read_text()
    assert 'model: "opus"' in logic and 'effort: "high"' in logic and 'tools: "Read, Grep, Glob"' in logic, logic
    assert logic.rstrip().endswith("Also check the glossary."), logic
    codex = (root / ".codex/agents/nio-triage.toml").read_text()
    assert 'model = "gpt-mini"' in codex and 'model_reasoning_effort = "medium"' in codex and "shell_tool = false" in codex, codex
    assert any("no model for tier `max`" in line for line in out), out  # codex has no built-in names
    excluded = (root / ".git/info/exclude").read_text()
    assert ".claude/agents/nio-*" in excluded and ".codex/agents/nio-*" in excluded
    # unchanged cards aren't rewritten; a deleted card's files go, files nio didn't write stay
    (root / ".claude/agents/mine.md").write_text("hand-written")
    (team / "triage.md").unlink()
    out, _ = agents.sync(root)
    assert not any(line.startswith("wrote") for line in out), out
    assert not (root / ".claude/agents/nio-triage.md").exists() and (root / ".claude/agents/mine.md").exists()
    assert (root / ".git/info/exclude").read_text() == excluded
    # a bad card stops the sync before anything is written
    (team / "bad.md").write_text(CARD.format(name="bad", tier="huge").replace("## Stop when\nDone.\n", ""))
    _, errors = agents.sync(root)
    assert any("`tier` must be" in e for e in errors) and any("Stop when" in e for e in errors), errors
    (team / "bad.md").write_text("no frontmatter")
    try:
        agents.load(root)
        raise AssertionError("card without frontmatter accepted")
    except ValueError as e:
        assert "bad.md" in str(e), e
    (team / "bad.md").unlink()
    (team / "orphan.append.md").write_text("x")
    try:
        agents.load(root)
        raise AssertionError("append without a card accepted")
    except ValueError:
        pass
    print("ok")


def test_verify():
    root = setup()
    agents.sync(root)
    runs = Path(os.environ["CLAUDE_CONFIG_DIR"], "projects", re.sub(r"[^A-Za-z0-9]", "-", str(root)), "s1/subagents")
    runs.mkdir(parents=True)
    for i, (kind, model) in enumerate([("nio-logic", "claude-sonnet-5-5"), ("nio-logic", "claude-opus-5-5"), ("general-purpose", "x")]):
        (runs / f"agent-{i}.meta.json").write_text(json.dumps({"agentType": kind}))
        shape = {"type": "api-request-shape", "shape": {"model": "claude-opus-5-5"}}  # the parent's, not this run's
        reply = {"type": "assistant", "message": {"model": model}}
        (runs / f"agent-{i}.jsonl").write_text(json.dumps(shape) + "\n" + json.dumps(reply) + '\n{"type": "assist')  # still being written
    out, bad = agents.verify(root)
    assert bad == 1 and len([line for line in out if "nio-logic" in line]) == 2, out
    assert any(line.startswith("MISMATCH") and "claude-opus-5-5" in line for line in out), out
    print("ok")


if __name__ == "__main__":
    test_shipped_cards_are_valid()
    test_sync()
    test_verify()
