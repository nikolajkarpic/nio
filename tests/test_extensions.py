"""Self-check for nio extensions add / list / remove. Run: uv run python tests/test_extensions.py"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from test_records import repo

import selfcheck

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


selfcheck.main([v for k, v in list(globals().items()) if k.startswith("test_")])
