"""Self-check for nio new / nio check. Run: uv run python tests/test_records.py"""
import json
import subprocess
import tempfile
from pathlib import Path

from nio import records

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
    assert any("superseded by several" in e for e in errors(root))
    # verdicts carry `outcome`, never `status`
    v = records.new(root, "verdict", "auth", "Sessions ruling", run="R-261024-a1b2")
    v.write_text(v.read_text().replace("outcome:", "status: approved\noutcome:", 1))
    assert any("unknown field `status`" in e and v.name in e for e in errors(root))
    print("ok")


if __name__ == "__main__":
    test()
