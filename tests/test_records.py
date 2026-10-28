"""Self-check for nio new / nio check. Run: uv run python tests/test_records.py"""
import json
import subprocess
import tempfile
from pathlib import Path

from nio import records

# every suite imports this module: one temp folder per run, removed at exit, holds every fixture repo
_TMP = tempfile.TemporaryDirectory(prefix="nio-test-")
tempfile.tempdir = _TMP.name

GOOD_BODY = """## Decision
Store sessions in Redis.
## Why
A Postgres sessions table adds a write on every request.
## Rejected alternatives
- Postgres: one write per request.
## Reuse
Any per-request state.
"""


def repo():
    root = Path(tempfile.mkdtemp())
    run = lambda *a: subprocess.run(["git", *a], cwd=root, check=True, capture_output=True)
    run("init", "-q")
    (root / ".nio").mkdir()
    (root / ".nio/config.json").write_text(json.dumps({"memory": {"areas": ["auth"]}}))
    (root / "app.py").write_text("")
    run("add", "-A")
    run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
    return root


def fill(path, body=GOOD_BODY, **fields):
    head, _ = path.read_text().split("\n---\n", 1)
    for k, v in fields.items():
        head = "\n".join(f"{k}: {v}" if line.startswith(f"{k}:") else line for line in head.splitlines())
    path.write_text(head + "\n---\n" + body)


def errors(root):
    return records.check(root)[0]


def test():
    assert records.slug("Spec gate for refund-double-charge: approved") == "spec-gate-for-refund-double-charge"
    assert records.slug("Don't store it/keep it") == "dont-store-it-keep-it"
    root = repo()
    # a fresh template fails until filled in
    p = records.new(root, "decision", "auth", 'Sessions in "Redis"')
    assert any("TODO" in e for e in errors(root))
    fill(p, paths='["app.py"]')
    assert errors(root) == [], errors(root)

    # unlisted area is refused at creation and caught by check
    try:
        records.new(root, "decision", "billing", "x")
        raise AssertionError("unlisted area accepted")
    except ValueError:
        pass
    (root / ".nio/memory/billing").mkdir()
    bad = root / ".nio/memory/billing" / p.name
    bad.write_text(p.read_text().replace(p.name[:13], "D-261024-zzzz"))
    bad.rename(bad.with_name("D-261024-zzzz-x.md"))
    assert any("not a listed area" in e for e in errors(root))
    (root / ".nio/memory/billing/D-261024-zzzz-x.md").unlink()

    # YAML 1.2 keeps `no` a string; an unquoted number is still rejected
    fill(p, title="no")
    assert errors(root) == [], errors(root)
    fill(p, title="42")
    assert any("quoted string" in e for e in errors(root))
    fill(p, title='"ok"')

    # Why that repeats the Decision; unknown link; new path that matches nothing
    fill(p, body=GOOD_BODY.replace("A Postgres sessions table adds a write on every request.", "Store sessions in Redis."))
    assert any("repeats" in e for e in errors(root))
    fill(p, supersedes='["D-261024-aaaa"]', paths='["nope.py"]')
    errs = errors(root)
    assert any("unknown record" in e for e in errs) and any("nope.py" in e for e in errs), errs

    # two records superseding the same one is a conflict
    fill(p, supersedes="[]", paths='["app.py"]')
    old = p.name[:13]
    for t in ("A", "B"):
        q = records.new(root, "decision", "auth", f"Replace {t}")
        fill(q, supersedes=f'["{old}"]')
    errs = errors(root)
    assert any("superseded by several" in e for e in errs)
    # the old record must be flagged with both, and may only name records that supersede or challenge it
    assert sum("add `outdated_by" in e for e in errs) == 2, errs
    news = sorted(q.name[:13] for q in (root / ".nio/memory/auth").glob("*-replace-*.md"))
    p.write_text(p.read_text().replace("\n---\n", f'\noutdated_by: {json.dumps(news + [old])}\n---\n', 1))
    assert any("neither supersedes" in e for e in errors(root))
    p.write_text(p.read_text().replace(f', "{old}"]', "]"))
    # ...unless a verdict rejected one of them; a fresh verdict must have outcome and tier chosen
    v = records.new(root, "verdict", "auth", "Replace A ruling", by="writer / t / t")
    errs = errors(root)
    assert any("`outcome`" in e and v.name in e for e in errs) and any("`tier`" in e and v.name in e for e in errs), errs
    a = next((root / ".nio/memory/auth").glob("*-replace-a.md"))
    vbody = "## Ruling\nNo.\n## Jurors\n| a | b | c | no |\n## Reasons\nWrong.\n## What was rejected\nA.\n"
    fill(v, body=vbody, subject=a.name[:13], outcome="rejected", tier="low")
    assert errors(root) == [], errors(root)
    # verdicts carry `outcome`, never `status`
    v.write_text(v.read_text().replace("outcome:", "status: approved\noutcome:", 1))
    assert any("unknown field `status`" in e and v.name in e for e in errors(root))
    v.write_text(v.read_text().replace("status: approved\n", ""))
    # a verdict sits in its subject's area
    (root / ".nio/config.json").write_text(json.dumps({"memory": {"areas": ["auth", "project"]}}))
    (root / ".nio/memory/project").mkdir()
    moved = v.rename(root / ".nio/memory/project" / v.name)
    assert any("subject's area" in e for e in errors(root))
    moved.rename(v)
    # stored jury standing is gone: `approved` is no longer a status
    fill(p, status="approved")
    assert any("`status`" in e for e in errors(root))
    fill(p, status="human")
    # a path to a new, not yet added file is fine; an ignored one is not
    (root / "new.py").write_text("")
    (root / ".gitignore").write_text("ignored.py\n")
    (root / "ignored.py").write_text("")
    fill(p, paths='["new.py"]')
    assert errors(root) == [], errors(root)
    fill(p, paths='["ignored.py"]')
    assert any("ignored.py" in e for e in errors(root))
    # runs get an R- ID and an empty promote.md
    rid = records.new_run(root)
    assert rid.startswith("R-") and (root / ".nio/runs" / rid / "promote.md").exists()
    print("ok")


def commit(root, msg="c"):
    for a in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", msg]):
        subprocess.run(["git", *a], cwd=root, check=True, capture_output=True)


def test_history():
    root = repo()
    git = lambda *a: subprocess.run(["git", *a], cwd=root, check=True, capture_output=True)
    p = records.new(root, "decision", "auth", "Sessions")
    fill(p, paths='["app.py"]')
    commit(root)
    rid = p.name[:13]
    added = records.added_in(root)[rid]
    # a renamed file is followed through git history, so the old path is not stale
    git("mv", "app.py", "main.py")
    commit(root, "rename")
    assert records.touches(["app.py"], records.git(root, "ls-files"), records.renamed_since(root, added)) == ["main.py"]
    errors, warnings, _ = records.check(root)
    assert not errors and not warnings, (errors, warnings)
    # a deleted file is stale: warning only
    git("rm", "-q", "main.py")
    commit(root, "delete")
    assert any("app.py" in w for w in records.check(root)[1])
    # a committed record may change `paths` and nothing else
    (root / "new.py").write_text("")
    fill(p, paths='["new.py"]')
    assert records.check(root)[0] == [], records.check(root)[0]
    fill(p, paths='["new.py"]', title='"Sessions, renamed"')
    assert any("may only change `paths`" in e for e in records.check(root)[0])
    fill(p, paths='["new.py"]', title='"Sessions"', body=GOOD_BODY + "More.\n")
    assert any("may only change `paths`" in e for e in records.check(root)[0])
    fill(p, paths='["new.py"]', body=GOOD_BODY)
    commit(root, "repath")
    # `outdated_by` may be added to a committed record, but never shrinks
    q = records.new(root, "decision", "auth", "Sessions v2")
    fill(q, supersedes=f'["{rid}"]', paths='["new.py"]')
    assert any("add `outdated_by" in e for e in records.check(root)[0])
    p.write_text(p.read_text().replace("\n---\n", f'\noutdated_by: ["{q.name[:13]}"]\n---\n', 1))
    assert records.check(root)[0] == [], records.check(root)[0]
    commit(root, "supersede")
    p.write_text(p.read_text().replace(f'outdated_by: ["{q.name[:13]}"]', "outdated_by: []"))
    assert any("may only grow" in e for e in records.check(root)[0])
    p.write_text(p.read_text().replace("outdated_by: []", f'outdated_by: ["{q.name[:13]}"]'))
    # ...also once committed, checked against an older base as CI does
    assert records.check(root, added)[0] == [], records.check(root, added)[0]
    fill(p, paths='["new.py"]', title='"Sessions, renamed"')
    commit(root, "sneaky edit")
    assert records.check(root)[0] == [] and any("only change `paths`" in e for e in records.check(root, added)[0])
    fill(p, paths='["new.py"]', title='"Sessions"')
    commit(root, "undo")
    # moving a record to another area keeps its ID's commit
    (root / ".nio/config.json").write_text(json.dumps({"memory": {"areas": ["auth", "core"]}}))
    (root / ".nio/memory/core").mkdir()
    git("mv", str(p.relative_to(root)), f".nio/memory/core/{p.name}")
    commit(root, "move")
    assert records.added_in(root)[rid] == added
    assert records.check(root)[0] == [], records.check(root)[0]
    print("ok")


if __name__ == "__main__":
    test()
    test_history()
