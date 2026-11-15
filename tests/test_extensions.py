"""Self-check for nio extensions add / list / remove. Run: uv run python tests/test_extensions.py"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from test_records import repo

import selfcheck
import test_flow
from nio import extensions, flow

S, BY = test_flow.S, "driver / test / test"

SHIPPED = "step %s fires only"


def step(name, after="plan_jury", **kw):
    return {"name": name, "after": after, "skill": f"skills/{name}/SKILL.md", "check": "true", **kw}


def src(tmp, name, steps=(), cards=(), hooks=(), version="1.0.0", raw=None, files=None, **extra):
    d = Path(tmp) / "src" / name
    d.mkdir(parents=True, exist_ok=True)
    for s in steps:
        (d / s["skill"]).parent.mkdir(parents=True, exist_ok=True)
        (d / s["skill"]).write_text(f"skill {s['name']}\n")
    for c in cards:
        (d / f"agents/{c}.md").parent.mkdir(parents=True, exist_ok=True)
        (d / f"agents/{c}.md").write_text(f"card {c}\n")
    for f, t in (files or {}).items():
        (d / f).write_text(t)
    if raw is not False:
        (d / "manifest.json").write_text(raw if raw is not None else json.dumps(
            {"name": name, "version": version, "steps": list(steps), "cards": list(cards), "hooks": list(hooks), **extra}))
    return d


def nio(root, *args):
    r = subprocess.run([sys.executable, "-c", "import sys; from nio.cli import main; sys.argv = ['nio'] + sys.argv[1:]; main()", *args],
                       cwd=root, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def snap(root):
    d = root / ".nio/extensions"
    return {str(p.relative_to(d)): p.read_bytes() for p in d.rglob("*") if p.is_file()} if d.is_dir() else None


def fixture():
    os.environ["NIO_HOME"] = tempfile.mkdtemp()
    return repo(), tempfile.mkdtemp()


def refused(root, source, text):
    before = snap(root)
    code, out = nio(root, "extensions", "add", str(source))
    assert code == 1 and text in out, (code, out)
    assert snap(root) == before


def test_manifest_missing_or_bad_field():
    root, tmp = fixture()
    base = {"name": "x", "version": "1.0.0", "steps": [], "cards": [], "hooks": []}
    bad = lambda **kw: json.dumps({k: v for k, v in {**base, **kw}.items() if v is not None})
    refused(root, src(tmp, "a", raw=False), "manifest.json is missing")
    refused(root, src(tmp, "b", raw="{"), "manifest.json is not JSON")
    refused(root, src(tmp, "c", raw=bad(version=None)), "missing field version")
    s = step("t")
    refused(root, src(tmp, "d", steps=[s], raw=json.dumps({**base, "steps": [{**s, "after": 3}]})), "steps[0].after must be")
    refused(root, src(tmp, "e", steps=[s], raw=json.dumps({**base, "steps": [{**s, "colour": "red"}]})), "unknown field steps[0].colour")


def test_after_unknown_step_refused():
    root, tmp = fixture()
    refused(root, src(tmp, "x", [step("tests", after="planing")]),
            "step tests follows planing, which is neither a built-in step nor a step of an added extension")


def test_add_only_rule():
    root, tmp = fixture()
    refused(root, src(tmp, "a", remove=["plan_jury"]), "remove would change built-in plan_jury")
    refused(root, src(tmp, "b", [step("t", before="tasking")]), "before would change built-in tasking")
    refused(root, src(tmp, "c", skip=["tasks_jury"]), "skip would change built-in tasks_jury")
    refused(root, src(tmp, "d", [step("planning")]), "step planning would replace built-in planning")


def test_card_named_like_shipped_refused():
    root, tmp = fixture()
    refused(root, src(tmp, "x", cards=["worker"]), "card worker has the name of a shipped card")


def test_unknown_event_refused():
    root, tmp = fixture()
    refused(root, src(tmp, "x", hooks=[{"event": "after-task-green", "command": "true"}]),
            "hook on after-task-green: NIO fires only step-passed, step-skipped, gate-approved, gate-rejected, epic-closed, waiting-on-human, effort-done")


def test_plan_trigger_before_plan_gate_refused():
    root, tmp = fixture()
    refused(root, src(tmp, "x", [step("tests", after="spec_jury", trigger={"plan_path": "web/"})]),
            "step tests: trigger plan_path reads the plan, which isn't approved before plan_jury; it follows spec_jury")
    code, out = nio(root, "extensions", "add", str(src(tmp, "y", [step("tests", after="plan_jury", trigger={"plan_path": "web/"})])))
    assert code == 0 and (root / ".nio/extensions/y").is_dir(), out


def test_add_from_folder():
    root, tmp = fixture()
    d = src(tmp, "x", [step("tests")])
    code, out = nio(root, "extensions", "add", str(d))
    assert code == 0, out
    h = hashlib.sha256()
    for p in sorted(p for p in d.rglob("*") if p.is_file()):
        assert (root / ".nio/extensions/x" / p.relative_to(d)).read_bytes() == p.read_bytes()
        h.update(p.relative_to(d).as_posix().encode() + b"\0" + p.read_bytes())
    rec = json.loads((root / ".nio/extensions/record.json").read_text())["x"]
    assert rec == {"source": str(d), "version": "1.0.0", "hash": h.hexdigest()}, rec


def test_add_from_git_url():
    root, tmp = fixture()
    d = src(tmp, "x", [step("tests")])
    git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=tmp + "/repo", capture_output=True, text=True, check=True)
    os.rename(d, tmp + "/repo")
    git("init", "-q")
    git("add", "-A")
    git("commit", "-qm", "x")
    rev = git("rev-parse", "HEAD").stdout.strip()
    url = f"file://{tmp}/repo"
    code, out = nio(root, "extensions", "add", url)
    assert code == 0, out
    assert (root / ".nio/extensions/x/manifest.json").is_file() and not (root / ".nio/extensions/x/.git").exists()
    rec = json.loads((root / ".nio/extensions/record.json").read_text())["x"]
    assert rec["source"] == url and rec["version"] == rev, rec


def test_add_again_replaces():
    root, tmp = fixture()
    assert nio(root, "extensions", "add", str(src(tmp, "x", files={"old.txt": "o"})))[0] == 0
    new = src(Path(tmp) / "n", "x", version="2.0.0")
    code, out = nio(root, "extensions", "add", str(new))
    assert code == 0, out
    d = root / ".nio/extensions"
    assert sorted(p.name for p in d.iterdir()) == ["record.json", "x"] and not (d / "x/old.txt").exists()
    rec = json.loads((d / "record.json").read_text())["x"]
    h = hashlib.sha256()
    for p in sorted(p for p in new.rglob("*") if p.is_file()):
        h.update(p.relative_to(new).as_posix().encode() + b"\0" + p.read_bytes())
    assert rec["version"] == "2.0.0" and rec["hash"] == h.hexdigest(), rec


def test_add_runs_nothing_lists_commands():
    root, tmp = fixture()
    d = src(tmp, "x", [step("tests", check="touch ran-check")], hooks=[{"event": "step-passed", "command": "touch ran-hook"}])
    code, out = nio(root, "extensions", "add", str(d))
    assert code == 0, out
    assert not any(p.name in ("ran-check", "ran-hook") for base in (root, d) for p in base.rglob("ran-*"))
    for line in ("commands it brings (none run):", "check x.tests: touch ran-check", "hook step-passed: touch ran-hook"):
        assert line in out, out


def test_list_shows_each():
    root, tmp = fixture()
    a = src(tmp, "a", [step("one")], cards=["a-card"], hooks=[{"event": "step-passed", "command": "true"}])
    b = src(tmp, "b")
    assert nio(root, "extensions", "add", str(a))[0] == 0 and nio(root, "extensions", "add", str(b))[0] == 0
    code, out = nio(root, "extensions", "list")
    assert code == 0 and out.splitlines() == [
        f"a · 1.0.0 · {a}", "  steps: a.one (after plan_jury)", "  cards: a-card", "  hooks: step-passed: true",
        f"b · 1.0.0 · {b}", "  steps: none", "  cards: none", "  hooks: none"], out


def test_followed_steps_and_names_protected():
    root, tmp = fixture()
    add = lambda d: nio(root, "extensions", "add", str(d))
    assert add(src(tmp, "a", [step("one")]))[0] == 0
    assert add(src(tmp, "b", [step("two", after="a.one")], cards=["b-card"]))[0] == 0
    before = snap(root)
    code, out = nio(root, "extensions", "remove", "a")
    assert code == 1 and "b.two follows a.one" in out, out
    code, out = add(src(Path(tmp) / "v2", "a", version="2.0.0"))
    assert code == 1 and "b.two follows a.one" in out, out
    code, out = add(src(tmp, "c", [step("two")]))
    assert code == 1 and "step two is already a step of extension b" in out, out
    code, out = add(src(tmp, "d", cards=["b-card"]))
    assert code == 1 and "card b-card is already a card of extension b" in out, out
    assert snap(root) == before
    assert add(src(Path(tmp) / "v3", "a", [step("one"), step("three", after="b.two")], version="3.0.0"))[0] == 0
    before = snap(root)
    code, out = add(src(Path(tmp) / "v4", "b", [step("two", after="a.three")], cards=["b-card"], version="2.0.0"))
    assert code == 1 and "step two follows a.three, which never reaches a built-in step: b.two → a.three → b.two" in out, out
    assert snap(root) == before


# --- the flow runs an extension step at its spot (E-2) ---

def effort(stage="plan_jury", slug=S, root=None, edits=()):
    """tests/test_flow.py's effort at `stage` with that stage's ledger approved (not committed); `edits` are
    (fixture file, old, new) replacements made to the fixtures it is built from."""
    os.environ.setdefault("NIO_HOME", tempfile.mkdtemp())
    saved = test_flow.FIXTURES
    if edits:
        test_flow.FIXTURES = Path(tempfile.mkdtemp()) / "f"
        shutil.copytree(saved, test_flow.FIXTURES)
        for f, old, new in edits:
            p = test_flow.FIXTURES / f
            assert old in p.read_text(), (f, old)
            p.write_text(p.read_text().replace(old, new, 1))
    try:
        root = test_flow.effort(stage, slug=slug, root=root)
    finally:
        test_flow.FIXTURES = saved
    test_flow.approve(root, slug, {"plan_jury": "plan", "spec_jury": "spec"}[stage], commit=False)
    return root


def add(root, name, steps=(), **kw):
    code, out = nio(root, "extensions", "add", str(src(tempfile.mkdtemp(), name, steps, **kw)))
    assert code == 0, out
    return out


def pass_plan(root, slug=S):
    code, out = nio(root, "flow", "done", "plan_jury", slug, "--commit", "--by", "human")
    assert code == 0, out
    return out


def moves_of(root, slug=S, kinds=("pass", "skip", "override")):
    return [(x["kind"], x["from"], x["to"]) for x in flow.load(root, slug)[1] if x["kind"] in kinds]


def flowfiles(root, slug=S):
    d = root / ".nio/specs" / slug
    return (d / "state.json").read_bytes(), (d / "history.jsonl").read_bytes()


def test_no_extensions_changes_nothing():
    root = repo()
    assert not (root / ".nio/extensions").exists()
    assert all(a is b for a, b in zip(flow.table(root), (flow.STAGES, flow.GATES, flow.SKILL, flow.INPUTS, flow.EXIT)))
    here = Path(__file__).parent
    r = subprocess.run([sys.executable, str(here / "test_flow.py")], cwd=here.parent, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    diff = subprocess.run(["git", "diff", "main", "--", "tests/test_flow.py"], cwd=here.parent, capture_output=True, text=True).stdout
    changed = [x for x in diff.splitlines() if x[:1] in "+-" and not x.startswith(("+++", "---"))]
    assert all(x.startswith("+") for x in changed) and any("def test_status_speed_with_three_extensions" in x for x in changed), diff


def test_shipped_off_until_added():
    root = effort(edits=[("spec/spec.md", "Level: integration.", "Level: e2e."), ("plan/tests.md", "(AC-1; integration)", "(AC-1; e2e)")])
    pass_plan(root)
    assert flow.table(root)[0] is flow.STAGES
    assert flow.where(root, S)["stage"] == "tasking"
    code, out = nio(root, "flow", "status")
    assert code == 0 and "e2e." not in out and "e2e." not in (root / ".nio/specs" / S / "history.jsonl").read_text(), out


def test_step_runs_after_its_gate():
    root = effort()
    add(root, "x", [step("tests")])
    pass_plan(root)
    assert moves_of(root)[-1] == ("pass", "plan_jury", "x.tests"), moves_of(root)
    code, out = nio(root, "flow", "next", S)
    assert code == 0 and "state: x.tests (working)" in out and "skill: .nio/extensions/x/skills/tests/SKILL.md" in out, out
    assert f"done: nio flow done x.tests {S}" in out and "tasking" not in out, out


def test_two_steps_run_in_name_order():
    root = effort()
    add(root, "beta", [step("two")])
    add(root, "alpha", [step("one")])
    pass_plan(root)
    code, out = nio(root, "flow", "done", "beta.two", S, "--by", BY)
    assert code == 1 and f"{S} is at alpha.one" in out, out
    for st in ("alpha.one", "beta.two"):
        code, out = nio(root, "flow", "done", st, S, "--by", BY)
        assert code == 0, out
    passes = [m for m in moves_of(root, kinds=("pass",)) if m[1] != "spec_jury"]
    assert passes[-3:] == [("pass", "plan_jury", "alpha.one"), ("pass", "alpha.one", "beta.two"), ("pass", "beta.two", "tasking")], passes


def test_status_shows_the_step():
    root = effort()
    other = "2026-10-19-other"
    effort(slug=other, root=root)
    add(root, "x", [step("tests")])
    pass_plan(root)
    code, out = nio(root, "flow", "status")
    row = next(x for x in out.splitlines() if x.startswith(S))
    assert row.startswith(f"{S} · x.tests · manual · working · "), out
    assert nio(root, "flow", "done", "x.tests", S, "--by", BY)[0] == 0
    pass_plan(root, other)
    test_flow.history(root, other, {"kind": "skip", "from": "x.tests", "to": "tasking", "reason": "skipped: by hand"})
    for slug, kind in ((S, "pass"), (other, "skip")):
        code, out = nio(root, "flow", "show", slug, "--json")
        rows = [(r["kind"], r["from"], r["to"]) for r in json.loads(out)["timeline"]]
        i = rows.index(("pass", "plan_jury", "x.tests"))
        assert rows[i + 1] == (kind, "x.tests", "tasking"), rows


def test_trigger_not_applying_skips():
    root = effort()
    add(root, "x", [step("tests", trigger={"plan_path": "nowhere/"})])
    pass_plan(root)
    lines = flow.load(root, S)[1]
    assert [(x["kind"], x["from"], x["to"]) for x in lines[-2:]] == [("pass", "plan_jury", "x.tests"), ("skip", "x.tests", "tasking")], lines
    assert lines[-1]["reason"] == "skipped: the plan touches no file under nowhere/"
    assert "state: tasking" in nio(root, "flow", "next", S)[1]


def two_efforts(trigger, *edits, dirs=()):
    """Efforts S, S2, ... at plan_jury in one repo, each from its own fixture edits; `x` with a triggered step; the plan
    gates passed."""
    slugs = [S] + [f"2026-10-2{i}-e" for i in range(1, len(edits))]
    root = None
    for slug, e in zip(slugs, edits):
        root = effort(slug=slug, root=root, edits=e)
    add(root, "x", [step("tests", trigger=trigger)])
    for d in dirs:  # a new file's folder exists, so the plan adds no module
        (root / d).mkdir(parents=True, exist_ok=True)
    for slug in slugs:
        pass_plan(root, slug)
    return root, slugs


def test_spec_level_trigger():
    root, (s1, s2) = two_efforts({"spec_level": "e2e"},
                                 [("spec/spec.md", "Given a paid order,", "Given a paid order noted as Level: e2e,")],
                                 [("spec/spec.md", "Level: integration.", "Level: e2e."), ("plan/tests.md", "(AC-1; integration)", "(AC-1; e2e)")])
    lines = flow.load(root, s1)[1]
    assert (lines[-1]["kind"], lines[-1]["from"], lines[-1]["to"], lines[-1]["reason"]) == (
        "skip", "x.tests", "tasking", "skipped: the spec has no AC at Level: e2e"), lines[-1]
    assert moves_of(root, s2)[-1] == ("pass", "plan_jury", "x.tests")
    assert "state: x.tests (working)" in nio(root, "flow", "next", s2)[1]


def test_plan_path_trigger():
    root, (s1, s2, s3) = two_efforts({"plan_path": "web/"},
                                     [("plan/contracts.md", "`app.py:refund_order`", "`src/web/x.py:refund_order`")],
                                     [("plan/tests.md", "`tests/test_refunds.py:test_full_refund`", "`web/app.spec.ts:loads`")],
                                     [("plan/contracts.md", "`app.py:refund_order`", "`web/app.tsx:App`")], dirs=("src/web", "web"))
    lines = flow.load(root, s1)[1]
    assert (lines[-1]["kind"], lines[-1]["from"], lines[-1]["reason"]) == ("skip", "x.tests", "skipped: the plan touches no file under web/")
    for slug in (s2, s3):
        assert flow.where(root, slug)["stage"] == "x.tests", slug


def at_step(check, **kw):
    root = effort()
    add(root, "x", [step("tests", check=check, **kw)])
    pass_plan(root)
    return root


def test_check_zero_passes():
    root = at_step(f'test "$NIO_SLUG" = {S} && test "$NIO_STAGE" = x.tests && test -d "$NIO_EXTENSION_DIR" && echo ok >> passed.log')
    code, out = nio(root, "flow", "done", "x.tests", S, "--by", BY)
    assert code == 0, out
    assert (root / "passed.log").read_text() == "ok\n"  # the check ran once
    last = flow.load(root, S)[1][-1]
    assert (last["kind"], last["from"], last["to"], last["who"]["role"]) == ("pass", "x.tests", "tasking", "driver"), last
    assert "state: tasking" in nio(root, "flow", "next", S)[1]


def test_check_failing_records_tail():
    root = at_step("for i in $(seq 1 80); do echo line-$i; done; exit 3")
    code, out = nio(root, "flow", "done", "x.tests", S, "--by", BY)
    assert code == 1 and "check failed: exit 3" in out and "line-80" in out, out
    assert flow.where(root, S)["stage"] == "x.tests"
    last = flow.load(root, S)[1][-1]
    ev = last["evidence"]
    assert (last["kind"], last["from"], last["to"]) == ("fail", "x.tests", "x.tests"), last
    assert ev["code"] == 3 and ev["timed_out"] is False and ev["tail"] == [f"line-{i}" for i in range(31, 81)], ev


def test_misplaced_step_fails_at_check():
    root = effort("spec_jury")
    add(root, "x", [step("tests", after="spec_jury", check="test -f .nio/specs/$NIO_SLUG/tasks.md")])
    code, out = nio(root, "flow", "done", "spec_jury", S, "--commit", "--by", "human")
    assert code == 0, out
    assert moves_of(root)[-1] == ("pass", "spec_jury", "x.tests"), moves_of(root)
    code, out = nio(root, "flow", "done", "x.tests", S, "--by", BY)
    assert code == 1 and "check failed: exit 1" in out, out
    assert flow.where(root, S)["stage"] == "x.tests"


def test_remove_drops_the_step():
    root = effort()
    add(root, "x", [step("tests")])
    code, out = nio(root, "extensions", "remove", "x")
    assert code == 0, out
    assert not (root / ".nio/extensions/x").exists() and "x" not in json.loads((root / ".nio/extensions/record.json").read_text())
    assert "x.tests" not in flow.table(root)[0]
    pass_plan(root)
    assert moves_of(root)[-1] == ("pass", "plan_jury", "tasking"), moves_of(root)
    assert " x." not in nio(root, "flow", "status")[1]


S1, S2 = S, "2026-10-21-past"


def past_step(root=None, at=True):
    """S2 past `x.tests` (its pass to tasking written) and, with `at`, S1 at it."""
    root = effort(slug=S2, root=root)
    if at:
        effort(slug=S1, root=root)
    add(root, "x", [step("tests")])
    for slug in (S1, S2) if at else (S2,):
        pass_plan(root, slug)
    assert nio(root, "flow", "done", "x.tests", S2, "--by", BY)[0] == 0
    return root


def test_remove_at_step_and_past_step():
    root = past_step()
    code, out = nio(root, "extensions", "remove", "x")
    assert code == 1 and f"effort {S1} is at x.tests" in out and (root / ".nio/extensions/x").is_dir(), out
    before = snap(root)
    code, out = nio(root, "extensions", "add", str(src(tempfile.mkdtemp(), "x", version="2.0.0")))
    assert code == 1 and f"effort {S1} is at x.tests, which the new version drops or moves" in out and snap(root) == before, out
    assert nio(root, "flow", "abandon", S1, "stop", "--by", "human")[0] == 0
    files = flowfiles(root, S2)
    code, out = nio(root, "extensions", "remove", "x")
    assert code == 0, out
    assert flowfiles(root, S2) == files and "state: tasking" in nio(root, "flow", "next", S2)[1]
    root = past_step(at=False)
    files = flowfiles(root, S2)
    code, out = nio(root, "extensions", "add", str(src(tempfile.mkdtemp(), "x", version="2.0.0")))
    assert code == 0, out
    assert flowfiles(root, S2) == files and "state: tasking" in nio(root, "flow", "next", S2)[1]


def test_remove_hand_broken_extension():
    """T-8 (J-19), on TC-44's setup: a hand-broken extension is still removed, and no effort file is written."""
    for broken in ("hash", "unplaced"):
        root = past_step(at=False)
        files = flowfiles(root, S2)
        d = root / ".nio/extensions/x"
        if broken == "hash":
            (d / "skills/tests/SKILL.md").write_text("changed by hand\n")
        else:
            m = json.loads((d / "manifest.json").read_text())
            m["steps"][0]["after"] = "nowhere.step"
            (d / "manifest.json").write_text(json.dumps(m))
        code, out = nio(root, "extensions", "remove", "x")
        assert code == 0 and not d.exists(), (broken, out)
        assert flowfiles(root, S2) == files, broken


def test_hand_edit_skipping_gate_stops_flow():
    root = effort()
    add(root, "x", [step("tests")])
    pass_plan(root)
    d = root / ".nio/extensions/x"
    m = json.loads((d / "manifest.json").read_text())
    m["skip"] = ["plan_jury"]
    (d / "manifest.json").write_text(json.dumps(m))
    rec = json.loads((root / ".nio/extensions/record.json").read_text())
    rec["x"]["hash"] = extensions.digest(d)
    (root / ".nio/extensions/record.json").write_text(json.dumps(rec))
    files = flowfiles(root)
    for args in (("next", S, "--by", BY), ("done", "planning", S, "--by", BY)):
        code, out = nio(root, "flow", *args)
        assert code != 0 and "extension x breaks the add-only rule: skip would change built-in plan_jury" in out, out
    assert flowfiles(root) == files


def test_hand_edited_check_needs_add_again():
    root = effort()
    add(root, "x", [step("tests")])
    pass_plan(root)
    d = root / ".nio/extensions/x"
    before = json.loads((root / ".nio/extensions/record.json").read_text())["x"]
    m = json.loads((d / "manifest.json").read_text())
    m["steps"][0]["check"] = "false"
    (d / "manifest.json").write_text(json.dumps(m))
    files = flowfiles(root)
    for args in (("next", S, "--by", BY), ("done", "x.tests", S, "--by", BY)):
        code, out = nio(root, "flow", *args)
        assert code != 0 and "extension x changed since it was added" in out and "nio extensions add .nio/extensions/x" in out, out
    assert flowfiles(root) == files
    assert nio(root, "extensions", "add", ".nio/extensions/x")[0] == 0
    code, out = nio(root, "flow", "next", S)
    assert code == 0 and "x.tests" in out, out
    after = json.loads((root / ".nio/extensions/record.json").read_text())["x"]
    assert after["source"] == before["source"] and after["version"] == before["version"] and after["hash"] != before["hash"]


def test_half_states_are_recoverable():
    def fresh():
        root = effort()
        add(root, "x", [step("tests")])
        return root, root / ".nio/extensions"
    for case in "abc":
        root, d = fresh()
        if case == "a":
            shutil.rmtree(d / "x")
        elif case == "b":
            (d / "record.json").write_text("{}")
        else:
            (d / "x/manifest.json").write_text("{not json")
        code, out = nio(root, "flow", "next", S, "--by", BY)
        want = "extension x changed since it was added" if case == "c" else "extension x is half added or removed: run nio extensions remove x"
        assert code != 0 and want in out, (case, out)
        assert nio(root, "extensions", "remove", "x")[0] == 0
        assert not (d / "x").exists() and "x" not in json.loads((d / "record.json").read_text()), case
        assert nio(root, "flow", "next", S, "--by", BY)[0] == 0, case
    root, d = fresh()
    (d / ".x.new").mkdir()
    (d / ".x.new/manifest.json").write_text("{}")
    assert nio(root, "flow", "next", S, "--by", BY)[0] == 0
    code, out = nio(root, "extensions", "list")
    assert code == 0 and out.count("x \u00b7") == 1 and ".x.new" not in out, out


# --- an extension step can have its own jury gate (E-4) ---

def gate_effort(auto=False):
    """S at x.tests with x's gate (lens x-lens), x.md written."""
    root = effort()
    n = test_flow.grant_on(root, "plan_jury") if auto else 0
    add(root, "x", [step("tests", output="x.md", gate={"lenses": ["x-lens"]})], cards=["x-lens"],
        files={"agents/x-lens.md": "---\nname: x-lens\ndescription: x lens\ntier: medium\neffort: low\n---\nJudge x.\n"})
    pass_plan(root)
    (root / ".nio/specs" / S / "x.md").write_text("# x\n")
    return (root, n) if auto else root


def gate_approved(root, gate, commit=True):
    """A real jury round that approves the extension gate with its lens, then the `nio: approve` commit."""
    run = f"R-{gate}"
    path = root / ".nio/runs" / run / "jury" / f"{gate}-x-lens.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nlens: x-lens\ngate: {gate}\nsubject: {S}\nby: \"juror / claude-code / opus\"\n"
                    "context: sufficient\n---\n## Reasoning\nChecked.\n\n## Findings\nnone\n")
    from nio import jury
    jury.collect(root, S, gate, run)
    assert jury.check(root, S, gate, record=True)[0] == "approved"
    if commit:
        test_flow.git(root, "add", "-A")
        test_flow.git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", f"nio: approve {gate}")


def test_extension_gate_runs_its_jury():
    root = gate_effort()
    assert nio(root, "flow", "done", "x.tests", S, "--by", BY)[0] == 0
    assert flow.where(root, S)["stage"] == "x.tests.jury"
    code, out = nio(root, "jury", "plan", S, "x.tests")
    assert code == 0 and "x-lens (core)" in out and out.count("(") == out.count("(core)") + out.count("(~"), out
    assert "lenses: x-lens (core)" in out, out
    code, out = nio(root, "flow", "done", "x.tests.jury", S, "--commit", "--by", "human")
    assert code != 0 and flow.where(root, S)["stage"] == "x.tests.jury", out
    gate_approved(root, "x.tests", commit=False)
    code, out = nio(root, "flow", "done", "x.tests.jury", S, "--commit", "--by", "human")
    assert code == 0, out
    assert (root / ".nio/specs" / S / "jury/x.tests.json").exists()
    assert "nio: approve x.tests" in test_flow.git(root, "log", "--format=%s")
    assert flow.where(root, S)["stage"] == "tasking"


def test_auto_extension_gate():
    root, n = gate_effort(auto=True)
    nio(root, "flow", "done", "x.tests", S, "--by", BY)
    gate_approved(root, "x.tests", commit=False)
    code, out = nio(root, "flow", "done", "x.tests.jury", S, "--by", BY)
    assert code == 0, out
    line = next(x for x in flow.load(root, S)[1] if x["kind"] == "pass" and x["from"] == "x.tests.jury")
    assert line["to"] == "tasking" and line["who"]["role"] == "driver" and line["evidence"]["auto"]["grant"] == n, line
    assert "nio: approve x.tests" in test_flow.git(root, "log", "--format=%s")
    # case two: the outcome is human with a finding open
    root, _ = gate_effort(auto=True)
    nio(root, "flow", "done", "x.tests", S, "--by", BY)
    test_flow.ledger(root, "x.tests", round=1, outcome="human", findings=[test_flow.finding("J-1")])
    code, out = nio(root, "flow", "done", "x.tests.jury", S, "--by", BY)
    assert code == 1 and not [x for x in flow.load(root, S)[1] if x["kind"] == "pass" and x["from"] == "x.tests.jury"], out
    _, got = nio(root, "flow", "next", S)
    ref = test_flow.effort("plan_jury")
    test_flow.grant_on(ref, "plan_jury")
    test_flow.ledger(ref, "plan", round=1, outcome="human", findings=[test_flow.finding("J-1")])
    nio(ref, "flow", "done", "plan_jury", S, "--by", BY)
    _, want = nio(ref, "flow", "next", S)
    pick = lambda t: [x for x in t.replace("x.tests.jury", "plan_jury").splitlines() if x.split(":")[0] in ("state", "skill", "next", "done")]
    assert pick(got) == pick(want) and pick(got), (got, want)


def test_extension_gate_rejected_goes_back():
    root = gate_effort()
    nio(root, "flow", "done", "x.tests", S, "--by", BY)
    from nio import jury
    led = jury.load(root, S, "x.tests")
    jury.save(root, {**led, "round": 1, "outcome": "rejected", "versions": {"1": jury.version_now(root, S, "x.tests")}})
    code, out = nio(root, "flow", "next", S)
    assert code == 0 and "state: x.tests (working: the x.tests jury rejected round 1)" in out, out


# --- cards and hooks (E-5) ---

def test_agents_sync_renders_extension_cards():
    root, tmp = fixture()
    (root / ".nio").mkdir(exist_ok=True)
    (root / ".nio/config.json").write_text(json.dumps({"agents": {"hosts": ["claude", "codex"]}}))
    card = "---\nname: x-card\ndescription: x card\ntier: strong\neffort: low\n---\n## Job\n\nJudge the x thing.\n\n## Inputs\n\nThe pack.\n\n## Output format\n\nA list.\n\n## Stop when\n\nDone.\n"
    assert nio(root, "extensions", "add", str(src(tmp, "x", cards=["x-card"], files={"agents/x-card.md": card})))[0] == 0
    code, out = nio(root, "agents", "sync")
    assert code == 0, out
    for rel in (".claude/agents/nio-x-card.md", ".codex/agents/nio-x-card.toml"):
        assert "Judge the x thing." in (root / rel).read_text(), rel


def hook(command, event="step-passed", **kw):
    return {"event": event, "command": command, **kw}


def hooks_of(root):
    return [x["evidence"] for x in flow.load(root, S)[1] if x["kind"] == "hook"]


def test_gate_approved_hook_runs_once():
    root = effort()
    copy = Path(tempfile.mkdtemp()) / "copy"
    shutil.copytree(root, copy)
    add(root, "x", hooks=[hook("echo $NIO_EVENT $NIO_STAGE $(git log -1 --format=%s) >> hook.log", "gate-approved")])
    pass_plan(root)
    assert (root / "hook.log").read_text() == "gate-approved plan_jury nio: approve plan\n"
    got = hooks_of(root)
    assert len(got) == 1 and (got[0]["extension"], got[0]["event"], got[0]["code"]) == ("x", "gate-approved", 0), got
    # a copy where git refuses the approval commit: no hook runs
    add(copy, "x", hooks=[hook("echo hi >> hook.log", "gate-approved")])
    h = copy / ".git/hooks/pre-commit"
    h.write_text("#!/bin/sh\nexit 1\n")
    h.chmod(0o755)
    assert nio(copy, "flow", "done", "plan_jury", S, "--commit", "--by", "human")[0] != 0
    assert not (copy / "hook.log").exists() and not hooks_of(copy)


def at_planning(*named):
    root = effort("plan_jury")
    for name, hooks in named:
        add(root, name, hooks=hooks)
    return root


def test_hooks_run_in_name_order():
    root = at_planning(("b", [hook("echo b >> order.log")]), ("a", [hook("echo a >> order.log")]))
    pass_plan(root)
    assert (root / "order.log").read_text() == "a\nb\n"
    assert [h["extension"] for h in hooks_of(root)] == ["a", "b"]


def test_failing_hook_never_blocks():
    root = at_planning(("x", [hook("echo nope; exit 4")]))
    pass_plan(root)
    (h,) = hooks_of(root)
    assert h["code"] == 4 and h["tail"] == ["nope"], h
    ref = effort("plan_jury")
    pass_plan(ref)
    assert flow.where(root, S)["stage"] == flow.where(ref, S)["stage"]


def test_timeouts_stop_commands():
    import time
    root = effort()
    add(root, "x", [step("tests", check="sleep 5 # nio-t-check", timeout=1)], hooks=[hook("sleep 5 # nio-t-hook", timeout=1)])
    pass_plan(root)
    t = time.time()
    code, out = nio(root, "flow", "done", "x.tests", S, "--by", BY)
    assert time.time() - t < 5 and code == 1 and "check timed out after 1 seconds" in out, out
    assert flow.load(root, S)[1][-1]["evidence"]["timed_out"] is True
    add(root, "x", [step("tests", check="true", timeout=1)], hooks=[hook("sleep 5 # nio-t-hook", timeout=1)])
    t = time.time()
    assert nio(root, "flow", "done", "x.tests", S, "--by", BY)[0] == 0
    assert time.time() - t < 5 and hooks_of(root)[-1]["timed_out"] is True
    r = subprocess.run(["pgrep", "-af", "^/bin/sh -c sleep 5 # nio-t-"], capture_output=True, text=True)
    assert r.returncode == 1, r.stdout
    for bad in (0, 1.5, "1"):
        code, out = nio(root, "extensions", "add", str(src(tempfile.mkdtemp(), "y", [step("s", timeout=bad)])))
        assert code == 1 and "steps[0].timeout must be a whole number of seconds of at least 1" in out, (bad, out)



# --- the shipped e2e tester (E-6) ---

ORIG_PATH = os.environ["PATH"]
NPX = ('#!/usr/bin/env python3\nimport json, os, sys\nd = os.path.dirname(os.path.abspath(__file__))\n'
       'open(os.path.join(d, "npx.log"), "a").write(json.dumps(sys.argv[1:]) + "\\n")\nc = json.load(open(os.path.join(d, "stub.json")))\n'
       'if c.get("report") is not None and os.environ.get("PLAYWRIGHT_JSON_OUTPUT_NAME"):\n'
       '    open(os.environ["PLAYWRIGHT_JSON_OUTPUT_NAME"], "w").write(json.dumps(c["report"]))\nprint(c.get("out", ""))\nsys.exit(c.get("code", 0))\n')


def npx_stub(code=0, out="", report=None, d=None):
    """A fake `npx` first on PATH: logs its argv to npx.log, prints `out`, writes `report` where Playwright's JSON reporter
    would, exits `code`. Called again with `d`, it changes the answer."""
    d = d or Path(tempfile.mkdtemp())
    if not (d / "npx").exists():
        (d / "npx").write_text(NPX)
        (d / "npx").chmod(0o755)
    (d / "stub.json").write_text(json.dumps({"code": code, "out": out, "report": report}))
    os.environ["PATH"] = f"{d}:{ORIG_PATH}"
    return d


def test_tasks_name_the_e2e_test():
    import test_tasks as tt
    from nio import implement, spec, tasks
    root = tt.repo(write=False)
    folder = spec.path(root, tt.SLUG).parent
    sp = (folder / "spec.md").read_text().replace("Level: integration.", "Level: e2e.")
    (folder / "spec.md").write_text(sp.replace("- **AC-2**", "- **AC-3** (FR-2) Given x, when y, then z. [human]\n  Observable: z. Level: unit.\n- **AC-2**", 1))
    (folder / "tests.md").write_text((folder / "tests.md").read_text().split("## Quality tests")[0].replace(
        "tests/test_refunds.py:test_full_refund` (new)", "e2e/a.spec.ts:AC-1 loads`").replace(
        "tests/test_refunds.py:test_second_refund` (new)", "e2e/b.spec.ts:AC-2 shows (x)`").replace(
        "(AC-2; integration)", "(AC-2; e2e)").replace("(AC-1; integration)", "(AC-1; e2e)") +
        "### TC-3 Three (AC-3; unit) [default]\n- File: `tests/test_app.py:test_three`\n- Covers: CT-1\n\n")
    (root / "playwright.config.ts").write_text("export default {};\n")
    (root / ".nio/config.json").write_text(json.dumps({"tests": {"suite": "python -m pytest"}}))
    mk = lambda one: tt.TASKS.split("## E-1")[0] + (
        "## E-1 Refunds (US-1)\n- Tier: max: x\n- Effort: med\n\n"
        f"### T-1 One\n- Files: `app.py`\n- Serves: AC-1, AC-2\n- Test: {one}\n- Depends on: none\n- Parallel: no\n\n"
        "### T-2 Two\n- Files: `app.py`\n- Serves: AC-3\n- Test: TC-3\n- Depends on: T-1\n- Parallel: no\n")
    tasks.path(root, tt.SLUG).write_text(mk("TC-3"))
    errs = [e for e in tt.errs(root) if "Level: e2e" in e]
    assert errs == [f"T-1 serves AC-{n} (Level: e2e) but its Test: cites no TC aimed at it" for n in (1, 2)], errs
    tasks.path(root, tt.SLUG).write_text(mk("TC-1, TC-2"))
    assert not [e for e in tt.errs(root) if "Level: e2e" in e]
    got = implement.epic_tests(root, tt.SLUG, implement.tasks_of(root, tt.SLUG))[0]
    assert got == r"npx playwright test e2e/a.spec.ts e2e/b.spec.ts -g 'AC\-1\ loads|AC\-2\ shows\ \(x\)' && python -m pytest tests/test_app.py::test_three", got


def pw_effort(code, tasks=None):
    """test_implement's refunds effort whose TC-1 is the Playwright test `e2e/a.spec.ts:AC-1 loads`, a playwright config
    committed, `npx` stubbed to exit `code`; (root, stub folder)."""
    import test_implement as ti
    root = ti.impl(tasks=tasks, tests_md=lambda t: t.replace("`tests/test_refund.py:T.test_refund`", "`e2e/a.spec.ts:AC-1 loads`"))
    (root / "playwright.config.ts").write_text("export default {};\n")
    ti.commit_all(root, "playwright config")
    return root, npx_stub(code, "1 failed" * bool(code))


def test_failing_e2e_keeps_epic_open():
    import test_implement as ti
    one = "## E-1 Customer refunds a paid order (US-1)\n- Tier: max: x\n- Effort: med\n\n### T-1 Refund\n- Files: `app.py`\n- Serves: AC-1\n- Test: TC-1\n- Depends on: none\n- Parallel: no\n"
    root, d = pw_effort(1, ti.REFUNDS.split("## E-1")[0] + one)
    code, out = ti.flow(root, "claim", ti.S)
    assert code == 0, out
    code, out = ti.flow(root, "finish", ti.S, "E-1")
    assert code != 0, out
    lines = ti.lines(root)
    ev = [x["evidence"] for x in lines if x["kind"] == "epic_test"][-1]
    assert ev["passed"] is False and "npx playwright test e2e/a.spec.ts -g" in ev["command"], ev
    assert not [x for x in lines if x["kind"] == "task_done"]
    assert json.loads((d / "npx.log").read_text().splitlines()[-1])[:4] == ["playwright", "test", "e2e/a.spec.ts", "-g"]


def test_pr_evidence_lists_e2e_tests():
    import test_effort as te
    import test_evidence as tev
    import test_implement as ti
    from nio import evidence
    for code, want in ((1, "failed"), (0, "passed")):
        root, d = pw_effort(0, ti.TWO)
        for eid in ("E-1", "E-2"):
            ti.close_epic(root, eid)
        npx_stub(code, d=d)
        (d / "npx.log").unlink()
        run, _ = tev.pr_run(root)
        got = [x for x in evidence.load(root, run)["tests"] if x["file"] == "e2e/a.spec.ts"]
        assert [(x["name"], x["result"]) for x in got] == [("AC-1 loads", want)], got
        log = (d / "npx.log").read_text().splitlines()
        assert len(log) == 1 and json.loads(log[0])[-1] == "AC\\-1\\ loads", log


def test_add_shipped_e2e():
    root, tmp = fixture()
    shipped = Path(__file__).parent.parent / "src/nio/shipped/e2e"
    code, out = nio(root, "extensions", "add", "e2e")
    assert code == 0, out
    mine = root / ".nio/extensions/e2e"
    files = lambda d: {str(p.relative_to(d)): p.read_bytes() for p in d.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    assert files(mine) == files(shipped)
    from importlib import metadata
    rec = json.loads((root / ".nio/extensions/record.json").read_text())["e2e"]
    assert rec["source"] == "shipped" and rec["version"] == metadata.version("nio"), rec
    home = Path(os.environ["NIO_HOME"]) / "extensions/e2e"
    shutil.copytree(shipped, home)
    (home / "manifest.json").write_text((home / "manifest.json").read_text().replace('"1.0.0"', '"9.9.9"'))
    code, out = nio(root, "extensions", "add", "e2e")
    rec = json.loads((root / ".nio/extensions/record.json").read_text())["e2e"]
    assert code == 0 and rec["version"] == "9.9.9" and rec["source"].endswith("extensions/e2e"), (out, rec)


def test_nothing_names_the_e2e_extension():
    base = Path(__file__).parent.parent / "src/nio"
    shipped = base / "shipped/e2e"
    for p in base.rglob("*"):
        if p.is_file() and shipped not in p.parents and "__pycache__" not in p.parts:
            text = p.read_text(errors="ignore")
            assert not [w for w in ("shipped/e2e", "e2e-tester", "e2e.tests") if w in text], p
    assert extensions.check(shipped, None, [], extensions.stage_names([])) == []
    root, tmp = fixture()
    broken = Path(tmp) / "broken"
    shutil.copytree(shipped, broken)
    m = json.loads((broken / "manifest.json").read_text())
    del m["version"]
    (broken / "manifest.json").write_text(json.dumps(m))
    refused(root, broken, "missing field version")


CHECK = Path(__file__).parent.parent / "src/nio/shipped/e2e/check.py"


def e2e_spec(root, acs):
    """A repo with a spec whose ACs are at Level: e2e, a TC for each aimed at it, and its test file `e2e/<AC>.spec.ts`
    holding the test `<AC> shows the page`."""
    d = root / ".nio/specs" / S
    d.mkdir(parents=True, exist_ok=True)
    (d / "spec.md").write_text("## Acceptance criteria\n\n" + "".join(
        f"- **{ac}** (FR-1) Given x, when y, then z. [agent]\n  Observable: z. Level: e2e.\n" for ac in acs))
    (d / "tests.md").write_text("## Acceptance tests\n\n" + "".join(
        f"### TC-{n} Shows (AC-{n}; e2e) [agent]\n- File: `e2e/AC-{n}.spec.ts:AC-{n} shows the page` (new)\n\n" for n in range(1, len(acs) + 1)))
    (root / "e2e").mkdir(exist_ok=True)
    for ac in acs:
        (root / f"e2e/{ac}.spec.ts").write_text(f"test('{ac} shows the page', async ({{ page }}) => {{}});\n")
    return root


def report(*results, errors=()):
    """A Playwright JSON report: one (status, message) per test, named AC-n shows the page."""
    specs = [{"title": f"AC-{n} shows the page", "tests": [{"results": [{"status": st, "error": {"message": msg},
              "attachments": [{"name": "trace", "path": f"{os.getcwd()}/test-results/x/trace.zip"}]}]}]}
             for n, (st, msg) in enumerate(results, 1)]
    return {"suites": [{"title": "f", "specs": specs, "suites": []}], "errors": list(errors)}


def run_check(root, **stub):
    npx_stub(**stub)
    r = subprocess.run([sys.executable, str(CHECK)], cwd=root, capture_output=True, text=True, env={**os.environ, "NIO_SLUG": S})
    return r.returncode, r.stdout + r.stderr


FAIL = ("failed", "Error: expect(locator).toBeVisible() failed")


def test_e2e_check_wants_assertion_failures():
    root = e2e_spec(repo(), ["AC-1", "AC-2"])
    code, out = run_check(root, code=1, report=report(FAIL, FAIL))
    assert code == 0 and "e2e: 2 tests fail on their assertions, as they should before implementation" in out, out
    (root / "e2e/AC-2.spec.ts").unlink()
    code, out = run_check(root, code=1, report=report(FAIL, FAIL))
    assert code == 1 and "AC-2 has no e2e test" in out, out
    e2e_spec(root, ["AC-1", "AC-2"])
    code, out = run_check(root, code=1, report=report(("passed", ""), FAIL))
    assert code == 1 and "AC-1 AC-1 shows the page: passes before any code is written" in out, out


def test_e2e_check_app_not_started():
    root = e2e_spec(repo(), ["AC-1"])
    line = "Error: Process from config.webServer was not able to start. Exit code: 1"
    code, out = run_check(root, code=1, out=line)
    assert code == 1 and "setup error: the app didn't start" in out and line in out and "fail on their assertions" not in out, out


def test_e2e_check_failure_kinds():
    root = e2e_spec(repo(), ["AC-1"])
    page = "Error: expect(page).toHaveTitle(expected) failed"
    colour = "\u001b[31mError: \u001b[39mexpect(\u001b[2mpage\u001b[22m).toHaveTitle(\u001b[32mexpected\u001b[39m) failed"
    boom = lambda m: {"suites": [], "errors": [{"message": m, "location": {"file": f"{root}/e2e/AC-1.spec.ts"}}]}
    for rep in (report(("failed", page)), report(("failed", colour))):
        assert run_check(root, code=1, report=rep)[0] == 0
    for rep, text in ((boom("SyntaxError: Unexpected token"), "setup error: e2e/AC-1.spec.ts: SyntaxError"),
                      (boom("Error: Cannot find module './nope'"), "setup error: e2e/AC-1.spec.ts: Error: Cannot find module"),
                      (report(("timedOut", "Test timeout of 30000ms exceeded.")),
                       "AC-1 AC-1 shows the page: fails on Test timeout of 30000ms exceeded., not on a web-first assertion"),
                      (report(("failed", "Error: expect(received).toBe(expected)")),
                       "AC-1 AC-1 shows the page: fails on Error: expect(received).toBe(expected), not on a web-first assertion")):
        code, out = run_check(root, code=1, report=rep)
        assert code == 1 and text in out, out


selfcheck.main([v for k, v in list(globals().items()) if k.startswith("test_") and callable(v)])
