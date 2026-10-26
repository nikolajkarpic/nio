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
    assert jury.changed(root, "refund-double-charge", "spec") == (["EB-1"], ["logic"])
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
