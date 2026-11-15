"""Self-check for nio hooks and the cross-branch merge check. Run: uv run python tests/test_hooks.py"""
import json
import re
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

from test_index import flag
from test_records import GOOD_BODY, commit, fill, repo

from nio import hooks, records
import selfcheck

ROOT = Path(__file__).resolve().parents[1]


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
        for cmd in ("flow red", "flow green", "flow seen", "flow abandon", "flow unblock", "hooks"):
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


def test_wheel_ships_mods():
    # TC-30: the built wheel carries both mods and the marketplace file
    with tempfile.TemporaryDirectory() as tmp:
        built = subprocess.run(["uv", "build", "--wheel", "--out-dir", tmp], cwd=ROOT, capture_output=True, text=True)
        assert built.returncode == 0, built.stderr
        wheels = list(Path(tmp).glob("*.whl"))
        assert len(wheels) == 1, wheels
        with zipfile.ZipFile(wheels[0]) as wheel:
            names = set(wheel.namelist())
        for want in ("nio/mods/.claude-plugin/marketplace.json",
                     "nio/mods/background-nio-commands/.claude-plugin/plugin.json",
                     "nio/mods/nio-status-pane/.claude-plugin/plugin.json"):
            assert want in names, want
    print("ok")


FAKE_CLAUDE = """#!/bin/sh
echo "$@" >> "$0.log"
case "$*" in
  "plugin list --json") echo "[]";;
  "plugin install background-nio-commands"*) echo "boom: marketplace unreadable" >&2; exit 1;;
  *) exit 0;;
esac
"""


def _mods(root, *args, path):
    import os
    from test_flow import run_main
    old = os.environ["PATH"]
    os.environ["PATH"] = path
    try:
        return run_main(root, "mods", "install", *args)
    finally:
        os.environ["PATH"] = old


def test_mods_install_one_fails():
    # TC-23 and the AC-26 recording
    import os
    with tempfile.TemporaryDirectory() as tmp:
        fake = Path(tmp) / "claude"
        fake.write_text(FAKE_CLAUDE)
        fake.chmod(0o755)
        code, out, err = _mods(Path(tmp), path=f"{tmp}:{os.environ['PATH']}")
        assert code == 0, err
        assert out == "background-nio-commands: failed: boom: marketplace unreadable\nnio-status-pane: installed\n", out
        log = Path(str(fake) + ".log").read_text()
        assert "plugin install nio-status-pane" in log and "--scope local" in log and str(hooks.mods_dir()) in log, log
    print("ok")


def test_mods_install_without_claude():
    # TC-36
    with tempfile.TemporaryDirectory() as tmp:
        code, out, _ = _mods(Path(tmp), path=tmp)
        assert code == 0
        assert out == "background-nio-commands: failed: claude not found\nnio-status-pane: failed: claude not found\n", out
        code, out, _ = _mods(Path(tmp), "--skip", path=tmp)
        assert code == 0 and out == "background-nio-commands: skipped\nnio-status-pane: skipped\n", out
    print("ok")


def test_mods_install_e2e():
    # TC-20..22: real claude, only with NIO_E2E=1, in a temp CLAUDE_CONFIG_DIR
    import os
    if os.environ.get("NIO_E2E") != "1":
        print("skip (NIO_E2E=1 runs it)")
        return
    ids = ("background-nio-commands", "nio-status-pane")
    from test_flow import run_main

    def listed(root, cfg):
        r = subprocess.run(["claude", "plugin", "list", "--json"], cwd=root, capture_output=True, text=True,
                           env={**os.environ, "CLAUDE_CONFIG_DIR": cfg})
        return [e["id"] for e in json.loads(r.stdout)]

    old = os.environ.get("CLAUDE_CONFIG_DIR")
    try:
        with tempfile.TemporaryDirectory() as cfg, tempfile.TemporaryDirectory() as cfg2:
            os.environ["CLAUDE_CONFIG_DIR"] = cfg
            root = repo()
            code, out, err = run_main(root, "mods", "install")
            assert code == 0 and out == "background-nio-commands: installed\nnio-status-pane: installed\n", (out, err)
            assert all(f"{i}@nio-mods" in listed(root, cfg) for i in ids)
            before = git(root, "status", "--porcelain").stdout
            code, out, _ = run_main(root, "mods", "install")
            assert out == "background-nio-commands: already installed\nnio-status-pane: already installed\n", out
            code, out, _ = run_main(root, "mods", "install", "--skip")
            assert out == "background-nio-commands: already installed (left as is)\nnio-status-pane: already installed (left as is)\n", out
            assert [i for i in listed(root, cfg) if i.endswith("@nio-mods")].count(f"{ids[0]}@nio-mods") == 1
            assert git(root, "status", "--porcelain").stdout == before
            os.environ["CLAUDE_CONFIG_DIR"] = cfg2
            root2 = repo()
            code, out, _ = run_main(root2, "mods", "install", "--skip")
            assert out == "background-nio-commands: skipped\nnio-status-pane: skipped\n", out
            assert not [i for i in listed(root2, cfg2) if i.endswith("@nio-mods")]
    finally:
        if old is None:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = old
    print("ok")


def _skill_steps():
    text = (ROOT / "skills/install/SKILL.md").read_text()
    steps_text = text.split("## Steps", 1)[1].split("## When to stop", 1)[0]
    pieces = re.split(r"^(?=\d+\. )", steps_text, flags=re.M)
    return [re.sub(r"^\d+\. ", "", p).strip() for p in pieces if re.match(r"\d+\. ", p)]


def test_install_skill_mods_step():
    # TC-24 (AC-22)
    steps = _skill_steps()
    mods = [s for s in steps if "mod" in s.lower()]
    assert len(mods) == 1, mods
    assert mods[0].startswith("On Claude Code"), mods[0]
    assert "nio mods install" in mods[0] and "nio mods install --skip" in mods[0], mods[0]
    print("ok")


def test_mods_install_local_scope():
    # TC-31 (AC-26): a fake claude that records its working directory and arguments, succeeding for both mods
    import os
    with tempfile.TemporaryDirectory() as tmp:
        fake = Path(tmp) / "claude"
        fake.write_text('#!/bin/sh\necho "$PWD $@" >> "$0.log"\nif [ "$1 $2" = "plugin list" ]; then echo "[]"; fi\nexit 0\n')
        fake.chmod(0o755)
        root = Path(tmp) / "repo"
        root.mkdir()
        assert hooks.mods_install(root, claude=str(fake)) == [
            "background-nio-commands: installed", "nio-status-pane: installed"]
        log = Path(str(fake) + ".log").read_text().splitlines()
        for mod in ("background-nio-commands", "nio-status-pane"):
            want = f"{root} plugin install {mod} --marketplace {hooks.mods_dir()} --scope local --json"
            assert want in log, (want, log)
    text = (ROOT / "skills/install/SKILL.md").read_text()
    questions = [line for line in text.splitlines() if line.rstrip().endswith("?")]
    mods_q = [q for q in questions if "nio mods install" in q or "mod" in q.lower()]
    assert len(questions) == 1 and len(mods_q) == 1, questions
    print("ok")


def test_readmes_call_mods_optional():
    texts = [(ROOT / f).read_text() for f in (
        "README.md", "tools/claude-mods/README.md",
        "tools/claude-mods/nio-status-pane/README.md",
        "tools/claude-mods/background-nio-commands/README.md")]
    docs = [(ROOT / f).read_text() for f in (".nio/project/architecture.md", ".nio/project/stack.md")]
    for text in texts + docs:
        assert "not part of the NIO product" not in text
        assert "dev tooling" not in text
    for text in texts:
        assert "optional Claude Code part of NIO" in text, text[:80]
        assert "the skills work the same without" in text, text[:80]
    for text in docs:
        assert "optional Claude Code part of NIO" in text
        assert "D-261115-e6nx" in text
    print("ok")


if __name__ == "__main__":
    selfcheck.main([test_install, test_allow, test_checks_block_commit_and_push, test_two_branches_supersede_the_same_decision,
                    test_wheel_ships_mods, test_mods_install_one_fails, test_mods_install_without_claude,
                    test_mods_install_e2e, test_install_skill_mods_step, test_mods_install_local_scope,
                    test_readmes_call_mods_optional])
