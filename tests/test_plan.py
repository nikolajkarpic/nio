"""Self-check for nio new plan / nio check plan. Run: uv run python tests/test_plan.py"""
import re
import subprocess
from pathlib import Path

from test_records import repo
from test_spec import has, put

from nio import plan, spec

FIXTURES = Path(__file__).parent / "fixtures/plan"
SLUG = "checkout-refunds"


def setup(edits=None):
    """A repo with the refunds spec and its plan; `edits` maps a plan file to a function over its text."""
    root = repo()
    put(root, "spec.md")
    for f in plan.FILES:
        text = (FIXTURES / f).read_text()
        (spec.path(root, SLUG).parent / f).write_text((edits or {}).get(f, lambda t: t)(text))
    (spec.path(root, SLUG).parent / "research.md").write_text(
        '- **RF-5** The payments client retries without a key. Source: app.py:1: "retry()"\n')
    return root


def errors(root, gate=False):
    return plan.check(root, SLUG, gate)[0]


def test_example_passes():
    root = setup()
    assert errors(root) == [], errors(root)
    assert errors(root, gate=True) == []
    assert plan.check(root, SLUG)[1] == ["proposals for the plan jury: CT-2, TC-1, TC-2, TC-3, QS-1"], plan.check(root, SLUG)[1]
    print("ok")


def test_templates_need_filling():
    root = repo()
    put(root, "spec.md")
    paths = plan.new(root, SLUG)
    assert [p.name for p in paths] == list(plan.FILES)
    errs = errors(root)
    has(errs, "<placeholders>")
    has(errs, "AC-2 has no test")
    try:
        plan.new(root, SLUG)
        raise AssertionError("overwrote existing plan files")
    except ValueError:
        pass
    # a lost file is created again; the others are kept as they are
    tests = spec.path(root, SLUG).parent / "tests.md"
    contracts = spec.path(root, SLUG).parent / "contracts.md"
    contracts.write_text(contracts.read_text() + "edited\n")
    tests.unlink()
    assert plan.new(root, SLUG) == [tests] and contracts.read_text().endswith("edited\n")
    try:
        plan.new(root, "no-such-spec")
        raise AssertionError("made a plan without a spec")
    except ValueError:
        pass
    print("ok")


def test_coverage():
    # a test dropped from tests.md: its AC is untested and the table no longer matches
    root = setup({"tests.md": lambda t: t.split("### TC-2")[0] + "## Quality tests" + t.split("## Quality tests")[1]})
    errs = errors(root)
    has(errs, "AC-2 has no test")
    has(errs, "coverage row AC-2: Tests must be none")
    has(errs, "build order `### US-1 Customer refunds a paid order` lists TC-2, which isn't in the plan")
    # a contract that stops citing FR-2 leaves the table out of sync
    root = setup({"contracts.md": lambda t: t.replace("(FR-1, FR-2, NFR-1)", "(FR-1, NFR-1)")})
    has(errors(root), "coverage row FR-2: Contracts must be CT-1")
    # a missing row, a journey with no scenario, a story with no build entry
    root = setup({"plan.md": lambda t: t.replace("| NFR-1 | CT-2 | TC-3 |\n", "").replace("### US-1", "### Foundation"),
                  "quickstart.md": lambda t: t.replace("(UJ-1; auto)", "(UJ-9; auto)")})
    errs = errors(root)
    has(errs, "coverage: NFR-1 has no row")
    has(errs, "QS-1 walks UJ-9, which isn't in the spec")
    has(errs, "UJ-1 has no quickstart scenario")
    has(errs, "build order: US-1 has no entry")
    print("ok")


def test_broken_items():
    root = setup({"tests.md": lambda t: t.replace("(AC-1; integration)", "(AC-1; unit)").replace("- Setup: an order already refunded\n", ""),
                  "contracts.md": lambda t: t.replace("`app.py` (existing)", "`gone.py` (existing)").replace(" [default]\n- Binding", "\n- Binding"),
                  "quickstart.md": lambda t: t.replace("- Pass when: every step matched\n", "")})
    errs = errors(root)
    has(errs, "TC-1 is unit, but AC-1 asks for integration")
    has(errs, "TC-2: needs `- Setup:`")
    has(errs, "binds `gone.py` as existing, but there is no such file")
    has(errs, "CT-2: its heading must end with")
    has(errs, "QS-1: needs numbered steps")
    print("ok")


def test_wrong_ids_and_duplicates():
    root = setup({"tests.md": lambda t: t.replace("- Covers: CT-1\n- Setup: a paid order\n", "- Covers: TC-1\n- Setup: a paid order\n"),
                  "contracts.md": lambda t: t.replace("(FR-1, FR-2) [research", "(FR-1; FR-2) [research"),
                  "plan.md": lambda t: t.replace("- Tests: TC-1,", "- Tests: CT-1, TC-1,")
                  .replace("| AC-1 | CT-1, CT-2 | TC-1 |", "| AC-1 | CT-1, CT-2 | TC-1 |\n| AC-1 | CT-1, CT-2 | TC-1 |")})
    errs = errors(root)
    has(errs, "TC-4 covers TC-1, which isn't a contract")
    has(errs, "CT-1: cite the FRs it serves")
    has(errs, "lists CT-1 under `Tests:`, which takes TC IDs")
    has(errs, "coverage: AC-1 has more than one row")
    root = setup({"plan.md": lambda t: t.replace("## Coverage", "### US-1 Again\n- Delivers: CT-1\n\n## Coverage")})
    has(errors(root), "build order: US-1 has more than one entry")
    print("ok")


def test_provenance_sources():
    root = setup({"contracts.md": lambda t: t.replace("[research: RF-5]", "[research: RF-9]").replace(
        "(FR-1, FR-2, NFR-1) [default]", "(FR-1, FR-2, NFR-1) [derived: CT-77]")})
    errs = errors(root)
    has(errs, "cites RF-9, which isn't in research.md")
    has(errs, "is derived from CT-77, which isn't defined")
    print("ok")


def test_bindings():
    root = setup({"contracts.md": lambda t: t.replace("`app.py:refund_order` (new)", "`../../etc/passwd` (existing)")
                  .replace("`app.py` (existing)", "`app.py` (new)"),
                  "tests.md": lambda t: t.replace("`tests/test_refunds.py:test_full_refund` (new)", "`tests/gone.py:test_x` (existing)")})
    errs = errors(root)
    has(errs, "CT-1 binds `../../etc/passwd`, which is outside the repository")
    has(errs, "CT-2 binds `app.py` as new, but the file exists")
    has(errs, "TC-1 binds `tests/gone.py` as existing, but there is no such file")
    # a new test file in a new folder is fine without architecture: only contracts and data are on the stop list
    assert not [e for e in errors(setup()) if "architecture" in e]
    print("ok")


def test_robustness():
    # a missing section is reported, never a crash; an NFR nothing can serve may say none
    root = setup({"plan.md": lambda t: t.replace("## Build order", "## Bogus").replace("## Coverage", "## Other")})
    errs = errors(root)
    has(errs, "section `## Build order` is missing or empty")
    has(errs, "section `## Coverage` is missing or empty")
    root = setup({"plan.md": lambda t: t.replace("| NFR-1 | CT-2 | TC-3 |", "| NFR-1 | none | none |"),
                  "contracts.md": lambda t: t.replace("(FR-1, FR-2, NFR-1)", "(FR-1, FR-2)"),
                  "tests.md": lambda t: t.split("## Quality tests")[0] + "## Misuse tests" + t.split("## Misuse tests")[1]})
    assert [e for e in errors(root) if "NFR-1" in e] == [], errors(root)
    # a story the spec renumbers doesn't trip the plan's own ID history
    import subprocess
    root = setup()
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "plan"], cwd=root, check=True)
    p = spec.path(root, SLUG).parent / "plan.md"
    p.write_text(p.read_text().replace("### US-1 Customer", "### US-2 Customer"))
    assert not [e for e in errors(root) if "retired" in e or "renumbered" in e], errors(root)
    # only a full spec has a plan stage
    put(root, "spec-bugfix.md")
    try:
        plan.check(root, "refund-double-charge")
        raise AssertionError("checked a plan for a bug-fix spec")
    except ValueError as e:
        assert "only a full spec" in str(e)
    print("ok")


def test_second_review():
    # a data model entry with field lines, as the template shows it
    model = ('\n## Data model\n- **Refund** (spec Key entity) in `app.py:Refund` (new) [default]\n'
             '  - amount: decimal. "refund the full order amount" (FR-1)\n')
    root = setup({"contracts.md": lambda t: t + model, "plan.md": lambda t: t.replace("architecture: none", "architecture: approved")})
    (spec.path(root, SLUG).parent / "architecture.md").write_text("# Architecture\n")
    assert errors(root) == [], errors(root)
    # an empty field doesn't borrow the next line; Covers must name a contract
    root = setup({"contracts.md": lambda t: t.replace("- Kind: function", "- Kind:"),
                  "tests.md": lambda t: t.replace("- Covers: CT-1\n- Setup: a paid order\n", "- Covers: everything\n- Setup: a paid order\n")})
    errs = errors(root)
    has(errs, "CT-1: needs `- Kind:`")
    has(errs, "TC-4: `Covers:` names the contracts it tests")
    # every coverage cell is computed: an FR's tests are its ACs' tests
    root = setup({"plan.md": lambda t: t.replace("| FR-1 | CT-1, CT-2 | TC-1 |", "| FR-1 | CT-1, CT-2 | TC-4 |")})
    has(errors(root), "coverage row FR-1: Tests must be TC-1")
    # open point targets, dependencies and double deliveries
    root = setup({"plan.md": lambda t: t.replace("- Delivers: CT-1, CT-2", "- Depends on: US-9\n- Delivers: CT-1, CT-2")
                  .replace("## Build order\n", "## Build order\n### Foundation\n- Delivers: CT-1\n\n")
                  + "\n## Open points\n- **OP-1** (decision; XYZ) Which?\n- **OP-2** (fact; CT-9) What?\n"})
    errs = errors(root)
    has(errs, "depends on US-9, which has no entry")
    has(errs, "CT-1 is delivered by more than one entry")
    has(errs, "OP-1: name the ID it belongs to")
    has(errs, "OP-2 is about CT-9, which is neither in the plan nor the spec")
    # broken frontmatter is an error, not a crash; a bug-fix spec gets no plan files
    root = setup({"tests.md": lambda t: t.replace("retired: []", "retired: [")})
    has(errors(root), "frontmatter is not valid YAML")
    put(root, "spec-bugfix.md")
    try:
        plan.new(root, "refund-double-charge")
        raise AssertionError("made plan files for a bug-fix spec")
    except ValueError as e:
        assert "only a full spec" in str(e)
    print("ok")


def test_architecture_stop():
    # new stored data or a new folder with no approved architecture: the plan must stop for @nio:architecture
    model = "\n## Data model\n- **Refund** (spec Key entity) in `app.py:Refund` (new) [default]\n"
    root = setup({"contracts.md": lambda t: t.replace("`app.py:refund_order` (new)", "`refunds/core.py:refund_order` (new)") + model})
    errs = errors(root)
    has(errs, "CT-1 adds a module (`refunds/core.py`)")
    has(errs, "data model Refund stores new data (`app.py`)")
    root = setup({"contracts.md": lambda t: t + model, "plan.md": lambda t: t.replace("architecture: none", "architecture: approved")})
    has(errors(root), "`architecture: approved` but there is no architecture.md")
    (spec.path(root, SLUG).parent / "architecture.md").write_text("# Architecture\n")
    assert errors(root) == [], errors(root)
    print("ok")


def test_gate_and_ids():
    op = "\n## Open points\n- **OP-1** (decision; CT-2) Should a refund over HTTP need a reason?\n"
    root = setup({"plan.md": lambda t: t + op})
    assert errors(root) == [], errors(root)
    has(errors(root, gate=True), "`## Open points` must be empty at the gate")
    root = setup({"tests.md": lambda t: t.replace("### TC-3", "### TC-1"), "plan.md": lambda t: t.replace("retired: []", "retired: [CT-1]")})
    errs = errors(root)
    has(errs, "TC-1 is defined 2 times")
    has(errs, "`retired` must be a list of OP IDs")
    print("ok")


# --- the `Like:` line and the tasks stage's check (#57, spec 2026-10-28-plan-jury) ---

def with_like(ct1=None, ct2_new=False, ct2=None):
    """Contracts with CT-1's `Like:` value (None: the line removed) and CT-2 bound new (with its own `Like:` value)."""
    def edit(t):
        t = t.replace("- Like: none: the first payment code in the app\n", f"- Like: {ct1}\n" if ct1 else "")
        if ct2_new:
            t = t.replace("- Binding: `app.py` (existing)", "- Binding: `app.py:refund_http` (new)" + (f"\n- Like: {ct2}" if ct2 else ""))
        return t
    return {"contracts.md": edit}


def like_errors(root):
    return [e for e in errors(root) if "Like" in e]


def test_ac27_it_fails_naming_ct_2():
    errs = like_errors(setup(with_like("none: the first payment code", ct2_new=True)))
    assert errs == [f".nio/specs/{SLUG}/contracts.md: CT-2: a new contract needs `- Like: <file>:<symbol>` or `- Like: none: <reason>`"], errs
    print("ok")


def test_ac49_only_ct_6_is_an_error():
    errs = like_errors(setup(with_like("none: first HTTP endpoint in the project", ct2_new=True, ct2="none")))
    assert len(errs) == 1 and "CT-2: `Like: none` needs a reason" in errs[0], errs
    print("ok")


def test_ac28_it_fails():
    errs = like_errors(setup(with_like("`src/nio/nope.py:thing`")))
    assert len(errs) == 1 and "CT-1" in errs[0] and "`src/nio/nope.py`" in errs[0], errs
    print("ok")


def code(root):
    (root / "app.py").write_text("def plan(root):\n    return root\n")
    return root


def test_ac29_it_fails():
    errs = like_errors(code(setup(with_like("`app.py:no_such_symbol`"))))
    assert len(errs) == 1 and "CT-1" in errs[0] and "`no_such_symbol`" in errs[0], errs
    print("ok")


def test_ac30_ct_2_raises_no_error():
    root, calls, run = code(setup(with_like("`app.py:plan`"))), [], subprocess.run
    subprocess.run = lambda args, *a, **k: calls.append(args) or run(args, *a, **k)
    try:
        errs = [e for e in errors(root) if "CT-1" in e]
    finally:
        subprocess.run = run
    assert errs == [] and all(c[0] == "git" for c in calls), (errs, calls)
    print("ok")


def test_ac31_ct_4_raises_no_error():
    assert not [e for e in errors(setup()) if "CT-2" in e]  # CT-2 is bound (existing) and has no `Like:`
    print("ok")


def test_ac32_it_raises_no_error_for_it():
    order = ("### Foundation\n- Delivers: CT-2\n- Tests: TC-2\n- Scenario: QS-1\n\n"
             "### US-1 Customer refunds a paid order\n- Depends on: Foundation\n- Delivers: CT-1\n- Tests: TC-1, TC-3, TC-4\n")
    edit = lambda t: re.sub(r"(## Build order\n).*?(?=\n## )", lambda m: m[1] + order, t, flags=re.S)
    errs = errors(setup({"plan.md": edit}))
    assert not [e for e in errs if "US-1" in e or "Scenario" in e], errs
    print("ok")


def set_route(root, route):
    path = spec.path(root, SLUG)
    path.write_text(re.sub(r"^route: \w+", f"route: {route}", path.read_text(), count=1, flags=re.M))
    return root


def test_ac40_it_refuses():
    root = setup()
    ok, why = plan.approved(root, SLUG)
    assert not ok and why.startswith("the plan must be approved first") and not (spec.path(root, SLUG).parent / "tasks.md").exists(), why
    print("ok")


def test_ac55_it_refuses_given_a_bug_fix_spec_with_no():
    root = setup()
    for f in plan.FILES:
        (spec.path(root, SLUG).parent / f).unlink()
    ok, why = plan.approved(root, SLUG)
    assert not ok and why == "the plan must be approved first (there is no plan.md)", why
    assert plan.approved(set_route(root, "lite"), SLUG) == (True, "a bug-fix spec has no plan stage")
    print("ok")


def test_ac41_it_proceeds():
    from test_jury import approve_plan, plan_repo
    root = plan_repo()
    approve_plan(root)
    assert plan.approved(root, SLUG) == (True, "the plan jury approved the plan")
    print("ok")


if __name__ == "__main__":
    test_example_passes()
    test_templates_need_filling()
    test_coverage()
    test_broken_items()
    test_architecture_stop()
    test_gate_and_ids()
    test_wrong_ids_and_duplicates()
    test_provenance_sources()
    test_bindings()
    test_robustness()
    test_second_review()
    test_ac27_it_fails_naming_ct_2()
    test_ac49_only_ct_6_is_an_error()
    test_ac28_it_fails()
    test_ac29_it_fails()
    test_ac30_ct_2_raises_no_error()
    test_ac31_ct_4_raises_no_error()
    test_ac32_it_raises_no_error_for_it()
    test_ac40_it_refuses()
    test_ac55_it_refuses_given_a_bug_fix_spec_with_no()
    test_ac41_it_proceeds()
