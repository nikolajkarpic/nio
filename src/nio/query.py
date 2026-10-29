"""Find records: hybrid full-text and vector search, files they touch, graph walks, and the grep fallback."""
import datetime
import re
import sys

from nio import index, records

# looser than the CI duplicate warning: a false alarm before writing costs one read, a duplicate lasts forever
DEDUP_SIMILARITY = 0.85
HIDDEN = ("superseded", "rejected")
RRF_K = 60  # standard reciprocal-rank-fusion constant
MAX_GET = 5
LEAVES = ("file", "commit")  # graph walks stop here: a file links to every record on it


def search(root, text="", paths=(), limit=10, show_all=False):
    """Return [(id, type, standing, similarity or None, shared paths, title, links)], best first.

    Refreshes the index first, so a record written minutes ago is found. Falls back to grep if the index is down."""
    try:
        index.build(root)
        db = index.connect(root)
        model, _ = index.settings(root)
        q = index.embed(model, [text])[0] if text and db.execute("select 1 from vec limit 1").fetchone() else None  # NFR-1: no records, no model loaded
    except Exception as e:
        print(f"warning: index unavailable ({e}); using the grep fallback", file=sys.stderr)
        return grep(root, text, paths, limit, show_all)
    touching = {}
    for src, dst in db.execute(f"select src, dst from edges where rel = 'touches' and dst in ({','.join('?' * len(paths))})", list(paths)):
        touching.setdefault(src, set()).add(dst)
    if paths:  # edges only know files that exist; a file the task will create still matches a record's globs
        for rid, (_, meta, _, _) in index.load(root).items():
            for f in records.touches(meta.get("paths") or [], list(paths)):
                touching.setdefault(rid, set()).add(f)
    sims, score = {}, {}
    if text:
        fts = db.execute("select id from fts where fts match ? order by rank", (fts_query(text),)).fetchall() if fts_query(text) else []
        # ponytail: brute-force cosine over every vector; a vec0 KNN index once records reach the tens of thousands
        sims = dict(db.execute("select id, 1 - vec_distance_cosine(vec_int8(embedding), vec_int8(?)) from vec", (q,))) if q is not None else {}
        for ranked in ([r[0] for r in fts], sorted(sims, key=sims.get, reverse=True)):
            for i, rid in enumerate(ranked):
                score[rid] = score.get(rid, 0) + 1 / (RRF_K + i + 1)
    for rid in touching:
        score[rid] = score.get(rid, 0) + 1 / RRF_K  # sharing files with the question counts as one top hit
    rows = {r[0]: r[1:] for r in db.execute("select id, type, standing, title from nodes where kind = 'record'")}
    out = []
    for rid in sorted(score, key=score.get, reverse=True):
        rtype, standing, title = rows[rid]
        if standing in HIDDEN and not show_all:
            continue
        out.append((rid, rtype, standing, sims.get(rid), sorted(touching.get(rid, [])), title, links(db, rid)))
        if len(out) == limit:
            break
    db.close()
    return out


def fts_query(text):
    return " OR ".join(f'"{w}"' for w in re.findall(r"\w+", text))


def links(db, rid, at=None):
    """One graph hop: records that point at this one (verdicts, supersedes, change requests) or that it points at.
    `at` overrides standings, e.g. as they stood before a diff."""
    rows = db.execute(
        """select e.rel, e.src, n.standing from edges e join nodes n on n.id = e.src where e.dst = ? and n.kind = 'record'
           union all
           select e.rel, e.dst, n.standing from edges e join nodes n on n.id = e.dst where e.src = ? and n.kind = 'record'""",
        (rid, rid),
    )
    return [f"{rel} {other} {(at or {}).get(other, standing)}" for rel, other, standing in rows]


def grep(root, text, paths, limit, show_all):
    """Lookup without the index: word overlap and path globs over the record files. Never fails because the index is down."""
    words = {w.lower() for w in re.findall(r"\w{3,}", text)}
    hits = []
    for rid, (_, meta, body, _) in index.load(root).items():
        # without the index only the flag is known: a record with `outdated_by` counts as superseded
        standing = "superseded" if meta.get("outdated_by") else meta.get("status") or meta.get("outcome")
        if standing in HIDDEN and not show_all:
            continue
        shared = records.touches(meta.get("paths") or [], list(paths))  # matches files that don't exist yet too
        found = set(re.findall(r"\w{3,}", f"{meta.get('title')} {' '.join(body)}".lower()))
        score = len(words & found) / max(len(words), 1) + len(shared)
        if score:
            hits.append((score, (rid, meta.get("type"), standing, None, shared, str(meta.get("title")), [])))
    return [h for _, h in sorted(hits, key=lambda h: -h[0])][:limit]


def graph(root, rid, depth=2):
    """Walk links both ways from `rid`. Returns [(depth, direction, rel, id, kind, standing, title)] in walk order."""
    index.build(root)
    db = index.connect(root)
    nodes = {r[0]: r[1:] for r in db.execute("select id, kind, standing, title from nodes")}
    if rid not in nodes:
        raise ValueError(f"no record `{rid}` in the index")
    out, seen, frontier = [], {rid}, [rid]
    for d in range(1, depth + 1):
        nxt = []
        for node in frontier:
            if nodes.get(node, ("commit",))[0] in LEAVES:  # commits are edges' targets, not node rows
                continue
            rows = db.execute("select '→', rel, dst from edges where src = ? union all select '←', rel, src from edges where dst = ?", (node, node))
            for direction, rel, other in rows:
                if other in seen:
                    continue
                seen.add(other)
                nxt.append(other)
                kind, standing, title = nodes.get(other, ("commit" if rel == "commit" else "?", None, None))
                out.append((d, direction, rel, other, kind, standing, title))
        frontier = nxt
    db.close()
    return out


def get(root, ids):
    """Return [(path, text)] for up to MAX_GET records, found by filename so it works without the index."""
    if len(ids) > MAX_GET:
        raise ValueError(f"at most {MAX_GET} records at a time; pick the ones that matter")
    out = []
    for rid in ids:
        found = sorted((root / ".nio/memory").glob(f"*/{rid}-*.md"))
        if not found:
            raise ValueError(f"no record `{rid}` under .nio/memory")
        out.append((found[0].relative_to(root), found[0].read_text()))
    return out


def status(root):
    """Freshness of the index: lines to print."""
    path = root / ".nio/cache/index.db"
    if not path.exists():
        return ["no index: run `nio index`"]
    db = index.connect(root)
    meta = dict(db.execute("select key, value from meta where key not like 'hash:%'"))
    hashes = dict(db.execute("select substr(key, 6), value from meta where key like 'hash:%'"))
    db.close()
    current = {rid: r[3] for rid, r in index.load(root).items()}
    changed = sum(hashes.get(rid) != h for rid, h in current.items()) + len(hashes.keys() - current.keys())
    head = (records.git(root, "rev-parse", "HEAD") or [""])[0]
    return [
        f"indexed commit {meta.get('commit', '')[:12]}, HEAD {head[:12]}" + ("" if meta.get("commit") == head else " (behind)"),
        f"records {len(current)}, changed since last index {changed}",
        f"model {meta.get('model')}",
        f"store sqlite {path.relative_to(root)} ({path.stat().st_size // 1024} KB)",
    ]


def format_hit(rid, rtype, standing, sim, shared, title, linked):
    mark = "≈ " if sim is not None and sim >= DEDUP_SIMILARITY else "  "
    sim_s = f"{sim:.2f}" if sim is not None else "  - "
    line = f"{mark}{rid} {rtype} {standing} {sim_s} {title}" + (f"  [shares {', '.join(shared)}]" if shared else "")
    return line + "".join(f"\n      {link}" for link in linked)


def format_step(depth, direction, rel, other, kind, standing, title):
    label = " ".join(str(x) for x in (kind if kind != "record" else "", standing or "", title or "") if x)
    return f"{'  ' * depth}{direction} {rel} {other}  {label}".rstrip()


def log(root, kind, asked, ids, text):
    """Append one line to .nio/cache/usage.log: time, kind, what was asked, approximate tokens returned, IDs.
    v0 only logs; comparing it with workers' `memory-used` lines comes later."""
    path = root / ".nio/cache/usage.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')}\t{kind}\t{' '.join(asked.split())}\t{len(text) // 4}\t{','.join(ids)}\n")
