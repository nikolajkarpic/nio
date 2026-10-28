"""End-to-end checks of the plan gate's lenses (#57): each runs a lens card on a real model against a fixture plan with
a known flaw, and reads what it finds. They cost a max-model run each, so they run only when asked:
    NIO_E2E=1 uv run python tests/test_lenses.py
Without NIO_E2E they print `skipped` and pass. Run them after changing a lens card or the jury skill."""
import os
import re
import subprocess
from importlib import resources
from pathlib import Path

from test_jury import PSLUG, plan_repo

from nio import agents, jury, plan

E2E = os.environ.get("NIO_E2E") == "1"
TOOLS = {"read": "Read Grep Glob"}


def run_lens(root, lens):
    """Run one lens card on the plan gate of the fixture, the way the jury skill builds its pack. Returns its findings."""
    meta, body, _ = agents.load(root)[lens]
    files = "\n".join(f"- {p.relative_to(root)}" for p in jury.sources(root, PSLUG, "plan"))
    check = "\n".join(plan.check(root, PSLUG)[0]) or "0 errors"
    template = resources.files("nio").joinpath("templates/lens-output.md").read_text()
    pack = (f"Gate: plan. Slug: {PSLUG}. Read these files, and nothing else:\n{files}\n\n`nio check plan` output:\n{check}\n\n"
            f"Answer in this format, with lens: {lens}, gate: plan, subject: {PSLUG}, by: \"juror / claude-code / opus\":\n\n{template}")
    tiers = agents.DEFAULT_TIERS["claude"]
    # the prompt goes on stdin: --allowedTools takes every argument after it as a tool name
    r = subprocess.run(["claude", "-p", "--model", tiers[meta["tier"]], "--system-prompt", body, "--allowedTools", TOOLS["read"]],
                       input=pack, cwd=root, capture_output=True, text=True, timeout=900)
    out = r.stdout
    assert out.strip(), r.stderr
    path = root / ".nio/runs/R-E2E/jury" / f"plan-{lens}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(out[out.index("---"):] if "---" in out else out)
    meta, findings, errs = jury.parse_lens(path, "plan", PSLUG)
    assert not errs, (errs, out)
    return meta, findings, path.read_text()


def edit(root, name, old, new):
    path = root / ".nio/specs" / PSLUG / name
    assert old in path.read_text(), (name, old)
    path.write_text(path.read_text().replace(old, new))


def cites(findings, *ids):
    return [f for f in findings if all(i in f["cites"] for i in ids)]


def e2e(test):
    def run():
        if not E2E:
            print(f"skipped {test.__name__} (set NIO_E2E=1)")
            return
        test()
        print("ok")
    run.__name__ = test.__name__
    return run


def code(root, text="def refund_order(order_id, by):\n    if order_state(order_id) != 'paid':\n        raise AlreadyRefunded('already refunded')\n    return pay_back(order_total(order_id))\n"):
    (root / "app.py").write_text(text)
    return root


def test_ac11_it_runs_the_plan_gate():  # reads the skill only: free, so it always runs
    skill = (Path(__file__).parent.parent / "skills/jury/SKILL.md").read_text()
    gate = skill.split("## At the plan gate")[1].split("\n## ")[0]
    assert "`nio jury plan <slug> plan`" in gate and "nio jury plan <slug> spec" not in gate
    print("ok")


@e2e
def test_ac13_its_reasoning_names_a_concrete_bug_for_a():
    _, _, text = run_lens(code(plan_repo()), "test-proof")
    reasoning = text.split("## Reasoning")[1].split("## Findings")[0]
    assert "TC-1" in reasoning and "refund amount is 40.00" in reasoning, reasoning


@e2e
def test_ac14_it_raises_a_finding_on_tc_2():
    root = code(plan_repo())
    edit(root, "tests.md", '- Assert: 409 "already refunded"; one payment only', "- Assert: the call doesn't throw")
    hits = cites(run_lens(root, "test-proof")[1], "TC-2")
    assert hits and any(f["kind"] == "untestable" and "the call doesn't throw" in " ".join(f["quotes"]) for f in hits), hits


@e2e
def test_ac15_it_raises_a_finding_on_tc_3():
    root = code(plan_repo())
    edit(root, "tests.md", "- Setup: a paid order of 40.00", "- Setup: a paid order of 40.00; `refund_order` replaced by a mock that returns a refund")
    hits = cites(run_lens(root, "test-proof")[1], "TC-1")
    assert any("mock" in " ".join(f["quotes"]) for f in hits), hits


@e2e
def test_ac16_it_raises_a_finding_on_tc_4():
    root = code(plan_repo())
    edit(root, "tests.md", "refund amount is 40.00", "refund amount equals `order_total(order)` computed in the test")
    hits = cites(run_lens(root, "test-proof")[1], "TC-1")
    said = lambda f: (f["title"] + " " + f["situation"]).lower()
    assert any(any(w in said(f) for w in ("independent", "same way", "code under test")) for f in hits), hits


@e2e
def test_ac17_it_raises_a_finding_that_tc_5_would_pass():
    root = code(plan_repo())  # refund_order exists and already rejects a second refund: TC-2 passes before any work
    edit(root, "contracts.md", "- Binding: `app.py:refund_order` (new)\n- Like: none: the first payment code in the app", "- Binding: `app.py:refund_order` (existing)")
    hits = cites(run_lens(root, "test-proof")[1], "TC-2")
    said = lambda f: (f["title"] + " " + f["situation"]).lower()
    assert any("already" in said(f) and ("today" in said(f) or "before any work" in said(f)) for f in hits), hits
    assert agents.load(root)["test-proof"][0]["tools"] == ["read"]  # it can't run a test


@e2e
def test_ac18_it_raises_a_finding_on_tc_6():
    root = code(plan_repo())
    edit(root, "plan.md", "- Delivers: CT-1, CT-2", "- Delivers: CT-1")
    edit(root, "plan.md", "- Scenario: QS-1", "- Scenario: QS-1\n\n### US-2 Refunds over HTTP\n- Depends on: US-1\n- Delivers: CT-2\n- Tests: TC-3")
    edit(root, "plan.md", "- Tests: TC-1, TC-2, TC-3, TC-4", "- Tests: TC-1, TC-2, TC-4")
    hits = cites(run_lens(root, "test-proof")[1], "TC-1")  # TC-1 posts over HTTP, which only US-2's CT-2 delivers
    assert any("US-2" in f["situation"] for f in hits), hits


@e2e
def test_ac19_it_raises_no_test_missing_finding_withou():
    root = code(plan_repo())
    (root / "tests").mkdir()
    (root / "tests/test_refunds.py").write_text("def test_second_refund():\n    assert refund_twice() == 409\n")
    _, findings, _ = run_lens(root, "test-proof")
    missing = [f for f in findings if "missing" in (f["title"] + f["situation"]).lower()]
    assert not cites(missing, "TC-2") and all("search" in f["situation"].lower() for f in missing), missing


@e2e
def test_ac21_it_raises_a_finding_on_ct_3():
    root = code(plan_repo())
    (root / "views.py").write_text("def list_orders(request):\n    return {'orders': all_orders()}\n")
    edit(root, "contracts.md", "- Binding: `app.py` (existing)", "- Binding: `app.py:RefundHandler` (new)\n- Like: `views.py:list_orders`")
    edit(root, "contracts.md", "- Shape: `POST /orders/<id>/refund`", "- Shape: `class RefundHandler(BaseHTTPRequestHandler)` serving `POST /orders/<id>/refund`")
    hits = cites(run_lens(root, "architecture-fit")[1], "CT-2")
    assert any("views.py:list_orders" in " ".join(f["quotes"]) for f in hits), hits


@e2e
def test_ac22_it_raises_a_finding_quoting_that_rule():
    root = code(plan_repo())
    (root / "CLAUDE.md").write_text("# Rules\n- Never commit without the human asking.\n")
    edit(root, "contracts.md", "- Rules: \"refund the full order amount\" (FR-1)", "- Rules: \"refund the full order amount\" (FR-1); commits the refund to git after each call")
    hits = cites(run_lens(root, "architecture-fit")[1], "CT-1")
    assert any(f["kind"] == "contradiction" and "Never commit without the human asking" in " ".join(f["quotes"]) for f in hits), hits


@e2e
def test_ac23_it_raises_a_finding_that_the_component_i():
    root = code(plan_repo())
    edit(root, "contracts.md", "### CT-2 Refund over HTTP", "### CT-3 Refund audit hook (FR-1) [default]\n- Binding: `app.py:audit_refund` (new)\n"
         "- Like: none: the first hook\n- Kind: function\n- Shape: `audit_refund(refund) -> None`\n\n### CT-2 Refund over HTTP")
    edit(root, "plan.md", "- Delivers: CT-1, CT-2", "- Delivers: CT-1, CT-2, CT-3")
    assert cites(run_lens(root, "architecture-fit")[1], "CT-3")


@e2e
def test_ac24_it_raises_a_finding_on_it():
    root = code(plan_repo())
    edit(root, "contracts.md", "### CT-2 Refund over HTTP", "### CT-3 Refund analytics module (FR-2) [default]\n- Binding: `analytics/refunds.py` (new)\n"
         "- Like: none: the first analytics module\n- Kind: function\n- Shape: `track(refund)`\n\n### CT-2 Refund over HTTP")
    edit(root, "plan.md", "- Delivers: CT-1, CT-2", "- Delivers: CT-1, CT-2, CT-3")
    hits = cites(run_lens(root, "architecture-fit")[1], "CT-3")
    assert any(f["kind"] == "scope" for f in hits), hits


@e2e
def test_ac25_it_raises_a_finding_on_us_2():
    root = code(plan_repo())
    edit(root, "plan.md", "- Scenario: QS-1", "- Scenario: QS-1\n\n### US-2 Internal refund bookkeeping\n- Depends on: US-1\n- Delivers: CT-2\n- Tests: TC-3")
    edit(root, "plan.md", "- Delivers: CT-1, CT-2", "- Delivers: CT-1")
    edit(root, "plan.md", "- Tests: TC-1, TC-2, TC-3, TC-4", "- Tests: TC-1, TC-2, TC-4")
    # ponytail: the fixture spec has one story, so the lens may judge US-1 or US-2 unshowable; either proves the question
    hits = [f for f in run_lens(root, "architecture-fit")[1] if any(c.startswith("US-") for c in f["cites"])]
    said = lambda f: (f["title"] + " " + f["situation"] + " " + f["fix"]).lower()
    assert any("shown" in said(f) or "demo" in said(f) for f in hits), hits


@e2e
def test_ac26_it_raises_a_finding_citing_both():
    root = code(plan_repo())
    edit(root, "contracts.md", "- Accepts: the ID of an order in state `paid`", "- Accepts: the ID of an order in state `paid`; amounts up to 500.00")
    edit(root, "contracts.md", "- Shape: `POST /orders/<id>/refund`", "- Shape: `POST /orders/<id>/refund`\n- Accepts: amounts up to 1,000.00")
    hits = cites(run_lens(root, "architecture-fit")[1], "CT-1", "CT-2")
    assert any(f["kind"] == "inconsistency" for f in hits), hits


@e2e
def test_ac50_it_raises_a_finding_naming_the_existing():
    root = plan_repo()  # refund_order is new: app.py stays empty, so only the parser is there to find
    (root / "parsers.py").write_text("def parse_amount(text):\n    return round(float(text), 2)\n")
    edit(root, "contracts.md", "- Like: none: the first payment code in the app", "- Like: none: first parser")
    edit(root, "contracts.md", "- Shape: `refund_order(order_id: str, by: str) -> Refund`", "- Shape: `refund_order(order_id: str, by: str, amount_text: str) -> Refund`, parsing `amount_text` itself")
    hits = cites(run_lens(root, "architecture-fit")[1], "CT-1")
    assert any("parsers.py" in f["title"] + f["situation"] + f["fix"] and "Like: none: first parser" in " ".join(f["quotes"]) for f in hits), hits


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if re.match(r"test_ac\d+", name):
            test()
