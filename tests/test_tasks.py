"""Self-check for nio new tasks / nio check tasks / nio task show (#42). Run: uv run python tests/test_tasks.py"""
import re
import subprocess
from pathlib import Path

from test_jury import PLAN_FINDING, PSLUG, approve_plan, approve_spec, change, plan_lens, plan_repo

from nio import jury, records, tasks

SLUG = PSLUG
TASKS = (Path(__file__).parent / "fixtures/tasks/tasks.md").read_text()


def repo(edit=lambda t: t, route="full", write=True):
    """The refunds spec and plan (tests/fixtures/plan), with tasks.md from tests/fixtures/tasks, after `edit`."""
    root = plan_repo(route=route)
    if write:
        tasks.path(root, SLUG).write_text(edit(TASKS))
    return root


def errs(root):
    return tasks.check(root, SLUG)[0]


def has(errors, text):
    assert any(text in e for e in errors), (text, errors)


def field(task, name, value):
    """An edit: set `name:` of `task` to `value` (None removes the line)."""
    def edit(t):
        head = t.index(f"### {task} ")
        end = t.find("\n### ", head + 1)
        end = len(t) if end < 0 else end
        block = re.sub(rf"^- {name}:.*\n", "" if value is None else f"- {name}: {value}\n", t[head:end], count=1, flags=re.M)
        return t[:head] + block + t[end:]
    return edit


def chain(*edits):
    def edit(t):
        for e in edits:
            t = e(t)
        return t
    return edit


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout


def approve_commit(root):
    git(root, "add", "-A")
    git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "nio: approve tasks")


def approve_tasks(root, run="R-T1"):
    plan_lens(root, run, "executability", gate="tasks")
    jury.collect(root, SLUG, "tasks", run)
    assert jury.check(root, SLUG, "tasks", record=True)[0] == "approved"


FIX = "\n#### Fixes\n\n### {tid} Fix the finding\n- From: {src}\n- Files: `{file}`\n- Serves: {serves}\n- Test: TC-1\n- Depends on: T-3\n- Parallel: {par}\n- Tier: cheap: small\n- Effort: low\n- Mode: split: small\n"


def fix(tid="T-4", src="J-4 (implementation-E-1, round 1)", serves="J-4", file="app.py", par="no"):
    return lambda t: t + FIX.format(tid=tid, src=src, serves=serves, file=file, par=par)


# --- starting the stage (CT-3) ---

def test_ac3_it_refuses():
    root = repo(write=False)
    try:
        tasks.new(root, SLUG)
        raise AssertionError("tasks.md was created for an unapproved spec")
    except ValueError as e:
        assert str(e) == "the spec must be approved first", e
    assert not tasks.path(root, SLUG).exists()
    print("ok")


def test_ac4_it_refuses_and_points_to_its_slices():
    root = repo(route="epic", write=False)
    ok, why = tasks.may_start(root, SLUG)
    assert not ok and "run the tasks stage on each slice's spec" in why, why
    print("ok")


def test_ac59_it_refuses_given_a_bug_fix_spec_whose_sp():
    root = repo(write=False)
    approve_spec(root, "R-S1")
    try:
        tasks.new(root, SLUG)
        raise AssertionError("tasks.md was created without an approved plan")
    except ValueError as e:
        assert str(e).startswith("the plan must be approved first"), e
    assert not tasks.path(root, SLUG).exists()
    lite = repo(route="lite", write=False)
    approve_spec(lite, "R-S1")
    assert tasks.new(lite, SLUG).exists()
    print("ok")


def test_ac42_it_proceeds():
    root = repo(write=False)
    plan_lens(root, "R-S1", "logic", PLAN_FINDING.format(n=1, what="x", sev="minor", quote="refund the full order amount").replace("CT-1", "FR-1"), gate="spec")
    jury.collect(root, SLUG, "spec", "R-S1")
    jury.check(root, SLUG, "spec", record=True, human="the human accepts the finding")
    approve_plan(root)
    assert tasks.may_start(root, SLUG) == (True, "the tasks stage may start")
    print("ok")


def test_ac43_it_refuses():
    root = repo(write=False)
    bad = root / ".nio/runs/R-S1/jury/spec-logic.md"
    for n in (1, 2):  # a juror that fails twice hands the gate to the human
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.write_text(f"---\nlens: logic\ngate: spec\nsubject: {SLUG}\nby: x\ncontext: sufficient\n---\nattempt {n}\n")
        jury.collect(root, SLUG, "spec", "R-S1")
    assert jury.check(root, SLUG, "spec")[0] == "human"
    assert tasks.may_start(root, SLUG) == (False, "the spec must be approved first")
    print("ok")


# --- the check (CT-4) ---

def test_ac22_it_passes():
    assert errs(repo()) == []
    print("ok")


def test_ac5_it_fails():
    root = repo(chain(lambda t: t.replace("`app.py`", "`other.py`"), field("T-3", "Test", "TC-4")))
    e = errs(root)
    has(e, "E-1 names `app.py` in no `Files:` line")
    has(e, "E-1 has no task citing TC-3")
    print("ok")


def test_ac8_it_fails():
    has(errs(repo(field("T-3", "Effort", None))), "T-3: needs `- Effort:`")
    print("ok")


def test_ac9_it_fails():
    has(errs(repo(field("T-3", "Serves", "AC-1, AC-2, AC-99"))), "T-3 cites AC-99, which the spec doesn't define")
    print("ok")


def test_ac10_it_fails():
    has(errs(repo(field("T-2", "Depends on", "T-40"))), "T-2 cites T-40, which tasks.md doesn't define")
    print("ok")


def test_ac11_it_fails():
    root = repo(chain(lambda t: t.replace("retired: []", "retired: [T-9]"), field("T-3", "Depends on", "T-2, T-9")))
    has(errs(root), "T-3 cites T-9, which is retired")
    print("ok")


def test_ac12_it_fails():
    root = repo(lambda t: t + "\n" + t[t.index("### T-2"):t.index("### T-3")])
    has(errs(root), "T-2 is defined 2 times")
    print("ok")


def test_ac13_only_the_second_is_an_error():
    root = repo(chain(field("T-1", "Parallel", "yes"), field("T-2", "Parallel", "maybe")))
    assert errs(root) == ["T-2: `Parallel:` must be yes or no, not `maybe`"], errs(root)
    print("ok")


def test_ac14_both_are_errors():
    e = errs(repo(chain(field("T-1", "Tier", "strong"), field("T-2", "Tier", "huge: big change"))))
    assert e == ["T-1: `Tier: strong` needs a reason, as `Tier: strong: <why>`", "T-2: `huge` is not cheap, strong, max or frontier"], e
    print("ok")


def test_ac15_it_fails():
    for line in ("- [ ] done", "- Status: in review"):
        root = repo(lambda t: t.replace("- Effort: med\n", f"- Effort: med\n{line}\n"))
        has(errs(root), "T-1 holds a status or a checkbox; status lives in the CLI's state")
    print("ok")


def test_ac16_it_fails():
    root = repo(chain(field("T-2", "Serves", "AC-1"), field("T-3", "Serves", "AC-1")))
    has(errs(root), "AC-2 is served by no task")
    print("ok")


def test_ac17_it_fails():
    has(errs(repo(field("T-3", "Serves", "none"))), "T-3 serves no AC")
    print("ok")


def test_ac18_it_fails():
    e = errs(repo(field("T-1", "Depends on", "T-2")))
    assert any(x.startswith("dependency cycle:") and "T-1" in x and "T-2" in x and "T-3" not in x for x in e), e
    print("ok")


def test_ac19_it_fails():
    e = errs(repo(field("T-1", "Depends on", "T-3")))
    assert any(x.startswith("dependency cycle:") and all(t in x for t in ("T-1", "T-2", "T-3")) for x in e), e
    print("ok")


def test_ac20_it_fails():
    root = repo(chain(*(field(t, "Parallel", "yes") for t in ("T-2", "T-3")), field("T-2", "Depends on", "none"), field("T-3", "Depends on", "none")))
    has(errs(root), "parallel clash: T-2 and T-3 both name `app.py`")
    print("ok")


def test_ac21_there_is_no_clash():
    root = repo(chain(field("T-2", "Parallel", "yes"), field("T-2", "Depends on", "none"), field("T-3", "Depends on", "none")))
    assert not [e for e in errs(root) if "clash" in e]
    print("ok")


def test_ac24_size_raises_no_error():
    many = ", ".join(f"`src/f{n}.py`" for n in range(11)) + ", `app.py`"
    assert errs(repo(field("T-3", "Files", many))) == []
    print("ok")


def test_ac46_it_fails_naming_t_1_and_ac_4():
    text = TASKS.replace("## E-1 Customer refunds a paid order (US-1)", "## E-1 Shared setup (Foundation)").replace(
        "### T-2 Reject a second refund", "## E-2 Customer refunds a paid order (US-1)\n\n### T-2 Reject a second refund")
    root = repo(chain(lambda t: text, field("T-1", "Serves", "AC-1, AC-2"), field("T-2", "Serves", "AC-1"),
                      field("T-3", "Depends on", "none"), field("T-3", "Serves", "AC-2")))
    has(errs(root), "T-1 serves AC-2, which no task depending on it serves")
    print("ok")


def test_ac49_it_fails_naming_both():
    text = TASKS.replace("### T-3 ", "## E-2 Second epic (US-1)\n\n### T-3 ")
    root = repo(chain(lambda t: text, *(field(t, "Parallel", "yes") for t in ("T-1", "T-3")), field("T-3", "Depends on", "none"),
                      *(field(t, "Files", "`src/cart.py`, `app.py`") for t in ("T-1", "T-3"))))
    has(errs(root), "parallel clash: T-1 and T-3 both name `src/cart.py`")
    print("ok")


def test_ac50_it_passes_and_t_4_is_listed_as_parallel():
    e, notes = tasks.check(repo(field("T-3", "Parallel", "yes")), SLUG)  # T-3 depends on T-2
    assert e == [] and notes[0].endswith("parallel: T-3"), (e, notes)
    print("ok")


def test_ac62_it_fails_given_a_task_with_test_second_r():
    e = errs(repo(chain(field("T-1", "Test", "TC-99"), field("T-2", "Test", "second refund gets 409"))))
    has(e, "T-1 cites TC-99, which the plan doesn't define")
    has(e, "T-2: on a full spec `Test:` cites the plan's `TC-n`")
    print("ok")


def test_ac54_tasks_md_has_exactly_one_epic_e_1_whose():
    root = repo(chain(field("T-1", "Test", "a paid order of 40.00 is refunded 40.00"), field("T-2", "Test", "a second refund gets 409"),
                      field("T-3", "Test", "two refunds at once pay once")), route="lite")
    e, notes = tasks.check(root, SLUG)
    assert e == [] and len(tasks.parse(tasks.path(root, SLUG).read_text())["epics"]) == 1, (e, notes)
    print("ok")


# --- the estimate (CT-5) ---

def test_ac27_it_prints_e_1_s_estimate_row():
    text = chain(field("T-1", "Tier", "cheap: x"), field("T-1", "Effort", "low"), field("T-1", "Parallel", "yes"),
                 field("T-2", "Tier", "cheap: x"), field("T-2", "Effort", "med"), field("T-2", "Parallel", "yes"),
                 field("T-3", "Tier", "max: x"), field("T-3", "Effort", "high"))(TASKS)
    row = tasks.estimate(tasks.parse(text))[0]
    assert row == "E-1: 3 tasks; tier cheap 2, strong 0, max 1, frontier 0; effort low 1, med 1, high 1; parallel: T-1, T-2", row
    print("ok")


def test_ac28_it_holds_no_token_or_money_figure():
    row = tasks.check(repo(), SLUG)[1][0]
    assert not re.search(r"token|\$|€|cost|price", row, re.I), row
    print("ok")


def test_ac48_both_are_listed_as_parallel():
    text = chain(field("T-1", "Parallel", "yes"), field("T-1", "Tier", "cheap: x"), field("T-1", "Files", "`a.py`"),
                 field("T-2", "Parallel", "yes"), field("T-2", "Tier", "max: x"), field("T-2", "Files", "`b.py`"),
                 field("T-2", "Depends on", "none"))(TASKS)
    assert tasks.estimate(tasks.parse(text))[0].endswith("parallel: T-1, T-2")
    print("ok")


# --- show (CT-6) ---

def test_ac39_it_prints_t_3_alone():
    out = "\n".join(tasks.show(repo(), SLUG, "T-3"))
    assert out.startswith("## E-1 Customer refunds a paid order (US-1)") and "### T-3 " in out, out
    assert "### T-1" not in out and "### T-2" not in out and all(f"- {f}:" in out for f in tasks.FIELDS), out
    print("ok")


# --- fix tasks (CT-16) ---

def test_ac51_it_passes_the_same_serves_j_4_on_a_plann():
    assert errs(repo(fix())) == []
    has(errs(repo(field("T-3", "Serves", "AC-1, AC-2, J-4"))), "T-3 cites J-4; a finding is served only by a fix task whose `From:` names it")
    print("ok")


def test_ac34_it_fails():
    has(errs(repo(lambda t: fix()(t).replace("- From: J-4 (implementation-E-1, round 1)\n", ""))), "T-4: a fix task needs `- From:`")
    print("ok")


def test_ac35_it_fails_as_a_parallel_clash():
    root = repo(chain(field("T-3", "Parallel", "yes"), field("T-3", "Depends on", "none"),
                      lambda t: fix(par="yes")(t).replace("- Depends on: T-3\n- Parallel: yes", "- Depends on: none\n- Parallel: yes")))
    has(errs(root), "parallel clash: T-3 and T-4 both name `app.py`")
    print("ok")


def test_ac31_t_12_is_added_under_e_2_s_fixes_heading():
    retire = lambda t: t.replace("retired: []", "retired: [T-11]")
    assert errs(repo(chain(retire, fix("T-12")))) == []
    has(errs(repo(chain(retire, fix("T-8")))), "T-8: a fix task takes the next free ID, T-12")
    print("ok")


def test_ac32_the_planned_tasks_above_the_heading_are():
    root = repo()
    approve_commit(root)
    tasks.path(root, SLUG).write_text(fix()(TASKS))
    assert errs(root) == []
    tasks.path(root, SLUG).write_text(field("T-2", "Files", "`app.py`, `views.py`")(fix()(TASKS)))
    has(errs(root), "T-2 changed after `nio: approve tasks`; planned tasks are frozen after approval")
    print("ok")


def test_ac52_it_fails_naming_the_task():
    root = repo()
    approve_commit(root)
    tasks.path(root, SLUG).write_text(field("T-1", "Files", "`app.py`, `views.py`")(TASKS))
    has(errs(root), "T-1 changed after `nio: approve tasks`; planned tasks are frozen after approval")
    print("ok")


def test_uj3_edited_planned_task_fails():
    root = repo()
    approve_commit(root)
    tasks.path(root, SLUG).write_text(TASKS.replace("### T-3 ", "### T-5 "))  # renumbered to make room
    e = errs(root)
    has(e, "T-3 was removed after `nio: approve tasks` without being retired")
    print("ok")


def test_ac53_it_sits_under_fixes_with_from_c_1_and_th():
    root = repo()
    approve_commit(root)
    cid = change(root, "accepted")
    tasks.path(root, SLUG).write_text(fix(src=cid, serves="AC-1")(TASKS))
    assert errs(root) == []
    print("ok")


def test_ac33_it_goes_under_the_epic_s_fixes_heading_c():
    root = repo()
    cid = change(root, "rejected")
    tasks.path(root, SLUG).write_text(fix(src=cid, serves="AC-2")(TASKS))
    assert errs(root) == []
    tasks.path(root, SLUG).write_text(fix(src="C-261028-zzzz", serves="AC-2")(TASKS))
    has(errs(root), "T-4: `From: C-261028-zzzz` names no finding")
    print("ok")


# --- may the implement stage start (CT-14) and finished (CT-15) ---

def test_ac29_it_refuses():
    ok, why = tasks.approved(repo(), SLUG)
    assert not ok and why.startswith("the tasks must be approved first"), why
    print("ok")


def test_uj2_unapproved_tasks_block_implement():
    root = repo()
    approve_plan(root)
    assert not tasks.approved(root, SLUG)[0]
    print("ok")


def test_ac30_it_still_refuses():
    root = repo()
    plan_lens(root, "R-T1", "executability", PLAN_FINDING.format(n=1, what="is too big", sev="minor", quote="Refunds stay fast").replace("CT-1", "AC-1"), gate="tasks")
    jury.collect(root, SLUG, "tasks", "R-T1")
    assert jury.check(root, SLUG, "tasks", record=True)[0] == "rejected"
    assert not tasks.approved(root, SLUG)[0]
    print("ok")


def test_ac45_one_nio_approve_tasks_commit_holds_tasks():
    root = repo()
    assert not tasks.approved(root, SLUG)[0]
    approve_tasks(root)
    assert tasks.approved(root, SLUG) == (True, "the tasks jury approved the tasks")
    assert [p for p in (root / ".nio/memory").rglob("V-*.md") if f'"tasks:{SLUG}"' in p.read_text()]
    print("ok")


def test_ac55_it_proceeds():
    root = repo()
    approve_tasks(root)
    approve_commit(root)
    assert tasks.approved(root, SLUG)[0]
    print("ok")


def test_ac63_the_tasks_approval_no_longer_stands():
    root = repo()
    approve_tasks(root)
    tasks.path(root, SLUG).write_text(fix()(TASKS))  # a fix task doesn't withdraw it
    assert tasks.approved(root, SLUG)[0]
    contracts = tasks.path(root, SLUG).parent / "contracts.md"
    contracts.write_text(contracts.read_text().replace("refund the full order amount", "refund the order amount"))
    ok, why = tasks.approved(root, SLUG)
    assert not ok and why.startswith("the tasks must be approved first") and jury.check(root, SLUG, "tasks")[0] == "rerun", why
    print("ok")


def test_ac37_it_is_not_finished():
    epic = tasks.parse(fix("T-12")(TASKS.replace("retired: []", "retired: [T-11]")))["epics"][0]
    states = {"T-1": "done", "T-2": "done", "T-3": "done", "T-12": "review"}
    assert tasks.finished(states, epic) == (False, ["T-12"])
    assert tasks.finished({**states, "T-12": "done"}, epic) == (True, [])
    print("ok")


# --- the tasks gate (CT-11) ---

def test_ac23_it_does_not_start():
    lines, ok = jury.plan(repo(field("T-3", "Effort", None)), SLUG, "tasks")
    assert not ok and lines == [f"`nio check tasks {SLUG}` fails (1 errors): the check must pass first"], lines
    print("ok")


# --- misuse and quality ---

def test_uj1_layered_tasks_fail_coverage():
    text = TASKS.replace("## E-1 Customer refunds a paid order (US-1)", "## E-1 Database layer")
    e = errs(repo(chain(lambda t: text, field("T-2", "Serves", "AC-1"), field("T-3", "Serves", "none"))))
    has(e, "AC-2 is served by no task")
    has(e, "T-3 serves no AC")
    print("ok")


def test_nfr1_check_tasks_makes_no_model_call():
    root, calls, run = repo(), [], subprocess.run
    subprocess.run = lambda args, *a, **k: calls.append(args) or run(args, *a, **k)
    try:
        e, notes = tasks.check(root, SLUG)
    finally:
        subprocess.run = run
    assert e == [] and notes and all(c[0] == "git" for c in calls), (e, calls)
    print("ok")


def test_cli():
    root = repo()
    run = lambda *a: subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", *a], cwd=root,
                                    capture_output=True, text=True)
    out = run("check", "tasks", SLUG)
    assert out.returncode == 0 and "0 errors" in out.stdout and "E-1: 3 tasks" in out.stdout, out
    out = run("task", "show", SLUG, "T-2")
    assert out.returncode == 0 and out.stdout.startswith("## E-1"), out
    out = run("check", "tasks", SLUG, "--approved")
    assert out.returncode == 1 and "the tasks must be approved first" in out.stdout, out
    print("ok")


def test_own():
    assert tasks.own("TC-10; TC-38 proved later by T-11") == ["TC-10"]
    assert tasks.own("a direct unit check calling `load`; TC-6 and TC-7 proved later by T-8") == []
    assert tasks.own("TC-38, plus a direct check; TC-38 proved later by T-11") == ["TC-38"]
    print("ok")


def test_ac10_fix_keeps_approval():
    # TC-10: a fix task appended under #### Fixes keeps an approved tasks gate approved (CT-4, FR-8)
    root = repo()
    approve_tasks(root)
    approve_commit(root)
    tasks.path(root, SLUG).write_text(fix(tid="T-30")(tasks.path(root, SLUG).read_text()))
    ok, why = tasks.approved(root, SLUG)
    assert ok, why
    print("ok")


def test_ac25_edit_withdraws_approval():
    # TC-21: changing one word of a planned task's title withdraws the approval (CT-4, FR-8)
    root = repo()
    approve_tasks(root)
    approve_commit(root)
    text = tasks.path(root, SLUG).read_text()
    assert "### T-1 Refund a paid order in full" in text
    tasks.path(root, SLUG).write_text(text.replace("### T-1 Refund a paid order in full", "### T-1 Refund a paid order in part", 1))
    ok, why = tasks.approved(root, SLUG)
    assert not ok and why.startswith("the tasks must be approved first"), why
    print("ok")


def rated_run(edit_after, edit_before=lambda t: t):
    """Run `nio check tasks --rated-from` on a rated tasks.md; `before` holds `to be rated`."""
    root = repo(chain(field("T-1", "Tier", "to be rated"), field("T-1", "Mode", "to be rated"), edit_before))
    copy = root / "before.md"
    copy.write_text(tasks.path(root, SLUG).read_text())
    tasks.path(root, SLUG).write_text(edit_after(copy.read_text()))
    return subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "check", "tasks", SLUG,
                           "--rated-from", str(copy)], cwd=root, capture_output=True, text=True)


RATE = chain(field("T-1", "Tier", "strong: money moves"), field("T-1", "Mode", "split: two workers"))


def test_ac26_rated_from_stray_edit():
    out = rated_run(chain(RATE, field("T-2", "Files", "`other.py`")))
    assert out.returncode == 1, out
    assert "ERROR" in out.stdout and "- Files: `other.py`" in out.stdout, out.stdout
    assert out.stdout.strip().splitlines()[-1].endswith("1 errors"), out.stdout
    print("ok")


def test_ac27_rated_from_ok():
    out = rated_run(RATE)
    assert out.returncode == 0, out
    out = rated_run(field("T-1", "Effort", "high"))
    assert out.returncode == 1 and "not rated" in out.stdout, out
    print("ok")


def test_ac26_rated_from_stray_edit_misuse():
    out = rated_run(chain(RATE, lambda t: t.replace("## E-1 Customer refunds a paid order (US-1)\n", "", 1)))
    assert out.returncode == 1, out
    print("ok")


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
