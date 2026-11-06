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
    parsed = {p.stem: tomllib.loads(p.read_text()) for p in (root / ".codex/agents").glob("*.toml")}  # hand-built TOML parses
    assert parsed["nio-triage"]["description"] == "Does one thing 🚀." and parsed["nio-logic"]["developer_instructions"], parsed
    logic = (root / ".claude/agents/nio-logic.md").read_text()
    assert 'model: "opus"' in logic and 'effort: "medium"' in logic and 'tools: "Read, Grep, Glob"' in logic, logic
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


def card(name):
    meta, body, path = agents.load(setup())[name]
    assert not agents.check(name, meta, body), agents.check(name, meta, body)
    return meta, body


def test_ac12_test_proof_exists_with_an_at_plan_secti():
    meta, body = card("test-proof")
    assert (meta["tier"], meta["effort"], meta["tools"]) == ("max", "med", ["read"]) and "\n## At plan\n" in body
    print("ok")


def test_ac20_architecture_fit_exists_with_an_at_plan():
    meta, body = card("architecture-fit")
    assert (meta["tier"], meta["effort"]) == ("max", "med") and "\n## At plan\n" in body
    print("ok")


def test_ac46_risk_rollback_exists_with_an_at_plan_se():
    meta, body = card("risk-rollback")
    assert (meta["tier"], meta["effort"]) == ("max", "med") and "\n## At plan\n" in body
    print("ok")


def test_ac47_it_has_an_at_plan_section_next_to_at_spe():
    _, body = card("security")
    assert "\n## At spec\n" in body and "\n## At plan\n" in body
    print("ok")


def test_ac40_executability_exists_with_tier_cheap_an():
    meta, body = card("executability")
    assert meta["tier"] == "cheap" and "\n## At tasks\n" in body
    print("ok")


def test_ac44_the_evaluator_card_exists_with_tier_stro():
    meta, _ = card("evaluator")
    assert (meta["tier"], meta["effort"]) == ("strong", "med")
    print("ok")


def test_ac58_the_card_runs_on_the_strong_model_and_a():
    cfg = {"agents": {"tiers": {"codex": {"cheap": "m-cheap", "strong": "m-strong"}}}}
    tier, model, _, warning = agents.resolve(cfg, "logic", {"tier": "max", "effort": "high"}, "codex")
    assert (tier, model) == ("max", "m-strong") and warning == "no model for tier `max`; using `strong` (m-strong)", warning
    root = setup()
    (root / ".nio/config.json").write_text(json.dumps({"agents": {"hosts": ["codex"], "tiers": {"codex": {"cheap": "m-cheap", "strong": "m-strong"}}}}))
    out, errors = agents.sync(root)
    assert not errors and any(l.startswith("WARN  codex: nio-test-proof: no model for tier `max`; using `strong` (m-strong)") for l in out), out
    assert 'model = "m-strong"' in (root / ".codex/agents/nio-test-proof.toml").read_text()
    print("ok")


def test_ac26_it_runs_on_fable_on_a_host_that_maps_no():
    task = {"tier": "frontier", "effort": "med"}
    assert agents.resolve({}, None, task, "claude")[1:] == ("fable", "medium", "")
    cfg = {"agents": {"tiers": {"codex": {"cheap": "c", "strong": "s", "max": "m"}}}}
    _, model, _, warning = agents.resolve(cfg, None, task, "codex")
    assert model == "m" and "`frontier`" in warning and "(m)" in warning, warning
    print("ok")


def test_tier_all_renders_once_per_tier():
    """A `tier: all` card renders as nio-<name>-<tier> for each tier, each on that tier's model; others render once."""
    root = setup()
    team = root / ".nio/agents"
    team.mkdir()
    (team / "helper.md").write_text(CARD.format(name="helper", tier="all"))
    (team / "triage.md").write_text(CARD.format(name="triage", tier="cheap"))
    assert agents.check("bad", {"name": "bad", "description": "x", "tier": "every", "effort": "med"}, "") \
        and not agents.check("helper", *agents.load(root)["helper"][:2])
    out, errors = agents.sync(root)
    assert not errors, errors
    claude = root / ".claude/agents"
    for tier, model in agents.DEFAULT_TIERS["claude"].items():
        assert f'model: "{model}"' in (claude / f"nio-helper-{tier}.md").read_text(), tier
    assert not (claude / "nio-helper.md").exists() and (claude / "nio-triage.md").exists()
    assert not (claude / "nio-triage-cheap.md").exists()
    print("ok")


def test_no_shipped_card_defaults_to_high_effort():
    """#66: high is for a rated task that needs it, never a card's default."""
    high = [p.name for p in (Path(agents.__file__).parent / "agents").glob("*.md") if "\neffort: high\n" in p.read_text()]
    assert not high, high


def test_ac12_evaluator_edits_in_place():
    """AC-12 / TC-12: the evaluator card gets Edit, never Write, and is told to edit tasks.md lines in place."""
    meta, body = card("evaluator")
    rendered = agents.render_claude("evaluator", meta, body, "sonnet", "medium")
    assert 'tools: "Read, Grep, Glob, Edit"' in rendered and "Write" not in rendered.split("---")[1], rendered
    assert "in place" in body and "never write `tasks.md` whole" in body, body
    print("ok")


if __name__ == "__main__":
    test_shipped_cards_are_valid()
    test_no_shipped_card_defaults_to_high_effort()
    test_sync()
    test_verify()
    test_ac12_test_proof_exists_with_an_at_plan_secti()
    test_ac20_architecture_fit_exists_with_an_at_plan()
    test_ac46_risk_rollback_exists_with_an_at_plan_se()
    test_ac47_it_has_an_at_plan_section_next_to_at_spe()
    test_ac40_executability_exists_with_tier_cheap_an()
    test_ac44_the_evaluator_card_exists_with_tier_stro()
    test_ac58_the_card_runs_on_the_strong_model_and_a()
    test_ac26_it_runs_on_fable_on_a_host_that_maps_no()
    test_tier_all_renders_once_per_tier()
    test_ac12_evaluator_edits_in_place()
