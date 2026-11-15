"""Self-check for nio hooks and the cross-branch merge check. Run: uv run python tests/test_hooks.py"""
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from test_index import flag
from test_records import GOOD_BODY, commit, fill, repo

from nio import hooks, records
import selfcheck


def git(root, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=root, capture_output=True, text=True)


def wait_for(path, lines):
    for _ in range(50):  # the hooks start nio in the background
        if path.exists() and len(path.read_text().splitlines()) >= lines:
            return path.read_text().splitlines()
        time.sleep(0.1)
    return path.read_text().splitlines() if path.exists() else []


def test_install():
    root = repo()
    log = root / "calls.log"
    fake = root / "fake-nio"
    fake.write_text(f'#!/bin/sh\necho "$@" >> {log}\n')
    fake.chmod(0o755)
    (root / ".git/hooks/post-merge").write_text("#!/bin/sh\necho mine >> theirs.log\n")
    hooks.install(root, str(fake))
    merge = root / ".git/hooks/post-merge"
    merge.write_text(merge.read_text().replace("agents sync", "old-step"))  # a hook from an older nio
    merge.write_text(merge.read_text() + "echo after >> theirs.log\n")
    hooks.install(root, str(fake))  # twice replaces the block instead of adding a second
    text = merge.read_text()
    assert text.count(hooks.MARK) == 1 and "echo mine" in text and "echo after" in text and "old-step" not in text, text
    # a branch switch refreshes the index and the agent files; checking out a single file does not
    assert git(root, "checkout", "-q", "-b", "other").returncode == 0
    assert sorted(wait_for(log, 2)) == ["agents sync", "index"], wait_for(log, 2)
    assert git(root, "checkout", "-q", "--", "app.py").returncode == 0
    time.sleep(0.5)
    assert len(wait_for(log, 2)) == 2
    # with nio gone the hooks do nothing, and git still succeeds
    fake.unlink()
    assert git(root, "checkout", "-q", "-").returncode == 0
    print("ok")


def test_two_branches_supersede_the_same_decision():
    """Both branches flag the old record, so git stops at that line; once resolved, the check CI runs fails,
    and so does the post-merge hook's on a merge that went through."""
    root = repo()
    old = records.new(root, "decision", "auth", "Sessions in Redis")
    fill(old, paths='["app.py"]')
    commit(root)
    base = git(root, "branch", "--show-current").stdout.strip()
    rids = []
    for name in ("Valkey", "Memcached"):
        git(root, "checkout", "-q", "-b", name.lower(), base)
        new = records.new(root, "decision", "auth", f"Sessions in {name}")
        fill(new, paths='["app.py"]', supersedes=f'["{old.name[:13]}"]', body=GOOD_BODY.replace("Redis", name))
        flag(old, new.name[:13])
        commit(root, name)
        rids.append(new.name[:13])
    git(root, "checkout", "-q", "valkey")
    assert git(root, "merge", "-q", "memcached").returncode, "git should stop at the flagged line"
    head, rest = old.read_text().split("<<<<<<<", 1)
    old.write_text(head + f'outdated_by: ["{rids[0]}", "{rids[1]}"]\n' + rest.split(">>>>>>>", 1)[1].split("\n", 1)[1])
    commit(root, "merge")
    assert any("superseded by several records" in e for e in records.check(root, base)[0])
    hooks.install(root, str(Path(sys.prefix) / "bin/nio"))
    out = subprocess.run([str(root / ".git/hooks/post-merge"), "0"], cwd=root, capture_output=True, text=True).stdout
    assert "superseded by several records" in out and "nio: memory has errors after this merge" in out, out
    print("ok")


def test_checks_block_commit_and_push():
    """pre-commit and pre-push run the CI check and stop git when memory is broken."""
    root = repo()
    remote = root.parent / f"{root.name}-remote.git"
    git(root.parent, "init", "-q", "--bare", str(remote))
    git(root, "remote", "add", "origin", str(remote))
    assert git(root, "push", "-q", "-u", "origin", "HEAD").returncode == 0
    hooks.install(root, str(Path(sys.prefix) / "bin/nio"))
    a = records.new(root, "decision", "auth", "Sessions in Redis")  # still has its template TODOs
    git(root, "add", "-A")
    bad = git(root, "commit", "-qm", "half-written record")
    assert bad.returncode and "TODO" in bad.stdout + bad.stderr and "nio: memory check failed" in bad.stdout + bad.stderr, bad
    fill(a, paths='["app.py"]')
    git(root, "add", "-A")
    assert git(root, "commit", "-qm", "record").returncode == 0
    assert git(root, "push", "-q").returncode == 0
    # an edit to a committed record's meaning, smuggled past pre-commit, is stopped at push
    a.write_text(a.read_text().replace("Store sessions in Redis.", "Store sessions in Postgres."))
    git(root, "commit", "-qam", "rewrite history", "--no-verify")
    pushed = git(root, "push", "-q")
    assert pushed.returncode and "nio: memory check failed" in pushed.stdout + pushed.stderr, pushed
    print("ok")


def test_allow():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / ".claude").mkdir()
        local = root / ".claude/settings.local.json"
        local.write_text('{"model": "opus", "permissions": {"allow": ["Bash(git log:*)"]}}')
        assert hooks.allow(root, False) == local
        hooks.allow(root, False)  # twice adds nothing
        cfg = json.loads(local.read_text())
        rules = cfg["permissions"]["allow"]
        assert cfg["model"] == "opus" and "Bash(git log:*)" in rules and len(rules) == len(set(rules))
        assert "Bash(nio flow next:*)" in rules and "Bash(uv run nio flow next:*)" in rules
        assert "Bash(nio jury evidence:*)" in rules and "Bash(uv run nio jury evidence:*)" in rules
        assert not (root / ".claude/settings.json").exists()
        # commands that run anything, or are the human's alone, are never allowed
        for cmd in ("flow finish", "flow seen", "flow abandon", "flow unblock", "hooks"):
            assert not any(cmd in r for r in rules), cmd
        assert "Bash(nio *human*)" in cfg["permissions"]["ask"] and "Bash(nio flow done *--c*)" in cfg["permissions"]["ask"]
        assert "Bash(nio jury plan *--pick*)" in cfg["permissions"]["ask"]
        assert hooks.allow(root, True) == root / ".claude/settings.json"
        local.write_text("{broken")
        try:
            hooks.allow(root, False)
            assert False, "broken settings must be refused"
        except ValueError:
            assert local.read_text() == "{broken"


if __name__ == "__main__":
    selfcheck.main([test_install, test_allow, test_checks_block_commit_and_push, test_two_branches_supersede_the_same_decision])
