"""Scenarios for nio pack: a small memory, a piece of work, and what the pack tells the agent.
Run: uv run python tests/test_pack.py  (add -v to print every pack)."""
import subprocess
import sys

from test_index import VERDICT, flag
from test_records import GOOD_BODY, commit, fill, repo

from nio import index, pack, records
import selfcheck

VERBOSE = "-v" in sys.argv
RULE = """## Decision
Do not use claude-mem, Cognee or Google Memory Bank as the memory store.
## Why
Memory must be plain files in git that work on every host; external memory systems lock it to one tool.
## Rejected alternatives
- Cognee as the store: a second source of truth.
## Reuse
Any proposal to add a memory backend or vector service.
"""
LESSON = """## Problem
Webhook calls fail at random under load.
## Solution
Retry three times with exponential backoff and an idempotency key.
## Where it applies
Any outbound webhook call.
"""


def memory():
    """A repo with an approved session decision, a cross-cutting rule and a webhook lesson. Returns (root, ids)."""
    root = repo()
    s = records.new(root, "decision", "auth", "Store sessions in Redis")
    fill(s, paths='["src/session/*"]')
    r = records.new(root, "decision", "auth", "No external memory systems")
    fill(r, body=RULE)
    w = records.new(root, "lesson", "auth", "Retry flaky webhooks")
    fill(w, paths='["payments/*"]', tags='["webhooks"]', body=LESSON)
    commit(root)
    v = records.new(root, "verdict", "auth", "Sessions ruling")
    fill(v, body=VERDICT, subject=s.name[:13], outcome="approved", tier="low")
    commit(root, "verdict")
    return root, {k: p.name[:13] for k, p in dict(s=s, r=r, w=w, v=v).items()}


def run(root, text, **kw):
    out, ids = pack.build(root, text, **kw)
    if VERBOSE:
        print(f"\n{'=' * 30} {text}\n{out}")
    full, _, rest = out.partition("## Related")
    lines = [l for l in rest.splitlines() if l.startswith("- ")]
    return out, full, lines, ids


def test_new_file_in_a_decided_area():
    """The worker will create a file nobody has touched yet; the approved decision on its folder arrives in full."""
    root, id = memory()
    out, full, lines, _ = run(root, "add a session store with a 24h TTL", paths=["src/session/store.py"])
    assert f"### {id['s']} decision approved: Store sessions in Redis  [shares src/session/store.py]" in full, out
    assert f"- subject {id['v']} approved" in full and "#### Why" in full, out  # the verdict is a link, the record in full
    assert f"### {id['r']}" not in full and f"### {id['w']}" not in full, out  # nothing else in full
    assert "`approved` (binding)" in out and "`drifted`" not in out, out  # only the standings present
    assert id["v"] not in "\n".join(lines), lines  # the verdict is not repeated as its own line
    assert "## How to use this" in out and "memory-used:" in out, out
    print("ok")


def test_rule_found_by_text_only():
    """A cross-cutting rule has no paths; only the description can reach it, and it arrives as a line."""
    root, id = memory()
    out, full, lines, _ = run(root, "add a Cognee backend so memory can live in a vector service", paths=["src/nio/cognee.py"])
    assert "## On your files" not in out, out  # no record sits on the new file
    assert lines[0].startswith(f"- {id['r']} decision current: No external memory systems"), lines
    assert "#### Decision" not in out, out
    print("ok")


def test_lesson_reused_on_other_files():
    """Same problem, different files: the webhook lesson reaches a shipping task through text."""
    root, id = memory()
    out, full, lines, _ = run(root, "call the shipping provider's webhook and retry when it fails", paths=["shipping/client.py"])
    assert lines[0].startswith(f"- {id['w']} lesson current: Retry flaky webhooks"), lines
    print("ok")


def test_warned_records_come_in_full_with_their_weight():
    """A drifted decision and a challenged one sit on the files; both arrive in full, flagged, with their map rows."""
    root, id = memory()
    (root / "app.py").write_text("".join(f"line {i}\n" for i in range(10)))
    d = records.new(root, "decision", "auth", "App boots from one config file")
    fill(d, paths='["app.py"]', body=GOOD_BODY.replace("Store sessions in Redis", "Boot from one config file"))
    commit(root, "app")
    (root / "app.py").write_text("".join(f"line {i}{'!' if i < 5 else ''}\n" for i in range(10)))
    c = records.new(root, "change", "auth", "Redis is wrong for sessions")
    fill(c, body="## What is wrong\nX.\n## Proposed change\nY.\n## Human decision\nPending.\n", against=id["s"])
    flag(next((root / ".nio/memory/auth").glob(f"{id['s']}-*.md")), c.name[:13])
    commit(root, "refactor")
    out, full, _, _ = run(root, "move the session config into app.py", paths=["app.py", "src/session/store.py"])
    assert f"### {d.name[:13]} decision drifted" in full and f"### {id['s']} decision challenged" in full, out
    assert f"- against {c.name[:13]} pending" in full, out  # the pending change request shows under its record
    assert "`drifted` (verify)" in out and "`challenged` (disputed)" in out and "`approved`" not in out, out
    print("ok")


def test_superseded_gives_way_to_its_replacement():
    root, id = memory()
    n = records.new(root, "decision", "auth", "Store sessions in Valkey")
    fill(n, supersedes=f'["{id["s"]}"]', body=GOOD_BODY.replace("Redis", "Valkey"))  # no paths: reached only through the old record
    flag(next((root / ".nio/memory/auth").glob(f"{id['s']}-*.md")), n.name[:13])
    out, full, _, ids = run(root, "add a session store", paths=["src/session/store.py"])
    assert f"### {n.name[:13]} decision uncommitted: Store sessions in Valkey  [shares src/session/store.py]" in full, out
    assert id["s"] not in ids and "`uncommitted` (tentative)" in out, out
    print("ok")


def test_juror_pack_from_a_diff():
    """The juror gets the records on the diff's files and the check to apply."""
    root, id = memory()
    (root / "src/session").mkdir(parents=True)
    (root / "src/session/store.py").write_text("POSTGRES = True\n")
    commit(root, "store sessions in postgres")
    n = records.new(root, "decision", "auth", "Pool Postgres connections")  # written inside the diff, then its code changes
    fill(n, paths='["src/session/store.py"]', body=GOOD_BODY.replace("Store sessions in Redis", "Pool Postgres connections"))
    commit(root, "pool")
    (root / "src/session/store.py").write_text("POOL = 4\n")
    commit(root, "pool size")
    out, full, _, _ = run(root, "review: sessions move to Postgres", diff="HEAD~3")
    assert f"### {id['s']} decision approved" in full, out  # the diff under review is not drift
    assert f"### {n.name[:13]} decision current" in full, out  # nor for a record confirmed inside it
    assert "decision drifted" in pack.build(root, "add a session store", ["src/session/store.py"])[0]  # a worker after it: it is
    assert "You are judging a diff. Reject it if it contradicts an approved or current record" in out, out
    assert "nio query --path" not in out, out  # worker-only instruction
    print("ok")


def test_juror_links_use_standings_before_the_diff():
    """Link lines under a record show linked records as they stood before the diff too."""
    root, id = memory()
    (root / "src/session").mkdir(parents=True)
    (root / "src/session/store.py").write_text("x\n")
    rivals = []
    for name in ("Valkey", "Memcached"):  # two records supersede the same one: a conflict, linked both ways
        r = records.new(root, "decision", "auth", f"Store sessions in {name}")
        fill(r, paths='["src/session/*"]', supersedes=f'["{id["s"]}"]', body=GOOD_BODY.replace("Redis", name))
        rivals.append(r.name[:13])
    commit(root, "rivals")
    (root / "src/session/store.py").write_text("y\n")
    commit(root, "the diff")
    juror = pack.build(root, "review the store", diff="HEAD~1")[0]
    worker = pack.build(root, "change the store", ["src/session/store.py"])[0]
    assert f"### {id['s']} decision conflict" in juror, juror
    assert all(f"- supersedes {r} current" in juror and f"- supersedes {r} drifted" in worker for r in rivals), (juror, worker)
    print("ok")


def test_cli_saves_under_the_run_and_logs():
    """`nio pack --run` prints the pack, saves the same text under the run and logs size and IDs."""
    root, id = memory()
    run_id = records.new_run(root)
    cmd = [sys.executable, "-c", "from nio.cli import main; main()", "pack", "add a session store",
           "--path", "src/session/store.py", "--task", "T-1", "--run", run_id]
    p = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    assert (root / f".nio/runs/{run_id}/packs/T-1.md").read_text() == p.stdout and p.stdout.startswith("# Memory for T-1")
    _, _, name, size, ids = (root / ".nio/cache/usage.log").read_text().splitlines()[-1].split("\t")
    assert name == "T-1" and int(size) == len(p.stdout) // 4 and ids.split(",")[0] == id["s"], ids
    bad = subprocess.run(cmd[:-1] + ["R-000000-none"], cwd=root, capture_output=True, text=True)
    assert bad.returncode and "no run" in bad.stderr, bad.stderr
    print("ok")


def test_offline_still_packs():
    """With no model, the grep fallback still puts the decision on the file in full."""
    root, id = memory()
    index.build(root)
    real, index.embed = index.embed, lambda *a: (_ for _ in ()).throw(RuntimeError("offline"))
    try:
        out, full, _, _ = run(root, "add a session store", paths=["src/session/store.py"])
        assert f"### {id['s']} decision" in full, out
    finally:
        index.embed = real
    print("ok")


def test_empty_memory():
    root = repo()
    out, _, _, ids = run(root, "anything at all", paths=["app.py"])
    assert ids == [] and "Memory has nothing on this work" in out and "memory-used:" in out, out
    print("ok")


def test_worker_pack_leaves_out_the_closing_instructions():
    """A task's worker pack (implement-stage CT-6): no `How to use this` and no @nio:remember; the default keeps them."""
    root, id = memory()
    out, *_ = run(root, "add a session store", paths=["src/session/store.py"])
    assert "## How to use this" in out and "@nio:remember" in out, out
    out, _ = pack.build(root, "add a session store", paths=["src/session/store.py"], worker=False)
    assert id["s"] in out and "## How to use this" not in out and "@nio:remember" not in out, out
    assert "## Standings in this pack" in out, out
    print("ok")


def test_missing_record_and_whole_old_index():
    """TC-30: a record the index names but whose file is gone is skipped, not a crash; a rebuild stopped half-way leaves
    the whole old index in place and no half-built copy."""
    import sqlite3
    from nio import query
    root, id = memory()
    index.build(root)
    gone = next((root / ".nio/memory").glob(f"*/{id['s']}-*.md"))
    gone.unlink()  # deleted after the index was built: a claim during the rebuild
    real = index.build
    index.build = lambda r: (0, 0)  # the reader comes before the rebuild that would drop it
    try:
        out, _ = pack.build(root, "add a session store", paths=["src/session/store.py"])
    finally:
        index.build = real
    assert id["s"] not in out.split("## Related")[0], out
    db = root / ".nio/cache/index.db"
    rows = lambda: sqlite3.connect(db).execute("select count(*) from nodes").fetchone()[0]
    before, fill = rows(), index.fill
    index.fill = lambda *a: (_ for _ in ()).throw(RuntimeError("stopped half-way"))
    try:
        index.build(root)
        raise AssertionError("the rebuild must stop")
    except RuntimeError:
        pass
    finally:
        index.fill = fill
    assert rows() == before and not (root / ".nio/cache/index.db.new").exists()
    assert query.search(root, "webhooks") is not None
    print("ok")


if __name__ == "__main__":
    selfcheck.main([f for n, f in list(globals().items()) if n.startswith("test_") and callable(f)])
