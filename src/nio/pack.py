"""Context packs: the memory that applies to a piece of work, as markdown an agent reads before it starts."""
from nio import index, query, records

# ponytail: provisional cap on text-only lines; calibrate on the first ~30 real records
TEXT_LINES = 10
FULL_TYPES = ("decision", "lesson")  # verdicts and change requests show as lines and links, never in full

# standing -> (weight, what it means for the agent); the pack prints only the standings it contains
WEIGHTS = {
    "approved": ("binding", "the jury confirmed it. Follow it; to go against it, write a change request first (@nio:remember)"),
    "current": ("strong", "in force, not jury-reviewed. Follow it; going against it also needs a change request"),
    "uncommitted": ("tentative", "written in this change, not reviewed. Usable, but it may still change"),
    "drifted": ("verify", "its code moved since it was confirmed. Check it against the code; tell the memory writer if it no longer holds"),
    "challenged": ("disputed", "a change request is pending against it. Ask the human before relying on it"),
    "escalated": ("undecided", "the jury could not settle it. Treat the question as open; ask the human"),
    "conflict": ("blocked", "two records contradict each other. Stop and ask the human which holds"),
}

WORKER = """- The records above apply to this work. Weigh each by its standing (map below).
- To go against an approved or current record, write a change request first (@nio:remember).
- Before editing a file not covered here, run: nio query --path <file>
- When you finish, end your reply with: memory-used: <IDs you relied on, or none>"""

JUROR = """- You are judging a diff. Reject it if it contradicts an approved or current record above without a change request against that record.
- Weigh each record by its standing (map below); a drifted record may no longer hold, so check it against the code.
- End your verdict with: memory-used: <IDs you relied on, or none>"""


def build(root, text, paths=(), acs=(), task="", diff=None, worker=True, reader="", slug=""):
    """Return (markdown, IDs in the pack). Tier A: records on the scope's files, AC or task, in full.
    Tier B: records related only by text, as index lines. `worker=False` leaves out the closing instructions to the
    worker: a task's worker card carries its own (implement-stage CT-6)."""
    paths = list(paths)
    if diff:
        paths += [f for f in records.git(root, "diff", "--name-only", diff) if f not in paths]
    hits = query.search(root, text, paths, limit=None, show_all=True)
    db = index.connect(root)
    nodes = {r[0]: r[1:] for r in db.execute("select id, type, standing, title from nodes where kind = 'record'")}
    nodes.update({h[0]: (h[1], h[2], h[5]) for h in hits})  # the grep fallback works without the index
    at = {}
    if diff:  # judge against memory as it stood before the diff, or the diff itself reads as drift
        at = index.standings_at(root, diff)
        nodes = {rid: (t, at.get(rid, s), title) for rid, (t, s, title) in nodes.items()}
    keys = [(rel, k) for rel, ks in (("serves", acs), ("task", [task] if task else [])) for k in ks]
    linked = {src for rel, k in keys for (src,) in db.execute("select src from edges where rel = ? and dst = ?", (rel, k))}

    tiers, seen = {"A": [], "B": []}, set()
    for rid, _, _, _, shared, _, _ in hits:
        tier = "A" if shared or rid in linked else "B"
        for rid in live(db, rid, nodes[rid][1]):  # a superseded record gives way to what replaced it; a rejected one drops out
            if rid not in seen and rid in nodes:
                seen.add(rid)
                tiers[tier].append((rid, *nodes[rid], shared if tier == "A" else []))
    tiers["B"] = tiers["B"][:TEXT_LINES]

    out, used = [], set()
    full = [h for h in tiers["A"] if h[1] in FULL_TYPES]
    shown = {h[0] for h in full}
    about = lambda rid: {d for (d,) in db.execute("select dst from edges where src = ? and rel in ('subject', 'against')", (rid,))}
    # a verdict or change request on a record printed in full is already a link under it
    lines = [h for h in [h for h in tiers["A"] if h[1] not in FULL_TYPES] + tiers["B"] if not about(h[0]) & shown]
    if full:
        out.append("## On your files, AC and task\n")
        for rid, rtype, standing, title, shared in full:
            out.append(f"### {rid} {rtype} {standing}: {title}" + (f"  [shares {', '.join(shared)}]" if shared else ""))
            out += [f"- {link}" for link in query.links(db, rid, at)]
            found = sorted((root / ".nio/memory").glob(f"*/{rid}-*.md"))
            out += [f"##{l}" if l.startswith("## ") else l for l in records.parse(found[0])[1]] + [""]  # nest under the record
            used.add(standing)
    if lines:
        out.append("## Related (open with `nio get <ID>`)\n")
        for rid, rtype, standing, title, shared in lines:
            out.append(f"- {rid} {rtype} {standing}: {title}" + (f"  [shares {', '.join(shared)}]" if shared else ""))
            out += [f"    - {link}" for link in query.links(db, rid, at)]
            used.add(standing)
        out.append("")
    db.close()
    if not full and not lines:
        out.append("Memory has nothing on this work. Carry on.\n")
    if reader:
        from nio import onboard
        docs = onboard.docs_for(root, reader, slug)
        if docs:
            out += [docs]
    if diff or worker:
        out += ["## How to use this\n", JUROR if diff else WORKER, ""]
    shown = [s for s in WEIGHTS if s in used]
    if shown:
        means = lambda s: WEIGHTS[s][1] if diff or worker else WEIGHTS[s][1].replace(" (@nio:remember)", "")
        out += ["## Standings in this pack\n"] + [f"- `{s}` ({WEIGHTS[s][0]}): {means(s)}" for s in shown]

    body = "\n".join(out).rstrip() + "\n"
    ids = [h[0] for h in full + lines]
    head = (f"# Memory for {task or text}\n\n{len(full)} in full, {len(lines)} as lines, about {len(body) // 4:,} tokens. "
            "Generated by `nio pack`; the records in .nio/memory are the truth.\n\n")
    return head + body, ids


def live(db, rid, standing):
    """The record itself, or for a superseded one the records that replaced it, followed until one still holds."""
    if standing not in query.HIDDEN:
        return [rid]
    if standing == "rejected":
        return []
    out = []
    for (new, new_standing) in db.execute(
        "select e.src, n.standing from edges e join nodes n on n.id = e.src where e.rel = 'supersedes' and e.dst = ?", (rid,)
    ):
        out += live(db, new, new_standing)
    return out


def save(root, run, name, text):
    """Write the pack under the run; returns its path."""
    folder = root / ".nio/runs" / run
    if not folder.is_dir():
        raise ValueError(f"no run `{run}`; start one with `nio run`")
    path = folder / "packs" / f"{name}.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text(text)
    return path
