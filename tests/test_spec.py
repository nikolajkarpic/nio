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
    has(errors(root, "checkout-refunds", gate=True), "OP-1: Can sup` is still [default]")
    assert errors(root, "refund-double-charge", gate=True) == []
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


if __name__ == "__main__":
    test_examples_pass()
    test_templates_need_filling()
    test_broken_specs()
    test_ids_are_permanent()
