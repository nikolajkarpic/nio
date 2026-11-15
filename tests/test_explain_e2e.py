"""End-to-end checks of the `@nio:explain` skill in plan mode: each runs the skill on a real model against the refunds
fixture and reads the explainer.md it writes. They cost a model run each, so they run only when asked:
    NIO_E2E=1 uv run python tests/test_explain_e2e.py
Without NIO_E2E they print `skipped` and pass. Diagram rendering (AC-12, AC-13) needs Node and network."""
import os
import re
import shutil
import subprocess
from pathlib import Path

from test_explain import npx_bin
from test_jury import PSLUG, approve_plan, plan_repo
from test_lenses import e2e

from nio import agents, explain, implement
import selfcheck

SKILL = Path(__file__).resolve().parent.parent / "skills/explain/SKILL.md"
TOOLS = "Read Grep Glob Edit Write Bash"
UJ2 = "**UJ-2 Support looks a refund up** (A-1) [human]\n1. Support opens the refund.\n2. The system shows its status.\n\n"


def folder(root):
    return root / ".nio/specs" / PSLUG


def with_two_journeys(root):
    spec = folder(root) / "spec.md"
    text = spec.read_text()
    assert "### State table" in text
    spec.write_text(re.sub(r"(?m)^(### State table)", lambda m: UJ2 + m[1], text, count=1))


def explain_run(root, ask=f"@nio:explain {PSLUG}", path=None):
    """Run the skill's text as the system prompt on the default strong model; `path` replaces PATH."""
    model = agents.DEFAULT_TIERS["claude"]["strong"]
    env = dict(os.environ, **({"PATH": path} if path else {}))
    r = subprocess.run(["claude", "-p", "--model", model, "--system-prompt", SKILL.read_text(), "--allowedTools", TOOLS],
                       input=ask + " The CLI here is `uv run nio`.", cwd=root, capture_output=True, text=True, timeout=1500, env=env)
    assert r.stdout.strip(), r.stderr
    return r.stdout


def secs(root):
    return explain.sections((folder(root) / "explainer.md").read_text())


def mermaid(root):
    return [s for s in secs(root) if s["fence"] == "mermaid" and not s["drill"]]


def nio_check(root):
    return subprocess.run(["uv", "run", "nio", "check", "explainer", PSLUG], cwd=root, capture_output=True, text=True)


def approved(root):
    root = plan_repo()
    approve_plan(root)
    return root


@e2e
def test_ac1_core_diagrams():
    root = approved(None)
    explain_run(root)
    by = {s["title"].lower(): s for s in secs(root)}
    for t in ("component map", "build order"):
        assert by[t]["fence"] and 1 <= len(by[t]["walk"].split()) <= 120, by.get(t)


@e2e
def test_ac2_flows_and_state():
    root = approved(None)
    with_two_journeys(root)
    approve_plan(root, "R-P2")
    explain_run(root)
    flows = [s for s in secs(root) if s["title"].startswith("Flow: ")]
    states = [s for s in secs(root) if s["title"].startswith("State: ")]
    assert len(flows) == 2 and all(s["block"] for s in flows), flows
    assert "UJ-1" in flows[0]["title"] + flows[1]["title"] and "UJ-2" in flows[0]["title"] + flows[1]["title"]
    assert len(states) == 1 and "order" in states[0]["title"], states


@e2e
def test_ac3_no_state_table():
    root = plan_repo()
    spec = folder(root) / "spec.md"
    spec.write_text(re.sub(r"(?ms)^### State table: order.*?(?=^#{1,3} |\Z)", "", spec.read_text(), count=1))
    approve_plan(root)
    explain_run(root)
    assert not [s for s in secs(root) if s["title"].startswith("State: ")]
    assert nio_check(root).returncode == 0, nio_check(root).stdout


@e2e
def test_ac30_refused_open_gate():
    root = plan_repo()
    out = explain_run(root)
    assert not (folder(root) / "explainer.md").exists() and "plan jury" in out and "topic" in out, out


@e2e
def test_ac32_rerun_keeps_drill():
    root = approved(None)
    explain_run(root)
    ex = folder(root) / "explainer.md"
    ex.write_text(ex.read_text().rstrip() + "\n\n## Drill-down: refund retries\nRetries reuse one key.\n")
    subprocess.run(["uv", "run", "nio", "explain", "finish", str(ex)], cwd=root, check=True)
    c = folder(root) / "contracts.md"
    c.write_text(c.read_text().rstrip() + "\n\n### CT-3 Refund list (FR-1) [agent]\n- Binding: `app.py:list_refunds` (new)\n- Like: none: the first listing\n- Kind: function\n- Shape: `list_refunds() -> list`\n")
    approve_plan(root, "R-P2")
    explain_run(root)
    t = ex.read_text()
    assert "## Drill-down: refund retries (written for an earlier plan)\nRetries reuse one key." in t, t
    for f in ("spec.md", "plan.md", "contracts.md"):
        assert implement.digest(root, folder(root) / f)[:12] in t, f


@e2e
def test_ac12_svgs():
    root = approved(None)
    with_two_journeys(root)
    approve_plan(root, "R-P2")
    explain_run(root)
    n, text = len(mermaid(root)), (folder(root) / "explainer.md").read_text()
    svgs = sorted(p.name for p in folder(root).glob("explainer-*.svg"))
    assert n >= 4 and len(svgs) == n, (n, svgs)
    for name in svgs:
        assert re.search(rf"(?m)^!\[.*\]\({re.escape(name)}\)", text) and re.search(rf"(?mi)^.*images.*{re.escape(name)}", text), name


@e2e
def test_ac13_one_broken():
    root = approved(None)
    with_two_journeys(root)
    approve_plan(root, "R-P2")
    explain_run(root)
    ex = folder(root) / "explainer.md"
    text = re.sub(r"(?s)(## Build order.*?```mermaid\n.*?)(\n```)", r"\1\n    X[unclosed\2", ex.read_text(), count=1, flags=re.I)
    ex.write_text(text)
    subprocess.run(["uv", "run", "nio", "explain", "finish", str(ex)], cwd=root, capture_output=True, text=True)
    for s in secs(root):
        if s["fence"] != "mermaid" or s["drill"]:
            continue
        if s["title"].lower() == "build order":
            assert "\n> Broken diagram:" in "\n" + s["walk"] + "\n" or "> Broken diagram:" in ex.read_text(), s
        else:
            assert re.search(r"!\[", ex.read_text()) and list(folder(root).glob("explainer-*.svg")), s["title"]


@e2e
def test_ac14_text_only():
    root = approved(None)
    keep = os.pathsep.join(d for d in os.environ["PATH"].split(os.pathsep) if not (Path(d) / "npx").exists())
    explain_run(root, path=keep)
    ex = folder(root) / "explainer.md"
    assert not list(folder(root).glob("*.svg")) and "> Images not rendered: Node is not installed." in ex.read_text()
    ex.unlink()
    os.environ["FAKE_NPX"] = "down"
    try:
        ex.unlink(missing_ok=True)
        explain_run(root, path=str(npx_bin()) + os.pathsep + keep)
    finally:
        del os.environ["FAKE_NPX"]
    assert not list(folder(root).glob("*.svg")) and "> Images not rendered: the renderer could not be fetched." in ex.read_text()


@e2e
def test_nfr1_node_cap():
    root = approved(None)
    with_two_journeys(root)
    approve_plan(root, "R-P2")
    explain_run(root)
    for s in secs(root):
        if s["block"]:
            assert len(explain.nodes(s["block"])) <= 20, s["title"]

def topic_repo():
    root = plan_repo()
    shutil.rmtree(root / ".nio/specs")
    return root


def topic_cli(root, text):
    return subprocess.run(["uv", "run", "nio", "explain", "topic", text], cwd=root, capture_output=True, text=True)


def today():
    return __import__("datetime").date.today().isoformat()


@e2e
def test_ac18_topic_path():
    root = topic_repo()
    explain_run(root, "@nio:explain git hooks. Reply `stop` to the first offer.")
    ex = root / f".nio/research/{today()}-git-hooks-explainer.md"
    assert ex.is_file()
    for svg in re.findall(r"[\w./-]+\.svg", ex.read_text()):
        assert (root / ".nio/research" / Path(svg).name).is_file() and "/" not in svg.replace(".nio/research/", "")
    r = topic_cli(root, "../Auth / Tokens!")
    assert r.stdout.strip() == f"new: .nio/research/{today()}-auth-tokens-explainer.md", r.stdout
    r = topic_cli(root, "//")
    assert r.returncode == 1 and 'error: the topic "//" gives an empty file name' in r.stdout + r.stderr


@e2e
def test_ac19_no_research_skill():
    root = topic_repo()
    skills = root / "skills"
    shutil.rmtree(skills, ignore_errors=True)
    (skills / "explain").mkdir(parents=True)
    shutil.copy(SKILL, skills / "explain/SKILL.md")
    explain_run(root, "@nio:explain git hooks. Reply `stop` to the first offer.")
    assert (root / f".nio/research/{today()}-git-hooks-explainer.md").is_file()


@e2e
def test_ac35_clash():
    root = topic_repo()
    first = root / f".nio/research/{today()}-auth-tokens-explainer.md"
    first.parent.mkdir(parents=True, exist_ok=True)
    first.write_text("# Auth tokens\n\n(topic: Auth tokens)\n\n## Overview\nTokens.\n")
    before = first.read_bytes()
    out = explain_run(root, "@nio:explain auth/tokens. Reply `stop` to the first offer.")
    second = first.with_name(first.name.replace("explainer.md", "explainer-2.md"))
    assert second.is_file() and "(topic: auth/tokens)" in second.read_text()
    assert first.read_bytes() == before and second.name in out


def test_ac34_topic_whitespace():
    # J-9 (no model): a padded or multi-line topic still continues its own file
    from test_records import repo
    root = repo()
    r = root / ".nio/research"
    r.mkdir(parents=True, exist_ok=True)
    (r / f"{today()}-auth-tokens-explainer.md").write_text("# Auth tokens\n\n(topic: Auth\n  tokens)\n")
    want = f"continue: .nio/research/{today()}-auth-tokens-explainer.md"
    assert explain.topic(root, "  Auth   tokens\n") == want
    assert explain.topic(root, "Auth\n  tokens") == want


HOOKS = "@nio:explain git hooks."


def hooks_file(root):
    fs = list((root / ".nio/research").glob("*explainer*.md"))
    assert len(fs) == 1, fs
    return fs[0]


def drills(root):
    return re.findall(r"(?m)^## Drill-down: (.+)$", hooks_file(root).read_text())


def offers(out):
    low = out.lower()
    return all(k in low for k in ("component", "flow", "decision"))


@e2e
def test_ac15_three_offers():
    root = topic_repo()
    out = explain_run(root, HOOKS + " Reply `stop` to the first offer.")
    assert offers(out), out


@e2e
def test_ac16_pick_appends():
    root = topic_repo()
    out = explain_run(root, HOOKS + " Reply to the first offer by picking its first item, then reply `stop` to the next offer.")
    assert len(drills(root)) == 1, drills(root)
    assert offers(out), out


@e2e
def test_ac17_stop():
    root = topic_repo()
    out = explain_run(root, HOOKS + " Reply to the first offer by picking its first item, then reply `stop` to the next offer.")
    text = hooks_file(root).read_text()
    assert re.findall(r"(?m)^## (.+)$", text)[-1].startswith("Drill-down: ")
    assert not re.search(r"(?i)\b(want|would you like|pick|zoom into)\b", out.strip().splitlines()[-1]), out


@e2e
def test_ac34_same_topic():
    root = topic_repo()
    explain_run(root, HOOKS + " Reply to the first offer by picking its first item, then reply `stop`.")
    f = hooks_file(root)
    before = f.read_text()
    explain_run(root, HOOKS + " Reply to the first offer by picking its first item, then reply `stop`.")
    assert hooks_file(root) == f
    after = f.read_text()
    secs = lambda t: re.split(r"(?m)^(?=## )", t)[1:]  # the header's record lines may change; the sections may not
    old = secs(before)
    assert [x.rstrip("\n") for x in secs(after)[:len(old)]] == [x.rstrip("\n") for x in old], "earlier sections changed"
    assert len(re.findall(r"(?m)^## Drill-down: ", after)) == len(re.findall(r"(?m)^## Drill-down: ", before)) + 1


@e2e
def test_uj2_no_repeat():
    root = topic_repo()
    explain_run(root, HOOKS + " Reply to the first offer by picking its first item, reply to the second offer by picking its first item again, then reply `stop`.")
    d = drills(root)
    assert len(d) == 2 and d[0] != d[1], d


def with_format(fmt):
    root = approved(None)
    if fmt:
        (root / ".nio").mkdir(exist_ok=True)
        (root / ".nio/config.json").write_text('{"explain": {"format": "%s"}}' % fmt)
    return root


@e2e
def test_ac26_mermaid_default():
    root = with_format(None)
    explain_run(root)
    ds = [s for s in secs(root) if s["block"] or s["fence"]]
    assert ds and all(s["fence"] == "mermaid" for s in ds), ds


@e2e
def test_ac28_fallback():
    root = with_format("no-such-skill")
    out = explain_run(root)
    ds = [s for s in secs(root) if s["block"] or s["fence"]]
    assert ds and all(s["fence"] == "mermaid" for s in ds), ds
    assert "no-such-skill" in out or "no-such-skill" in (folder(root) / "explainer.md").read_text(), out


if __name__ == "__main__":
    selfcheck.main([f for n, f in list(globals().items()) if n.startswith("test_") and callable(f)])
