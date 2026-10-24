"""Self-check for nio hooks and the cross-branch merge check. Run: uv run python tests/test_hooks.py"""
import subprocess
import sys
import time
from pathlib import Path

from test_index import flag
from test_records import GOOD_BODY, commit, fill, repo

from nio import hooks, records


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
    hooks.install(root, str(fake))  # twice is harmless
    merge = (root / ".git/hooks/post-merge").read_text()
    assert merge.count(hooks.MARK) == 1 and "echo mine" in merge, merge
    # a branch switch refreshes the index; checking out a single file does not
    assert git(root, "checkout", "-q", "-b", "other").returncode == 0
    assert wait_for(log, 1) == ["index"], wait_for(log, 1)
    assert git(root, "checkout", "-q", "--", "app.py").returncode == 0
    time.sleep(0.5)
    assert wait_for(log, 1) == ["index"]
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


if __name__ == "__main__":
    test_install()
    test_checks_block_commit_and_push()
    test_two_branches_supersede_the_same_decision()
