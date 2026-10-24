"""Self-check for nio index. Run: uv run python tests/test_index.py (downloads the model once)."""
from test_records import GOOD_BODY, commit, fill, repo

from nio import index, query, records


def test():
    root = repo()
    a = records.new(root, "decision", "auth", "Sessions in Redis")
    fill(a, paths='["app.py"]', serves='["AC-1"]')
    b = records.new(root, "decision", "auth", "Keep sessions in Redis")
    fill(b, paths='["app.py"]', body=GOOD_BODY.replace("Store", "Keep"))
    assert index.build(root) == (2, 2)
    assert index.build(root) == (2, 0)  # incremental: nothing changed, nothing embedded
    assert (root / ".nio/cache/INDEX.md").read_text().count("app.py:") == 1
    db = index.connect(root)
    assert ("serves", "AC-1") in db.execute("select rel, dst from edges where src = ?", (a.name[:13],)).fetchall()
    assert db.execute("select id from fts where fts match 'postgres'").fetchall()
    # the same decision twice on the same path warns
    assert any("same decision" in w for w in index.check(root)[1])
    # ...unless one supersedes the other; only the two edited records are re-embedded
    fill(b, paths='["app.py"]', body=GOOD_BODY.replace("Store", "Keep"), supersedes=f'["{a.name[:13]}"]')
    a.write_text(a.read_text().replace("\n---\n", f'\noutdated_by: ["{b.name[:13]}"]\n---\n', 1))
    assert index.build(root) == (2, 2)
    errors, warnings, _ = index.check(root)
    assert not errors and not warnings, (errors, warnings)
    # the cache can be deleted and rebuilt
    (root / ".nio/cache/index.db").unlink()
    assert index.build(root) == (2, 2)
    print("ok")


VERDICT = "## Ruling\nOk.\n## Jurors\n| a | b | c | yes |\n## Reasons\nFine.\n## What was rejected\nNothing.\n"


def standing(root, rid):
    index.build(root)
    return index.connect(root).execute("select standing from nodes where id = ?", (rid,)).fetchone()[0]


def flag(old, new):
    text = old.read_text()
    if "outdated_by: [" in text:
        old.write_text(text.replace("outdated_by: [", f'outdated_by: ["{new}", ', 1))
    else:
        old.write_text(text.replace("\n---\n", f'\noutdated_by: ["{new}"]\n---\n', 1))


def test_standing():
    root = repo()
    (root / "app.py").write_text("".join(f"line {i}\n" for i in range(10)))
    a = records.new(root, "decision", "auth", "Sessions in Redis")
    fill(a, paths='["app.py"]')
    rid = a.name[:13]
    assert standing(root, rid) == "uncommitted"
    commit(root)
    assert standing(root, rid) == "current"
    # 4 of 10 lines changed since it was written: drifted
    (root / "app.py").write_text("".join(f"line {i}{'!' if i < 4 else ''}\n" for i in range(10)))
    commit(root, "refactor")
    assert standing(root, rid) == "drifted"
    # a fresh verdict confirms it still holds and resets the drift clock
    v = records.new(root, "verdict", "auth", "Recheck")
    fill(v, body=VERDICT, subject=rid, outcome="approved", tier="low")
    commit(root, "recheck")
    assert standing(root, rid) == "approved"
    # a pending change request challenges it
    c = records.new(root, "change", "auth", "Redis is wrong")
    fill(c, body="## What is wrong\nX.\n## Proposed change\nY.\n## Human decision\nPending.\n", against=rid)
    flag(a, c.name[:13])
    assert standing(root, rid) == "challenged"
    # ...and a superseding decision outdates it, unless the jury rejects the replacement
    fill(c, body="## What is wrong\nX.\n## Proposed change\nY.\n## Human decision\nNo.\n", against=rid, outcome="rejected")
    b = records.new(root, "decision", "auth", "Sessions in Postgres")
    fill(b, paths='["app.py"]', supersedes=f'["{rid}"]', body=GOOD_BODY.replace("Redis", "Postgres"))
    flag(a, b.name[:13])
    assert records.check(root)[0] == [], records.check(root)[0]
    assert standing(root, rid) == "superseded"
    r = records.new(root, "verdict", "auth", "Postgres ruling")
    fill(r, body=VERDICT, subject=b.name[:13], outcome="rejected", tier="low")
    assert standing(root, rid) == "approved" and standing(root, b.name[:13]) == "rejected"
    print("ok")


def test_query():
    root = repo()
    (root / "jobs.py").write_text("")
    a = records.new(root, "decision", "auth", "Sessions in Redis")
    fill(a, paths='["app.py"]')
    b = records.new(root, "decision", "auth", "Jobs in a Postgres table")
    fill(b, paths='["jobs.py"]', body=GOOD_BODY.replace("Store sessions in Redis", "Queue background jobs in a Postgres table")
         .replace("A Postgres sessions table adds a write on every request", "We already run Postgres and need jobs in the same transaction"))
    commit(root)
    hits = query.search(root, "Sessions in Redis. Decision: keep user sessions in Redis. Why: a sessions table in Postgres writes on every request.")
    assert hits[0][0] == a.name[:13] and hits[0][3] >= query.DEDUP_SIMILARITY, hits
    assert all(h[3] < query.DEDUP_SIMILARITY for h in hits[1:]), hits
    assert [h[0] for h in query.search(root, paths=["jobs.py"])] == [b.name[:13]]
    # a file the task will create matches a record's globs too
    fill(b, paths='["jobs*.py"]', body=b.read_text().split("\n---\n", 1)[1])
    assert [h[0] for h in query.search(root, paths=["jobs_new.py"])] == [b.name[:13]]
    # superseded records are hidden unless asked
    c = records.new(root, "decision", "auth", "Sessions in Valkey")
    fill(c, paths='["app.py"]', supersedes=f'["{a.name[:13]}"]')
    flag(a, c.name[:13])
    assert a.name[:13] not in [h[0] for h in query.search(root, paths=["app.py"])]
    assert a.name[:13] in [h[0] for h in query.search(root, paths=["app.py"], show_all=True)]
    # graph walk both ways; one-hop links on search hits
    walk = query.graph(root, a.name[:13])
    assert (1, "←", "supersedes", c.name[:13]) in [s[:4] for s in walk] and any(s[3] == "app.py" for s in walk), walk
    hit = query.search(root, paths=["app.py"])[0]
    assert hit[0] == c.name[:13] and f"supersedes {a.name[:13]} superseded" in hit[6], hit
    # get reads files directly, at most 5
    assert query.get(root, [a.name[:13]])[0][1] == a.read_text()
    try:
        query.get(root, [a.name[:13]] * 6)
        raise AssertionError("more than 5 records returned")
    except ValueError:
        pass
    # status notices records changed since the last index
    assert "changed since last index 0" in "\n".join(query.status(root))
    b.write_text(b.read_text() + "\n")
    assert "changed since last index 1" in "\n".join(query.status(root))
    # with no model, lookup falls back to grep instead of failing
    real, index.embed = index.embed, lambda *a: (_ for _ in ()).throw(RuntimeError("offline"))
    try:
        hits = query.search(root, "background jobs Postgres", paths=["jobs.py"])
        assert hits[0][0] == b.name[:13] and hits[0][4] == ["jobs.py"], hits
        assert a.name[:13] not in [h[0] for h in query.search(root, "sessions", paths=["app.py"])]
    finally:
        index.embed = real
    print("ok")


if __name__ == "__main__":
    test()
    test_standing()
    test_query()
