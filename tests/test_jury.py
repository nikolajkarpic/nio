"""Self-check for nio jury collect / dispose / check. Run: uv run python tests/test_jury.py"""
import json
from importlib import resources

from test_records import repo

from nio import jury, records

SPEC = """# Refunds
- FR-1: A refund is allowed while the order is paid or shipped.
- FR-2: Shipped orders can never be refunded; they must be returned first.
- AC-1 (FR-1): Given a paid order, when a refund is requested, then it is refunded.
"""
CONTRADICTION = """### F{n} Shipped orders are both refundable and not
- cites: FR-1, FR-2
- kind: contradiction
- severity: blocker
- evidence: observed
- quote: "Shipped orders can never be refunded"
- quote: "allowed while the order is paid or shipped"
- situation: a shipped order gets a refund request; FR-1 refunds it, FR-2 rejects it
- fix: keep one rule
"""


def lens(root, run, name, findings="none", lens_name=None, reasoning="Checked every rule.", context="sufficient"):
    path = root / ".nio/runs" / run / "jury" / f"spec-{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"""---
lens: {lens_name or name}
gate: spec
subject: refunds
by: "juror / claude-code / sonnet"
context: {context}
---
## Reasoning
{reasoning}

## Findings
{findings}
""")


def setup():
    root = repo()
    (root / ".nio/config.json").write_text(json.dumps({"memory": {"areas": ["auth", "project"]}}))
    (root / ".nio/specs/refunds").mkdir(parents=True)
    (root / ".nio/specs/refunds/spec.md").write_text(SPEC)
    return root


def test_gate():
    root = setup()
    untestable = """### F2 AC-1 has no observable
- cites: AC-1
- kind: untestable
- severity: minor
- evidence: observed
- quote: "then it is refunded"
- situation: a test can't tell refunded from pending
- fix: name the state the order ends in
"""
    invented = CONTRADICTION.replace("F{n}", "F3").replace("FR-1, FR-2", "FR-9, state table row `paid`").replace("contradiction", "gap")
    lens(root, "R-1", "logic", CONTRADICTION.format(n=1) + untestable + invented)
    # a label cite (a table row) is grounded by its quotes, not looked up
    lens(root, "R-1", "testability", CONTRADICTION.format(n=1).replace("blocker", "major").replace("FR-1, FR-2", "FR-1, FR-2, rule table"))
    lens(root, "R-1", "scope", reasoning="")  # invalid: no reasoning
    # same kind, overlapping but different cites: a different problem, kept apart
    other = CONTRADICTION.replace("F{n}", "F4").replace("FR-1, FR-2", "FR-1").replace("Shipped orders are both", "Paid orders are both")
    (root / ".nio/runs/R-1/jury/spec-logic.md").write_text((root / ".nio/runs/R-1/jury/spec-logic.md").read_text() + "\n" + other)
    out = jury.collect(root, "refunds", "spec", "R-1", expect=["logic", "testability", "scope"])
    led = jury.load(root, "refunds", "spec")
    j1 = led["findings"][0]
    assert {s["lens"] for s in j1["sources"]} == {"logic", "testability"} and j1["severity"] == "blocker", j1  # merged
    assert led["findings"][2]["status"] == "dropped", led["findings"][2]  # FR-9 isn't in the spec
    assert any("INVALID spec-scope.md" in line for line in out) and "### J-1 " in "\n".join(out), out
    assert "### J-2" not in "\n".join(out)  # minors skip the refuter
    assert jury.check(root, "refunds", "spec")[0] == "rerun"

    lens(root, "R-1", "scope")  # the retry
    jury.collect(root, "refunds", "spec", "R-1")
    assert jury.check(root, "refunds", "spec")[0] == "pending"
    (root / ".nio/runs/R-1/jury/spec-refuter.md").write_text(
        "### J-1\n- result: confirmed\n- reason: FR-2 forbids what FR-1 allows\n\n### J-4\n- result: confirmed\n- reason: yes\n")
    jury.collect(root, "refunds", "spec", "R-1")
    outcome, lines = jury.check(root, "refunds", "spec")
    assert outcome == "rejected" and "unresolved: 3" in lines, lines
    jury.dispose(root, "refunds", "spec", "J-4", "out-of-scope", "human", "paid-order refunds are the next spec")

    try:
        jury.dispose(root, "refunds", "spec", "J-1", "accepted-risk", "agent", "fine")
        raise AssertionError("an agent accepted a risk")
    except ValueError:
        pass
    jury.dispose(root, "refunds", "spec", "J-2", "spec-fix", "agent", "AC-1 now says the order ends in `refunded`")
    jury.dispose(root, "refunds", "spec", "J-1", "spec-fix", "grill", "the human kept FR-2; FR-1 no longer lists shipped")
    (root / ".nio/specs/refunds/spec.md").write_text(SPEC.replace("paid or shipped", "paid"))
    lens(root, "R-2", "logic")  # only the blocking lens re-runs, and finds nothing
    out = jury.collect(root, "refunds", "spec", "R-2")
    assert any(line.startswith("fixed   J-1") for line in out), out
    outcome, lines = jury.check(root, "refunds", "spec", record=True)
    assert outcome == "approved" and any("J-2 spec-fix" in line for line in lines), lines  # the agent's call, shown
    assert any(line.startswith("recorded") for line in lines), lines
    assert not any(line.startswith("recorded") for line in jury.check(root, "refunds", "spec", record=True)[1])  # once
    errors = [e for e in records.check(root)[0] if "project/" in e]
    assert not errors, errors
    ledger = (root / ".nio/specs/refunds/jury/spec.md").read_text()
    assert "| J-1 | blocker | contradiction | FR-1, FR-2 | logic, testability | confirmed | fixed |" in ledger, ledger
    print("ok")


def test_persisting_finding_goes_to_the_human():
    root = setup()
    for r in (1, 2, 3):
        lens(root, f"R-{r}", "logic", CONTRADICTION.format(n=1))
        jury.collect(root, "refunds", "spec", f"R-{r}")
        if r == 1:
            (root / ".nio/runs/R-1/jury/spec-refuter.md").write_text("### J-1\n- result: confirmed\n- reason: yes\n")
            jury.collect(root, "refunds", "spec", "R-1")
    led = jury.load(root, "refunds", "spec")
    assert led["findings"][0]["rounds"] == 2 and led["findings"][0]["baseline"] == "unchanged", led["findings"][0]
    outcome, lines = jury.check(root, "refunds", "spec")
    assert outcome == "human" and any("J-1 failed 2 rounds" in line for line in lines), lines
    print("ok")


def test_majority_overrules_one_juror():
    root = setup()
    lens(root, "R-1", "logic-1", CONTRADICTION.format(n=1), lens_name="logic")
    lens(root, "R-1", "logic-2", lens_name="logic")
    lens(root, "R-1", "logic-3", lens_name="logic")
    jury.collect(root, "refunds", "spec", "R-1")
    (root / ".nio/runs/R-1/jury/spec-refuter.md").write_text("### J-1\n- result: confirmed\n- reason: yes\n")
    jury.collect(root, "refunds", "spec", "R-1")
    outcome, _ = jury.check(root, "refunds", "spec")
    assert outcome == "approved" and jury.load(root, "refunds", "spec")["findings"][0]["status"] == "overruled"
    # a lens whose pack was too thin doesn't mark old findings fixed, and an ungrounded repeat keeps its ID
    lens(root, "R-3", "logic-1", CONTRADICTION.format(n=1).replace("FR-1, FR-2", "FR-9"), lens_name="logic", context="needs-more")
    jury.collect(root, "refunds", "spec", "R-3")
    lens(root, "R-4", "logic-2", CONTRADICTION.format(n=1).replace("FR-1, FR-2", "FR-9"), lens_name="logic")
    jury.collect(root, "refunds", "spec", "R-4")
    found = jury.load(root, "refunds", "spec")["findings"]
    assert found[0]["status"] == "overruled" and len(found) == 2 and found[1]["status"] == "dropped", found
    # an inferred finding can't block on its own
    lens(root, "R-2", "adversary", CONTRADICTION.format(n=1).replace("observed", "inferred").replace("contradiction", "risk"))
    jury.collect(root, "refunds", "spec", "R-2")
    assert jury.load(root, "refunds", "spec")["findings"][2]["severity"] == "major"
    print("ok")


def test_format_template_parses():
    """The lens output template the jury skill hands to lenses is itself a valid lens output."""
    root = setup()
    path = root / "lens.md"
    path.write_text(resources.files("nio").joinpath("templates/lens-output.md").read_text())
    meta, findings, errors = jury.parse_lens(path, "spec", "checkout-refunds")
    assert not errors and len(findings) == 1 and findings[0]["quotes"][1] == "allowed while the order is paid or shipped", errors
    print("ok")


if __name__ == "__main__":
    test_format_template_parses()
    test_gate()
    test_persisting_finding_goes_to_the_human()
    test_majority_overrules_one_juror()
