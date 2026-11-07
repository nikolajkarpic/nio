"""Self-check for nio new spec / nio check spec. Run: uv run python tests/test_spec.py"""
import subprocess
from pathlib import Path

from test_records import repo

from nio import spec
import selfcheck

FIXTURES = Path(__file__).parent / "fixtures/spec"
SLUGS = {"spec.md": "checkout-refunds", "spec-epic.md": "checkout", "spec-bugfix.md": "refund-double-charge"}


def put(root, name, edit=lambda t: t):
    slug = SLUGS[name]
    p = spec.path(root, slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(edit((FIXTURES / name).read_text()))
    return slug


def errors(root, slug, gate=False):
    return spec.check(root, slug, gate)[0]


def has(errs, text):
    assert any(text in e for e in errs), (text, errs)


def test_examples_pass():
    root = repo()
    for name in SLUGS:
        slug = put(root, name)
        assert errors(root, slug) == [], (name, errors(root, slug))
    # the slice example still has an open point and a [default]: fine while drafting, not at the gate
    has(errors(root, "checkout-refunds", gate=True), "Open points")
    has(errors(root, "checkout-refunds", gate=True), "`- Refunds to a different payment method. [default]` is still [default]")
    assert errors(root, "refund-double-charge", gate=True) == []
    # Decisions can wait for the grill, but not past the gate
    put(root, "spec.md", lambda t: t.split("## Decisions")[0] + "## Open points" + t.split("## Open points")[1])
    assert errors(root, "checkout-refunds") == [], errors(root, "checkout-refunds")
    has(errors(root, "checkout-refunds", gate=True), "`## Decisions` is missing")
    put(root, "spec.md")
    assert spec.check(root, "checkout-refunds")[1] == ["lenses: testability, logic, adversary"]
    print("ok")


def test_templates_need_filling():
    root = repo()
    for route in spec.ROUTES:
        p = spec.new(root, f"new-{route}", route, today="2026-10-26")
        assert p == spec.path(root, f"2026-10-26-new-{route}"), p
        has(errors(root, f"2026-10-26-new-{route}"), "<placeholders>")
    # TC-6: a new lite spec is built from the bugfix template, which has the four bugfix sections
    template = Path(spec.__file__).parent.joinpath("templates/spec-bugfix.md").read_text()
    for heading in ("## Current behaviour", "## Expected behaviour", "## Unchanged behaviour", "## Acceptance criteria"):
        assert heading in template, heading
    try:
        spec.new(root, "new-full", today="2026-10-27")  # same name another day is still a duplicate
        raise AssertionError("overwrote an existing spec")
    except ValueError:
        pass
    print("ok")


def test_lite_unchanged_required():
    """TC-7: a bugfix spec with an empty unchanged-behaviour section, or an unchanged item with no AC, fails the check."""
    root = repo()
    slug = put(root, "spec-bugfix.md")
    assert errors(root, slug) == [], errors(root, slug)
    unchanged = "- **UB-1** WHEN a customer requests one refund on a paid order THE SYSTEM SHALL CONTINUE TO refund the full amount. [human]\n"
    slug = put(root, "spec-bugfix.md", lambda t: t.replace(unchanged, ""))
    has(errors(root, slug), "section `## Unchanged behaviour` is missing or empty")
    ac2 = "- **AC-2** (UB-1) Given a paid order, when one refund request arrives, then it is refunded in full. [human]\n  Observable: order state `refunded`, amount equals total. Level: integration.\n"
    slug = put(root, "spec-bugfix.md", lambda t: t.replace(ac2, ""))
    has(errors(root, slug), "UB-1 has no AC")
    print("ok")


def test_broken_specs():
    root = repo()
    cases = [
        (lambda t: t.replace("  Observable: order state is `refunded`; refund amount equals the order total. Level: integration.\n", ""),
         ["AC-1: needs `Observable:`", "AC-1: needs `Level:`"]),
        (lambda t: t.replace("**AC-2** (FR-2)", "**AC-2** (FR-9)"), ["AC-2 cites FR-9", "FR-2 has no AC"]),
        (lambda t: t.replace("refund the full order amount. [human]", "refund the full order amount."), ["FR-1: its line must end"]),
        (lambda t: t.replace("THE SYSTEM SHALL refund the full", "the system refunds the full"), ["FR-1: state it with SHALL"]),
        (lambda t: t.replace("| shipped | ignore |", "| shipped |  |"), ["shipped × ship must be"]),
        (lambda t: t.replace("final: shipped, refunded", "final: refunded"), ["`shipped` has no way out"]),
        (lambda t: t.replace("| returned | some | returned items only | [human] |\n", ""), ["gap, no row covers order state=returned, items returned=some"]),
        (lambda t: t.replace("| paid | - | full | [human] |", "| paid | - | full | [human] |\n| paid | all | full | [human] |"), ["overlap, 2 rows match"]),
        (lambda t: t.replace("(P1) [human]", "[human]"), ["US-1: the heading needs a priority"]),
        (lambda t: t.replace("risk: [money, external-input]", "risk: [money, crypto]"), ["`risk` must be a list"]),
        (lambda t: t.replace("## Glossary", "## Notes"), ["`## Notes` is not part of a full spec"]),
        (lambda t: t.replace("- Marketplace", "N/A\n- Marketplace").replace(
            "## Key entities\n- **Refund**: amount, order, created at, by (customer or support). [human]", "## Key entities\nN/A"), ["Key entities` says N/A"]),
        (lambda t: t.replace("- **NFR-1**", "- **CB-1**"), ["`CB` IDs don't belong in a full spec"]),
        (lambda t: t.replace("## Non-goals\n", "## Non-goals\n- Gift cards.\n"), ["non-goal `Gift cards.…` must end"]),
        (lambda t: t.replace("(decision; FR-1)", "(guess; FR-1)"), ["OP-1: write it as"]),
        (lambda t: t.replace("(decision; FR-1)", "(fact; FR-7)"), ["OP-1: its target `FR-7`"]),
        # a bolded memory record ID in Decisions is not a spec item
        (lambda t: t.replace("D-261025-k2m4", "**D-261025-k2m4**").replace("- **NFR-1**", "- **CB-1**"), ["`CB` IDs"]),
    ]
    for edit, wanted in cases:
        slug = put(root, "spec.md", edit)
        errs = errors(root, slug)
        assert not any("`D` IDs" in e for e in errs), errs
        for w in wanted:
            has(errs, w)
    slug = put(root, "spec-bugfix.md", lambda t: t.replace(
        "- **UB-1** WHEN a customer requests one refund on a paid order THE SYSTEM SHALL CONTINUE TO refund the full amount. [human]\n", ""))
    has(errors(root, slug), "`## Unchanged behaviour` is missing or empty")
    has(errors(root, slug), "AC-2 cites UB-1, which isn't defined")
    # an open point may target a section that isn't written yet
    slug = put(root, "spec.md", lambda t: t.replace("(decision; FR-1)", "(decision; Glossary)").replace(
        "## Glossary\n- **Refund**: money returned to the original payment method. Never \"reimbursement\" or \"chargeback\".\n\n", ""))
    assert "## Glossary" not in spec.path(root, slug).read_text() and errors(root, slug) == [], errors(root, slug)
    print("ok")


def test_ids_are_permanent():
    root = repo()
    git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=root, capture_output=True)
    slug = put(root, "spec.md")
    git("add", "-A")
    git("commit", "-qm", "spec")
    gone = lambda t: t.replace("- **NFR-1** THE SYSTEM SHALL confirm a refund request within 2 s at the 95th percentile. [human]\n", "")
    put(root, "spec.md", gone)
    has(errors(root, slug), "NFR-1 was removed without being retired")
    put(root, "spec.md", lambda t: gone(t).replace("retired: []", "retired: [NFR-1]"))
    assert errors(root, slug) == [], errors(root, slug)
    git("commit", "-qam", "retire NFR-1")
    put(root, "spec.md", lambda t: t.replace("retired: []", "retired: [NFR-1]"))
    has(errors(root, slug), "NFR-1 is retired and can't be used again")
    # renumbering: FR-2's text moves to FR-3 and FR-2 is retired to make room
    put(root, "spec.md", lambda t: gone(t).replace("retired: []", "retired: [NFR-1, FR-2]").replace("**FR-2**", "**FR-3**").replace("(FR-2)", "(FR-3)"))
    has(errors(root, slug), "FR-3 now has FR-2's text")
    print("ok")


def test_edge_cases():
    root = repo()
    # guidance comments neither count as a [default] at the gate nor fill a section
    slug = put(root, "spec-bugfix.md", lambda t: t.replace("# Double refund", "<!-- tag items [human] or [default] -->\n# Double refund"))
    assert errors(root, slug, gate=True) == [], errors(root, slug, gate=True)
    slug = put(root, "spec.md", lambda t: t.replace("- Full refunds only for paid orders: D-261025-k2m4 (grill, 2026-10-25).",
                                                    "<!-- the grill fills this -->"))
    has(errors(root, slug, gate=True), "`## Decisions` is missing or empty")
    cases = [
        (lambda t: t.replace("retired: []", 'retired: "FR-12"'), "`retired` must be a list of IDs"),
        (lambda t: t.replace("route: full", "route: [full]"), "`route` must be one of"),
        (lambda t: t.replace("risk: [money, external-input]", "risk: [{money: yes}]"), "`risk` must be a list"),
        (lambda t: t.replace("| shipped | ignore |", "| paid | → shipped | → refunded | [human] |\n| shipped | ignore |"), "`paid` has more than one row"),
    ]
    for edit, wanted in cases:
        has(errors(root, put(root, "spec.md", edit)), wanted)
    # a placeholder-looking word inside a code span is content
    slug = put(root, "spec.md", lambda t: t.replace("refund the full order amount. [human]", "refund the full order amount via `refund <order>`. [human]"))
    assert errors(root, slug) == [], errors(root, slug)
    # a synonym the glossary bans can't appear elsewhere, even when the glossary entry wraps
    slug = put(root, "spec.md", lambda t: t.replace("the customer requests a refund again", "the customer asks for a reimbursement again"))
    has(errors(root, slug), "says \"reimbursement\"; the glossary says Refund")
    slug = put(root, "spec.md", lambda t: t.replace('Never "reimbursement" or "chargeback".', 'Never "reimbursement" or\n  "chargeback".').replace(
        "the customer requests a refund again", "the customer files a chargeback again"))
    has(errors(root, slug), "says \"chargeback\"")
    slug = put(root, "spec.md", lambda t: t.replace("(grill, 2026-10-25).", "(grill, 2026-10-25); renamed from reimbursement."))
    assert errors(root, slug) == [], errors(root, slug)  # Decisions may record a rename
    # the term's own uses don't trip a banned word inside it, but a banned phrase containing the term still does
    glossary = lambda entry, line: spec.check_glossary({"Glossary": [entry], "Scope": [line]})
    assert not glossary('- **Refund request**: x. Never "request".', "A Refund request is sent.")
    assert glossary('- **Refund**: x. Never "refund request".', "A refund request is sent.")
    assert not glossary('- **Run**: x. Never "re".', "We rerun it.")
    two = lambda line: spec.check_glossary({"Glossary": ['- **Order**: x. Never "purchase".', "- **Purchase order**: y."], "Scope": [line]})
    assert not two("Send the Purchase order.") and two("Send the purchase.")  # another term holding the word is vocabulary too
    # an item outside its home section
    slug = put(root, "spec.md", lambda t: t.replace("- **FR-2** IF the order", "- **NFR-9** placeholder-free line. [human]\n- **FR-2** IF the order").replace(
        "## Non-functional requirements\n", "## Non-functional requirements\n- **FR-9** WHEN x THE SYSTEM SHALL y. [human]\n"))
    has(errors(root, slug), "FR-9 is under `## Non-functional requirements`; FR items belong in `## Functional requirements`")
    has(errors(root, slug), "NFR-9 is under `## Functional requirements`")
    # a wrapped non-goal carries its tag on its last line
    slug = put(root, "spec.md", lambda t: t.replace("- Refunds to a different payment method. [default]", "- Refunds to a different\n  payment method. [default]"))
    assert errors(root, slug) == [], errors(root, slug)
    # a table row's Src cell counts
    slug = put(root, "spec.md", lambda t: t.replace("| paid | → shipped | → refunded | [human] |", "| paid | → shipped | → refunded | [default] |"))
    has(errors(root, slug, gate=True), "`| paid | → shipped | → refunded | [default] |` is still [default]")
    # prose that mentions the tag is not an unsettled item
    slug = put(root, "spec-bugfix.md", lambda t: t.replace("Repro: open", "Repro (no `[default]` here): open"))
    assert errors(root, slug, gate=True) == [], errors(root, slug, gate=True)
    # the values are in the last parentheses of a condition header
    slug = put(root, "spec.md", lambda t: t.replace("items returned (all, some)", "items returned (count) (all, some)"))
    assert errors(root, slug) == [], errors(root, slug)
    try:
        spec.new(root, "x", epic='a"b')
        raise AssertionError("a malformed --epic was accepted")
    except ValueError:
        pass
    print("ok")


def test_grill_provenance():
    """What the grill writes: agent calls, derived items and deferred points pass the gate and are listed for the human."""
    root = repo()
    settled = lambda t: t.replace("[default]", "[agent]").replace(
        "- **OP-1** (decision; FR-1) Can support refund an order after 30 days?\n", "").replace("retired: []", "retired: [OP-1]")
    deferred = "\n## Deferred\n- **DF-1** (from OP-1) Can support refund an order after 30 days? Deferred: the human ended early.\n"
    slug = put(root, "spec.md", lambda t: settled(t).replace("refund the full order amount. [human]", "refund the full order amount. [agent]").replace(
        "then it is rejected. [human]", "then it is rejected. [derived: FR-2]") + deferred)
    errs, notes = spec.check(root, slug, gate=True)
    assert errs == [], errs
    assert "agent calls: FR-1, 1 line without an ID" in notes and "derived: AC-2" in notes and "deferred points: DF-1" in notes, notes
    cases = [
        (lambda t: settled(t).replace("then it is rejected. [human]", "then it is rejected. [derived: FR-9]"), "derived from FR-9, which isn't defined"),
        (lambda t: settled(t).replace("refund the full order amount. [human]", "refund the full order amount. [derived: FR-2]").replace(
            "the refund request. [human]", "the refund request. [derived: AC-1]"), "derived from FR-2, which is derived: AC-1"),
        (lambda t: settled(t).replace("retired: [OP-1]", "retired: []") + deferred, "comes from OP-1, which must move to `retired:`"),
        (lambda t: settled(t) + "\n## Deferred\n- **DF-2** (from FR-2; contradiction) FR-2 and FR-1 disagree.\n", "whose line must end with [deferred: DF-2]"),
        (lambda t: settled(t).replace("the refund request. [human]", "the refund request. [deferred: DF-3]"), "points at DF-3"),
        # an unknown tag, a missing one, or an empty argument is no provenance
        (lambda t: settled(t).replace("the refund request. [human]", "the refund request. [guess]"), "its line must end with [human]"),
        (lambda t: settled(t).replace("the refund request. [human]", "the refund request."), "its line must end with [human]"),
        (lambda t: settled(t).replace("the refund request. [human]", "the refund request. [research: ]"), "its line must end with [human]"),
        # a table row's Src is checked too, and a proposal can't be a source
        (lambda t: settled(t).replace("| paid | - | full | [human] |", "| paid | - | full | [derived: FR-9] |"), "is derived from FR-9, which isn't defined"),
        (lambda t: t.replace("then it is rejected. [human]", "then it is rejected. [derived: FR-1]").replace(
            "refund the full order amount. [human]", "refund the full order amount. [default]"), "is derived from FR-1, which is default"),
    ]
    for edit, wanted in cases:
        has(errors(root, put(root, "spec.md", edit)), wanted)
    # a research finding as a source must be in research.md, next to the spec
    edit = lambda t: settled(t).replace("then it is rejected. [human]", "then it is rejected. [derived: RF-1]")
    has(errors(root, put(root, "spec.md", edit)), "derived from RF-1, which isn't in research.md")
    (spec.path(root, slug).parent / "research.md").write_text("# Research\n\n- **RF-1** A fact. Source: x\n")
    assert errors(root, put(root, "spec.md", edit)) == [], errors(root, put(root, "spec.md", edit))
    # a line without an ID is deferred from its section
    slug = put(root, "spec.md", lambda t: settled(t).replace("| paid | - | full | [human] |", "| paid | - | full | [deferred: DF-4] |")
               + "\n## Deferred\n- **DF-4** (from Rules) Is a paid order refunded in full?\n")
    assert errors(root, slug, gate=True) == [], errors(root, slug, gate=True)
    has(errors(root, put(root, "spec.md", lambda t: settled(t) + "\n## Deferred\n- **DF-5** (from Somewhere) x\n")), "comes from `Somewhere`")
    # an item deferred with a contradiction, pointing both ways
    slug = put(root, "spec.md", lambda t: settled(t).replace("the refund request. [human]", "the refund request. [deferred: DF-2]")
               + "\n## Deferred\n- **DF-2** (from FR-2; contradiction) FR-2 and the state table disagree on refunded orders.\n")
    errs, notes = spec.check(root, slug, gate=True)
    assert errs == [] and "deferred points: DF-2 (contradiction)" in notes, (errs, notes)
    print("ok")


def test_secrets_flag_brings_in_security():
    root = repo()
    slug = put(root, "spec.md", lambda t: t.replace("risk: [money, external-input]", "risk: [secrets]"))
    errs, notes = spec.check(root, slug)
    assert errs == [], errs
    assert notes == ["lenses: testability, logic, security"], notes
    print("ok")


if __name__ == "__main__":
    selfcheck.main([test_lite_unchanged_required, test_secrets_flag_brings_in_security, test_grill_provenance, test_edge_cases, test_examples_pass, test_templates_need_filling, test_broken_specs, test_ids_are_permanent])
