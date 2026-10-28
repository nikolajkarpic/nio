"""Self-check for nio jury collect / dispose / check. Run: uv run python tests/test_jury.py"""
import json
import re
import subprocess
from importlib import resources

from test_records import repo

from nio import agents, jury, plan, records, spec

PSLUG = "checkout-refunds"
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


def lens(root, run, name, findings="none", lens_name=None, reasoning="Checked every rule.", context="sufficient", verdicts=""):
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
{f"{chr(10)}## Verdicts{chr(10)}{verdicts}{chr(10)}" if verdicts else ""}
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
    outcome, lines = jury.check(root, "refunds", "spec")  # disposed as fixed, but the spec still reads the same
    assert outcome == "rejected" and "- spec-fix without a change to the spec: J-1, J-2" in lines, lines
    assert jury.check(root, "refunds", "spec", human="ship it", record=True)[0] == "human"
    assert jury.check(root, "refunds", "spec")[0] == "human"  # a later plain check keeps the human's closure
    (root / ".nio/specs/refunds/spec.md").write_text(SPEC.replace("paid or shipped", "paid"))
    jury.dispose(root, "refunds", "spec", "J-1", "spec-fix", "human", "FR-1 no longer lists shipped")  # after the edit
    (root / ".nio/specs/refunds/spec.md").write_text(SPEC)  # ...which is then undone: the fix isn't in the spec
    outcome, lines = jury.check(root, "refunds", "spec")  # the closure still holds (same round and spec): the jury's word shows under it
    assert outcome == "human" and "- (the jury said rejected: spec-fix without a change to the spec: J-1, J-2)" in lines, lines
    (root / ".nio/specs/refunds/spec.md").write_text(SPEC.replace("paid or shipped", "paid"))
    outcome, lines = jury.check(root, "refunds", "spec")  # every finding disposed, but no juror saw the fixed spec yet
    assert outcome == "rerun" and any("changed since round" in line for line in lines), lines
    lens(root, "R-2", "logic")  # only the blocking lenses re-run (both raised J-1), and find nothing
    lens(root, "R-2", "testability")
    out = jury.collect(root, "refunds", "spec", "R-2")
    assert any(line.startswith("fixed   J-1") for line in out), out
    assert jury.load(root, "refunds", "spec")["findings"][3]["status"] == "disposed"  # J-4, out of scope: not "fixed"
    outcome, lines = jury.check(root, "refunds", "spec", record=True)
    assert outcome == "approved" and any("J-2 spec-fix" in line for line in lines), lines  # the agent's call, shown
    assert any(line.startswith("recorded") for line in lines), lines
    assert not any(line.startswith("recorded") for line in jury.check(root, "refunds", "spec", record=True)[1])  # once
    # the human can close a gate themselves: recorded as outcome human with their reason, never approved
    outcome, lines = jury.check(root, "refunds", "spec", human="good enough for now")
    assert outcome == "human" and "the human closed the gate: good enough for now" in " ".join(lines), lines
    assert jury.check(root, "refunds", "spec")[0] == "approved"  # the jury's own approval outranks a closure
    errors = [e for e in records.check(root)[0] if "project/" in e]
    assert not errors, errors
    ledger = (root / ".nio/specs/refunds/jury/spec.md").read_text()
    assert "| J-1 | blocker | contradiction | FR-1, FR-2 | logic, testability | confirmed | fixed |" in ledger, ledger
    print("ok")


def test_persisting_finding_goes_to_the_human():
    root = setup()
    for r in (1, 2, 3):
        if r > 1:  # a fix attempt that doesn't fix it: the spec changes, the finding stays
            spec_md = root / ".nio/specs/refunds/spec.md"
            spec_md.write_text(spec_md.read_text() + f"- FR-{r + 2}: An attempt {r}.\n")
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


def test_escalation_is_not_a_fix():
    """Extra jurors judging the same version neither fix nor fail what the first juror found, and two findings with
    the same IDs but different labelled targets stay apart."""
    root = setup()
    table = CONTRADICTION.format(n=1).replace("FR-1, FR-2", "FR-1, FR-2, state table row paid")
    lens(root, "R-1", "logic", CONTRADICTION.format(n=1).replace("FR-1, FR-2", "FR-1, FR-2, the non-goal on refunds"))
    lens(root, "R-1", "scope", table.replace("Shipped orders are both", "The table and FR-1 disagree"), lens_name="scope")
    jury.collect(root, "refunds", "spec", "R-1")
    assert len(jury.load(root, "refunds", "spec")["findings"]) == 2  # a label pointing elsewhere: a second problem
    lens(root, "R-1", "logic-2", lens_name="logic")  # escalation juror, same spec version, finds nothing
    out = jury.collect(root, "refunds", "spec", "R-1")
    f = jury.load(root, "refunds", "spec")["findings"][0]
    assert f["status"] == "open" and f["rounds"] == 0 and not any(line.startswith("fixed") for line in out), (f, out)
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


def test_deferred_points_need_the_human():
    root = setup()
    (root / ".nio/specs/refunds/spec.md").write_text(SPEC + "\n## Deferred\n- **DF-1** (from FR-2; contradiction) FR-1 and FR-2 disagree on shipped orders.\n"
                                                    "- **DF-2** (from OP-3) How long is a refund window?\n")
    lens(root, "R-1", "logic")
    out = jury.collect(root, "refunds", "spec", "R-1")
    found = jury.load(root, "refunds", "spec")["findings"]
    assert [(f["severity"], f["kind"]) for f in found] == [("blocker", "contradiction"), ("major", "gap")], found
    assert "J-1" not in "\n".join(line for line in out if line.startswith("###")), out  # no refuter for them
    jury.collect(root, "refunds", "spec", "R-1")
    assert len(jury.load(root, "refunds", "spec")["findings"]) == 2  # added once
    assert jury.check(root, "refunds", "spec")[0] == "rejected"
    try:
        jury.dispose(root, "refunds", "spec", "J-1", "spec-fix", "agent", "picked FR-2")
        raise AssertionError("an agent closed a deferred point")
    except ValueError:
        pass
    try:
        jury.dispose(root, "refunds", "spec", "J-1", "spec-fix", "grill", "the human kept FR-2 in a second session")
        raise AssertionError("a spec-fix closed a deferred point still in ## Deferred")
    except ValueError as e:
        assert "DF-1 is still in `## Deferred`" in str(e), e
    try:  # the human's own spec-fix waits for the DF line to go too
        jury.dispose(root, "refunds", "spec", "J-1", "spec-fix", "human", "kept FR-2")
        raise AssertionError("a human spec-fix closed a deferred point still in ## Deferred")
    except ValueError as e:
        assert "DF-1 is still in `## Deferred`" in str(e), e
    spec = root / ".nio/specs/refunds/spec.md"
    spec.write_text(spec.read_text().replace("- **DF-1** (from FR-2; contradiction) FR-1 and FR-2 disagree on shipped orders.\n", ""))
    jury.dispose(root, "refunds", "spec", "J-1", "spec-fix", "grill", "the human kept FR-2 in a second session")
    jury.dispose(root, "refunds", "spec", "J-2", "accepted-risk", "human", "30 days, revisit after launch")
    assert jury.check(root, "refunds", "spec")[0] == "rerun"  # the fix is in: the lenses judge it next
    print("ok")


def test_plan_and_changed():
    """The lens plan comes from the gate, the risk flags and the FR count; a re-review knows what a fix changed."""
    from pathlib import Path
    root = setup()
    fixture = (Path(__file__).parent / "fixtures/spec/spec-bugfix.md").read_text()
    path = root / ".nio/specs/refund-double-charge/spec.md"
    path.parent.mkdir(parents=True)
    path.write_text(fixture)
    lines, ok = jury.plan(root, "refund-double-charge", "spec")
    assert ok and lines[0] == "tier: high (money)" and "adversary (risk: money)" in lines[1] and lines[2] == "runs: 3 of 6", lines
    lines, ok = jury.plan(root, "refund-double-charge", "spec", ["consistency:D-1 approved", "nosuch:a reason"])
    assert not ok and "missing cards: nosuch" in lines[-1] and "consistency (D-1 approved)" in lines[1], lines
    assert [jury.rung(r) for r in ([], ["pii"], ["pii", "auth"])] == ["low", "medium", "high"]
    path.write_text(fixture.replace("[human]", "[default]", 1))  # not settled: no lens may run
    assert jury.plan(root, "refund-double-charge", "spec") == (["`nio check spec refund-double-charge --gate` fails (1 errors): finish the grill first"], False)
    # a round records the judged spec; a fix to EB-1 re-runs the lens that blocked on it
    path.write_text(fixture)
    finding = CONTRADICTION.format(n=1).replace("FR-1, FR-2", "EB-1").replace('- quote: "Shipped orders can never be refunded"\n', "").replace(
        '"allowed while the order is paid or shipped"', '"create exactly one refund"')
    run = root / ".nio/runs/R-1/jury/spec-logic.md"
    run.parent.mkdir(parents=True)
    run.write_text(f"---\nlens: logic\ngate: spec\nsubject: refund-double-charge\nby: juror / claude / sonnet\ncontext: sufficient\n---\n"
                   f"## Reasoning\nChecked.\n\n## Findings\n{finding}")
    jury.collect(root, "refund-double-charge", "spec", "R-1")
    (root / ".nio/runs/R-1/jury/spec-refuter.md").write_text("### J-1\n- result: confirmed\n- reason: yes\n")
    jury.collect(root, "refund-double-charge", "spec", "R-1")
    path.write_text(fixture.replace("create exactly one refund", "create exactly one refund per order"))
    assert jury.changed(root, "refund-double-charge", "spec")[:2] == (["EB-1"], ["logic"])
    print("ok")


def test_answers_for_scope():
    root = setup()
    (root / ".nio/specs/refunds/grill.md").write_text("""# Grill log
## Q1 · OP-3 · 2026-10-25
Question: When does it end?
Options: 1. Green and you confirm (recommended) 2. Green is enough
3. You decide
Answer: 1 [human]
Patched: FR-17

## Call · US-1 · 2026-10-25
Below the bar. [agent]

## Q2 · FR-3 · 2026-10-25
Question: Which to adopt?
Options (several allowed): 1. Glossary 2. Fidelity 3. Rounds
Answer: 1 and 3 [human]

## Q3 · OP-4 · 2026-10-25
Question: Where do deferred points go?
Answer: free form: in their own section [human]

## Q4 · J-16 · 2026-10-25
Question: What if a lookup finds nothing?
Answer: 1. Show it, then you choose: decide now or defer; conflicting
sources are a contradiction [human]
Patched: FR-34

## Q5 · OP-6 · 2026-10-25
Question: Cap the retries?
Options: 1. Cap at 5. Then stop 2. No cap
Answer: 1 [human]

## Q7 · OP-8 · 2026-10-25
Question: Retry?
Options:
1. Retry up to 2. Then stop
   at once (recommended)
2. Never
Answer: 1 [human]

## Q6 · OP-7 · 2026-10-25
Question: Keep it?
Options: (pick one) 1. Keep (Recommended) 2. Drop
Answer: 1 [human]
""")
    assert jury.answers(root, "refunds") == [
        "## Q1 · OP-3 · 2026-10-25", "Question: When does it end?", "Answer: Green and you confirm [human]", "",
        "## Q2 · FR-3 · 2026-10-25", "Question: Which to adopt?", "Answer: Glossary; Rounds [human]", "",
        "## Q3 · OP-4 · 2026-10-25", "Question: Where do deferred points go?", "Answer: free form: in their own section [human]", "",
        "## Q4 · J-16 · 2026-10-25", "Question: What if a lookup finds nothing?",
        "Answer: 1. Show it, then you choose: decide now or defer; conflicting sources are a contradiction [human]", "",
        "## Q5 · OP-6 · 2026-10-25", "Question: Cap the retries?", "Answer: Cap at 5. Then stop [human]", "",
        "## Q7 · OP-8 · 2026-10-25", "Question: Retry?", "Answer: Retry up to 2. Then stop at once [human]", "",
        "## Q6 · OP-7 · 2026-10-25", "Question: Keep it?", "Answer: Keep [human]", ""], jury.answers(root, "refunds")
    print("ok")


def test_cli_dispose_order():
    """The documented order is `nio jury dispose <slug> <gate> <J-n> <disposition>`; the tests above call Python."""
    import contextlib, io, os, sys
    from nio import cli
    root = setup()
    lens(root, "R-1", "logic", CONTRADICTION.format(n=1).replace("blocker", "minor"))
    jury.collect(root, "refunds", "spec", "R-1")
    here, argv = os.getcwd(), sys.argv
    try:
        os.chdir(root)
        sys.argv = ["nio", "jury", "dispose", "refunds", "spec", "J-1", "spec-fix", "--by", "agent", "--note", "wording"]
        with contextlib.redirect_stdout(io.StringIO()) as out:
            cli.main()
        assert out.getvalue().strip() == "J-1: spec-fix by agent", out.getvalue()
    finally:
        os.chdir(here)
        sys.argv = argv
    print("ok")


def test_review_scenarios():
    """The independent review's reproductions: version-aware fixes and failed rounds per finding, no approval of what
    nothing judged, whole-artefact versions for the plan gate, and grounding that ignores grill log headers."""
    root = setup()
    spec_md = root / ".nio/specs/refunds/spec.md"
    blocker = CONTRADICTION.format(n=1)
    confirm = lambda run: (root / f".nio/runs/{run}/jury/spec-refuter.md").write_text("### J-1\n- result: confirmed\n- reason: yes\n")
    # 3: nothing collected is never approved
    assert jury.check(root, "refunds", "spec")[0] == "rerun"
    # 1: testability raised J-1 on v1; the spec changed; logic re-ran alone; testability judges v2 later and is clean
    lens(root, "R-1", "testability", blocker)
    lens(root, "R-1", "logic")
    jury.collect(root, "refunds", "spec", "R-1")
    confirm("R-1")
    jury.collect(root, "refunds", "spec", "R-1")
    spec_md.write_text(spec_md.read_text().replace("paid or shipped", "paid"))
    lens(root, "R-2", "logic")
    jury.collect(root, "refunds", "spec", "R-2")
    assert jury.load(root, "refunds", "spec")["findings"][0]["status"] == "open"  # testability hasn't judged v2 yet
    lens(root, "R-3", "testability")
    out = jury.collect(root, "refunds", "spec", "R-3")
    assert any(line.startswith("fixed   J-1") for line in out), out
    # 2: raised again after it was marked fixed: reopened, and a failed round (v1 -> v2 didn't fix it)
    lens(root, "R-4", "logic", blocker.replace("blocker", "major"))
    jury.collect(root, "refunds", "spec", "R-4")
    f = jury.load(root, "refunds", "spec")["findings"][0]
    assert f["status"] == "open" and f["rounds"] == 1, f
    # 5: a retired ID in a grill log header, or a rejected option, doesn't ground a finding
    (root / ".nio/specs/refunds/grill.md").write_text("## Q1 · FR-9 · 2026-10-25\nQuestion: Keep it?\n"
                                                    "Options: 1. Keep it (recommended) 2. Drop the refund rule\nAnswer: 1 [human]\n")
    stray = CONTRADICTION.format(n=1).replace("FR-1, FR-2", "FR-9").replace('- quote: "Shipped orders can never be refunded"\n', "").replace(
        '"allowed while the order is paid or shipped"', '"Drop the refund rule"').replace("contradiction", "gap")
    lens(root, "R-5", "scope", stray)
    out = jury.collect(root, "refunds", "spec", "R-5")
    assert any("dropped" in line and "(ungrounded)" in line for line in out), out
    print("ok")


def test_plan_gate_versions():
    """4: the plan gate's version covers all four plan files, without plan.md too."""
    root = setup()
    contracts = root / ".nio/specs/refunds/contracts.md"
    contracts.write_text("- **FR-1** THE SYSTEM SHALL expose POST /refunds. [human]\n")
    path = root / ".nio/runs/R-1/jury/plan-logic.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\nlens: logic\ngate: plan\nsubject: refunds\nby: juror / claude / sonnet\ncontext: sufficient\n---\n"
                    "## Reasoning\nChecked.\n\n## Findings\nnone\n")
    jury.collect(root, "refunds", "plan", "R-1")  # no plan.md: no crash
    assert jury.check(root, "refunds", "plan")[0] == "approved"
    contracts.write_text(contracts.read_text().replace("POST", "PUT"))
    assert jury.check(root, "refunds", "plan")[0] == "rerun"  # an edit to contracts.md is an unjudged version
    assert jury.changed(root, "refunds", "plan")[0] == ["FR-1"]
    print("ok")


def test_needs_more_doesnt_fix():
    """6: a juror whose pack was too thin judged nothing, so its silence doesn't mark its finding fixed."""
    root = setup()
    spec_md = root / ".nio/specs/refunds/spec.md"
    lens(root, "R-1", "logic", CONTRADICTION.format(n=1).replace("blocker", "minor"))
    jury.collect(root, "refunds", "spec", "R-1")
    spec_md.write_text(spec_md.read_text() + "- FR-3: Another rule.\n")
    lens(root, "R-2", "logic", context="needs-more")
    jury.collect(root, "refunds", "spec", "R-2")
    assert jury.load(root, "refunds", "spec")["findings"][0]["status"] == "open"
    lens(root, "R-3", "logic")
    out = jury.collect(root, "refunds", "spec", "R-3")
    assert any(line.startswith("fixed   J-1") for line in out), out
    print("ok")


def test_format_template_parses():
    """The lens output template the jury skill hands to lenses is itself a valid lens output."""
    root = setup()
    path = root / "lens.md"
    path.write_text(resources.files("nio").joinpath("templates/lens-output.md").read_text())
    meta, findings, errors = jury.parse_lens(path, "spec", "checkout-refunds")
    assert not errors and len(findings) == 1 and findings[0]["quotes"][1] == "allowed while the order is paid or shipped", errors
    assert findings[0]["cites"] == ["FR-1", "FR-2"] and findings[0]["kind"] == "contradiction", findings  # comments stripped
    print("ok")


def test_versions_decide_fixed():
    """Regressions from the second independent review: what a re-run on a new version may and may not settle."""
    def edit(root, extra):
        spec = root / ".nio/specs/refunds/spec.md"
        spec.write_text(spec.read_text() + extra)
    led = lambda root: jury.load(root, "refunds", "spec")
    confirm = "### J-{n}\n- result: confirmed\n- reason: yes\n"

    # fixed only once every source juror judged a newer version, even across rounds
    root = setup()
    lens(root, "R-1", "logic", CONTRADICTION.format(n=1))
    lens(root, "R-1", "logic-2", CONTRADICTION.format(n=1), lens_name="logic")
    jury.collect(root, "refunds", "spec", "R-1")
    edit(root, "- FR-3: new.\n")
    lens(root, "R-2", "logic")
    jury.collect(root, "refunds", "spec", "R-2")
    assert led(root)["findings"][0]["status"] == "open"
    lens(root, "R-3", "logic-2", lens_name="logic")
    jury.collect(root, "refunds", "spec", "R-3")
    assert led(root)["findings"][0]["status"] == "fixed" and jury.check(root, "refunds", "spec")[0] == "approved"

    # a fix made before a round that skipped the finding's lens counts when disposed afterwards (fifth review)
    root = setup()
    lens(root, "R-1", "logic", CONTRADICTION.format(n=1))
    lens(root, "R-1", "testability")
    jury.collect(root, "refunds", "spec", "R-1")
    (root / ".nio/runs/R-1/jury/spec-refuter.md").write_text(confirm.format(n=1))
    jury.collect(root, "refunds", "spec", "R-1")
    edit(root, "- FR-3: new.\n")
    lens(root, "R-2", "testability")
    jury.collect(root, "refunds", "spec", "R-2")
    jury.dispose(root, "refunds", "spec", "J-1", "spec-fix", "agent", "FR-3 settles it")
    outcome, lines = jury.check(root, "refunds", "spec")
    assert not any("spec-fix without a change" in line for line in lines), lines
    # ...but undone and judged again, the spec reads as when the finding was raised: the fix isn't there
    (root / ".nio/specs/refunds/spec.md").write_text(SPEC)
    lens(root, "R-3", "testability")
    jury.collect(root, "refunds", "spec", "R-3")
    assert "spec-fix without a change to the spec: J-1" in " ".join(jury.check(root, "refunds", "spec")[1])

    # attempts count per version: one invalid output on a new version is retried, not sent to the human
    root = setup()
    lens(root, "R-1", "logic")
    jury.collect(root, "refunds", "spec", "R-1")
    edit(root, "- FR-3: new.\n")
    lens(root, "R-2", "logic", reasoning="")
    jury.collect(root, "refunds", "spec", "R-2")
    assert jury.check(root, "refunds", "spec")[0] == "rerun"

    # an overruled finding the majority raises on a newer version reopens
    root = setup()
    lens(root, "R-1", "logic", CONTRADICTION.format(n=1))
    lens(root, "R-1", "logic-2", lens_name="logic")
    lens(root, "R-1", "logic-3", lens_name="logic")
    jury.collect(root, "refunds", "spec", "R-1")
    (root / ".nio/runs/R-1/jury/spec-refuter.md").write_text(confirm.format(n=1))
    jury.collect(root, "refunds", "spec", "R-1")
    assert jury.check(root, "refunds", "spec")[0] == "approved" and led(root)["findings"][0]["status"] == "overruled"
    edit(root, "- FR-3: new.\n")
    for name in ("logic", "logic-2", "logic-3"):
        lens(root, "R-2", name, CONTRADICTION.format(n=1), lens_name="logic")
    jury.collect(root, "refunds", "spec", "R-2")
    found = led(root)["findings"]
    assert len(found) == 1 and found[0]["status"] == "open", found
    assert jury.check(root, "refunds", "spec")[0] == "rejected"

    # a retry under another file name supersedes the invalid output
    root = setup()
    lens(root, "R-1", "logic")
    lens(root, "R-1", "testability", reasoning="")
    jury.collect(root, "refunds", "spec", "R-1", expect=["logic", "testability"])
    lens(root, "R-2", "testability-2", lens_name="testability")
    jury.collect(root, "refunds", "spec", "R-2")
    assert jury.check(root, "refunds", "spec")[0] == "approved"

    # an emptied artefact is a new version
    root = setup()
    lens(root, "R-1", "logic")
    jury.collect(root, "refunds", "spec", "R-1")
    (root / ".nio/specs/refunds/spec.md").write_text("")
    assert jury.check(root, "refunds", "spec")[0] == "rerun"

    # two lenses re-raising one finding count one failed round, not two
    root = setup()
    for rnd, extra in (("R-1", ""), ("R-2", "- FR-3: new.\n")):
        edit(root, extra)
        lens(root, rnd, "logic", CONTRADICTION.format(n=1))
        lens(root, rnd, "testability", CONTRADICTION.format(n=1))
        jury.collect(root, "refunds", "spec", rnd)
    found = led(root)["findings"]
    assert len(found) == 1 and found[0]["rounds"] == 1, found

    # a lens citing a deferred point doesn't stand in for the deferred finding
    root = setup()
    edit(root, "\n## Deferred\n- **DF-1** (from FR-2; contradiction) whether shipped orders refund\n")
    minor = CONTRADICTION.format(n=1).replace("FR-1, FR-2", "DF-1").replace("blocker", "minor").replace("contradiction\n", "ambiguity\n")
    lens(root, "R-1", "logic", minor)
    jury.collect(root, "refunds", "spec", "R-1")
    found = led(root)["findings"]
    assert [f["kind"] for f in found] == ["ambiguity", "contradiction"], found
    jury.dispose(root, "refunds", "spec", "J-1", "spec-fix", "agent", "reworded")
    assert jury.check(root, "refunds", "spec")[0] == "rejected"

    # the refuter can't merge a finding into a dropped one
    root = setup()
    ungrounded = CONTRADICTION.format(n=2).replace("FR-1, FR-2", "FR-9").replace("contradiction\n", "gap\n")
    lens(root, "R-1", "logic", CONTRADICTION.format(n=1) + ungrounded)
    jury.collect(root, "refunds", "spec", "R-1")
    (root / ".nio/runs/R-1/jury/spec-refuter.md").write_text("### J-1\n- same-as: J-2\n")
    jury.collect(root, "refunds", "spec", "R-1")
    assert [f["status"] for f in led(root)["findings"]] == ["open", "dropped"]
    assert jury.check(root, "refunds", "spec")[0] == "pending"
    print("ok")


# --- #52: the stop rule, fix verdicts and the final fix check ---
MAJOR = CONTRADICTION.format(n=1).replace("blocker", "major")
MINOR = """### F2 AC-1 has no observable
- cites: AC-1
- kind: untestable
- severity: minor
- evidence: observed
- quote: "then it is refunded"
- situation: a test can't tell refunded from pending
- fix: name the state the order ends in
"""
NEW_MAJOR = """### F3 Returns have no rule
- cites: FR-2
- kind: gap
- severity: major
- evidence: observed
- quote: "they must be returned first"
- situation: a return arrives and no rule says what happens
- fix: add a return rule
"""
NEW_BLOCKER = NEW_MAJOR.replace("F3", "F1").replace("major", "blocker")
CONFIRM = "### J-{n}\n- result: confirmed\n- reason: yes\n"
REFUTE = "### J-{n}\n- result: refuted\n- reason: FR-2 settles it\n"


def first_review(findings=MAJOR + MINOR, refuter=CONFIRM.format(n=1), text=SPEC):
    """A first review that the jury rejects and records, with every finding then fixed by the agent (#52)."""
    root = setup()
    (root / ".nio/specs/refunds/spec.md").write_text(text)
    lens(root, "R-1", "logic", findings)
    jury.collect(root, "refunds", "spec", "R-1")
    (root / ".nio/runs/R-1/jury/spec-refuter.md").write_text(refuter)
    jury.collect(root, "refunds", "spec", "R-1")
    outcome, lines = jury.check(root, "refunds", "spec", record=True)
    assert outcome == "rejected" and any(line.startswith("recorded") for line in lines), lines
    fix(root, *[f["id"] for f in jury.load(root, "refunds", "spec")["findings"] if f["status"] == "open"])
    return root


def fix(root, *ids, by="agent", text="- FR-3: fixed.\n"):
    for i in ids:
        jury.dispose(root, "refunds", "spec", i, "spec-fix", by, f"{i} fixed")
    spec_md = root / ".nio/specs/refunds/spec.md"
    spec_md.write_text(spec_md.read_text() + text)


def verdicts(**given):
    return "\n".join(f"- {i.replace('_', '-')}: {v} — {'still there' if v == 'not fixed' else 'gone'}" for i, v in given.items())


def test_stop_rule():
    """AC-1, AC-2, AC-3, AC-4, AC-6, AC-7."""
    led = lambda root: {f["id"]: f for f in jury.load(root, "refunds", "spec")["findings"]}
    root = first_review()  # AC-1: a confirmed major in the first review is rejected, as today
    lens(root, "R-2", "logic", NEW_MAJOR, verdicts=verdicts(J_1="not fixed", J_2="not fixed"))  # AC-2
    out = jury.collect(root, "refunds", "spec", "R-2")
    assert any("J-3" in line and "a note only" in line for line in out), out
    outcome, lines = jury.check(root, "refunds", "spec", record=True)
    assert outcome == "human" and "- one list for the human; fix or accept each as risk: J-1, J-2" in lines, lines
    assert "notes (no ruling needed):" in lines and led(root)["J-3"]["status"] == "noted", lines
    jury.dispose(root, "refunds", "spec", "J-2", "accepted-risk", "human", "fine")  # AC-6: J-1 still open
    outcome, lines = jury.check(root, "refunds", "spec")
    assert outcome == "human" and "- one list for the human; fix or accept each as risk: J-1" in lines, lines

    root = first_review()  # AC-3: a new blocker the refuter confirms starts another round
    lens(root, "R-2", "logic", NEW_BLOCKER, verdicts=verdicts(J_1="fixed", J_2="fixed"))
    jury.collect(root, "refunds", "spec", "R-2")
    assert jury.check(root, "refunds", "spec")[0] == "pending"
    (root / ".nio/runs/R-2/jury/spec-refuter.md").write_text(CONFIRM.format(n=3))
    jury.collect(root, "refunds", "spec", "R-2")
    outcome, lines = jury.check(root, "refunds", "spec")
    assert outcome == "rejected" and "- unresolved: J-3" in lines, lines

    root = first_review()  # AC-4: refuted, nothing else open: approved
    lens(root, "R-2", "logic", NEW_BLOCKER, verdicts=verdicts(J_1="fixed", J_2="fixed"))
    jury.collect(root, "refunds", "spec", "R-2")
    (root / ".nio/runs/R-2/jury/spec-refuter.md").write_text(REFUTE.format(n=3))
    jury.collect(root, "refunds", "spec", "R-2")
    assert jury.check(root, "refunds", "spec")[0] == "approved" and led(root)["J-3"]["status"] == "refuted"

    # AC-7: a blocker that failed two rounds goes to the human before another re-review
    root = first_review(CONTRADICTION.format(n=1))
    for rnd in ("R-2", "R-3"):
        lens(root, rnd, "logic", verdicts=verdicts(J_1="not fixed"))
        jury.collect(root, "refunds", "spec", rnd)
        (root / f".nio/runs/{rnd}/jury/spec-refuter.md").write_text(CONFIRM.format(n=1))
        jury.collect(root, "refunds", "spec", rnd)
        if rnd == "R-2":
            assert jury.check(root, "refunds", "spec", record=True)[0] == "rejected"
            fix(root, "J-1", text="- FR-4: again.\n")
    outcome, lines = jury.check(root, "refunds", "spec")
    assert outcome == "human" and "- J-1 failed 2 rounds" in lines, lines
    print("ok")


def to_list(root, *not_fixed):
    """A re-review that finds `not_fixed` still there and the rest fixed: the human gets one list."""
    lens(root, "R-2", "logic", verdicts=verdicts(**{i.replace("-", "_"): "not fixed" if i in not_fixed else "fixed" for i in ("J-1", "J-2")}))
    jury.collect(root, "refunds", "spec", "R-2")
    assert jury.check(root, "refunds", "spec", record=True)[0] == "human"


def test_final_check():
    """AC-5, AC-21, AC-24, AC-25, AC-26, AC-27."""
    root = first_review()
    to_list(root, "J-1", "J-2")
    fix(root, "J-1", by="human")  # AC-5, AC-25: fix one, accept the other; the final check is owed
    jury.dispose(root, "refunds", "spec", "J-2", "accepted-risk", "human", "fine")
    outcome, lines = jury.check(root, "refunds", "spec", record=True)
    assert outcome == "rerun" and any("final fix check" in line and "J-1" in line for line in lines), lines
    assert "J-1" in "\n".join(jury.fixcheck(root, "refunds", "spec", "logic"))
    lens(root, "R-3", "logic", verdicts=verdicts(J_1="fixed"))
    jury.collect(root, "refunds", "spec", "R-3")
    outcome, lines = jury.check(root, "refunds", "spec", record=True)
    assert outcome == "approved" and any(line.startswith("recorded") for line in lines), lines

    root = first_review()  # AC-21, AC-26: the final check finds a fix didn't work; the human's second fix ends it
    to_list(root, "J-1")
    fix(root, "J-1", by="human")
    lens(root, "R-3", "logic", verdicts=verdicts(J_1="not fixed"))
    jury.collect(root, "refunds", "spec", "R-3")
    outcome, lines = jury.check(root, "refunds", "spec", record=True)
    assert outcome == "human" and "- the final fix check flagged these; fix or accept each as risk: J-1" in lines, lines
    fix(root, "J-1", by="human", text="- FR-4: again.\n")
    outcome, lines = jury.check(root, "refunds", "spec", record=True)
    assert outcome == "approved" and "- fixed after the final fix check, judged by no lens: J-1" in lines, lines

    root = first_review()  # AC-24: every listed finding accepted, none fixed: no final check
    to_list(root, "J-1", "J-2")
    for i in ("J-1", "J-2"):
        jury.dispose(root, "refunds", "spec", i, "accepted-risk", "human", "fine")
    assert jury.check(root, "refunds", "spec", record=True)[0] == "approved"

    root = first_review()  # AC-27: a new blocker in the final check goes to the human, not another round
    to_list(root, "J-1")
    fix(root, "J-1", by="human")
    lens(root, "R-3", "logic", NEW_BLOCKER, verdicts=verdicts(J_1="fixed"))
    jury.collect(root, "refunds", "spec", "R-3")
    (root / ".nio/runs/R-3/jury/spec-refuter.md").write_text(CONFIRM.format(n=3))
    jury.collect(root, "refunds", "spec", "R-3")
    outcome, lines = jury.check(root, "refunds", "spec")
    assert outcome == "human" and "- the final fix check flagged these; fix or accept each as risk: J-3" in lines, lines
    print("ok")


def test_fix_verdicts():
    """AC-10, AC-11, AC-12, AC-13, AC-20, AC-22, AC-23."""
    led = lambda root: {f["id"]: f for f in jury.load(root, "refunds", "spec")["findings"]}
    root = first_review()
    lens(root, "R-2", "logic", verdicts=verdicts(J_1="fixed"))  # AC-12: J-2 has no verdict
    out = jury.collect(root, "refunds", "spec", "R-2")
    assert any("INVALID" in line and "no verdict for J-2" in line for line in out), out
    lens(root, "R-2", "logic", verdicts=verdicts(J_1="fixed", J_2="fixed", J_7="fixed"))  # AC-13
    out = jury.collect(root, "refunds", "spec", "R-2")
    assert any("INVALID" in line and "J-7 is not in the fix-check pack" in line for line in out), out
    lens(root, "R-2", "logic", verdicts=verdicts(J_1="fixed", J_2="fixed") + "\n- J-2: not fixed — on second look")  # AC-22
    out = jury.collect(root, "refunds", "spec", "R-2")
    assert any("INVALID" in line and "J-2 has more than one verdict" in line for line in out), out
    lens(root, "R-2", "logic", verdicts=verdicts(J_1="fixed", J_2="not fixed"))  # AC-10, AC-11, AC-23
    jury.collect(root, "refunds", "spec", "R-2")
    assert led(root)["J-1"]["status"] == "fixed"
    j2 = led(root)["J-2"]
    assert j2["status"] == "open" and j2["rounds"] == 1, j2  # not fixed by silence, though its lens judged a new version

    root = first_review(CONTRADICTION.format(n=1))  # AC-20: a not-fixed blocker the refuter refutes starts no round
    lens(root, "R-2", "logic", verdicts=verdicts(J_1="not fixed"))
    out = jury.collect(root, "refunds", "spec", "R-2")
    assert "### J-1 " in "\n".join(out) and jury.check(root, "refunds", "spec")[0] == "pending", out
    (root / ".nio/runs/R-2/jury/spec-refuter.md").write_text(REFUTE.format(n=1))
    jury.collect(root, "refunds", "spec", "R-2")
    assert jury.check(root, "refunds", "spec")[0] == "approved" and led(root)["J-1"]["status"] == "refuted"
    print("ok")


def test_final_check_sees_cites_and_human_overrules():
    """#58: the fix-check pack shows what each finding cites as it reads now, not only what changed last; and the
    human can overrule a `not fixed` the final check flagged, so a clean spec is approved instead of closed."""
    root = first_review(text=re.sub(r"^- ([A-Z]+-\d+):", r"- **\1**", SPEC, flags=re.M))
    to_list(root, "J-1")
    fix(root, "J-1", by="human")
    pack = "\n".join(jury.fixcheck(root, "refunds", "spec", "logic"))
    cites = pack.split("- what it cites, now:\n")[1].split("\n\n")[0]  # FR-1 and FR-2 didn't change in the last edit
    assert "**FR-1**" in cites and "**FR-2**" in cites and "**FR-2**" not in pack.split("## Changed items")[1], pack
    try:
        jury.dispose(root, "refunds", "spec", "J-1", "overruled", "human", "it's fixed")
        raise AssertionError("overruled a finding the final check never flagged")
    except ValueError:
        pass
    lens(root, "R-3", "logic", verdicts=verdicts(J_1="not fixed"))
    jury.collect(root, "refunds", "spec", "R-3")
    assert jury.check(root, "refunds", "spec", record=True)[0] == "human"
    try:
        jury.dispose(root, "refunds", "spec", "J-1", "overruled", "agent", "it's fixed")
        raise AssertionError("an agent overruled a finding")
    except ValueError:
        pass
    jury.dispose(root, "refunds", "spec", "J-1", "overruled", "human", "FR-1 no longer lists shipped; the pack missed it")
    outcome, lines = jury.check(root, "refunds", "spec", record=True)
    assert outcome == "approved", lines
    assert "overruled by the human" in (root / ".nio/specs/refunds/jury/spec.md").read_text()
    print("ok")


def test_retry_after_another_lens_fixed_a_shared_finding():
    """#55: two lenses share J-1; logic marks it fixed, testability's output is invalid. Its retry gives verdicts on the
    pack it was handed: accepted, in the same round, and the gate is approved. A human closure later is its own record."""
    root = setup()
    lens(root, "R-1", "logic", MAJOR)
    lens(root, "R-1", "testability", MAJOR)
    jury.collect(root, "refunds", "spec", "R-1")
    (root / ".nio/runs/R-1/jury/spec-refuter.md").write_text(CONFIRM.format(n=1))
    jury.collect(root, "refunds", "spec", "R-1")
    assert jury.check(root, "refunds", "spec", record=True)[0] == "rejected"
    fix(root, "J-1")
    lens(root, "R-2", "logic", verdicts=verdicts(J_1="fixed"))
    lens(root, "R-2", "testability", reasoning="", verdicts=verdicts(J_1="fixed"))  # invalid: no reasoning
    jury.collect(root, "refunds", "spec", "R-2")
    rnd = jury.load(root, "refunds", "spec")["round"]
    lens(root, "R-2", "testability", verdicts=verdicts(J_1="fixed"))  # the retry
    out = jury.collect(root, "refunds", "spec", "R-2")
    assert not any("INVALID" in line for line in out), out
    assert jury.load(root, "refunds", "spec")["round"] == rnd  # a retry starts no round
    outcome, lines = jury.check(root, "refunds", "spec", record=True)
    assert outcome == "approved", lines

    # a stuck juror sends the round to the human; the human's own closure in that round is still recorded
    root = setup()
    lens(root, "R-1", "logic", reasoning="")
    jury.collect(root, "refunds", "spec", "R-1")
    lens(root, "R-1", "logic", reasoning="", findings="none\nstill no reasoning")
    jury.collect(root, "refunds", "spec", "R-1")
    assert jury.check(root, "refunds", "spec", record=True)[0] == "human"
    lines = jury.check(root, "refunds", "spec", record=True, human="the juror's output is fine; tooling bug")[1]
    assert any(line.startswith("recorded") for line in lines), lines
    assert not any(line.startswith("recorded") for line in jury.check(root, "refunds", "spec", record=True)[1])  # once
    print("ok")


BOLD = """# Refunds
## Functional requirements
- **FR-1** A refund is allowed while the order is paid.
- **FR-2** A refund needs a paid order (FR-1).
- **FR-3** Returns are logged.
## Acceptance criteria
- **AC-3** (FR-2) Given a paid order, when a refund is requested, then it is refunded.
  Observable: status `refunded`.
- **AC-4** (FR-3) Given a return, then it is logged.
"""


def test_changed_and_fixcheck():
    """AC-8, AC-9, AC-14: what changed, its neighbours, and the pack a lens gets."""
    root = setup()
    spec_md = root / ".nio/specs/refunds/spec.md"
    spec_md.write_text(BOLD)
    gap = NEW_MAJOR.replace("FR-2", "FR-2", 1).replace("they must be returned first", "A refund needs a paid order")
    other = MINOR.replace("AC-1", "AC-4").replace("then it is refunded", "then it is logged")
    lens(root, "R-1", "logic", gap.replace("F3", "F1") + other)
    jury.collect(root, "refunds", "spec", "R-1")
    (root / ".nio/runs/R-1/jury/spec-refuter.md").write_text(CONFIRM.format(n=1))
    jury.collect(root, "refunds", "spec", "R-1")
    assert jury.check(root, "refunds", "spec", record=True)[0] == "rejected"
    jury.dispose(root, "refunds", "spec", "J-1", "spec-fix", "agent", "FR-2 now says what a return does")
    jury.dispose(root, "refunds", "spec", "J-2", "out-of-scope", "human", "logging is the next spec")
    spec_md.write_text(BOLD.replace("needs a paid order (FR-1).", "needs a paid order (FR-1); a return refunds it.")
                       .replace("status `refunded`.", "status `refunded`, never `pending`."))
    ids, rerun, near, secs = jury.changed(root, "refunds", "spec")  # AC-8; AC-3's Observable line counts as a change
    assert ids == ["AC-3", "FR-2"] and near == ["FR-1"] and rerun == ["logic"] and not secs, (ids, near, rerun, secs)
    spec_md.write_text(spec_md.read_text().replace("never `pending`.", "never `pending`.\n- **AC-5** (FR-2) Given a return, then it refunds."))
    assert jury.changed(root, "refunds", "spec")[2] == ["FR-1"]  # AC-5 is changed (new), not a neighbour
    pack = "\n".join(jury.fixcheck(root, "refunds", "spec", "logic"))  # AC-9, AC-14
    assert "### J-1 " in pack and '"A refund needs a paid order"' in pack and "- fix asked: add a return rule" in pack, pack
    assert "Before:\n- **FR-2** A refund needs a paid order (FR-1)." in pack and "- **FR-1** A refund is allowed" in pack, pack
    assert "After:\n- **FR-2** A refund needs a paid order (FR-1); a return refunds it." in pack, pack
    assert "Returns are logged" not in pack and "then it is logged" not in pack, pack  # unrelated items stay out
    assert "- J-2 " in pack and "out-of-scope" in pack and "### J-2" not in pack, pack  # named, no verdict asked
    lens(root, "R-2", "logic", verdicts=verdicts(J_1="fixed"))  # no verdict for J-2 is valid
    out = jury.collect(root, "refunds", "spec", "R-2")
    assert not any("INVALID" in line for line in out) and any(line.startswith("fixed   J-1") for line in out), out
    print("ok")


def test_phases():
    """AC-18: the first review runs up to the first recorded rejection, escalation rounds included."""
    root = setup()
    lens(root, "R-1", "logic", MAJOR)
    jury.collect(root, "refunds", "spec", "R-1")
    lens(root, "R-1", "logic-2", MAJOR, lens_name="logic")  # an escalation juror: round 2, still the first review
    jury.collect(root, "refunds", "spec", "R-1")
    (root / ".nio/runs/R-1/jury/spec-refuter.md").write_text(CONFIRM.format(n=1))
    jury.collect(root, "refunds", "spec", "R-1")
    led = jury.load(root, "refunds", "spec")
    assert led["round"] == 2 and jury.phase(led) == "first"
    assert jury.check(root, "refunds", "spec", record=True)[0] == "rejected"
    fix(root, "J-1")
    lens(root, "R-2", "logic", verdicts=verdicts(J_1="not fixed"))
    jury.collect(root, "refunds", "spec", "R-2")
    assert jury.phase(jury.load(root, "refunds", "spec")) == "re-review"
    outcome, lines = jury.check(root, "refunds", "spec")
    assert outcome == "human" and "- one list for the human; fix or accept each as risk: J-1" in lines, lines  # not `rejected`
    print("ok")


def test_old_ledgers():
    """AC-15, AC-28: ledgers written before #52 load, and replayed at their second round they stop there."""
    from pathlib import Path
    for name in ("grill", "grill-checks"):
        led = json.loads((Path(__file__).parent / f"fixtures/jury/{name}.json").read_text())
        root = setup()
        folder = root / ".nio/specs/refunds/jury"
        folder.mkdir(parents=True)
        (folder / "spec.json").write_text(json.dumps(led))
        assert jury.check(root, "refunds", "spec")[0] in ("approved", "rejected", "human", "rerun", "pending")  # AC-15
        # AC-28: as of round 2, every round-2 major and minor found not fixed, earlier ones fixed, no blocker open
        led.update(round=2, recorded=[[1, "rejected"]])
        led["findings"] = [f for f in led["findings"] if f["first_round"] <= 2]
        for f in led["findings"]:
            if f["first_round"] == 2 and f["status"] not in ("merged", "refuted", "dropped"):
                f.update(status="open", disposition="", validation="confirmed" if f["severity"] != "minor" else "grounded")
            elif f["status"] not in ("merged", "refuted", "dropped"):
                f["status"] = "fixed"
        outcome, reasons, listed = jury.compose(led, jury.version(led, 2))
        assert outcome == "human" and listed, (name, outcome, reasons)
    print("ok")


def test_skill_and_cards():
    """AC-16, AC-17, AC-19: the skill, the lens cards and the output format describe the fix check."""
    from pathlib import Path
    top = Path(__file__).parent.parent
    skill = (top / "skills/jury/SKILL.md").read_text()
    step6, step8 = skill.split("6. **Decide.**")[1].split("7. **Dispose**")[0], skill.split("8. **Re-review.**")[1].split("## When to stop")[0]
    assert all(p in step6 for p in ("one message", "fix", "accept as risk")), step6
    assert all(p in step8 for p in ("fix-check pack", "not fixed", "only blockers")), step8
    assert "re-run only those lenses with packs that name the changed IDs" not in skill
    for card in ("adversary", "consistency", "logic", "scope", "security", "testability"):
        text = (top / f"src/nio/agents/{card}.md").read_text()
        section = text.split("## Re-review")[1] if "## Re-review" in text else ""
        assert all(p in section for p in ("fix-check pack", "fixed or not fixed", "Stop")), card
    assert "## Verdicts" in resources.files("nio").joinpath("templates/lens-output.md").read_text()
    print("ok")


def test_implementation_review():
    """Regressions from the implementation jury of #52 (run R-261026-tqt4)."""
    led = lambda root: {f["id"]: f for f in jury.load(root, "refunds", "spec")["findings"]}
    spec_md = lambda root: root / ".nio/specs/refunds/spec.md"

    # I-1: an unchanged item that cites a changed one is its neighbour
    root = setup()
    spec_md(root).write_text(BOLD)
    lens(root, "R-1", "logic", NEW_MAJOR.replace("F3", "F1").replace("they must be returned first", "A refund needs a paid order"))
    jury.collect(root, "refunds", "spec", "R-1")
    spec_md(root).write_text(BOLD.replace("needs a paid order (FR-1).", "needs a paid order (FR-1) first."))
    assert jury.changed(root, "refunds", "spec")[2] == ["AC-3", "FR-1"]

    # I-2: in a re-review an escalation juror gets the blocker's pack, gives no verdicts, and its output is valid
    root = first_review()
    lens(root, "R-2", "logic", NEW_BLOCKER, verdicts=verdicts(J_1="fixed", J_2="fixed"))
    jury.collect(root, "refunds", "spec", "R-2")
    pack = "\n".join(jury.fixcheck(root, "refunds", "spec", "logic", blocker="J-3"))
    assert "## The blocker to judge\n### J-3 " in pack and "Give no verdicts" in pack and "## Your findings" not in pack, pack
    lens(root, "R-2", "logic-2", NEW_BLOCKER, lens_name="logic")
    out = jury.collect(root, "refunds", "spec", "R-2")
    assert not any("INVALID" in line for line in out), out

    # I-4: right after the first rejection, every lens with a fix to check re-runs, even for a minor citing nothing changed
    root = setup()
    lens(root, "R-1", "logic", MAJOR)
    lens(root, "R-1", "testability", MINOR)
    jury.collect(root, "refunds", "spec", "R-1")
    (root / ".nio/runs/R-1/jury/spec-refuter.md").write_text(CONFIRM.format(n=1))
    jury.collect(root, "refunds", "spec", "R-1")
    assert jury.check(root, "refunds", "spec", record=True)[0] == "rejected"
    fix(root, "J-1", "J-2")
    assert jury.changed(root, "refunds", "spec")[1] == ["logic", "testability"]

    # I-5: an edit after a passed final check is approved, saying no lens judged it
    root = first_review()
    to_list(root, "J-1")
    fix(root, "J-1", by="human")
    lens(root, "R-3", "logic", verdicts=verdicts(J_1="fixed"))
    jury.collect(root, "refunds", "spec", "R-3")
    assert jury.check(root, "refunds", "spec", record=True)[0] == "approved"
    spec_md(root).write_text(spec_md(root).read_text() + "- FR-5: later.\n")
    outcome, lines = jury.check(root, "refunds", "spec")
    assert outcome == "approved" and any("no lens judged that change" in line for line in lines), lines

    # I-6a: a blocker matching an earlier note leaves the note and goes to the refuter
    root = first_review()
    lens(root, "R-2", "logic", NEW_MAJOR, verdicts=verdicts(J_1="not fixed", J_2="fixed"))
    jury.collect(root, "refunds", "spec", "R-2")
    assert led(root)["J-3"]["status"] == "noted"
    lens(root, "R-2", "testability", NEW_MAJOR.replace("major", "blocker"))
    out = jury.collect(root, "refunds", "spec", "R-2")
    j3 = led(root)["J-3"]
    assert j3["status"] == "open" and j3["validation"] == "pending" and "### J-3 " in "\n".join(out), (j3, out)

    # I-6b: a `fixed` verdict can't close a finding the same output raises again as a blocker
    root = first_review()
    lens(root, "R-2", "logic", MAJOR.replace("major", "blocker"), verdicts=verdicts(J_1="fixed", J_2="fixed"))
    jury.collect(root, "refunds", "spec", "R-2")
    j1 = led(root)["J-1"]
    assert j1["status"] == "open" and j1["severity"] == "blocker" and j1["validation"] == "pending", j1

    # I-7: a confirmed major raised to blocker by a merge goes back to the refuter
    root = setup()
    lens(root, "R-1", "logic", MAJOR)
    jury.collect(root, "refunds", "spec", "R-1")
    (root / ".nio/runs/R-1/jury/spec-refuter.md").write_text(CONFIRM.format(n=1))
    jury.collect(root, "refunds", "spec", "R-1")
    lens(root, "R-1", "testability", CONTRADICTION.format(n=1))
    jury.collect(root, "refunds", "spec", "R-1")
    assert led(root)["J-1"]["validation"] == "pending" and jury.check(root, "refunds", "spec")[0] == "pending"

    # I-8: a finding that failed twice still goes on the one list when no blocker is open
    root = first_review()
    lens(root, "R-2", "logic", verdicts=verdicts(J_1="not fixed", J_2="fixed"))
    jury.collect(root, "refunds", "spec", "R-2")
    fix(root, "J-1", text="- FR-4: again.\n")  # fixed again without asking the human, so it can fail a second time
    lens(root, "R-3", "logic", verdicts=verdicts(J_1="not fixed"))
    jury.collect(root, "refunds", "spec", "R-3")
    assert led(root)["J-1"]["rounds"] == 2
    outcome, lines = jury.check(root, "refunds", "spec", record=True)
    assert outcome == "human" and "- one list for the human; fix or accept each as risk: J-1" in lines, lines
    assert jury.load(root, "refunds", "spec")["list"]["ids"] == ["J-1"]

    # FR-25 (testability F5): an escalation juror judging a later version without raising J-1 doesn't fix it
    root = first_review(CONTRADICTION.format(n=1))
    lens(root, "R-2", "logic", NEW_BLOCKER, verdicts=verdicts(J_1="not fixed"))
    jury.collect(root, "refunds", "spec", "R-2")
    lens(root, "R-2", "logic-2", lens_name="logic")
    jury.collect(root, "refunds", "spec", "R-2")
    assert led(root)["J-1"]["status"] == "open"
    print("ok")


# --- the plan gate (#57, spec 2026-10-28-plan-jury) ---

PLAN_FINDING = """### F{n} The refund contract {what}
- cites: CT-1
- kind: gap
- severity: {sev}
- evidence: observed
- quote: "{quote}"
- situation: a refund for a paid order {what}
- fix: say it in CT-1
"""


def plan_repo(risk="[]", edits=None, route="full"):
    """The checkout-refunds spec and its plan (tests/fixtures/plan), with the spec's risk flags and route set."""
    from test_plan import setup as plan_setup
    root = plan_setup(edits)
    path = spec.path(root, PSLUG)
    text = re.sub(r"^risk: .*$", f"risk: {risk}", path.read_text(), count=1, flags=re.M)
    path.write_text(re.sub(r"^route: \w+", f"route: {route}", text, count=1, flags=re.M))
    (root / ".nio/config.json").write_text(json.dumps({"memory": {"areas": ["auth", "project"]}}))
    return root


def plan_lens(root, run, name, findings="none", verdicts="", gate="plan"):
    path = root / ".nio/runs" / run / "jury" / f"{gate}-{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nlens: {name.split('-')[0] if name.endswith(('-2', '-3')) else name}\ngate: {gate}\nsubject: {PSLUG}\n"
                    f"by: \"juror / claude-code / opus\"\ncontext: sufficient\n---\n## Reasoning\nChecked every contract.\n"
                    + (f"\n## Verdicts\n{verdicts}\n" if verdicts else "") + f"\n## Findings\n{findings}\n")


def lenses_line(root, extra=()):
    lines, ok = jury.plan(root, PSLUG, "plan", extra)
    return next((line for line in lines if line.startswith("lenses: ")), ""), lines, ok


def no_state(text):
    return text.replace("- State: follows the spec's state table order\n", "")


def major(n=1, what="never says the currency", quote="Refund an order"):
    return PLAN_FINDING.format(n=n, what=what, sev="major", quote=quote)


def confirm(*ids):
    return "\n".join(f"### {i}\n- result: confirmed\n- reason: it holds\n" for i in ids)


def plan_round(root, run, findings="none", refute=(), verdicts=""):
    plan_lens(root, run, "test-proof", findings, verdicts)
    out = jury.collect(root, PSLUG, "plan", run)
    if refute:
        (root / ".nio/runs" / run / "jury/plan-refuter.md").write_text(confirm(*refute))
        out += jury.collect(root, PSLUG, "plan", run)
    return out


def change(root, outcome="pending"):
    path = records.new(root, "change", "project", "Say the refund currency")
    path.write_text(path.read_text().replace('against: ""', f'against: "{PSLUG}/spec.md"').replace("outcome: pending", f"outcome: {outcome}"))
    return path.name[:13]


def set_change(root, cid, outcome):
    path = next((root / ".nio/memory").rglob(f"{cid}-*.md"))
    path.write_text(re.sub(r"^outcome: \w+", f"outcome: {outcome}", path.read_text(), count=1, flags=re.M))


def approve_spec(root, run):
    plan_lens(root, run, "logic", gate="spec")
    jury.collect(root, PSLUG, "spec", run)
    assert jury.check(root, PSLUG, "spec", record=True)[0] == "approved"


def approve_plan(root, run="R-P1"):
    plan_round(root, run)
    assert jury.check(root, PSLUG, "plan", record=True)[0] == "approved"


def to_human(root):
    """A first review rejected for a confirmed major, fixed by the agent, found not fixed: the gate goes to the human."""
    plan_round(root, "R-P1", major(), refute=["J-1"])
    assert jury.check(root, PSLUG, "plan", record=True)[0] == "rejected"
    jury.dispose(root, PSLUG, "plan", "J-1", "plan-fix", "agent", "said the currency")
    contracts = spec.path(root, PSLUG).parent / "contracts.md"
    contracts.write_text(contracts.read_text() + "\n")
    contracts.write_text(contracts.read_text().replace("- Kind: function", "- Kind: function (in EUR)"))
    plan_round(root, "R-P2", verdicts="- J-1: not fixed — still no currency")
    outcome, lines = jury.check(root, PSLUG, "plan", record=True)
    assert outcome == "human" and "- one list for the human; fix or accept each as risk: J-1" in lines, lines


def test_ac1_it_plans_the_two_core_lenses():
    root = plan_repo(edits={"contracts.md": no_state})
    line, lines, ok = lenses_line(root)
    assert ok and line == "lenses: test-proof (core), architecture-fit (core)", lines
    assert not any("only the spec gate" in x for x in lines)


def test_ac2_no_lens_is_planned():
    root = plan_repo(edits={"tests.md": lambda t: t.replace("### TC-1 ", "### TC-91 ")})
    line, lines, ok = lenses_line(root)
    assert not ok and not line and lines[0].startswith(f"`nio check plan {PSLUG} --gate` fails (") and "errors)" in lines[0], lines


def test_ac3_the_spec_check_is_not_what_decides_it():
    root = plan_repo()
    path = spec.path(root, PSLUG)
    fr1 = next(line for line in path.read_text().splitlines() if line.startswith("- **FR-1**"))
    path.write_text(path.read_text().replace(fr1, re.sub(r"\[[^\]]*\]$", "[default]", fr1)))
    assert spec.check(root, PSLUG, gate=True)[0]  # the spec fails its gate check
    line, lines, ok = lenses_line(root)
    assert ok and line and not any("nio check spec" in x for x in lines), lines


def test_ac4_logic_runs_with_its_reason():
    assert "logic (state: CT-1)" in lenses_line(plan_repo())[0]


def test_ac5_logic_does_not_run():
    assert "logic" not in lenses_line(plan_repo(edits={"contracts.md": no_state}))[0]


def test_ac6_security_runs_with_its_reason():
    assert "security (risk: pii)" in lenses_line(plan_repo("[pii]"))[0]


def test_ac53_security_runs_with_its_reason():
    assert "security (risk: auth)" in lenses_line(plan_repo("[auth]"))[0]


def test_ac54_risk_rollback_runs_with_its_reason():
    assert "risk-rollback (risk: data-deletion)" in lenses_line(plan_repo("[data-deletion]"))[0]


def test_ac48_risk_rollback_runs_with_its_reason():
    model = "\n## Data model\n- **Refund** (spec Key entity) in `app.py` (existing) [default]\n  - amount: integer cents.\n"
    line, lines, ok = lenses_line(plan_repo(edits={"contracts.md": lambda t: t + model}))
    assert ok and "risk-rollback (data model)" in line, lines


def test_ac7_the_gate_is_blocked_naming_the_missing_card():
    root, load = plan_repo("[migration]"), agents.load
    agents.load = lambda r: {k: v for k, v in load(r).items() if k != "risk-rollback"}
    try:
        line, lines, ok = lenses_line(root)
    finally:
        agents.load = load
    assert not ok and "risk-rollback (risk: migration)" in line, lines
    assert "missing cards: risk-rollback — the gate is blocked until they exist" in lines


def test_ac8_it_is_the_plan_gate_s_own_ledger():
    root = plan_repo()
    plan_round(root, "R-P1")
    folder = jury.folder(root, PSLUG)
    assert (folder / "plan.json").exists() and (folder / "plan.md").exists() and not (folder / "spec.json").exists()


def plan_files(root):
    return [str(p.relative_to(root)) for p in jury.sources(root, PSLUG, "plan")]


def test_ac9_it_holds_all_four_plan_files():
    files = plan_files(plan_repo())
    assert all(f".nio/specs/{PSLUG}/{n}" in files for n in ("plan.md", "contracts.md", "tests.md", "quickstart.md")), files


def test_uj1_juror_files_hold_all_plan_files():
    files = plan_files(plan_repo())
    assert all(files.count(f".nio/specs/{PSLUG}/{n}") == 1 for n in ("plan.md", "contracts.md", "tests.md", "quickstart.md")), files


def test_ac44_the_first_is_kept_and_the_second_dropped():
    root = plan_repo()
    (root / "app.py").write_text("def refund_order(order_id, by):\n    return order_total(order_id)\n")
    (root / "other.py").write_text("SECRET_FALLBACK = 1\n")
    plan_round(root, "R-P1", PLAN_FINDING.format(n=1, what="calls the total", sev="minor", quote="return order_total(order_id)")
               + PLAN_FINDING.format(n=2, what="keeps a secret", sev="minor", quote="SECRET_FALLBACK = 1"))
    status = {f["title"]: f["status"] for f in jury.load(root, PSLUG, "plan")["findings"]}
    assert status == {"The refund contract calls the total": "open", "The refund contract keeps a secret": "dropped"}, status


def test_ac45_they_hold_the_plan_files_the_spec_claude():
    extra = "\n### CT-9 More (FR-1) [default]\n- Binding: `src/a.py:f` (existing)\n- Like: `src/b.py:g`\n- Kind: function\n- Shape: `f()`\n"
    root = plan_repo(edits={"contracts.md": lambda t: t + extra})
    for name in ("src/a.py", "src/b.py", "CLAUDE.md"):
        (root / name).parent.mkdir(exist_ok=True)
        (root / name).write_text("def f(): pass\ndef g(): pass\n")
    want = {f".nio/specs/{PSLUG}/{n}" for n in ("plan.md", "contracts.md", "tests.md", "quickstart.md", "spec.md")}
    want |= {"CLAUDE.md", "app.py", "src/a.py", "src/b.py"}  # app.py: the fixture's contracts bind it
    assert set(plan_files(root)) == want, plan_files(root)
    (root / f".nio/specs/{PSLUG}/architecture.md").write_text("# Architecture\n")
    assert set(plan_files(root)) == want | {f".nio/specs/{PSLUG}/architecture.md"}


def test_ac10_it_is_invalid_as_at_the_spec_gate():
    root = plan_repo()
    six = "".join(PLAN_FINDING.format(n=n, what=f"misses point {n}", sev="minor", quote="Refund an order") for n in range(1, 7))
    out = plan_round(root, "R-P1", six)
    assert any("6 findings; a lens returns at most 5" in line for line in out), out


def test_ac33_the_ledger_records_it():
    root = plan_repo()
    plan_round(root, "R-P1", major(), refute=["J-1"])
    jury.dispose(root, PSLUG, "plan", "J-1", "plan-fix", "agent", "said the currency")
    f = jury.load(root, PSLUG, "plan")["findings"][0]
    assert (f["status"], f["disposition"]) == ("disposed", "plan-fix"), f


def test_ac34_the_disposition_is_refused():
    root = plan_repo()
    plan_lens(root, "R-S1", "logic", PLAN_FINDING.format(n=1, what="x", sev="minor", quote="Refunds").replace("CT-1", "FR-1"), gate="spec")
    jury.collect(root, PSLUG, "spec", "R-S1")
    try:
        jury.dispose(root, PSLUG, "spec", "J-1", "plan-fix", "agent", "x")
        raise AssertionError("plan-fix was taken at the spec gate")
    except ValueError as e:
        assert "`plan-fix` belongs to the plan gate" in str(e), e


def spec_rooted(root, *ids, cid=None):
    cid = cid or change(root)
    for i in ids:
        jury.dispose(root, PSLUG, "plan", i, "spec-change", "human", "the spec never says the currency", cid)
    return cid


def test_ac35_a_change_request_on_the_spec_is_written():
    root = plan_repo()
    plan_round(root, "R-P1", major(3, what="has no limit"), refute=["J-1"])
    cid = spec_rooted(root, "J-1")
    st, why = jury.state(root, PSLUG)
    assert st == "waiting-on-spec" and cid in why and "J-1" in why, (st, why)
    plan_lens(root, "R-P2", "architecture-fit")
    try:
        jury.collect(root, PSLUG, "plan", "R-P2")
        raise AssertionError("a plan round was collected while the plan jury waits on the spec")
    except ValueError as e:
        assert "paused until the spec change is settled" in str(e), e


def test_ac43_the_ledger_records_it_with_its_change_re():
    root = plan_repo()
    plan_round(root, "R-P1", major(), refute=["J-1"])
    cid = spec_rooted(root, "J-1")
    f = jury.load(root, PSLUG, "plan")["findings"][0]
    assert f["disposition"] == "spec-change" and f["note"].startswith(cid), f


def test_ac37_the_plan_does_not_state_its_own_limit_fo():
    root = plan_repo()
    folder = spec.path(root, PSLUG).parent
    before = {n: (folder / n).read_text() for n in ("plan.md", "contracts.md", "tests.md", "quickstart.md")}
    plan_round(root, "R-P1", major(what="leaves the refund limit unstated"), refute=["J-1"])
    spec_rooted(root, "J-1")
    f = jury.load(root, PSLUG, "plan")["findings"][0]
    assert f["disposition"] == "spec-change" and f["disposition"] != "plan-fix"
    assert before == {n: (folder / n).read_text() for n in before}  # the plan gains no limit while the spec is open


def test_ac36_only_fr_4_and_the_items_around_it_are_in():
    root = plan_repo()
    approve_spec(root, "R-S1")
    plan_round(root, "R-P1", major(), refute=["J-1"])
    cid = spec_rooted(root, "J-1")
    path = spec.path(root, PSLUG)
    fr1 = next(line for line in path.read_text().splitlines() if line.startswith("- **FR-1**"))
    path.write_text(path.read_text().replace(fr1, fr1.replace("SHALL", "SHALL, in the order's currency,")))
    ids, _, _, _ = jury.changed(root, PSLUG, "spec")
    assert ids == ["FR-1"], ids  # the spec jury's fix check gets the changed item only, and its neighbours
    pack = "\n".join(jury.fixcheck(root, PSLUG, "spec", "logic"))
    assert "### FR-1" in pack and "### FR-2\n" not in pack
    set_change(root, cid, "accepted")
    assert jury.changed(root, PSLUG, "spec")[1] == ["logic"]  # the approved spec gate re-checks the change (FR-35)
    assert jury.state(root, PSLUG)[0] == "waiting-on-spec"  # accepted, but not re-approved yet
    approve_spec(root, "R-S2")
    assert jury.state(root, PSLUG)[0] == "open"
    assert jury.pack_ids(jury.load(root, PSLUG, "plan"), "test-proof") == ["J-1"]  # its lens checks the spec change fixed it
    plan_round(root, "R-P2")  # the plan jury resumes


def test_ac38_it_tells_the_juror_not_to_raise_j_2_agai():
    root = plan_repo()
    plan_round(root, "R-P1", major() + major(2, what="never says who refunds", quote="Refund over HTTP"), refute=["J-1", "J-2"])
    jury.dispose(root, PSLUG, "plan", "J-2", "accepted-risk", "human", "who refunds is fine as is")
    contracts = spec.path(root, PSLUG).parent / "contracts.md"
    contracts.write_text(contracts.read_text() + "\n<!-- edited -->\n")
    pack = "\n".join(jury.fixcheck(root, PSLUG, "plan", "test-proof"))
    settled = pack.split("## Settled by the human: don't raise these again")[1].split("##")[0]
    assert "J-2" in settled and "J-1" not in settled, pack


def test_ac51_j_1_goes_to_the_refuter_before_any_outco():
    root = plan_repo()
    out = plan_round(root, "R-P1", major())
    assert any(line.startswith("## Refuter batch") for line in out) and "### J-1 The refund contract never says the currency" in out, out
    assert jury.check(root, PSLUG, "plan")[0] == "pending"


def test_ac52_no_new_round_is_asked_for_and_the_majors():
    root = plan_repo()
    to_human(root)  # asserts the outcome `human` and the one list
    assert jury.check(root, PSLUG, "plan")[0] != "rerun"


def test_ac59_it_is_refused_and_the_tasks_stage_refuse():
    root = plan_repo()
    to_human(root)
    plan_lens(root, "R-P3", "architecture-fit")
    try:
        jury.collect(root, PSLUG, "plan", "R-P3")
        raise AssertionError("a round was collected while the gate waits on the human")
    except ValueError as e:
        assert "waits on the human's ruling" in str(e), e
    ok, why = plan.approved(root, PSLUG)
    assert not ok and why.startswith("the plan must be approved first (with-human"), why


def test_ac42_it_proceeds_given_a_plan_gate_handed_to():
    root = plan_repo()
    to_human(root)
    assert not plan.approved(root, PSLUG)[0]
    jury.check(root, PSLUG, "plan", record=True, human="the currency is in the spec's glossary")
    assert plan.approved(root, PSLUG)[0] and jury.state(root, PSLUG)[0] == "closed-by-human"


def test_ac39_one_nio_approve_plan_commit_holds_the_pl():
    root = plan_repo()
    approve_plan(root)
    verdicts = [p for p in (root / ".nio/memory").rglob("V-*.md") if f'"plan:{PSLUG}"' in p.read_text()]
    assert len(verdicts) == 1, verdicts
    folder = spec.path(root, PSLUG).parent
    git = lambda *a: subprocess.run(["git", *a], cwd=root, check=True, capture_output=True, text=True).stdout
    git("add", *[str(folder / n) for n in ("plan.md", "contracts.md", "tests.md", "quickstart.md")], str(verdicts[0]))
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "nio: approve plan")
    touched = git("show", "--name-only", "--format=%s", "HEAD").split()
    assert touched[:3] == ["nio:", "approve", "plan"] and str(verdicts[0].relative_to(root)) in touched, touched
    assert all(f".nio/specs/{PSLUG}/{n}" in touched for n in ("plan.md", "contracts.md", "tests.md", "quickstart.md")), touched


def test_ac56_the_plan_gate_is_no_longer_approved_and():
    root = plan_repo()
    approve_plan(root)
    assert plan.approved(root, PSLUG)[0]
    path = spec.path(root, PSLUG)
    fr1 = next(line for line in path.read_text().splitlines() if line.startswith("- **FR-1**"))
    path.write_text(path.read_text().replace(fr1, fr1.replace("SHALL", "SHALL, in the order's currency,")))
    ok, why = plan.approved(root, PSLUG)
    assert not ok and why.startswith("the plan must be approved first"), why
    pack = "\n".join(jury.fixcheck(root, PSLUG, "plan", "architecture-fit"))
    assert "### FR-1" in pack and "### CT-1" in pack.split("## Neighbours")[1], pack


def test_ac57_j_6_joins_c_1():
    root = plan_repo()
    plan_round(root, "R-P1", major() + major(2, what="never says who refunds", quote="Refund over HTTP"), refute=["J-1", "J-2"])
    cid = spec_rooted(root, "J-1")
    spec_rooted(root, "J-2", cid=cid)
    notes = [f["note"] for f in jury.load(root, PSLUG, "plan")["findings"]]
    assert all(n.startswith(cid) for n in notes) and len(list((root / ".nio/memory").rglob("C-*.md"))) == 1
    assert jury.state(root, PSLUG)[0] == "waiting-on-spec"


def test_ac58_the_plan_jury_resumes_and_j_3_is_open_ag():
    root = plan_repo()
    plan_round(root, "R-P1", major(), refute=["J-1"])
    cid = spec_rooted(root, "J-1")
    set_change(root, cid, "rejected")
    outcome, lines = jury.check(root, PSLUG, "plan")
    assert f"reopened J-1: {cid} was dropped" in lines and not any("paused" in x for x in lines), lines
    f = jury.load(root, PSLUG, "plan")["findings"][0]
    assert f["status"] == "open" and "fix it in the plan or accept the risk" in f["note"], f


def test_uj2_spec_change_blocks_plan_fix():
    root = plan_repo()
    plan_round(root, "R-P1", major(), refute=["J-1"])
    cid = spec_rooted(root, "J-1")
    try:
        jury.dispose(root, PSLUG, "plan", "J-1", "plan-fix", "agent", "filled the limit in the plan")
        raise AssertionError("a spec-rooted finding took a plan-fix")
    except ValueError as e:
        assert f"J-1 is disposed and waits on {cid}" in str(e), e
    assert jury.load(root, PSLUG, "plan")["findings"][0]["disposition"] == "spec-change"


def test_uj1_plan_gate_needs_lens_outputs():
    root = plan_repo()
    outcome, lines = jury.check(root, PSLUG, "plan", record=True)
    assert outcome == "rerun" and "- no lens output has been collected yet: run the lenses" in lines, lines
    assert not list((root / ".nio/memory").rglob("V-*.md"))


def test_nfr1_plan_gate_makes_no_model_call():
    root, calls, run = plan_repo(), [], subprocess.run
    subprocess.run = lambda args, *a, **k: calls.append(args) or run(args, *a, **k)
    try:
        assert jury.plan(root, PSLUG, "plan")[1] and plan.check(root, PSLUG, gate=True)[0] == []
    finally:
        subprocess.run = run
    assert all(c[0] == "git" for c in calls), calls


def test_escaped_quotes_ground():
    """A juror that escapes the marks inside a quote is grounded on the artefact's bare text."""
    assert jury.unquote('"said \\"no\\""') == 'said "no"'
    assert jury.unquote('"+ \\"\\\\n\\")"') == '+ "\\n")'
    assert jury.unquote('plain') == 'plain'
    assert jury.grounded({"cites": ["FR-1"], "quotes": [jury.unquote('"said \\"no\\" twice"')]}, '- FR-1: it said "no" twice.')
    print("ok")



def test_ac41_it_plans_executability_as_the_core_lens():
    from test_tasks import repo
    root = repo()
    path = spec.path(root, PSLUG)
    path.write_text(re.sub(r"^risk: .*$", "risk: [auth, money]", path.read_text(), count=1, flags=re.M))
    lines, ok = jury.plan(root, PSLUG, "tasks")
    assert ok and lines[1] == "lenses: executability (core)", lines
    print("ok")


def test_ac38_it_sits_next_to_the_spec_gate_s_ledger_n():
    """FR-31: pins what already holds; collecting implementation-E-n rounds is #29's."""
    root = plan_repo()
    led = jury.load(root, PSLUG, "implementation-E-2")
    led["round"] = 1
    jury.save(root, led)
    path = jury.verdict(root, led, "approved", [])
    folder = jury.folder(root, PSLUG)
    assert (folder / "implementation-E-2.json").exists() and (folder / "implementation-E-2.md").exists()
    assert f'subject: "implementation-E-2:{PSLUG}"' in path.read_text()
    print("ok")


if __name__ == "__main__":
    test_review_scenarios()
    test_plan_gate_versions()
    test_needs_more_doesnt_fix()
    test_cli_dispose_order()
    test_escalation_is_not_a_fix()
    test_answers_for_scope()
    test_plan_and_changed()
    test_deferred_points_need_the_human()
    test_format_template_parses()
    test_gate()
    test_persisting_finding_goes_to_the_human()
    test_majority_overrules_one_juror()
    test_versions_decide_fixed()
    test_stop_rule()
    test_final_check()
    test_fix_verdicts()
    test_retry_after_another_lens_fixed_a_shared_finding()
    test_final_check_sees_cites_and_human_overrules()
    test_changed_and_fixcheck()
    test_phases()
    test_old_ledgers()
    test_skill_and_cards()
    test_implementation_review()
    test_ac1_it_plans_the_two_core_lenses()
    test_ac2_no_lens_is_planned()
    test_ac3_the_spec_check_is_not_what_decides_it()
    test_ac4_logic_runs_with_its_reason()
    test_ac5_logic_does_not_run()
    test_ac6_security_runs_with_its_reason()
    test_ac53_security_runs_with_its_reason()
    test_ac54_risk_rollback_runs_with_its_reason()
    test_ac48_risk_rollback_runs_with_its_reason()
    test_ac7_the_gate_is_blocked_naming_the_missing_card()
    test_ac8_it_is_the_plan_gate_s_own_ledger()
    test_ac9_it_holds_all_four_plan_files()
    test_uj1_juror_files_hold_all_plan_files()
    test_ac44_the_first_is_kept_and_the_second_dropped()
    test_ac45_they_hold_the_plan_files_the_spec_claude()
    test_ac10_it_is_invalid_as_at_the_spec_gate()
    test_ac33_the_ledger_records_it()
    test_ac34_the_disposition_is_refused()
    test_ac35_a_change_request_on_the_spec_is_written()
    test_ac43_the_ledger_records_it_with_its_change_re()
    test_ac37_the_plan_does_not_state_its_own_limit_fo()
    test_ac36_only_fr_4_and_the_items_around_it_are_in()
    test_ac38_it_tells_the_juror_not_to_raise_j_2_agai()
    test_ac51_j_1_goes_to_the_refuter_before_any_outco()
    test_ac52_no_new_round_is_asked_for_and_the_majors()
    test_ac59_it_is_refused_and_the_tasks_stage_refuse()
    test_ac42_it_proceeds_given_a_plan_gate_handed_to()
    test_ac39_one_nio_approve_plan_commit_holds_the_pl()
    test_ac56_the_plan_gate_is_no_longer_approved_and()
    test_ac57_j_6_joins_c_1()
    test_ac58_the_plan_jury_resumes_and_j_3_is_open_ag()
    test_uj2_spec_change_blocks_plan_fix()
    test_uj1_plan_gate_needs_lens_outputs()
    test_nfr1_plan_gate_makes_no_model_call()
    test_escaped_quotes_ground()
    test_ac41_it_plans_executability_as_the_core_lens()
    test_ac38_it_sits_next_to_the_spec_gate_s_ledger_n()
