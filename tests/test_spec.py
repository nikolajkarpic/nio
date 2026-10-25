"""Self-check for nio new spec / nio check spec. Run: uv run python tests/test_spec.py"""
import subprocess
from pathlib import Path

from test_records import repo

from nio import spec

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
        spec.new(root, f"new-{route}", route)
        has(errors(root, f"new-{route}"), "<placeholders>")
    try:
        spec.new(root, "new-full")
        raise AssertionError("overwrote an existing spec")
    except ValueError:
        pass
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
    # the values are in the last parentheses of a condition header
    slug = put(root, "spec.md", lambda t: t.replace("items returned (all, some)", "items returned (count) (all, some)"))
    assert errors(root, slug) == [], errors(root, slug)
    try:
        spec.new(root, "x", epic='a"b')
        raise AssertionError("a malformed --epic was accepted")
    except ValueError:
        pass
    print("ok")


if __name__ == "__main__":
    test_edge_cases()
    test_examples_pass()
    test_templates_need_filling()
    test_broken_specs()
    test_ids_are_permanent()
