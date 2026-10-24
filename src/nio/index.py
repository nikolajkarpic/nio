"""Build .nio/cache/index.db (graph, FTS5, int8 vectors) and INDEX.md from the committed records."""
import hashlib
import importlib.metadata
import json
import os
import sqlite3
import subprocess
from pathlib import Path

import sqlite_vec

from nio import records

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
DIM = 384
# ponytail: starting guess for "same decision twice"; tune on the first ~30 real records
DUP_SIMILARITY = 0.92
# share of a decision's lines changed since it was last confirmed that marks it `drifted`
DEFAULT_DRIFT = 0.3

# graph and full text are cheap, so they are dropped and rebuilt on every run; vectors and meta persist
SCHEMA = f"""
create table if not exists nodes(id text primary key, kind text, type text, state text, standing text, drift real, title text, path text);
create table if not exists edges(src text, rel text, dst text);
create table if not exists meta(key text primary key, value text);
create virtual table if not exists fts using fts5(id unindexed, title, body);
create virtual table if not exists vec using vec0(id text primary key, embedding int8[{DIM}]);
"""


def settings(root):
    cfg = json.loads((root / ".nio/config.json").read_text())["memory"].get("index", {})
    return cfg.get("model", DEFAULT_MODEL), cfg.get("drift", DEFAULT_DRIFT)


def connect(root):
    path = root / ".nio/cache/index.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.executescript(SCHEMA)
    return db


def embed(model, texts):
    """Embed texts as normalized int8 vectors (bytes). Loads the model only when called."""
    import numpy as np
    from fastembed import TextEmbedding

    cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "nio/fastembed"
    vecs = TextEmbedding(model, cache_dir=str(cache)).embed(texts)
    return [np.clip(np.round(v / np.linalg.norm(v) * 127), -127, 127).astype(np.int8).tobytes() for v in vecs]


def load(root):
    """Return {id: (rel path, meta, body lines, sha256)} for every parseable record."""
    out = {}
    for f in sorted((root / ".nio/memory").rglob("*.md")):
        try:
            meta, body = records.parse(f)
        except Exception:
            continue  # nio check reports it
        out[str(meta.get("id"))] = (str(f.relative_to(root)), meta, body, hashlib.sha256(f.read_bytes()).hexdigest())
    return out


def changed_lines(root, anchor):
    """Map path at HEAD -> lines changed since `anchor`, following renames."""
    out = subprocess.run(["git", "diff", "--numstat", "-z", "-M", anchor, "HEAD"], cwd=root, capture_output=True, text=True).stdout
    toks, i, changed = out.split("\0"), 0, {}
    while i < len(toks) and toks[i]:
        added, deleted, path = toks[i].split("\t")
        i += 1
        if not path:  # a rename: old and new names follow as their own tokens
            path, i = toks[i + 1], i + 2
        if added != "-":  # binary files have no line counts
            changed[path] = max(int(added), int(deleted))
    return changed


def standings(recs, commits, times, touched, root, threshold):
    """Map record ID -> (standing, drift). The record's own status or outcome is only how it entered memory;
    this is whether it still holds, derived from newer records and from how much its code changed."""
    verdicts, superseders, changes = {}, {}, {}
    for rid, (_, meta, _, _) in recs.items():
        if meta.get("type") == "verdict":
            verdicts.setdefault(meta.get("subject"), []).append(rid)
        for old in meta.get("supersedes") or []:
            superseders.setdefault(old, []).append(rid)
        if meta.get("type") == "change":
            changes.setdefault(meta.get("against"), []).append(meta.get("outcome"))
    when = lambda rid: times.get(commits.get(rid), float("inf"))  # uncommitted counts as newest
    latest = {s: recs[max(v, key=when)][1].get("outcome") for s, v in verdicts.items()}
    diffs, out = {}, {}
    for rid, (_, meta, _, _) in recs.items():
        if meta.get("type") in ("verdict", "change"):
            out[rid] = (meta.get("outcome"), None)
            continue
        live = [s for s in superseders.get(rid, []) if latest.get(s) != "rejected"]
        drift = None
        anchors = [commits[r] for r in [rid, *verdicts.get(rid, [])] if r in commits]
        if rid in commits and touched.get(rid):
            anchor = max(anchors, key=lambda c: times.get(c, 0))  # drift counts from the last confirmation
            if anchor not in diffs:
                diffs[anchor] = changed_lines(root, anchor)
            size = sum((root / f).read_bytes().count(b"\n") for f in touched[rid] if (root / f).is_file())
            drift = min(1.0, sum(diffs[anchor].get(f, 0) for f in touched[rid]) / max(size, 1))
        if len(live) > 1:
            standing = "conflict"
        elif live or "accepted" in changes.get(rid, []):
            standing = "superseded"
        elif "pending" in changes.get(rid, []):
            standing = "challenged"
        elif latest.get(rid) in ("rejected", "human"):
            standing = {"rejected": "rejected", "human": "escalated"}[latest[rid]]
        elif drift is not None and drift >= threshold:
            standing = "drifted"
        elif rid not in commits:
            standing = "uncommitted"
        elif latest.get(rid) == "approved":
            standing = "approved"
        else:
            standing = "current"
        out[rid] = (standing, drift)
    return out


def build(root):
    """(Re)build the index. Returns (record count, number re-embedded)."""
    recs = load(root)
    files = records.git(root, "ls-files", "--cached", "--others", "--exclude-standard")
    commits, renames = records.added_in(root), {}
    model, threshold = settings(root)
    version = f"{model}@fastembed-{importlib.metadata.version('fastembed')}"
    db = connect(root)
    with db:
        if (db.execute("select value from meta where key='model'").fetchone() or [None])[0] != version:
            db.execute("delete from vec")
            db.execute("delete from meta where key like 'hash:%'")
        for t in ("nodes", "edges", "fts"):
            db.execute(f"drop table {t}")
        db.executescript(SCHEMA)
        db.executemany("insert into nodes(id, kind, path) values (?, 'file', ?)", [(f, f) for f in files])
        edges, touched = [], {}
        for rid, (path, meta, body, _) in recs.items():
            db.execute("insert into fts values (?, ?, ?)", (rid, str(meta.get("title")), "\n".join(body)))
            for ac in meta.get("serves") or []:
                edges.append((rid, "serves", ac))
                db.execute("insert or ignore into nodes(id, kind) values (?, 'ac')", (ac,))
            if meta.get("task"):
                edges.append((rid, "task", meta["task"]))
                db.execute("insert or ignore into nodes(id, kind) values (?, 'task')", (meta["task"],))
            if meta.get("subject"):
                edges.append((rid, "subject", meta["subject"]))
            edges += [(rid, "supersedes", old) for old in meta.get("supersedes") or []]
            commit = commits.get(rid)
            if commit not in renames:
                renames[commit] = records.renamed_since(root, commit) if commit else None
            touched[rid] = records.touches(meta.get("paths") or [], files, renames[commit])
            edges += [(rid, "touches", f) for f in touched[rid]]
            if commit:
                edges.append((rid, "commit", commit))
        db.executemany("insert into edges values (?, ?, ?)", edges)
        # commit order from history, not timestamps: commits in the same second must still sort
        history = records.git(root, "log", "--topo-order", "--format=%H")
        times = {c: len(history) - i for i, c in enumerate(history)}
        for rid, (standing, drift) in standings(recs, commits, times, touched, root, threshold).items():
            path, meta = recs[rid][:2]
            state = meta.get("status") or meta.get("outcome")
            db.execute("insert into nodes values (?, 'record', ?, ?, ?, ?, ?, ?)", (rid, meta.get("type"), state, standing, drift, str(meta.get("title")), path))

        # vectors: re-embed only records whose file content changed
        old = dict(db.execute("select substr(key, 6), value from meta where key like 'hash:%'"))
        for rid in old.keys() - recs.keys():
            db.execute("delete from vec where id = ?", (rid,))
            db.execute("delete from meta where key = ?", (f"hash:{rid}",))
        todo = [rid for rid, r in recs.items() if old.get(rid) != r[3]]
        if todo:
            texts = [f"{recs[r][1].get('title')}\n" + "\n".join(recs[r][2]) for r in todo]
            for rid, v in zip(todo, embed(model, texts)):
                db.execute("delete from vec where id = ?", (rid,))
                db.execute("insert into vec values (?, vec_int8(?))", (rid, v))
                db.execute("insert or replace into meta values (?, ?)", (f"hash:{rid}", recs[rid][3]))
        head = records.git(root, "rev-parse", "HEAD")
        db.executemany("insert or replace into meta values (?, ?)", [("model", version), ("commit", head[0] if head else "")])
    write_index_md(root, db)
    db.close()
    return len(recs), len(todo)


def write_index_md(root, db):
    lines = ["# NIO memory index", "", "Generated by `nio index`; do not edit or commit.", "", "## Records", ""]
    for rid, rtype, standing, title, path in db.execute("select id, type, standing, title, path from nodes where kind='record' order by id"):
        lines.append(f"- {rid} {rtype} {standing} {Path(path).parent.name}: {title}")
    lines += ["", "## By path", ""]
    by_path = {}
    for dst, src in db.execute("select dst, src from edges where rel='touches' order by dst, src"):
        by_path.setdefault(dst, []).append(src)
    lines += [f"- {f}: {', '.join(ids)}" for f, ids in by_path.items()]
    (root / ".nio/cache/INDEX.md").write_text("\n".join(lines) + "\n")


def near_duplicates(root, threshold=DUP_SIMILARITY):
    """Pairs of records that share a touched file and embed above threshold, unless one supersedes the other."""
    db = connect(root)
    rows = db.execute(
        """
        select distinct a.src, b.src, 1 - vec_distance_cosine(vec_int8(va.embedding), vec_int8(vb.embedding)) as sim
        from edges a join edges b on a.rel = 'touches' and b.rel = 'touches' and a.dst = b.dst and a.src < b.src
        join vec va on va.id = a.src join vec vb on vb.id = b.src
        where not exists (select 1 from edges s where s.rel = 'supersedes'
                          and ((s.src = a.src and s.dst = b.src) or (s.src = b.src and s.dst = a.src)))
        """
    ).fetchall()
    db.close()
    return sorted((r for r in rows if r[2] >= threshold), key=lambda r: -r[2])


def check(root, base="HEAD"):
    """nio check plus the near-duplicate warning. Returns (errors, warnings, record count)."""
    errors, warnings, count = records.check(root, base)
    warnings += [f".nio/memory: `{a}` and `{b}` look like the same decision (similarity {s:.2f}) on shared paths; merge them with a supersede"
                 for a, b, s in near_duplicates(root)]
    return errors, warnings, count
