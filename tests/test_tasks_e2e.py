"""End-to-end checks of the tasks drafter and the evaluator (#42): each runs a card on a real model against the refunds
fixture and reads the tasks.md it writes. They cost a model run each, so they run only when asked:
    NIO_E2E=1 uv run python tests/test_tasks_e2e.py
Without NIO_E2E they print `skipped` and pass."""
import re
import subprocess
from importlib import resources

from test_jury import PSLUG, plan_repo
from test_lenses import e2e
from test_tasks import TASKS

from nio import agents, tasks

TOOLS = "Read Grep Glob Edit Write Bash"
US2_SPEC = """
### US-2 Support sees every refund (P2) [human]
- **Why this priority:** support answers refund questions.
- **Independent test:** list refunds after two refunds.

- **AC-3** (FR-3) Given two refunds, when support lists refunds, then both are listed with their amounts. [human]
  Observable: the list holds both refunds and their amounts. Level: integration.
"""
US2_PLAN = "\n### US-2 Support sees every refund\n- Depends on: {dep}\n- Delivers: CT-3\n- Tests: TC-5\n"
CT3 = "\n### CT-3 List refunds (FR-3) [default]\n- Binding: `app.py:list_refunds` (new)\n- Like: none: the first listing\n- Kind: function\n- Shape: `list_refunds() -> list[Refund]`\n"
TC5 = ("\n### TC-5 Both refunds are listed (AC-3; integration) [default]\n- File: `tests/test_refunds.py:test_list` (new)\n"
       "- Covers: CT-3\n- Setup: two refunds\n- Action: `list_refunds()`\n- Assert: both refunds, 40.00 and 25.00\n")


def two_stories(root, foundation=False):
    """Add US-2 (AC-3, FR-3) to the fixture spec and a build-order entry for it to the plan; optionally a Foundation entry."""
    folder = tasks.path(root, PSLUG).parent
    spec = folder / "spec.md"
    text = spec.read_text().replace("## Functional requirements", US2_SPEC.strip() + "\n\n## Functional requirements", 1)
    spec.write_text(text.replace("- **FR-2**", "- **FR-3** WHEN support lists refunds THE SYSTEM SHALL show each with its amount. [human]\n- **FR-2**", 1))
    (folder / "contracts.md").write_text((folder / "contracts.md").read_text().rstrip() + "\n" + CT3)
    (folder / "tests.md").write_text((folder / "tests.md").read_text().rstrip() + "\n" + TC5)
    plan = (folder / "plan.md").read_text()
    if foundation:
        plan = plan.replace("### US-1 ", "### Foundation\n- Delivers: CT-2\n- Tests: TC-3\n\n### US-1 ", 1)
        plan = plan.replace("- Delivers: CT-1, CT-2", "- Depends on: Foundation\n- Delivers: CT-1", 1)
    entry = US2_PLAN.format(dep="Foundation" if foundation else "US-1")
    (folder / "plan.md").write_text(plan.replace("\n## Coverage", entry + "\n## Coverage", 1))


def run_card(root, card, ask):
    meta, body, _ = agents.load(root)[card]
    model = agents.DEFAULT_TIERS["claude"][meta["tier"]]
    r = subprocess.run(["claude", "-p", "--model", model, "--system-prompt", body, "--allowedTools", TOOLS],
                       input=ask, cwd=root, capture_output=True, text=True, timeout=1500)
    assert r.stdout.strip(), r.stderr
    return r.stdout


def draft(root):
    tasks.path(root, PSLUG).write_text(resources.files("nio").joinpath("templates/tasks.md").read_text().replace("<slug>", PSLUG))
    return run_card(root, "tasks-drafter", f"Slug: {PSLUG}. Fill .nio/specs/{PSLUG}/tasks.md from the spec and plan files next to it. "
                                           "The CLI here is `uv run nio`; run `uv run nio check tasks " + PSLUG + "` until it passes.")


def epics(root):
    return tasks.parse(tasks.path(root, PSLUG).read_text())


@e2e
def test_ac1_it_writes_one_tasks_md_with_one_epic_per():
    root = plan_repo()
    two_stories(root)
    draft(root)
    got = epics(root)["epics"]
    assert [e["story"] for e in got] == ["US-1", "US-2"] and [e["id"] for e in got] == ["E-1", "E-2"], got
    assert all(e["tasks"] for e in got)


@e2e
def test_ac2_a_foundational_epic_comes_first_and_both():
    root = plan_repo()
    two_stories(root, foundation=True)
    draft(root)
    got = epics(root)
    first, below = got["epics"][0], tasks.reach(got["tasks"])
    assert first["story"] == "Foundation", got["epics"]
    for e in got["epics"][1:]:
        assert any(below[t] & set(first["tasks"]) for t in e["tasks"]), e


@e2e
def test_ac61_the_epics_follow_that_order_and_e_3_us_2():
    root = plan_repo()
    two_stories(root, foundation=True)
    draft(root)
    got = epics(root)
    assert [e["story"] for e in got["epics"]] == ["Foundation", "US-1", "US-2"], got["epics"]
    below, (_, e2, e3) = tasks.reach(got["tasks"]), got["epics"]
    assert any(below[t] & set(e2["tasks"]) for t in e3["tasks"])


@e2e
def test_ac6_every_task_names_its_files_from_the_spec():
    root = plan_repo(route="lite")
    draft(root)
    got = epics(root)["tasks"]
    assert got and all(t["fields"].get("Files", "").strip() for t in got.values()), got


@e2e
def test_ac60_it_stops_and_says_the_spec_must_become_a():
    root = plan_repo(route="lite")
    spec = tasks.path(root, PSLUG).parent / "spec.md"
    spec.write_text(spec.read_text().replace("refund the full order amount", "refund the full order amount, keeping each refund in a database table or a JSON file", 1))
    out = run_card(root, "tasks-drafter", f"Slug: {PSLUG}. Write .nio/specs/{PSLUG}/tasks.md from the spec and the code. Report what you did.")
    assert not tasks.path(root, PSLUG).exists() and re.search(r"full spec", out, re.I) and re.search(r"database|JSON", out), out


@e2e
def test_ac25_every_task_has_a_tier_with_a_reason_and():
    root = plan_repo()
    tasks.path(root, PSLUG).write_text(re.sub(r"- Tier: .*", "- Tier: strong: to be rated", TASKS))
    run_card(root, "evaluator", f"Rate every task in .nio/specs/{PSLUG}/tasks.md.")
    for t in epics(root)["tasks"].values():
        tier, effort = t["fields"].get("Tier", ""), t["fields"].get("Effort", "")
        assert re.match(r"(cheap|strong|max|frontier):\s*\S", tier) and "to be rated" not in tier and effort in tasks.EFFORTS, t


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_ac"):
            test()
