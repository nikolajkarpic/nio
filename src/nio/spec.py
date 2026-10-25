"""Specs (#20): create .nio/specs/<slug>/spec.md from a template, and run the mechanical checks of #21 on it:
structure, permanent IDs, provenance, AC coverage, SHALL statements, and complete state and decision tables."""
import itertools
import re
from importlib import resources

from nio import records

ROUTES = {
    "full": {"mandatory": ["Summary", "Actors and journeys", "User stories", "Functional requirements", "Non-goals", "Decisions"],
             "ids": {"A", "UJ", "US", "AC", "FR", "NFR", "SC"}, "template": "spec"},
    "lite": {"mandatory": ["Summary", "Current behaviour", "Expected behaviour", "Unchanged behaviour", "Acceptance criteria"],
             "ids": {"CB", "EB", "UB", "AC"}, "template": "spec-bugfix"},
    "epic": {"mandatory": ["Summary", "Actors and journeys", "Roadmap", "Non-goals"], "ids": {"A", "UJ", "R"}, "template": "spec-epic"},
}
OPTIONAL = ["Rules", "Key entities", "Non-functional requirements", "Success criteria", "Glossary", "Risks and evidence against",
            "Decisions", "Open points"]
RISKS = {"auth", "pii", "money", "external-input", "data-deletion", "migration", "multi-party", "public-api"}
# #47's triggers; `money` isn't in its mapping, so it brings in the adversary (abuse of payments)
LENSES = {"adversary": {"external-input", "multi-party", "public-api", "money"}, "security": {"auth", "pii"},
          "risk-rollback (plan gate)": {"migration", "data-deletion"}}
SCOPE_FRS = 8  # more FRs than this triggers the scope lens (#47)
TAGGED = {"A", "UJ", "US", "AC", "FR", "NFR", "SC", "CB", "EB", "UB"}  # items that must carry provenance
SHALL = {"FR", "EB", "UB"}
LEVELS = {"unit", "integration", "e2e"}
TAG = re.compile(r"\[(human|default|research: RF-\d+)\]\s*$")
# a spec ID is not followed by another dash, so a memory record ID like **D-261025-k2m4** isn't read as one
DEF = re.compile(r"^(?:- )?\*\*([A-Z]+-\d+)(?![-\w])[^*]*\*\*|^### ([A-Z]+-\d+)(?![-\w])")
CITE = re.compile(r"^\(([A-Z]+-\d+(?:,\s*[A-Z]+-\d+)*)\)")


def path(root, slug):
    return root / ".nio/specs" / slug / "spec.md"


def new(root, slug, route="full", epic=""):
    """Create the spec from its route's template and return the path."""
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        raise ValueError("slug must be lowercase words joined by dashes")
    out = path(root, slug)
    if out.exists():
        raise ValueError(f"{out.relative_to(root)} already exists")
    text = resources.files("nio").joinpath(f"templates/{ROUTES[route]['template']}.md").read_text()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text.replace("<slug>", slug).replace('epic: ""', f'epic: "{epic}"'))
    return out


def sections(body):
    """{## heading: [lines]} in order."""
    out, name = {}, None
    for line in body:
        if line.startswith("## "):
            name = line[3:].strip()
            out[name] = []
        elif name:
            out[name].append(line)
    return out


def items(lines):
    """[(id, [lines])]: each definition (`**FR-1**`, `### US-1`) with the lines up to the next one or a subheading."""
    out = []
    for line in lines:
        m = DEF.match(line)
        if m:
            out.append((m[1] or m[2], [line]))
        elif out and line.startswith("#"):
            out.append((None, []))  # a subheading ends the item
        elif out and out[-1][0]:
            out[-1][1].append(line)
    return [(i, ls) for i, ls in out if i]


def table(lines):
    """Rows of the first markdown table in `lines`, header first, separator dropped."""
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in lines if line.strip().startswith("|")]
    return [r for r in rows if not all(re.fullmatch(r":?-{3,}:?", c) for c in r)]


def subsections(lines):
    """[(### heading, [lines])] inside one section."""
    out = []
    for line in lines:
        if line.startswith("### "):
            out.append((line[4:].strip(), []))
        elif out:
            out[-1][1].append(line)
    return out


def check_state(name, rows):
    errs, m = [], re.match(r"^(.+?)\s*\(start:\s*([^;]+);\s*final:\s*([^)]+)\)$", name)
    if not m:
        return [f"state table `{name}`: heading must be `State table: <name> (start: <state>; final: <state>, …)`"]
    title, start, finals = m[1], m[2].strip(), {f.strip() for f in m[3].split(",")}
    if len(rows) < 2 or rows[0][0].lower() != "state" or rows[0][-1] != "Src":
        return [f"state table {title}: the first column is `State` and the last is `Src`"]
    events, states = rows[0][1:-1], {r[0] for r in rows[1:]}
    errs += [f"state table {title}: `{s}` is not a row" for s in {start} | finals if s not in states]
    edges = {}
    for r in rows[1:]:
        if len(r) != len(rows[0]):
            errs.append(f"state table {title} row {r[0]}: {len(r)} cells, the header has {len(rows[0])}")
            continue
        if not TAG.search(r[-1]):
            errs.append(f"state table {title} row {r[0]}: `Src` must be [human], [default] or [research: RF-n]")
        for event, cell in zip(events, r[1:-1]):
            go = re.fullmatch(r"(?:→|->)\s*(.+)", cell)
            if go:
                if go[1].strip() not in states:
                    errs.append(f"state table {title}: {r[0]} × {event} goes to `{go[1].strip()}`, which is not a row")
                edges.setdefault(r[0], set()).add(go[1].strip())
            elif cell != "ignore" and not re.fullmatch(r"reject:\s*\S.*", cell):
                errs.append(f"state table {title}: {r[0]} × {event} must be `→ <state>`, `ignore` or `reject: <why>`, got `{cell}`")
    seen, todo = {start}, [start]
    while todo:
        for nxt in edges.get(todo.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    errs += [f"state table {title}: `{s}` can't be reached from `{start}`" for s in sorted(states - seen)]
    errs += [f"state table {title}: `{s}` has no way out and isn't final" for s in sorted(states - finals) if not edges.get(s)]
    return errs


def check_decision(title, rows):
    if len(rows) < 2 or rows[0][-1] != "Src":
        return [f"decision table {title}: needs a header and rows, and the last column is `Src`"]
    errs, conds, outs = [], [], []
    for i, h in enumerate(rows[0][:-1]):
        if h.startswith("→") or h.startswith("->"):
            outs.append(i)
        elif m := re.fullmatch(r"(.+?)\s*\((.+)\)", h):
            conds.append((i, m[1], [v.strip() for v in m[2].split(",")]))
        else:
            errs.append(f"decision table {title}: condition `{h}` must list its values, e.g. `{h} (a, b)`")
    if not outs:
        errs.append(f"decision table {title}: needs at least one `→ <output>` column")
    if errs:
        return errs
    good = []
    for r in rows[1:]:
        label = " / ".join(r[i] for i, _, _ in conds)
        if len(r) != len(rows[0]):
            errs.append(f"decision table {title} row {label}: {len(r)} cells, the header has {len(rows[0])}")
            continue
        bad = [f"`{r[i]}` is not a value of {name}" for i, name, vals in conds if r[i] != "-" and r[i] not in vals]
        bad += [f"output `{rows[0][i]}` is empty" for i in outs if not r[i]]
        bad += ["`Src` must be [human], [default] or [research: RF-n]"] * (not TAG.search(r[-1]))
        errs += [f"decision table {title} row {label}: {b}" for b in bad]
        good.append(r)
    for combo in itertools.product(*[vals for _, _, vals in conds]):
        hits = [r for r in good if all(r[i] in ("-", v) for (i, _, _), v in zip(conds, combo))]
        case = ", ".join(f"{name}={v}" for (_, name, _), v in zip(conds, combo))
        if not hits:
            errs.append(f"decision table {title}: gap, no row covers {case}")
        elif len(hits) > 1:
            errs.append(f"decision table {title}: overlap, {len(hits)} rows match {case} (the hit policy is Unique)")
    return errs


def defined(text):
    """{id: normalised text} for every item defined in a spec's text, for the renumbering check."""
    out = {}
    for line in text.splitlines():
        if m := DEF.match(line):
            words = re.sub(r"\*\*|\[[^\]]*\]\s*$|[A-Z]+-\d+", "", line)
            out[m[1] or m[2]] = " ".join(words.split()).lower()
        elif m := re.match(r"^\|\s*(R-\d+)\s*\|", line):
            out[m[1]] = " ".join(line.split("|")[2].split()).lower()
    return out


def check(root, slug, gate=False, base="HEAD"):
    """(errors, notes) for one spec. Notes list the lenses its risk flags and size trigger."""
    p = path(root, slug)
    if not p.exists():
        raise ValueError(f"no spec at {p.relative_to(root)}")
    rel = p.relative_to(root)
    try:
        meta, body = records.parse(p)
    except ValueError as e:
        return [f"{rel}: {e}"], []
    errs = []
    route = meta.get("route")
    if route not in ROUTES:
        return [f"{rel}: `route` must be one of {sorted(ROUTES)}"], []
    if meta.get("slug") != slug:
        errs.append(f"`slug` must be `{slug}`, the folder name")
    risk = meta.get("risk")
    if not isinstance(risk, list) or any(r not in RISKS for r in risk):
        errs.append(f"`risk` must be a list from {sorted(RISKS)}, or []")
        risk = [r for r in risk or [] if r in RISKS] if isinstance(risk, list) else []
    retired = meta.get("retired") or []
    secs = sections(body)
    allowed = ROUTES[route]["mandatory"] + OPTIONAL
    errs += [f"section `## {s}` is not part of a {route} spec" for s in secs if s not in allowed]
    for s in ROUTES[route]["mandatory"]:
        if not "\n".join(secs.get(s, [])).strip():
            errs.append(f"section `## {s}` is missing or empty")
    for s, lines in secs.items():
        if re.fullmatch(r"(n/?a|none|tbd|-)\.?", "\n".join(lines).strip().lower()):
            errs.append(f"section `## {s}` says N/A; remove a section that doesn't apply")
        if any(re.search(r"<[a-z][^>]*>", line) for line in lines):
            errs.append(f"section `## {s}` still has template `<placeholders>`")

    found = {}
    for s, lines in secs.items():
        for iid, block in items(lines):
            found.setdefault(iid, []).append((s, block))
        if s == "Roadmap":
            for r in table(lines)[1:]:
                found.setdefault(r[0], []).append((s, [" | ".join(r)]))
    for iid, defs in found.items():
        prefix = iid.split("-")[0]
        if len(defs) > 1:
            errs.append(f"{iid} is defined {len(defs)} times")
        if prefix not in ROUTES[route]["ids"]:
            errs.append(f"{iid}: `{prefix}` IDs don't belong in a {route} spec ({', '.join(sorted(ROUTES[route]['ids']))})")
        if iid in retired:
            errs.append(f"{iid} is retired and can't be used again")
        s, block = defs[0]
        if prefix in TAGGED and not TAG.search(block[0]):
            errs.append(f"{iid}: its line must end with [human], [default] or [research: RF-n]")
        if prefix in SHALL and "SHALL" not in block[0]:
            errs.append(f"{iid}: state it with SHALL (EARS: THE SYSTEM SHALL, WHEN … THE SYSTEM SHALL, IF … THEN …)")
        if prefix == "US":
            text = "\n".join(block)
            if not re.search(r"\(P\d+\)", block[0]):
                errs.append(f"{iid}: the heading needs a priority, e.g. `(P1)`")
            errs += [f"{iid}: needs `{k}`" for k in ("Why this priority", "Independent test") if k not in text]
        if prefix == "AC":
            errs += check_ac(iid, block, found, route)
    for line in secs.get("Non-goals", []):
        if line.startswith("- ") and not TAG.search(line):
            errs.append(f"non-goal `{line[2:40]}…` must end with [human], [default] or [research: RF-n]")
    targets = {"full": ["FR"], "lite": ["EB", "UB"]}.get(route, [])
    cited = {c for iid, defs in found.items() if iid.startswith("AC-") for c in cites(defs[0][1][0])}
    errs += [f"{iid} has no AC" for iid in found if iid.split("-")[0] in targets and iid not in cited]

    for name, lines in subsections(secs.get("Rules", [])):
        rows = table(lines)
        if name.startswith("State table:"):
            errs += check_state(name[len("State table:"):].strip(), rows)
        elif name.startswith("Decision table:"):
            errs += check_decision(name[len("Decision table:"):].strip(), rows)
        else:
            errs.append(f"`### {name}` in Rules must be a `State table:` or a `Decision table:`")

    if gate:
        for line in body:  # name each one, so the grill can ask about it
            if "[default]" in line:
                m = DEF.match(line)
                what = (m[1] or m[2]) if m else f"`{line.strip()[:50]}`"
                errs.append(f"{what} is still [default]; the grill must confirm it ([human]) or research must back it")
        if "\n".join(secs.get("Open points", [])).strip():
            errs.append("`## Open points` must be empty at the gate")
    errs += history(root, rel, found, retired, base)

    lenses = ["testability", "logic"] + [lens for lens, flags in LENSES.items() if flags & set(risk)]
    if sum(i.startswith("FR-") for i in found) > SCOPE_FRS:
        lenses.append(f"scope (more than {SCOPE_FRS} FRs)")
    return [f"{rel}: {e}" for e in errs], [f"lenses: {', '.join(lenses)}"]


def cites(line):
    rest = DEF.sub("", line, count=1).strip()
    m = CITE.match(rest)
    return [c.strip() for c in m[1].split(",")] if m else []


def check_ac(iid, block, found, route):
    errs, text, refs = [], "\n".join(block), cites(block[0])
    want = {"full": {"FR"}, "lite": {"EB", "UB"}}.get(route, set())
    if not refs:
        errs.append(f"{iid}: cite what it tests right after the ID, e.g. `**{iid}** ({'FR-1' if route == 'full' else 'EB-1'})`")
    for r in refs:
        if r not in found:
            errs.append(f"{iid} cites {r}, which isn't defined")
        elif r.split("-")[0] not in want:
            errs.append(f"{iid} cites {r}; an AC cites {' or '.join(sorted(want))}")
    if not re.search(r"\bGiven\b.*\bwhen\b.*\bthen\b", text, re.I | re.S):
        errs.append(f"{iid}: needs Given / when / then")
    if not re.search(r"Observable:\s*\S", text):
        errs.append(f"{iid}: needs `Observable:` (what the test asserts)")
    level = re.search(r"Level:\s*([a-z0-9]+)", text)
    if not level or level[1] not in LEVELS:
        errs.append(f"{iid}: needs `Level:` {' | '.join(sorted(LEVELS))}")
    return errs


def history(root, rel, found, retired, base):
    """IDs are permanent: one defined at `base` must still be defined or be retired, and its text can't move to another ID."""
    old_text = "\n".join(records.git(root, "show", f"{base}:{rel}"))
    if not old_text:
        return []
    try:
        old_meta, _ = records.parse(rel, old_text + "\n")
    except ValueError:
        return []
    old, now = defined(old_text), defined(path(root, rel.parent.name).read_text())
    errs = [f"{iid} was removed without being retired; add it to `retired:` (IDs are never reused)"
            for iid in old if iid not in now and iid not in retired]
    errs += [f"{iid} was retired at {base} and can't be brought back" for iid in old_meta.get("retired") or [] if iid in now]
    errs += [f"{other} now has {iid}'s text from {base}: renumbered? IDs are permanent" for iid, text in old.items()
             for other, t in now.items() if other != iid and text and t == text and now.get(iid) != text]
    return errs
