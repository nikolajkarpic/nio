"""Find records: hybrid full-text and vector search, or every record touching given files."""
import re

from nio import index

# looser than the CI duplicate warning: a false alarm before writing costs one read, a duplicate lasts forever
DEDUP_SIMILARITY = 0.85
HIDDEN = ("superseded", "rejected")
RRF_K = 60  # standard reciprocal-rank-fusion constant


def search(root, text="", paths=(), limit=10, show_all=False):
    """Return [(id, type, standing, similarity or None, shared paths, title)], best first.

    Refreshes the index first, so a record written minutes ago is found."""
    index.build(root)
    db = index.connect(root)
    touching = {}
    for src, dst in db.execute(f"select src, dst from edges where rel = 'touches' and dst in ({','.join('?' * len(paths))})", list(paths)):
        touching.setdefault(src, []).append(dst)
    sims, score = {}, {}
    if text:
        words = re.findall(r"\w+", text)
        fts = db.execute("select id from fts where fts match ? order by rank", (" OR ".join(f'"{w}"' for w in words),)).fetchall() if words else []
        model, _ = index.settings(root)
        q = index.embed(model, [text])[0]
        # ponytail: brute-force cosine over every vector; a vec0 KNN index once records reach the tens of thousands
        sims = dict(db.execute("select id, 1 - vec_distance_cosine(vec_int8(embedding), vec_int8(?)) from vec", (q,)))
        for ranked in ([r[0] for r in fts], sorted(sims, key=sims.get, reverse=True)):
            for i, rid in enumerate(ranked):
                score[rid] = score.get(rid, 0) + 1 / (RRF_K + i + 1)
    else:
        score = {rid: 1 for rid in touching}
    for rid in touching:
        score[rid] = score.get(rid, 0) + 1 / RRF_K  # sharing files with the question counts as one top hit
    rows = {r[0]: r for r in db.execute("select id, type, standing, title from nodes where kind = 'record'")}
    db.close()
    out = []
    for rid in sorted(score, key=score.get, reverse=True):
        rtype, standing, title = rows[rid][1:]
        if standing in HIDDEN and not show_all:
            continue
        out.append((rid, rtype, standing, sims.get(rid), sorted(touching.get(rid, [])), title))
    return out[:limit]


def format_hit(rid, rtype, standing, sim, shared, title):
    mark = "≈ " if sim is not None and sim >= DEDUP_SIMILARITY else "  "
    sim_s = f"{sim:.2f}" if sim is not None else "  - "
    return f"{mark}{rid} {rtype} {standing} {sim_s} {title}" + (f"  [shares {', '.join(shared)}]" if shared else "")
